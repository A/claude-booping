# Install

## Prerequisites

Required:

- **`uv`** — drives the plugin's Python tooling. The `bin/booping` wrapper is `uv run --project booping-python booping ...`, so every skill load goes through uv.
- **`git`** — the plugin assumes a git working tree for branching, diffs, and commit attribution during the develop playbook and `/code-review`.

Optional:

- **A cross-review agent** — set `cross_review.agent` in your config and the [groom playbook](groom.md) hands the drafted plan to that agent for a second-model review before presenting it to you. With no agent configured the step is skipped silently — the rest of the loop is unaffected.

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
/playbook setup
```

The `setup` playbook takes the repo from any starting state to a working booping project in one conversation, and every phase already satisfied on entry is detected and skipped rather than redone — a re-run on a wired-up project reports the state instead of changing it.

It runs in two steps:

1. **Machine level** — when booping is not yet initialized, it asks for your preferred home dir (default `~/Claude/`), writes the machine config at `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml`, and makes the home dir exist as a git repo.
2. **Project level** — it asks where the vault lives (the default `<home_dir>/{project}/`, kept outside the repo, or a **repo-local** directory recorded via the `.booping` marker's `vault_path:` key), the project name, and marker visibility; then scaffolds the vault tree, writes the `.booping` marker, symlinks a repo-local vault into the home dir, and seeds `sprints.md`.

The scaffolded vault:

- `plans/` — sprint plans authored by the [groom playbook](groom.md), executed by the [develop playbook](develop.md).
- `retrospectives/` — legacy retro files; the retro playbook now writes `retro.md` into the plan's own directory.
- `_lessons/` — durable, targeted rules authored by the [learn playbook](learn.md).
- `notes/` — your own free-form notes (untouched by skills).
- `_booping/` — per-skill / per-agent extension files, kept current by learn. Setup creates the directory; it does not seed extension files or detect your stack.
- `sprints.md` — an Obsidian Bases fence over the vault's `plans/*/index.md` files; seeded once, evaluated live by Obsidian.
- `.gitignore` — vault-level ignores.
- `.booping` — marker file (written in the repo root, not the vault) telling skills which vault to resolve.

For the full directory tour (including `plan_templates/`, `review_templates/`, `sprints.md`, and `config.yaml`), see [Vault](vault.md).

## Verify

After setup, run `/chat` inside the same repo. It should orient against the freshly scaffolded vault and report that it is empty — your signal that you're ready to run your first [groom](groom.md).
