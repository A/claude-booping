'use strict';

// Reusable Gherkin-specification validator for promptfoo `javascript` asserts.
//   assert:
//     - type: javascript
//       value: file://../../_lib/asserts/gherkin.js
//       config:
//         blocks: 6
//         featurePerBlock: true
// It reads the fenced ```gherkin block(s) out of the output and parses them line-wise — no npm
// dependencies. A document may carry SEVERAL blocks (one `Feature:` per story, each under its own
// `## <Story Title>` heading); `blocks` bounds how many, and `headingPerBlock` ties each block to
// the heading above it. Params come from the assertion's own `config:` block, with
// `metadata.gherkin` still honoured as a fallback. Either way the params are NOT vars — vars are
// the only thing the judge sees, and it must stay judge-blind.
//   file            : string   regex of the written file to scope to (files mode); without it the
//                              whole answer is read, which is what a text-mode probe needs
//   blocks          : number | {min, max}   fenced ```gherkin blocks in the document (default 1)
//   feature         : number | {min, max}   total `Feature:` lines across the blocks. Omit when
//                              `featurePerBlock` is set; defaults to 1 when neither is given
//   featurePerBlock : boolean  exactly one `Feature:` line inside every block
//   headingPerBlock : boolean  every block sits under a `## ` heading (level from `headingLevel`,
//                              default 2) whose text equals its `Feature:` name
//   headingLevel    : number   the heading level `headingPerBlock` expects (default 2)
//   requireRules    : boolean  every scenario sits under a `Rule:` AND every `Rule:` holds >= 1
//                              scenario
//   minRules        : number   minimum `Rule:` blocks across the document
//   minScenarios    : number   minimum scenarios across the document (default 1)
//   maxScenarios    : number   maximum scenarios across the document (default Infinity)
//   minScenariosPerBlock : number   minimum scenarios inside EVERY block (default 1) — what
//                              fails a story section whose specification is empty
//   oneWhen         : boolean  exactly one `When` per scenario — `And`/`But`/`*` inherit the
//                              keyword of the step above them, so they never add a second `When`
//   gwtOrder        : boolean  Given -> When -> Then order inside a scenario (never a Given after
//                              a When, never a When after a Then), same inheritance rule
//   uniqueNames     : true | 'block' | 'global'   no two scenarios carry the same name
//                              (case-insensitive); 'block' scopes uniqueness to one Feature,
//                              `true` means 'global'
//   blocklist       : string[] phrases banned from step text — UI/implementation noise and
//                              relative dates (click, button, page, form, modal, field, reload,
//                              endpoint, status code, selector, table name, today …). Matched
//                              case-insensitively as a whole word plus the ordinary inflections,
//                              so `click` also catches `clicks`/`clicked`/`clicking` and `page`
//                              catches `pages`, while `form` does NOT catch `former`/`format`.
//   weakThen        : string[] phrases that make a `Then` a non-outcome (`it works`, `no error`,
//                              `successfully`, `as expected`); checked on `Then` steps only
//   maxAndChain     : number   max consecutive `And`/`But`/`*` steps hanging off one keyword
//   noFirstPerson   : boolean  step text names the actor by role, never the first person `I`
//   backgroundNoWhen: boolean  a `Background:` carries no `When` — it is shared context, and an
//                              action hidden there is the scenario's action taken out of sight.
//                              Background steps are screened by `blocklist` / `noFirstPerson`
//                              either way, but never counted as scenarios
//   tagPattern      : string   regex EVERY scenario tag must match, e.g. '^@Q[FL]-\\d+$'
//   requiredTags    : string[] tags that must each sit on at least one scenario
//   forbiddenTags   : string[] tags that must sit on no scenario
//   todoMarker      : string   substring marking a hand-author stub comment (e.g. 'open
//                              question'). A scenario whose body carries it is a declared gap:
//                              exempt from oneWhen / gwtOrder / weakThen / has-steps, still
//                              counted for tags and name uniqueness.
// Returns a promptfoo GradingResult { pass, score, reason }.

const fail = (reason) => ({ pass: false, score: 0, reason });
const ok = (reason) => ({ pass: true, score: 1, reason });

