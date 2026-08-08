'use strict';

// Bridge from a promptfoo `javascript` assert to the `mdcheck` binary — the deterministic
// markdown-structure checker (https://github.com/A/markdown-checker, `cargo install`).
//   assert:
//     - type: javascript
//       value: file://../../_lib/asserts/mdcheck.js
//       config:
//         file: 'index\.md$'
//         rules: |
//           - select: FRONTMATTER
//             has: { confirmed: { enum: [no] } }
//           - select: H1 > H2
//             ordered: [Roles, Features]
//             strict: true
// The structure spec is DECLARED in the test case and executed by mdcheck. This module owns
// none of it: it materializes what the run produced into a temp tree, calls the binary, and
// maps the findings back to a promptfoo GradingResult. Nothing here knows what a rule means,
// which is the point — a new document shape needs a new `rules:` block, never new JS.
//
// Materializing is not a workaround for the files-mode wrapper, it removes a whole class of
// bug: an answer whose `<return>` repeats the document (they do) is TWO copies of every table
// row to a regex-over-the-raw-output assert, and one document to mdcheck.
//
// Params come from the assertion's own `config:` block, so one test can call this module more
// than once (one call per written file) with the params next to each call. `metadata.mdcheck`
// works as a fallback. Either way the params are NOT vars — vars are the only thing the judge
// sees, and it must stay judge-blind.
// Params:
//   rules        : string   mdcheck rule YAML. A bare `- select: …` list is wrapped in
//                  `doc:`/`rules:`; a full rule file (its own `rules:` key) passes through.
//                  NEVER parsed here — it reaches a temp file verbatim, so the rule language
//                  stays mdcheck's alone and this module carries no YAML dependency.
//   file         : string   regex picking which written file to check out of the files-mode
//                  manifest. With exactly one written file it may be omitted; with several,
//                  omitting it is an error — name the one you mean.
//   on           : 'file' | 'return'  check a written artifact (default) or the trailing
//                  `<return>` body, which is markdown too — headings, lists, the lot.
//   allowMissing : boolean  pass vacuously when nothing matches (default false). What a
//                  text-mode probe run needs when the rules are written for files mode.
//   maxFindings  : number   findings quoted in the failure reason (default 12); the count is
//                  always reported in full.
//   bin          : string   mdcheck executable (default `$MDCHECK_BIN` or `mdcheck` on PATH)
// Returns a promptfoo GradingResult { pass, score, reason }.
//
// Exit codes are mdcheck's: 0 clean, 1 findings, 2 usage/rule-file/selector error, 3 internal.
// A 2 or 3 fails LOUDLY as a rules error — a rule file that will not load must never read as a
// clean document.

const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const fail = (reason) => ({ pass: false, score: 0, reason });
const ok = (reason) => ({ pass: true, score: 1, reason });

const FILE_RE = /^[ \t]*<file path="([^"]+)">\n([\s\S]*?)\n<\/file>[ \t]*$/gm;
const RETURN_RE = /^[ \t]*<return>\n([\s\S]*?)\n<\/return>[ \t]*$/m;

function parseManifest(output) {
  const files = [];
  FILE_RE.lastIndex = 0;
  let m;
  while ((m = FILE_RE.exec(output)) !== null) files.push({ path: m[1], content: m[2] });
  return files;
}

// The manifest paths come from the model, and we are about to write them to disk. Anything
// absolute or climbing out of the temp tree is refused rather than sanitized — a step that
// wrote there is a finding of its own, not something to quietly relocate.
function safeRelative(p) {
  if (!p || path.isAbsolute(p) || /^[a-zA-Z]:/.test(p)) return null;
  const norm = path.normalize(p);
  if (norm === '..' || norm.startsWith('..' + path.sep) || norm.startsWith('/')) return null;
  return norm;
}

// A bare rule list is the common case in a test file — wrap it so the case carries only the
// rules and none of the rule-file ceremony. A block that already declares `rules:` at column 0
// is a whole rule file and is left exactly as written.
function ruleFileText(rules, docName) {
  if (/^rules:/m.test(rules)) return rules;
  const indented = rules
    .split('\n')
    .map((l) => (l.trim() ? '  ' + l : l))
    .join('\n');
  return `doc: ${docName}\nrules:\n${indented}\n`;
}

