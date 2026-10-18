'use strict';

// Three checks over agent_provider.py's output:
//   config.check: tools — the agent emitted no tool_use block
//   config.check: score — the `score:` line is within ±1 of config.expect (hand-derived)
//   config.check: order — the `<return>` score is below the `<compare>` score
module.exports = (output, context) => {
  const config = (context && context.config) || {};
  if (config.check === 'tools') {
    const m = /<tool_calls>(\d+)<\/tool_calls>/.exec(output);
    if (!m) return { pass: false, score: 0, reason: 'no <tool_calls> marker in the provider output' };
    const n = Number(m[1]);
    return n === 0
      ? { pass: true, score: 1, reason: 'no tool call' }
      : { pass: false, score: 0, reason: n + ' tool call(s)' };
  }
  if (config.check === 'score') {
    const m = /^score: ([0-3])\s*$/m.exec(output);
    if (!m) return { pass: false, score: 0, reason: 'no `score: N` line' };
    const got = Number(m[1]);
    const pass = Math.abs(got - config.expect) <= 1;
    return { pass, score: pass ? 1 : 0, reason: 'score ' + got + ', ground truth ' + config.expect };
  }
  if (config.check === 'order') {
    const block = (tag) => {
      const b = new RegExp('<' + tag + '>([\\s\\S]*?)</' + tag + '>').exec(output);
      const m = b && /^score: ([0-3])\s*$/m.exec(b[1]);
      return m ? Number(m[1]) : null;
    };
    const low = block('return');
    const high = block('compare');
    if (low === null || high === null) return { pass: false, score: 0, reason: 'a `score: N` line is missing in <return> or <compare>' };
    const pass = low < high;
    return { pass, score: pass ? 1 : 0, reason: 'score ' + low + ' vs ' + high + ', expected the first below the second' };
  }
  return { pass: false, score: 0, reason: 'unknown check: ' + config.check };
};