const STEP_RE = /^(Given|When|Then|And|But|\*)\s+(.*)$/;
const SCENARIO_RE = /^(Scenario Outline|Scenario Template|Scenario|Example):\s*(.*)$/;
const HEADING_RE = /^(#{1,6})\s+(.*\S)\s*$/;
const FENCE_RE = /^(```+|~~~+)(.*)$/;
const RANK = { Given: 1, When: 2, Then: 3 };

const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const cut = (s, n) => (s.length > n ? s.slice(0, n) + '…' : s);
const norm = (s) => String(s).replace(/[`*_]/g, '').replace(/[.:;,\s]+$/, '').trim().toLowerCase();

// number | {min, max} -> {min, max}. `fallback` applies when the param is absent.
function range(v, fallback) {
  if (v == null) return fallback;
  if (typeof v === 'number') return { min: v, max: v };
  return { min: v.min != null ? v.min : 0, max: v.max != null ? v.max : Infinity };
}

const showRange = (r) => (r.min === r.max ? String(r.min) : r.min + '–' + (r.max === Infinity ? '∞' : r.max));

// Files-mode output concatenates several `<file …>` blocks; scope to the one under test so a
// second written document cannot supply the specification this check is looking for.
function scopeToFile(output, pattern) {
  const blocks = [...output.matchAll(/^[ \t]*<file path="([^"]+)">\n([\s\S]*?)\n<\/file>[ \t]*$/gm)];
  if (!blocks.length) return { content: output.split(/\n<return>/)[0], path: null };
  if (!pattern) return { content: blocks[0][2], path: blocks[0][1] };
  const re = new RegExp(pattern);
  const hit = blocks.find((b) => re.test(b[1]));
  return hit
    ? { content: hit[2], path: hit[1] }
    : { content: null, path: null, tried: blocks.map((b) => b[1]) };
}

// One fence-aware pass over the document: markdown headings outside fences, and the body of every
// ```gherkin block with the nearest heading above it. Scanning inside a fence is what keeps a
// `# TODO: …` stub comment from being read as a markdown heading.
function scan(text) {
  const lines = String(text || '').split('\n');
  const headings = [];
  const blocks = [];
  let fence = null;
  let lang = null;
  let buf = null;
  let openLine = -1;

  for (let i = 0; i < lines.length; i++) {
    const t = lines[i].trim();
    const f = FENCE_RE.exec(t);
    if (f) {
      if (fence === null) {
        fence = f[1];
        lang = f[2].trim().toLowerCase();
        buf = [];
        openLine = i;
        continue;
      }
      if (t.startsWith(fence)) {
        if (lang === 'gherkin') {
          const above = headings.filter((h) => h.line < openLine).pop() || null;
          blocks.push({ src: buf.join('\n'), line: openLine + 1, heading: above });
        }
        fence = null; lang = null; buf = null;
        continue;
      }
      buf.push(lines[i]);
      continue;
    }
    if (fence !== null) { buf.push(lines[i]); continue; }
    const h = HEADING_RE.exec(t);
    if (h) headings.push({ level: h[1].length, name: h[2].trim(), line: i });
  }
  return { blocks: blocks, headings: headings };
}

