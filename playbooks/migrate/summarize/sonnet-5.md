Close the run with **one** report — one however many migrations ran.

You carry, from this run: each migration it applied (id, title, outcome), the commit each one
landed in, and the pending set `survey` presented. Read the `latest_migration` key in the repo's
`.booping` marker and compare it against the highest id in that pending set — the highest id the
plugin ships. Currency is a checked fact, never an assumption.

Present in chat:

```
Vault migrated — {n} migrations applied, vault is now current.

| id  | migration       | outcome | commit    |
| --- | --------------- | ------- | --------- |
| 003 | plans_to_dirs   | applied | `a1b2c3d` |
| 004 | lessons_targets | applied | `e4f5a6b` |

`latest_migration`: `002` → `004` — the highest migration the plugin ships, so render surfaces
stop reporting the vault as behind and normal work resumes.

Migrations `001`–`002` landed in an earlier run; this report covers only what this run applied.
```

- one row per migration **this run** applied, in ascending id order
- the closing line only when earlier ids landed before this run — one line, never an enumeration
  of what those migrations did
- when `latest_migration` is below the highest shipped id, that mismatch is the headline: say the
  vault is **not** current, name the id it stopped at and the ids still pending, and drop the
  "normal work resumes" claim

Scope is the run just completed. Never reconstruct the vault's whole migration history — a
re-entry after an earlier halted run is an ordinary run. A failed run never reaches you:
`apply-migration` halts the sequence itself, so never describe a failure.

Return to the runner (the report above is what the user sees; this block is bookkeeping):

```
## Changed:

## Notes:
- {n} migration(s) applied; latest_migration {from} → {to}; vault current
```
