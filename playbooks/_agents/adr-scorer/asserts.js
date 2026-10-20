'use strict';

// Checks over agent_provider.py's output; the reply is the rubric's one JSON line.
//   config.check: tools     — the first tool_use is Bash running RENDER (the body render) and none
//                             is a reading tool (READERS); a stray extra Bash call is tolerated
//   config.check: contract  — the `<return>` reply is one JSON object on one line with the
//                             rubric's keys, `route` in its enum, `overlaps`/`missing` lists of
//                             at most 3 strings, `alt_score` an integer 0–3
//   config.check: route     — `route` equals config.expect
//   config.check: alt_score — `alt_score` within ±1 of config.expect (hand-derived)
//   config.check: order     — the `<return>` alt_score is below the `<compare>` one
const KEYS = ['alt_score', 'missing', 'overlaps', 'route', 'route_why'];
const ROUTES = ['adr', 'rule', 'value', 'story', 'reference', 'idea', 'open-item', 'none'];
const RENDER = 'booping render src/templates/agents/adr-scorer.md.j2';
const READERS = ['Read', 'Grep', 'Glob', 'WebFetch', 'WebSearch'];

const block = (output, tag) => {
  const b = new RegExp('<' + tag + '>([\\s\\S]*?)</' + tag + '>').exec(output);
  return b ? b[1].trim() : null;
};

const reply = (output, tag) => {
  const text = block(output, tag);
  if (text === null) return { error: 'no <' + tag + '> block' };
  try {
    return { text, json: JSON.parse(text) };
  } catch (e) {
    return { text, error: 'the <' + tag + '> reply is not JSON: ' + text.slice(0, 200) };
  }
};

const result = (pass, reason) => ({ pass, score: pass ? 1 : 0, reason });

const contract = (r) => {
  if (r.error) return r.error;
  if (r.text.includes('\n')) return 'the reply spans more than one line';
  const j = r.json;
  if (j === null || typeof j !== 'object' || Array.isArray(j)) return 'the reply is not a JSON object';
  const keys = Object.keys(j).sort();
  if (keys.join(',') !== KEYS.join(',')) return 'keys ' + keys.join(',') + ', expected ' + KEYS.join(',');
  if (!ROUTES.includes(j.route)) return 'route `' + j.route + '` is not in the enum';
  if (typeof j.route_why !== 'string' || !j.route_why.trim()) return 'route_why is not a sentence';
  for (const k of ['overlaps', 'missing']) {
    if (!Array.isArray(j[k]) || j[k].length > 3 || j[k].some((e) => typeof e !== 'string')) {
      return k + ' is not a list of at most 3 strings';
    }
  }
  if (!Number.isInteger(j.alt_score) || j.alt_score < 0 || j.alt_score > 3) return 'alt_score `' + j.alt_score + '` is not 0–3';
  return null;
};

module.exports = (output, context) => {
  const config = (context && context.config) || {};
  if (config.check === 'tools') {
    const m = /<tool_calls>(\d+)<\/tool_calls>/.exec(output);
    if (!m) return result(false, 'no <tool_calls> marker in the provider output');
    const n = Number(m[1]);
    const commands = block(output, 'tool_commands');
    if (commands === null) return result(false, 'no <tool_commands> block in the provider output');
    const lines = commands ? commands.split('\n') : [];
    const readers = lines.filter((l) => READERS.includes(l.split(' ')[0]));
    const pass = n >= 1 && lines[0] === 'Bash ' + RENDER && readers.length === 0;
    return result(pass, pass ? 'body render first, no reading tool' : n + ' tool call(s): ' + commands.slice(0, 300));
  }
  if (config.check === 'contract') {
    const why = contract(reply(output, 'return'));
    return result(why === null, why || 'one JSON line, rubric keys and ranges');
  }
  if (config.check === 'route') {
    const r = reply(output, 'return');
    if (r.error) return result(false, r.error);
    return result(r.json.route === config.expect, 'route ' + r.json.route + ', expected ' + config.expect);
  }
  if (config.check === 'alt_score') {
    const r = reply(output, 'return');
    if (r.error) return result(false, r.error);
    const got = r.json.alt_score;
    return result(Number.isInteger(got) && Math.abs(got - config.expect) <= 1,
      'alt_score ' + got + ', ground truth ' + config.expect);
  }
  if (config.check === 'order') {
    const low = reply(output, 'return');
    const high = reply(output, 'compare');
    if (low.error || high.error) return result(false, low.error || high.error);
    const a = low.json.alt_score;
    const b = high.json.alt_score;
    return result(Number.isInteger(a) && Number.isInteger(b) && a < b,
      'alt_score ' + a + ' vs ' + b + ', expected the first below the second');
  }
  return result(false, 'unknown check: ' + config.check);
};
