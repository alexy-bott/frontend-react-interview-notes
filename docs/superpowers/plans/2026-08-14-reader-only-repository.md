# Reader-Only Repository Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Оставить в текущем дереве GitHub только `README.md` и `notes/**`, сохранив весь служебный слой локально вне отслеживания Git.

**Architecture:** Служебные пути удаляются только из индекса Git и добавляются в локальный `.git/info/exclude`. Физические файлы остаются в рабочей папке и продолжают использоваться для генерации навигации и проверки заметок.

**Tech Stack:** Git, PowerShell, Python 3, Markdown.

## Global Constraints

- На GitHub остаются только `README.md` и `notes/**`.
- `_templates/**`, `docs/**`, `scripts/**`, `.github/**`, `.gitignore` и `.gitattributes` сохраняются на локальном диске.
- Служебные пути исключаются только для текущего клона через `.git/info/exclude`.
- Существующие заметки и читательская навигация не изменяются.
- Итог публикуется напрямую в `origin/main` без Pull Request.

---

### Task 1: Перевести служебный слой в локальное хранение

**Files:**
- Modify locally: `.git/info/exclude`
- Remove from Git index, keep on disk: `.github/**`
- Remove from Git index, keep on disk: `_templates/**`
- Remove from Git index, keep on disk: `docs/**`
- Remove from Git index, keep on disk: `scripts/**`
- Remove from Git index, keep on disk: `.gitignore`
- Remove from Git index, keep on disk: `.gitattributes`

**Interfaces:**
- Consumes: текущий индекс Git и существующие локальные служебные файлы.
- Produces: индекс, содержащий только `README.md` и `notes/**`, и локальный exclude-файл, предотвращающий повторное добавление служебных путей.

- [ ] **Step 1: Зафиксировать красную проверку публичного состава**

Run:

```powershell
$unexpected = git ls-files | Where-Object { $_ -ne 'README.md' -and $_ -notlike 'notes/*' }
if (-not $unexpected) { throw 'Expected tracked service files before cleanup' }
$unexpected
```

Expected: команда выводит `.github/**`, `_templates/**`, `docs/**`, `scripts/**`, `.gitignore` и `.gitattributes`.

- [ ] **Step 2: Зафиксировать наличие локальных исходников**

Run:

```powershell
$required = @('.github', '_templates', 'docs', 'scripts', '.gitignore', '.gitattributes')
$missing = $required | Where-Object { -not (Test-Path -LiteralPath $_) }
if ($missing) { throw "Missing local service paths: $($missing -join ', ')" }
```

Expected: exit code `0`, список отсутствующих путей пуст.

- [ ] **Step 3: Добавить локальные исключения**

В `.git/info/exclude` добавить один раз:

```gitignore
/.github/
/_templates/
/docs/
/scripts/
/.gitignore
/.gitattributes
```

- [ ] **Step 4: Удалить служебные пути только из индекса**

Run:

```powershell
git rm --cached -r -- .github _templates docs scripts .gitignore .gitattributes
```

Expected: Git показывает удаления; физические файлы остаются на диске.

- [ ] **Step 5: Проверить зелёный публичный состав**

Run:

```powershell
$unexpected = git ls-files | Where-Object { $_ -ne 'README.md' -and $_ -notlike 'notes/*' }
if ($unexpected) { throw "Unexpected tracked files: $($unexpected -join ', ')" }
```

Expected: exit code `0`, неожиданных отслеживаемых файлов нет.

- [ ] **Step 6: Проверить сохранность локального слоя**

Run:

```powershell
$required = @('.github', '_templates', 'docs', 'scripts', '.gitignore', '.gitattributes')
$missing = $required | Where-Object { -not (Test-Path -LiteralPath $_) }
if ($missing) { throw "Missing local service paths: $($missing -join ', ')" }
git status --short --untracked-files=all
```

Expected: все пути существуют, а `git status` не показывает их как неотслеживаемые.

- [ ] **Step 7: Запустить локальные проверки**

Run:

```powershell
python scripts/generate_navigation.py --check
python scripts/check_notes.py
git diff --check --cached
```

Expected: навигация актуальна для 286 Markdown-файлов; проверены 262 заметки в 23 разделах; ошибок пробелов нет.

- [ ] **Step 8: Зафиксировать очистку**

Run:

```powershell
git commit -m "chore: keep repository reader-only"
```

Expected: коммит содержит только удаление служебных файлов из текущего дерева Git.

### Task 2: Опубликовать читательский состав

**Files:**
- Publish: текущий `HEAD` в `origin/main`

**Interfaces:**
- Consumes: проверенный коммит Task 1.
- Produces: `origin/main`, чьё текущее дерево содержит только `README.md` и `notes/**`.

- [ ] **Step 1: Проверить актуальность удалённой базы**

Run:

```powershell
git fetch origin main
git rev-list --left-right --count origin/main...HEAD
```

Expected: удалённая сторона не содержит новых коммитов относительно текущего `HEAD`.

- [ ] **Step 2: Повторить проверки перед push**

Run:

```powershell
python scripts/generate_navigation.py --check
python scripts/check_notes.py
git status --short
```

Expected: обе проверки проходят, рабочее дерево чистое.

- [ ] **Step 3: Выполнить прямой push**

Run:

```powershell
git push origin HEAD:main
```

Expected: `origin/main` обновлён fast-forward без Pull Request.

- [ ] **Step 4: Проверить опубликованный коммит**

Run:

```powershell
git fetch origin main
if ((git rev-parse HEAD) -ne (git rev-parse origin/main)) { throw 'origin/main does not match HEAD' }
$unexpected = git ls-tree -r --name-only origin/main | Where-Object { $_ -ne 'README.md' -and $_ -notlike 'notes/*' }
if ($unexpected) { throw "Unexpected published files: $($unexpected -join ', ')" }
```

Expected: `HEAD` совпадает с `origin/main`; в опубликованном дереве нет служебных файлов.