// Line-wise Gherkin parse of ONE block.
// Returns { featureCount, rules, scenarios, backgrounds, errors }.
function parse(src) {
  const lines = src.split('\n');
  const rules = [];
  const scenarios = [];
  const backgrounds = [];
  const errors = [];
  let featureCount = 0;
  let currentRule = null;
  let current = null;
  let pendingTags = [];
  let lastKeyword = null;
  let andChain = 0;
  let docFence = null;

  for (let i = 0; i < lines.length; i++) {
    const n = i + 1;
    const t = lines[i].trim();
    if (docFence !== null) {
      if (t === docFence) docFence = null;
      continue;
    }
    if (!t) continue;
    if (t === '"""' || t === "'''") { docFence = t; continue; }
    if (t.startsWith('#')) {
      (current ? current.comments : currentRule ? currentRule.comments : []).push(t);
      continue;
    }
    if (t.startsWith('@')) {
      pendingTags = pendingTags.concat(t.split(/\s+/).filter((x) => x.startsWith('@')));
      continue;
    }
    if (/^Feature:/.test(t)) {
      featureCount++;
      current = null; lastKeyword = null; andChain = 0; pendingTags = [];
      continue;
    }
    // A Background is a step container, not an example: its steps are parsed and screened like
    // any other, but it is never counted as a scenario.
    if (/^Background:/.test(t)) {
      current = {
        name: t.slice(11).trim() || 'Background',
        isBackground: true,
        rule: currentRule,
        tags: [],
        steps: [],
        comments: [],
        maxAndChain: 0,
        hasExamples: false,
        line: n,
      };
      backgrounds.push(current);
      lastKeyword = null; andChain = 0; pendingTags = [];
      continue;
    }
    if (/^Rule:/.test(t)) {
      currentRule = { name: t.slice(5).trim(), scenarios: [], comments: [], line: n };
      rules.push(currentRule);
      current = null; lastKeyword = null; andChain = 0; pendingTags = [];
      continue;
    }
    if (/^Examples:/.test(t)) {
      if (current) current.hasExamples = true;
      lastKeyword = null; andChain = 0; pendingTags = [];
      continue;
    }
    const sc = t.match(SCENARIO_RE);
    if (sc) {
      current = {
        name: sc[2].trim(),
        outline: /Outline|Template/.test(sc[1]),
        rule: currentRule,
        tags: pendingTags,
        steps: [],
        comments: [],
        maxAndChain: 0,
        hasExamples: false,
        line: n,
      };
      scenarios.push(current);
      if (currentRule) currentRule.scenarios.push(current);
      pendingTags = []; lastKeyword = null; andChain = 0;
      continue;
    }
    if (t.startsWith('|')) continue; // data / Examples table row
    const st = t.match(STEP_RE);
    if (st) {
      if (!current) { errors.push('line ' + n + ': step outside any scenario: ' + cut(t, 60)); continue; }
      let kw = st[1];
      if (kw === 'And' || kw === 'But' || kw === '*') {
        if (!lastKeyword) { errors.push('line ' + n + ': `' + kw + '` with no Given/When/Then above it'); continue; }
        kw = lastKeyword;
        andChain += 1;
        if (andChain > current.maxAndChain) current.maxAndChain = andChain;
      } else {
        lastKeyword = kw;
        andChain = 0;
      }
      current.steps.push({ kw: kw, raw: st[1], text: st[2].trim(), line: n });
      continue;
    }
    errors.push('line ' + n + ': not a Gherkin line (prose leaked into the block?): ' + cut(t, 60));
  }
  return {
    featureCount: featureCount,
    rules: rules,
    scenarios: scenarios,
    backgrounds: backgrounds,
    errors: errors,
  };
}

function featureNamesOf(src) {
  const out = [];
  for (const line of src.split('\n')) {
    const m = /^\s*Feature:\s*(.*\S)\s*$/.exec(line);
    if (m) out.push(m[1].trim());
  }
  return out;
}

