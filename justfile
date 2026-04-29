default:
    @just --list

# Render static docs from templates (skills/agents are runtime-rendered)
build-docs:
	bin/booping render "docs/learn_review_table.md.j2" --output "docs/learn_review_table.md"
	bin/booping render "docs/plan_lifecycle_overview.md.j2" --output "docs/plan_lifecycle_overview.md"
	bin/booping render "docs/retro_summary_format.md.j2" --output "docs/retro_summary_format.md"
	bin/booping render "docs/template_plan_frontmatter.md.j2" --output "docs/template_plan_frontmatter.md"
	bin/booping render "plan_templates/backend.md.j2" --output "docs/plan_templates/backend.md"
	bin/booping render "plan_templates/claude_skill.md.j2" --output "docs/plan_templates/claude_skill.md"
	bin/booping render "plan_templates/cli.md.j2" --output "docs/plan_templates/cli.md"
	bin/booping render "plan_templates/frontend.md.j2" --output "docs/plan_templates/frontend.md"

# Build Python package
sync:
    cd booping-python && uv sync

# Lint
lint:
    cd booping-python && uv run ruff check .

# Typecheck
typecheck:
    cd booping-python && uv run basedpyright

# Test
test:
    cd booping-python && uv run pytest
