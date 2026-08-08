'use strict';

// Reusable written-files validator for promptfoo `javascript` asserts.
//   assert:
//     - type: javascript
//       value: file://../../_lib/asserts/files.js
// Reads the files-mode manifest the provider emits — `<file path="…">\n…\n</file>` blocks, one
// per file the run created or modified (see _lib/claude_provider.py) — and checks WHICH files
// exist and that each is substantial. WHAT is inside one is document.js's job.
// Params come from the assertion's own `config:` block, so one test can call this module more
// than once (e.g. one call per expected document) with the params next to each call:
//     - type: javascript
//       value: file://../../_lib/asserts/files.js
//       config:
//         expect: [{path: 'features/.+/index\.md$', minLines: 15}]
// `metadata.files` still works as a fallback. Either way the params are NOT vars — vars are
// the only thing the judge sees, and it must stay judge-blind.
// Params:
//   expect     : [{path, count, minLines, maxLines, contains, forbids, links}]
//                path     : string   regex the written path must match (required)
//                count    : number   exact number of files matching it (default 1)
//                minLines : number   every match carries >= n non-blank content lines
//                maxLines : number   … and <= n
//                contains : string[] regexes the file's content must match
//                forbids  : string[] regexes the file's content must NOT match
//                links    : {to, label, min}  the file must link ANOTHER written file:
//                           to    : string  regex the linked file's written path must match
//                           label : string  regex the link text must match (optional)
//                           min   : number  how many such links (default 1)
//                           Markdown `[text](target)` and wiki `[[target]]` / `[[target|text]]`
//                           are both read; a relative target is resolved against the linking
//                           file's own directory before comparing, and a target written without
//                           its `.md` extension (the wiki-link habit) still matches the file.
//   allow      : string[]  regexes for files the run MAY write but need not (e.g. the parent
//                index it links the new document into)
//   noOthers   : boolean   a written path matching neither expect nor allow fails (default true)
//   onTextMode : 'pass' | 'fail'  verdict when the output carries no manifest at all — probe
//                ladders run in text mode and have no files (default 'pass')
// Returns a promptfoo GradingResult { pass, score, reason }.

const fail = (reason) => ({ pass: false, score: 0, reason });
const ok = (reason) => ({ pass: true, score: 1, reason });

const BLOCK_RE = /^[ \t]*<file path="([^"]+)">\n([\s\S]*?)\n<\/file>[ \t]*$/gm;

function parseManifest(output) {
  const files = [];
  BLOCK_RE.lastIndex = 0;
  let m;
  while ((m = BLOCK_RE.exec(output)) !== null) {
    const content = m[2];
    files.push({
      path: m[1],
      content,
      lines: content.split('\n').filter((l) => l.trim()).length,
    });
  }
  return files;
}

// `a/b/../c.md` -> `a/c.md`; leading `./` and duplicate slashes dropped.
function resolvePath(dir, target) {
  const parts = (dir ? dir.split('/') : []).concat(String(target).split('/'));
  const out = [];
  for (const p of parts) {
    if (!p || p === '.') continue;
    if (p === '..') out.pop();
    else out.push(p);
  }
  return out.join('/');
}

// Markdown `[text](target)` plus wiki `[[target]]` / `[[target|text]]`.
function linksIn(content) {
  const found = [];
  for (const m of content.matchAll(/\[([^\]\n]*)\]\(([^)\s]+)[^)]*\)/g))
    found.push({ text: m[1], target: m[2] });
  for (const m of content.matchAll(/\[\[([^\]|\n]+)(?:\|([^\]\n]+))?\]\]/g))
    found.push({ text: m[2] || m[1], target: m[1] });
  return found;
}

function checkLinks(file, spec, files) {
  const toRe = new RegExp(spec.to);
  const labelRe = spec.label ? new RegExp(spec.label) : null;
  const min = spec.min != null ? spec.min : 1;
  const dir = file.path.includes('/') ? file.path.slice(0, file.path.lastIndexOf('/')) : '';
  const targets = files.filter((f) => f.path !== file.path && toRe.test(f.path));
  if (!targets.length) return fail('`' + file.path + '`: no other written file matches /' + spec.to + '/ to link to');

  const links = linksIn(file.content);
  const hits = links.filter((l) => {
    const bare = String(l.target).replace(/^\.\//, '').replace(/#.*$/, '');
    // a wiki link usually drops the extension — `[[features/x/stories]]` is that file
    const forms = /\.[a-z]+$/i.test(bare) ? [bare] : [bare, bare + '.md'];
    return forms.some((t) =>
      targets.some((f) => resolvePath(dir, t) === f.path || f.path === t || f.path.endsWith('/' + t))
    );
  });
  if (hits.length < min)
    return fail(
      '`' + file.path + '` does not link `' + targets.map((f) => f.path).join('`, `') + '`' +
        (links.length ? ' — links found: ' + links.map((l) => l.target).join(', ') : ' — no links at all')
    );
  if (labelRe && !hits.some((l) => labelRe.test(l.text)))
    return fail(
      '`' + file.path + '` links the file but the link text does not match /' + spec.label + '/: ' +
        hits.map((l) => '“' + l.text + '”').join(', ')
    );
  return ok('links ' + hits.map((l) => l.target).join(', '));
}

function validate(output, opts = {}) {
  const files = parseManifest(output);
  if (!files.length)
    return (opts.onTextMode || 'pass') === 'fail'
      ? fail('No files written (no `<file path="…">` manifest in the output)')
      : ok('Text mode — no file manifest to check');

  const expect = opts.expect || [];
  const matched = new Set();

  for (const spec of expect) {
    const re = new RegExp(spec.path);
    const hits = files.filter((f) => re.test(f.path));
    const want = spec.count != null ? spec.count : 1;
    if (hits.length !== want)
      return fail(
        'Expected ' + want + ' file(s) matching /' + spec.path + '/, got ' + hits.length +
          ' — written: ' + files.map((f) => f.path).join(', ')
      );
    for (const h of hits) {
      matched.add(h.path);
      if (spec.minLines != null && h.lines < spec.minLines)
        return fail('`' + h.path + '` carries ' + h.lines + ' non-blank line(s), expected >= ' + spec.minLines);
      if (spec.maxLines != null && h.lines > spec.maxLines)
        return fail('`' + h.path + '` carries ' + h.lines + ' non-blank line(s), expected <= ' + spec.maxLines);
      for (const p of spec.contains || [])
        if (!new RegExp(p, 'm').test(h.content)) return fail('`' + h.path + '` does not match /' + p + '/');
      for (const p of spec.forbids || []) {
        const m = new RegExp(p, 'm').exec(h.content);
        if (m) return fail('`' + h.path + '` matches forbidden /' + p + '/: ' + String(m[0]).trim().slice(0, 60));
      }
      if (spec.links) {
        const r = checkLinks(h, spec.links, files);
        if (!r.pass) return r;
      }
    }
  }

  if (opts.noOthers !== false) {
    const allowed = (opts.allow || []).map((p) => new RegExp(p));
    const extra = files.filter((f) => !matched.has(f.path) && !allowed.some((re) => re.test(f.path)));
    if (extra.length) return fail('Unexpected file(s) written: ' + extra.map((f) => f.path).join(', '));
  }

  return ok(files.map((f) => f.path + ' (' + f.lines + ' lines)').join(', '));
}

module.exports = (output, context) => {
  const ctx = context || {};
  const meta = (ctx.test && ctx.test.metadata) || ctx.metadata || {};
  const opts = ctx.config && Object.keys(ctx.config).length ? ctx.config : meta.files || {};
  return validate(output, opts);
};
module.exports.validate = validate;
