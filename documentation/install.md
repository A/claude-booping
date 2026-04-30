# Install

## Prerequisites

Required:

- **`uv`** — drives the plugin's Python tooling. The `bin/booping` wrapper is `uv run --project booping-python booping ...`, so every skill load goes through uv.
- **`git`** — the plugin assumes a git working tree for branching, diffs, and commit attribution during `/develop` and `/code-review`.

Optional:

- **`GEMINI_API_KEY`** — when set in your environment, `/groom` cross-validates the drafted plan against Gemini once before handing it to you for review. Without the key, cross-validation skips silently — the rest of the loop is unaffected.

Install the prerequisites:

```bash
# macOS
brew install uv git

# Linux (Debian/Ubuntu)
sudo apt install -y git
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Plugin install

Inside Claude Code, register the marketplace once and install the plugin:

```text
/plugin marketplace add A/claude-booping
/plugin install booping@booping
```

Update later with `/plugin update booping` (or from the `/plugin` UI).

## Scaffold the project vault

`cd` into the target repository and run:

```text
/install
```

`/install` is idempotent and scaffolds the per-project vault at `~/Claude/{project}/`:

- `plans/` — sprint plans authored by `/groom`, executed by `/develop`.
- `retrospectives/` — retro files authored by `/retro`.
- `lessons/` — durable rules authored by `/learn`.
- `notes/` — your own free-form notes (untouched by skills).
- `_booping/` — per-skill / per-agent extension files authored by `/learn`.
- `.booping` — marker file telling other skills the vault is ready.

For the full directory tour (including `plan_templates/`, `review_templates/`, `sprints.md`, and `config.yaml`), see [Vault](vault.md).

## Verify

After `/install`, run `/chat` inside the same repo. It should orient against the freshly scaffolded vault, regenerate `~/Claude/{project}/sprints.md`, and report that the vault is empty — your signal that you're ready to run your first [/groom](groom.md).
