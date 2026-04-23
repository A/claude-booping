## Extra instructions pattern

**Purpose.** The plugin ships stack-agnostic; project-specific rules belong in the vault under `~/Claude/{project}/_booping/<name>.md`. The extra instructions pattern externalizes those rules — wide-domain skills and agents name a specific file path; this guide defines what to do with it.

**Invocation shape.** The component (skill or agent) declares two things: the guide (this file) and the specific file path to read. The path is always explicit — it is never inferred from context.

**Semantics on read.**

- Read the file at the given path.
- If the file is absent, skip silently — no error, no warning, no fallback search.
- If the file is present, merge its content into the current operating context as if it had been read in Preflight.

**Forbidden actions.**

- Do NOT scan sibling files in the same directory — the file path is explicit, not a glob.
- Do NOT edit the extension file. Extension files are owned by `/learn` and the user; skills and agents are readers only.
