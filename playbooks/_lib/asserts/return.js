'use strict';

// Reusable return-contract validator for promptfoo `javascript` asserts. In files mode the
// provider appends the step's reply as a trailing `<return>` block (see _lib/claude_provider.py);
// this checks that the reply IS the declared return format and nothing else — and, where a
// section lists file paths, that those paths agree with what the run actually wrote.
//   assert:
//     - type: javascript
//       value: file://../../_lib/asserts/return.js
//       config:
//         sections:
//           - name: Changed
//             entry: '^-\s+\[(CREATED|UPDATED)\]\s+`?([^`\s]+)`?$'
//             matchManifest: true
//             seededVar: input
//           - {name: Notes, optional: true, entry: '^-\s+\S'}
//         onlyListed: true
// Params come from the assertion's own `config:`; `metadata.return` works as a fallback.
//
// Shape params:
//   requireBlock : boolean  fail when there is no `<return>` block at all. Probe ladders run in
//                  text mode and have none, so the default (false) passes vacuously.
//   allowFence   : boolean  tolerate a ``` wrapper around the return body, stripping the fence
//                  markers before parsing (default true; set false to reject a fenced return)
//   sections     : [{…}]    the return is a set of `## <name>` sections (see below). Without it
//                  the return is parsed flat, using the same per-section keys at top level
//                  (`header` + `entry` + …), which is the older one-list contract.
//   onlyListed   : boolean  no heading outside the declared sections, and no content before the
//                  first heading (default true in section mode)
//
// Per-section (or, flat mode, top-level) params:
//   name         : string   heading text, matched case-insensitively with a trailing `:` and
//                  emphasis/backticks ignored, so `## Changed:` matches `name: Changed`
//   optional     : boolean  the section may be absent (default false)
//   header       : string   flat mode only — regex the first non-empty line must match
//   entry        : string   regex every content line must match. Capture groups are read as
//                  (1) status, (2) path — override with statusGroup / pathGroup; a single-group
//                  regex is treated as the path, a group-less one as a plain content line
//   statusGroup / pathGroup : number  capture indexes
//   statuses     : string[] allowed status tokens (case-sensitive)
//   onlyEntries  : boolean  nothing but entries and blank lines inside the section — no prose,
//                  no rationale (default true)
//   fold         : boolean  an entry may run over several lines: INDENTED continuation lines and
//                  sub-bullets fold back into the entry above before the rule runs. A line at
//                  column 0 is always its own entry, so `onlyEntries` still catches prose
//   minEntries / maxEntries : number
//   matchManifest: boolean  the section's paths are exactly the files-mode `<file …>` manifest —
//                  nothing written but unlisted, nothing listed but unwritten
//   stripPrefix  : string[] leading prefixes removed from BOTH sides before comparing, so a step
//                  that returns specs-root-relative paths still matches a cwd-relative manifest
//   seededVar    : string   name of the var carrying the seeded corpus (its `<file path="…">`
//                  blocks). With it, CREATED vs UPDATED is checked: a path seeded into the run
//                  must be UPDATED, a path that was not must be CREATED
//   createdStatus / updatedStatus : string  tokens for that check (default CREATED / UPDATED)
// Returns a promptfoo GradingResult { pass, score, reason }.

const fail = (reason) => ({ pass: false, score: 0, reason });
const ok = (reason) => ({ pass: true, score: 1, reason });

const cut = (s, n) => (s.length > n ? s.slice(0, n) + '…' : s);

