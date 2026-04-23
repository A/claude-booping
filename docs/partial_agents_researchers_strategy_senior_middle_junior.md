When research is needed (reading large swaths of code, web search, comparing libraries, surveying GitHub / Reddit / docs), delegate it to a researcher to keep the orchestrator's context clean. Pick the tier based on request difficulty:

| Agent | When to use |
|-------|-------------|
| `booping-researcher-senior` (opus, high) | Hard, ambiguous, or cross-cutting research where judgment matters |
| `booping-researcher-middle` (sonnet) | Default tier — most research requests |
| `booping-researcher-junior` (haiku) | Narrow lookups, single-file reads, simple fact-finding |

The orchestrator owns the research request: state exactly what to investigate and what shape the summary should take. The researcher reads, summarizes, returns. No decisions, no file writes.