function validate(output, opts = {}) {
  const scoped = scopeToFile(output || '', opts.file);
  if (scoped.content === null)
    return fail('No written file matches /' + opts.file + '/ — wrote: ' + (scoped.tried || []).join(', '));

  const scanned = scan(scoped.content);
  const blocks = scanned.blocks;
  const wantBlocks = range(opts.blocks, { min: 1, max: 1 });
  if (!blocks.length) return fail('No fenced ```gherkin block in the output');
  if (blocks.length < wantBlocks.min || blocks.length > wantBlocks.max)
    return fail('Expected ' + showRange(wantBlocks) + ' fenced ```gherkin block(s), found ' + blocks.length);

  // Parse every block, keeping its own heading for locatable failure messages.
  const parsed = [];
  for (const b of blocks) {
    const p = parse(b.src);
    const names = featureNamesOf(b.src);
    const where = b.heading ? '`' + '#'.repeat(b.heading.level) + ' ' + b.heading.name + '`' : 'the block at line ' + b.line;
    if (p.errors.length) return fail('In ' + where + ': ' + p.errors[0]);
    parsed.push({ block: b, p: p, names: names, where: where });
  }

  if (opts.featurePerBlock) {
    const bad = parsed.find((x) => x.p.featureCount !== 1);
    if (bad)
      return fail('In ' + bad.where + ': expected exactly 1 `Feature:` line in the block, found ' + bad.p.featureCount);
  }
  if (opts.feature != null || !opts.featurePerBlock) {
    const wantFeature = range(opts.feature, { min: 1, max: 1 });
    const total = parsed.reduce((n, x) => n + x.p.featureCount, 0);
    if (total < wantFeature.min || total > wantFeature.max)
      return fail('Expected ' + showRange(wantFeature) + ' `Feature:` line(s), found ' + total);
  }

  if (opts.headingPerBlock) {
    const level = opts.headingLevel != null ? opts.headingLevel : 2;
    for (const x of parsed) {
      const h = x.block.heading;
      if (!h)
        return fail('A ```gherkin block (line ' + x.block.line + ') sits under no heading — every block belongs to one `' + '#'.repeat(level) + '` section');
      if (h.level !== level)
        return fail('The ```gherkin block at line ' + x.block.line + ' sits under `' + '#'.repeat(h.level) + ' ' + cut(h.name, 50) + '`, expected a level-' + level + ' heading');
      if (!x.names.length)
        return fail('In ' + x.where + ': the block carries no `Feature:` line');
      if (norm(x.names[0]) !== norm(h.name))
        return fail('In ' + x.where + ': `Feature: ' + cut(x.names[0], 50) + '` does not name its section — the Feature and its heading must carry the same story title');
    }
  }

  const allScenarios = [];
  const allRules = [];
  const allBackgrounds = [];
  for (const x of parsed) {
    for (const s of x.p.scenarios) { s._where = x.where; allScenarios.push(s); }
    for (const b of x.p.backgrounds) { b._where = x.where; allBackgrounds.push(b); }
    for (const r of x.p.rules) allRules.push(r);
  }
  // Step-text screening (blocklist, first person) reads Backgrounds too — a Background is where
  // shared context hides, so exempting it would open a hole in every wording rule.
  const allStepped = allScenarios.concat(allBackgrounds);

  if (opts.backgroundNoWhen) {
    for (const b of allBackgrounds) {
      const hit = b.steps.find((st) => st.kw === 'When');
      if (hit)
        return fail('`Background:` in ' + b._where + ' carries a `When` (line ' + hit.line + ') — a Background is shared context; the action belongs to the scenario');
    }
  }

  const minScenarios = opts.minScenarios != null ? opts.minScenarios : 1;
  const maxScenarios = opts.maxScenarios != null ? opts.maxScenarios : Infinity;
  if (allScenarios.length < minScenarios)
    return fail('Expected >= ' + minScenarios + ' scenario(s), found ' + allScenarios.length);
  if (allScenarios.length > maxScenarios)
    return fail('Expected <= ' + maxScenarios + ' scenario(s), found ' + allScenarios.length);

  const minPerBlock = opts.minScenariosPerBlock != null ? opts.minScenariosPerBlock : 1;
  const thin = parsed.find((x) => x.p.scenarios.length < minPerBlock);
  if (thin)
    return fail('In ' + thin.where + ': ' + thin.p.scenarios.length + ' scenario(s), expected >= ' + minPerBlock);

  if (opts.minRules != null && allRules.length < opts.minRules)
    return fail('Expected >= ' + opts.minRules + ' `Rule:` block(s), found ' + allRules.length);

  const marker = (opts.todoMarker || '').toLowerCase();
  const isStub = (s) => !!marker && s.comments.some((c) => c.toLowerCase().indexOf(marker) !== -1);

  if (opts.requireRules) {
    for (const x of parsed) {
      const orphan = x.p.scenarios.find((s) => !s.rule);
      if (orphan) return fail('In ' + x.where + ': scenario not under any `Rule:` (line ' + orphan.line + '): ' + cut(orphan.name, 60));
      const empty = x.p.rules.find((r) => !r.scenarios.length);
      if (empty) return fail('In ' + x.where + ': `Rule:` with no scenario (line ' + empty.line + '): ' + cut(empty.name, 60));
      if (!x.p.rules.length) return fail('In ' + x.where + ': no `Rule:` in the specification');
    }
  }

  if (opts.uniqueNames) {
    const scope = opts.uniqueNames === 'block' ? 'block' : 'global';
    const groups = scope === 'block' ? parsed.map((x) => ({ where: x.where, list: x.p.scenarios })) : [{ where: null, list: allScenarios }];
    for (const g of groups) {
      const seen = new Map();
      for (const s of g.list) {
        const k = s.name.toLowerCase();
        if (seen.has(k))
          return fail((g.where ? 'In ' + g.where + ': ' : '') + 'duplicate scenario name (lines ' + seen.get(k) + ' and ' + s.line + '): ' + cut(s.name, 60));
        seen.set(k, s.line);
      }
    }
  }

  for (const s of allScenarios) {
    const stub = isStub(s);
    const where = 'scenario "' + cut(s.name, 50) + '" in ' + s._where;
    if (!s.steps.length && !stub) return fail('No steps in ' + where + ' (line ' + s.line + ')');
    if (opts.oneWhen && !stub) {
      const whens = s.steps.filter((x) => x.kw === 'When');
      if (whens.length !== 1)
        return fail(where.charAt(0).toUpperCase() + where.slice(1) + ' has ' + whens.length + ' `When` step(s), expected exactly 1 (`And`/`But` inherit the keyword above them)');
    }
    if (opts.gwtOrder && !stub) {
      let rank = 0;
      for (const st of s.steps) {
        const r = RANK[st.kw];
        if (r < rank)
          return fail('Out-of-order step in ' + where + ' (line ' + st.line + '): `' + st.raw + '` after a ' + Object.keys(RANK).find((k) => RANK[k] === rank) + ' — Given/When/Then must run in order');
        rank = r;
      }
      if (s.steps.length && !s.steps.some((x) => x.kw === 'Then'))
        return fail('No `Then` in ' + where + ' — nothing observable is asserted');
    }
    if (opts.maxAndChain != null && s.maxAndChain > opts.maxAndChain)
      return fail(where.charAt(0).toUpperCase() + where.slice(1) + ' chains ' + s.maxAndChain + ' `And`/`But` steps off one keyword (cap ' + opts.maxAndChain + ')');
  }

  for (const phrase of opts.blocklist || []) {
    // whole word + ordinary inflections: `click`/`clicks`/`clicked`/`clicking`, `page`/`pages`,
    // but not `former` for `form` or `format` for `form`
    const re = new RegExp('\\b' + escapeRe(phrase) + '(?:s|es|ed|ing)?\\b', 'i');
    for (const s of allStepped) {
      const hit = s.steps.find((st) => re.test(st.text));
      if (hit)
        return fail('Imperative/UI wording "' + phrase + '" in step text (' + s._where + ', line ' + hit.line + '): `' + hit.raw + ' ' + cut(hit.text, 70) + '`');
    }
  }

  for (const phrase of opts.weakThen || []) {
    const re = new RegExp('\\b' + escapeRe(phrase), 'i');
    for (const s of allScenarios) {
      if (isStub(s)) continue;
      const hit = s.steps.find((st) => st.kw === 'Then' && re.test(st.text));
      if (hit)
        return fail('Weak assertion "' + phrase + '" — a `Then` must state an observable outcome (' + s._where + ', line ' + hit.line + '): `' + hit.raw + ' ' + cut(hit.text, 70) + '`');
    }
  }

  if (opts.noFirstPerson) {
    for (const s of allStepped) {
      const hit = s.steps.find((st) => /\bI\b/.test(st.text));
      if (hit)
        return fail('First-person `I` in step text — the actor must be named by role (' + s._where + ', line ' + hit.line + '): `' + hit.raw + ' ' + cut(hit.text, 70) + '`');
    }
  }

  const allTags = [];
  for (const s of allScenarios) for (const tg of s.tags) allTags.push(tg);

  if (opts.tagPattern) {
    const re = new RegExp(opts.tagPattern);
    const bad = allTags.find((tg) => !re.test(tg));
    if (bad) return fail('Tag `' + bad + '` does not match the required pattern ' + opts.tagPattern);
  }
  const missing = (opts.requiredTags || []).filter((tg) => allTags.indexOf(tg) === -1);
  if (missing.length)
    return fail('No scenario tagged ' + missing.join(', ') + ' — the open question it stands for must be carried into the specification, not settled silently');
  const present = (opts.forbiddenTags || []).filter((tg) => allTags.indexOf(tg) !== -1);
  if (present.length) return fail('Scenario tagged ' + present.join(', ') + ' — that id gets no scenario');

  const stubs = allScenarios.filter(isStub).length;
  return ok(
    parsed.length + ' block(s), ' + allRules.length + ' rule(s), ' + allScenarios.length +
      ' scenario(s)' + (stubs ? ' (' + stubs + ' declared-gap stub)' : '') +
      (allBackgrounds.length ? ', ' + allBackgrounds.length + ' Background(s)' : '') +
      (allTags.length ? ', tags ' + allTags.join(' ') : ', no tags')
  );
}

module.exports = (output, context) => {
  const ctx = context || {};
  const meta = (ctx.test && ctx.test.metadata) || ctx.metadata || {};
  const opts = ctx.config && Object.keys(ctx.config).length ? ctx.config : meta.gherkin || {};
  return validate(output, opts);
};
module.exports.validate = validate;
