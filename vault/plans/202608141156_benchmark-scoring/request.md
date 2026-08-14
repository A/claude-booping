# Request

> I'd like to setup benchmarks scoring. In the end I want to have a table per each model i tried, that shows how good is this model against the task described in vault/benchmarks/guide.md, and record it into vault/benchmarks/history.md. It can be done as a playbook. Some input from chat with claude -  Хорошая новость: у этой задачи необычно сильный «оракул» — план сам содержит эталон. Таблица кросс-чека в M03 перечисляет поимённо ~30 ожидаемых .txtar-кейсов плюс три gap-кейса, а Final Verification даёт жёсткие механические ворота. Значит бо́льшую часть оценки можно посчитать скриптом, без судейства. Я бы разбил метрики на четыре слоя.
>
> 1. Жёсткие ворота (pass/fail, считаются механически на ветке)
>
> Ключевой принцип: не верить чекбоксам, которые агент сам себе проставил, а перепроверять всё заново на bench/{model_slug}:
>
> спринт дошёл до конца / abort (и на каком milestone);
> just ci зелёный;
> uv run pytest e2e -k frontmatter зелёный на чистом прогоне;
> прогон с --txtar-update → git diff пустой (детерминизм, это прямо в Verify плана);
> frontmatter_update_test.py удалён, grep -rn frontmatter_update_test пустой;
> чистота скоупа: git diff e0d1796 --name-only содержит только e2e/cases/frontmatter-update/*.txtar, удаление юнит-файла и milestone-md. Любое касание src/, conftest.py или плагина — автоматический красный флаг, план это явно запрещает.
>
> 2. Качество корпуса (самое интересное, полумеханика)
>
> Тут ловятся модели, которые «прошли ворота», но написали слабые тесты:
>
> Recall по эталону: сколько из поимённо названных в M03 кейсов реально существует (совпадение по поведению, не обязательно по имени файла — тут может понадобиться маппинг), отдельно 3/3 gap-кейса и real-macro кейс с честным echo.
> Сила ассертов: доля кейсов, которые ассертят все четыре канала (exit + stdout + stderr + expected/-байты), а не только exit code. Парсится из txtar тривиально.
> Плотность вайлдкардов: [..] на кейс. Кейс, где вайлдкардом накрыт весь дифф — тест-пустышка. Можно считать отношение wildcarded-строк к общим в stdout/expected.
> Mutation testing — золотой стандарт: внести 10–15 заготовленных мутаций в frontmatter_update.py (сломать коэрцию bool, убрать идемпотентность append, перепутать exit 1/2, сломать summary на stderr) и посчитать kill rate корпуса каждой модели. Один и тот же набор мутаций для всех — получается честная сравнимая цифра, и она напрямую меряет то, ради чего вся миграция затевалась.
> Подозрение на «слепой rebaseline»: сколько раз в логах встречается --txtar-update до первого зелёного прогона. Модель, которая сгенерила expected из багнутой фикстуры и закоммитила — пройдёт ворота, но провалит мутации.
>
> 3. Процесс (из ndjson-логов)
>
> Стандартный агентский профиль, парсится из ~/.tmp/openrouter-developer/*.ndjson:
>
> attempts на milestone (1/2/fail) — это уже в отчёте плейбука;
> wall clock суммарно и по milestone;
> tokens in/out и стоимость (OpenRouter отдаёт usage, если он в логах);
> число tool calls всего и по типам; malformed tool inputs; дегенеративные циклы (одинаковый tool+args N раз подряд);
> context-limit смерти;
> churn: строк написано/переписано против финального размера диффа — мера «метаний».
>
> 4. Гигиена диффа
>
> Число коммитов и соответствие milestone-структуре, размер диффа против медианы по моделям (аномально большой = мусор, аномально маленький = недопокрытие), качество кросс-чек-таблицы, которую модель написала в M03 — тут единственное место, где я бы допустил LLM-judge, и то с механической предпроверкой: каждый упомянутый в таблице файл существует, ни одной строки «TODO».
>
> Схема таблицы — одна строка на модель, примерно так:
>
> | model | done | ci | e2e clean | update-diff empty | scope | recall | 4-channel % | mutation kill | attempts (M1/M2/M3) | tool calls | malformed | loops | tokens | cost | wall |
>
> Практически: я бы собрал bench-eval скрипт, который принимает имя ветки, сам делает checkout в worktree, гоняет ворота из слоя 1, парсит txtar-корпус для слоя 2 (кроме мутаций — их отдельным шагом, они дорогие), парсит ndjson для слоя 3, и выплёвывает строку в CSV/markdown. Тогда добавление новой модели в сравнение — одна команда после прогона бенчмарка.
>
> Если сокращать до минимума: ворота + mutation kill rate + attempts + cost. Эти четыре цифры почти полностью упорядочат модели; остальное — диагностика, почему модель слабее.. Start with a table with metrics and check to measure

# Task type

`feature` — new user-facing capability: a scoring surface (metrics spec, eval script, history table, and a playbook to drive them) that does not exist today. Not `bug`: nothing diverges from expected behavior. Not `refactoring`: nothing internal is restructured; the change is all new surface.

# Problem

Today a benchmark run (per `vault/benchmarks/guide.md`) ends in a hand-written report / PR body (e.g. PR #35): attempts, cost, wall clock, `just ci` verdict — assembled ad hoc, not comparable across models, not recorded anywhere durable. There is no scoring: gates are self-reported by the run, corpus quality is unmeasured, and nothing distinguishes a model that passed the gates with strong tests from one that squeaked through with wildcard-blanketed cases.

What must change: one command/playbook run per benchmarked branch `bench/{model_slug}` that (re-)verifies everything mechanically on the branch itself, measures corpus quality against the plan's built-in oracle (M03 cross-check table + Final Verification), profiles the process from the ndjson logs, and appends one comparable scorecard row per model to `vault/benchmarks/history.md`.

# Clarifications and Decisions

- Reference run: PR #35 (`bench/deepseek-deepseek-v4-pro-0813`, base `bench/reference`) — shows the report shape and confirms branch, milestone commits, ndjson logs are all available for scoring.
- First deliverable of grooming: the metric table — every metric with its check/measurement method — before any implementation.
- Layer 1 framing corrected: DoD checkboxes are set by the runner after validating the worker's milestone, not self-set by the worker — the develop playbook already covers most of layer 1. Gates stay in the scorecard as a cheap mechanical re-run on the branch, not as a distrust measure.
- Opus's original run of the reference task exists in git history — locate it and use it as the reference corpus (etalon) for quality comparison.
- Mutation testing: in scope — cheap, simple hand-authored mutations, count of killed tests. Modest value (runner already retries/stops failures) but worth having.
- Guide gap: add the explicit case where a model cannot handle the task and fails all restarts — a failed sprint is a recorded benchmark result.
- Guide gap: prepare must check/fix the venv BEFORE development starts — benchmark runs in a copy dir with stale venvs; fixing venvs is out of scope for the model under test.
- Diff size: keep as a scorecard column.
- LLM review: full-diff review (test quality, code quality), rubric abstract enough to survive swapping the reference plan for a coding-not-testing task. Two reviewers in parallel: the core review agent and a second model (opus:high or fable) for two independent visions.
- Delivery shape settled: a `model-benchmark` playbook with steps — `prepare` (model + benchmark id; benchmark registry doc with the default as its only entry; repo prep incl. venv), `run` (drives `/playbook develop`, possibly as an autonomous detached step), `measure` (the scoring discussed), `publish` (PR against `bench/reference`). `history.md` gets one appended scorecard row per run.