function validate(output, opts = {}) {
  if (typeof opts.rules !== 'string' || !opts.rules.trim())
    return fail('mdcheck assert has no `rules:` — the structure spec belongs in the test case');

  const on = opts.on || 'file';
  const files = parseManifest(output);
  const returnMatch = output.match(RETURN_RE);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'mdcheck-'));
  const tree = path.join(root, 'tree');

  try {
    // Every written file lands in the tree whatever we are checking: `--root` points at it, so
    // a `resolve: true` rule on links reaches the run's OWN siblings, not this machine's disk.
    fs.mkdirSync(tree, { recursive: true });
    for (const f of files) {
      const rel = safeRelative(f.path);
      if (!rel) return fail('The run wrote a path outside its working directory: ' + f.path);
      const dest = path.join(tree, rel);
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, f.content, 'utf8');
    }

    let target;
    let docName;
    if (on === 'return') {
      if (!returnMatch)
        return opts.allowMissing
          ? ok('No <return> block (allowMissing)')
          : fail('The answer carries no <return> block');
      // Outside the tree, so the return is never mistaken for an artifact the step wrote,
      // while `--root tree` still resolves the paths it links to.
      target = path.join(root, '__return__.md');
      fs.writeFileSync(target, stripFence(returnMatch[1]), 'utf8');
      docName = 'return';
    } else if (files.length) {
      const re = opts.file ? new RegExp(opts.file) : null;
      const hits = re ? files.filter((f) => re.test(f.path)) : files;
      if (!hits.length)
        return opts.allowMissing
          ? ok('No written file matches ' + opts.file + ' (allowMissing)')
          : fail('No written file matches `' + opts.file + '`. Written: ' + files.map((f) => f.path).join(', '));
      if (hits.length > 1)
        return fail(
          (opts.file ? '`' + opts.file + '` matches ' : 'The run wrote ') +
            hits.length +
            ' files (' + hits.map((f) => f.path).join(', ') +
            ') — name the one these rules describe with `file:`',
        );
      target = path.join(tree, safeRelative(hits[0].path));
      docName = path.basename(hits[0].path, '.md');
    } else {
      // Text mode: no manifest, the answer IS the document. Probe ladders run this way.
      if (opts.allowMissing) return ok('No files-mode manifest (allowMissing)');
      target = path.join(root, '__answer__.md');
      fs.writeFileSync(target, output.replace(RETURN_RE, '').trim() + '\n', 'utf8');
      docName = 'answer';
    }

    const rulesPath = path.join(root, 'rules.yaml');
    fs.writeFileSync(rulesPath, ruleFileText(opts.rules, docName), 'utf8');

    const bin = opts.bin || process.env.MDCHECK_BIN || 'mdcheck';
    const run = spawnSync(bin, [rulesPath, target, '--format', 'json', '--root', tree], {
      encoding: 'utf8',
      maxBuffer: 16 * 1024 * 1024,
    });

    if (run.error)
      return fail('cannot run `' + bin + '`: ' + run.error.message + ' — is mdcheck on PATH? (cargo install --git https://github.com/A/markdown-checker)');
    if (run.status === 0) return ok('mdcheck clean on ' + (docName + '.md'));
    if (run.status !== 1)
      return fail('mdcheck rules error (exit ' + run.status + '): ' + (run.stderr || '').trim().split('\n')[0]);

    let report;
    try {
      report = JSON.parse(run.stdout);
    } catch (e) {
      return fail('mdcheck emitted unparseable json: ' + (run.stdout || '').slice(0, 200));
    }
    const findings = report.findings || [];
    const cap = opts.maxFindings || 12;
    const lines = findings
      .slice(0, cap)
      .map((f) => 'line ' + f.line + ': ' + f.message)
      .join('; ');
    const more = findings.length > cap ? ' (+' + (findings.length - cap) + ' more)' : '';
    return fail(findings.length + ' mdcheck finding(s) in ' + docName + '.md — ' + lines + more);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

// A model that fences its whole return turns the body into one code block, and every structural
// rule then reports the document as empty. Strip a fence that wraps the WHOLE body only.
function stripFence(body) {
  const t = body.trim();
  const m = t.match(/^```[a-zA-Z]*\n([\s\S]*)\n```$/);
  return m ? m[1] : body;
}

module.exports = (output, context) => {
  const ctx = context || {};
  const meta = (ctx.test && ctx.test.metadata) || ctx.metadata || {};
  const opts = ctx.config && Object.keys(ctx.config).length ? ctx.config : meta.mdcheck || {};
  return validate(output, opts);
};
module.exports.validate = validate;
