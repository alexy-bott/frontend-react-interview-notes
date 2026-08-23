# Governance репозитория

Текущая рабочая модель:

```text
Пользователь
→ ChatGPT Web: анализ и смысловые решения
→ Codex: ограниченное исполнение
→ GitHub/CI: фактическое состояние и механические доказательства
→ ChatGPT Web: проверка результата и готовность
```

## Активные документы

- [`repository-rules.md`](<./repository-rules.md>) — структура репозитория, генераторы, CI и репозиторные инварианты;
- [`codex-execution.md`](<./codex-execution.md>) — постоянный контракт исполнителя;
- [`web-review/00-workflow.md`](<./web-review/00-workflow.md>) — канонический Web-led процесс;
- [`web-review/01-file-structure.md`](<./web-review/01-file-structure.md>) — внешний каркас заметки;
- [`web-review/02-block-structure.md`](<./web-review/02-block-structure.md>) — внутренние блоки и разметка;
- [`web-review/03-content-distribution.md`](<./web-review/03-content-distribution.md>) — состав и распределение материала;
- [`web-review/04-content-quality.md`](<./web-review/04-content-quality.md>) — техническое и текстовое качество;
- [`web-review/05-change-design.md`](<./web-review/05-change-design.md>) — проектирование правки ChatGPT Web;
- [`web-review/new-note-workflow.md`](<./web-review/new-note-workflow.md>) — создание новой заметки.

## Архив

[`archive/2026-08-23-local-autonomous-note-workflow/`](<./archive/2026-08-23-local-autonomous-note-workflow/>) хранит прежний автономный комплект без содержательных изменений. Архив неактивен и не должен использоваться как текущая инструкция.
