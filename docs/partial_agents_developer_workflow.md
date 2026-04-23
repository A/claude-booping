1. Skim the **related files** listed in the briefing — read the ones you'll touch; treat the rest as context if helpful.
2. Implement exactly what the task specifies. No extras. No "while I'm here" refactors.
3. Run the exact commands listed under `Verify:` in the briefing before reporting done.
4. Report back using the format below.

Do not edit any file under `~/Claude/{project}/` — the plan file, lesson files, and vault metrics are owned by the orchestrator skill. If you believe a vault file needs to change, report it; do not edit it yourself.

## Report format

Return a short structured message:

~~~markdown
## Done
- Files touched: ...

## Verify output
<output of test/lint commands>

## Notes for reviewer
- Tricky bits: ...
- Anything I want a second pair of eyes on: ...
~~~