const norm = (s) =>
  String(s)
    .replace(/[`*_]/g, '')
    .replace(/[.:;,\s]+$/, '')
    .trim()
    .toLowerCase();

const pathsIn = (text) => [...String(text || '').matchAll(/<file path="([^"]+)">/g)].map((m) => m[1]);

function normalizer(prefixes) {
  const list = prefixes || [];
  return (p) => {
    let s = String(p).trim().replace(/^\.\//, '').replace(/^`|`$/g, '');
    for (const pre of list) if (s.startsWith(pre)) s = s.slice(pre.length);
    return s.replace(/^\/+/, '');
  };
}

function extractReturn(output) {
  const m = /<return>\n([\s\S]*?)\n<\/return>/.exec(output);
  return m ? m[1] : null;
}

// One entry may run over several lines: a wrapped continuation and a sub-bullet under it are
// INDENTED, so they fold back into the entry above before the rule runs. A line at column 0 that
// is not an entry stays its own line — which is what keeps `onlyEntries` able to catch prose.
function foldContinuations(rawLines) {
  const out = [];
  for (const raw of rawLines) {
    if (!raw.trim()) continue;
    if (/^\s/.test(raw) && out.length) continue; // indented → belongs to the entry above
    out.push(raw.trim());
  }
  return out;
}

// One section's (or the whole flat return's) content lines against its entry contract.
function checkEntries(lines, spec, label, output, vars) {
  const entries = [];
  if (spec.entry) {
    const re = new RegExp(spec.entry);
    for (const l of lines) {
      const m = re.exec(l);
      if (!m) {
        if (spec.onlyEntries === false) continue;
        return fail(label + ': line does not match /' + spec.entry + '/: ' + cut(l, 70));
      }
      const groups = m.length - 1;
      const sIdx = spec.statusGroup != null ? spec.statusGroup : groups >= 2 ? 1 : 0;
      const pIdx = spec.pathGroup != null ? spec.pathGroup : groups >= 2 ? 2 : groups === 1 ? 1 : 0;
      entries.push({ status: sIdx ? m[sIdx] : null, path: pIdx ? m[pIdx] : null, line: l });
    }
  } else {
    for (const l of lines) entries.push({ status: null, path: null, line: l });
  }

  if (spec.statuses)
    for (const e of entries)
      if (!spec.statuses.includes(e.status))
        return fail(label + ': unknown status `' + e.status + '` (allowed: ' + spec.statuses.join(', ') + '): ' + cut(e.line, 70));

  const min = spec.minEntries != null ? spec.minEntries : spec.entry ? 1 : 0;
  if (entries.length < min) return fail(label + ': ' + entries.length + ' entry/entries, expected >= ' + min);
  if (spec.maxEntries != null && entries.length > spec.maxEntries)
    return fail(label + ': ' + entries.length + ' entries, expected <= ' + spec.maxEntries);

  const norm2 = normalizer(spec.stripPrefix);

  if (spec.matchManifest) {
    const written = pathsIn(output).map(norm2);
    if (written.length) {
      const listed = entries.filter((e) => e.path).map((e) => norm2(e.path));
      const unlisted = written.filter((p) => !listed.includes(p));
      const unwritten = listed.filter((p) => !written.includes(p));
      if (unlisted.length) return fail(label + ': file(s) written but not listed: ' + unlisted.join(', '));
      if (unwritten.length) return fail(label + ': path(s) listed but never written: ' + unwritten.join(', '));
    }
  }

  if (spec.seededVar) {
    const seeded = pathsIn(vars[spec.seededVar]).map(norm2);
    const created = spec.createdStatus || 'CREATED';
    const updated = spec.updatedStatus || 'UPDATED';
    for (const e of entries) {
      if (!e.path || (e.status !== created && e.status !== updated)) continue;
      const was = seeded.includes(norm2(e.path));
      if (was && e.status === created)
        return fail(label + ': `' + e.path + '` already existed in the corpus — expected ' + updated + ', got ' + created);
      if (!was && e.status === updated)
        return fail(label + ': `' + e.path + '` was not in the corpus — expected ' + created + ', got ' + updated);
    }
  }

  return ok(entries.map((e) => (e.status ? '[' + e.status + '] ' : '') + (e.path || cut(e.line, 30))).join(', ') || 'empty');
}

function validate(output, opts = {}, vars = {}) {
  const block = extractReturn(output);
  if (block === null)
    return opts.requireBlock
      ? fail('No `<return>` block in the output')
      : ok('No `<return>` block (text mode) — return contract not checked');

  let raw = block.split('\n');
  if (opts.allowFence === false) {
    const fenced = raw.find((l) => /^\s*(```|~~~)/.test(l));
    if (fenced) return fail('The return is fenced (```) — plain markdown expected');
  } else {
    raw = raw.filter((l) => !/^\s*(```|~~~)/.test(l));
  }
  const lines = raw.map((l) => l.trim());
  if (!lines.some(Boolean)) return fail('The `<return>` block is empty');

  // ---- flat mode: one list, no headings ----
  if (!opts.sections) {
    let rest = opts.fold ? foldContinuations(raw) : lines.filter(Boolean);
    if (opts.header) {
      if (!new RegExp(opts.header).test(rest[0]))
        return fail('First return line does not match /' + opts.header + '/: ' + cut(rest[0], 70));
      rest = rest.slice(1);
    }
    const r = checkEntries(rest, opts, 'return', output, vars);
    return r.pass ? ok(r.reason) : r;
  }

  // ---- section mode ----
  const heads = [];
  lines.forEach((l, i) => {
    const m = /^(#{1,6})\s+(.*\S)\s*$/.exec(l);
    if (m) heads.push({ level: m[1].length, name: m[2], line: i });
  });
  if (!heads.length) return fail('The return carries no `## <section>` heading');

  if (opts.onlyListed !== false) {
    const before = lines.slice(0, heads[0].line).filter(Boolean);
    if (before.length) return fail('Content before the first return section: ' + cut(before[0], 70));
    const declared = opts.sections.map((s) => norm(s.name));
    const stray = heads.filter((h) => !declared.includes(norm(h.name)));
    if (stray.length) return fail('Undeclared return section(s): ' + stray.map((h) => h.name).join(', '));
  }

  const summary = [];
  for (const spec of opts.sections) {
    const idx = heads.findIndex((h) => norm(h.name) === norm(spec.name));
    if (idx < 0) {
      if (spec.optional) continue;
      return fail('Missing return section `## ' + spec.name + '`');
    }
    const next = heads[idx + 1];
    const from = heads[idx].line + 1;
    const to = next ? next.line : undefined;
    const body = spec.fold
      ? foldContinuations(raw.slice(from, to))
      : lines.slice(from, to).filter(Boolean);
    const r = checkEntries(body, spec, '`' + spec.name + '`', output, vars);
    if (!r.pass) return r;
    summary.push(spec.name + ': ' + r.reason);
  }
  return ok(summary.join(' | '));
}

module.exports = (output, context) => {
  const ctx = context || {};
  const meta = (ctx.test && ctx.test.metadata) || ctx.metadata || {};
  const opts = ctx.config && Object.keys(ctx.config).length ? ctx.config : meta.return || {};
  return validate(output, opts, ctx.vars || {});
};
module.exports.validate = validate;
