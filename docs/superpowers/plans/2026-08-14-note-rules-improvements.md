# Note Rules Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Привести новый комплект `note-rules` к целевой модели конспекта, актуальному устройству репозитория и проверенным критериям качества без массовой миграции 262 заметок.

**Architecture:** Шесть файлов уровней остаются единственным нормативным источником правил отдельной страницы. К ним добавляются два ненормативных маршрута, а технические команды и граница миграции выносятся в отдельные репозиторные правила. Действующие корпусные проверки сохраняются и используются как источник репозиторных инвариантов.

**Tech Stack:** Markdown, Python 3.12, PowerShell, GitHub-flavored Markdown, существующие `scripts/generate_navigation.py` и `scripts/check_notes.py`.

## Global Constraints

- Целевая структура: `Быстрый ответ` → `Карта темы` → тематические H2/H3 → необязательная `Мини-задача` → `Где применяется во frontend` → `Ключевые уточнения` → `Связанные темы` → `Источники`.
- Имена заметок остаются ненумерованными; порядок задаётся `notes/<Раздел>/README.md`.
- Служебная навигация использует только `NOTE-NAV-TOP:*` и `NOTE-NAV-BOTTOM:*`.
- Новая структура обязательна только для новых, явно мигрируемых и уже мигрированных заметок.
- `scripts/check_notes.py` на этом этапе не требует новую содержательную структуру от всех 262 заметок.
- Карточечная модель `Вопрос` / `Дополнительные вопросы` не переносится.
- Уже существующие нормы не дублируются; уточнения встраиваются в их текущие разделы.

---

### Task 1: Согласовать внешний каркас и заголовки с репозиторием

**Files:**
- Modify: `_templates/note-rules/01-file-structure.md`
- Modify: `_templates/note-rules/02-block-structure.md`

**Interfaces:**
- Consumes: маркеры и ограничения из `scripts/generate_navigation.py` и `scripts/check_notes.py`.
- Produces: нормативный каркас заметки с ненумерованным именем, `NOTE-NAV-*`, одним H1 и заголовками не глубже H3.

- [ ] **Step 1: Зафиксировать исходные нарушения**

```powershell
rg -n 'CARD-NAV|двухзначного номера|номер страницы темы|номер файла' _templates/note-rules/01-file-structure.md
rg -n 'Единственность структурного H1|H4|H5|H6' _templates/note-rules/01-file-structure.md _templates/note-rules/02-block-structure.md
```

Expected: первая команда находит карточечные маркеры и нумерацию; вторая не находит полного набора требуемых ограничений.

- [ ] **Step 2: Исправить имя файла и навигацию уровня 1**

В `01-file-structure.md`:

- заменить правило числового префикса на `<Название темы>.md`;
- указать, что порядок определяется страницей раздела, а не именем файла;
- заменить все `CARD-NAV-TOP:*` и `CARD-NAV-BOTTOM:*` на `NOTE-NAV-TOP:*` и `NOTE-NAV-BOTTOM:*`;
- удалить нормативные упоминания номера файла;
- закрепить ровно один структурный H1 вне fenced code blocks.

- [ ] **Step 3: Уточнить иерархию уровня 2**

В `02-block-structure.md` закрепить:

- стандартизированные и тематические блоки используют H2;
- тематический подраздел использует H3;
- H4–H6 на странице темы запрещены;
- Markdown-подобные строки внутри fenced code blocks не являются структурными заголовками;
- служебный `<h2></h2>` внутри нормативного `<details>` не считается Markdown H2.

- [ ] **Step 4: Проверить исправления**

```powershell
$obsolete = rg -n 'CARD-NAV|двухзначного номера|номер страницы темы|номер файла' _templates/note-rules/01-file-structure.md
if ($LASTEXITCODE -ne 1) { $obsolete; exit 1 }
rg -n 'NOTE-NAV-TOP|NOTE-NAV-BOTTOM|ровно один структурный Markdown H1' _templates/note-rules/01-file-structure.md
rg -n 'H4–H6|fenced code block|<h2></h2>' _templates/note-rules/02-block-structure.md
```

Expected: устаревших требований нет; новые маркеры и ограничения найдены.

- [ ] **Step 5: Проверить и закоммитить структурные правила**

```powershell
git diff --check -- _templates/note-rules/01-file-structure.md _templates/note-rules/02-block-structure.md
git add -- _templates/note-rules/01-file-structure.md _templates/note-rules/02-block-structure.md
git commit -m "docs: align note structure rules with repository"
```

Expected: `git diff --check` завершается с кодом 0; коммит содержит только два структурных файла.

---

### Task 2: Усилить существующие критерии без дублирования

**Files:**
- Modify: `_templates/note-rules/00-workflow.md`
- Modify: `_templates/note-rules/03-content-distribution.md`
- Modify: `_templates/note-rules/04-content-quality.md`
- Modify: `_templates/note-rules/05-editing.md`

**Interfaces:**
- Consumes: общий контракт `PASS` / `FAIL` / `NOT CHECKED` и целевую структуру из Task 1.
- Produces: однозначные quality gates, блокирующую проверку актуальности и контроль крупной правки.

- [ ] **Step 1: Зафиксировать отсутствующие уточнения**

```powershell
rg -n 'блокирующ|карта смысла|Доказательность нарушения понятности|Ясность и грамматическая корректность названия|Диагностические границы' _templates/note-rules
```

Expected: уточнения отсутствуют либо присутствуют только как более общие правила без указанных контрактов.

- [ ] **Step 2: Уточнить workflow**

В `00-workflow.md`:

- определить блокирующий локальный `NOT CHECKED`;
- считать проверку актуальности существенных изменяемых утверждений блокирующей;
- не давать статус кандидата на завершение при таком `NOT CHECKED`;
- добавить временную карту смысла в финальное сравнение после крупной правки;
- разделить представление результата для репозиторного файла и отдельно переданного Markdown.

- [ ] **Step 3: Уточнить состав данных уровня 3**

В `03-content-distribution.md`:

- добавить ясность и грамматическую связность названия темы;
- установить минимум две обоснованные исходящие ссылки в `Связанных темах`;
- сохранить минимум одну входящую связь как репозиторный инвариант;
- связать изменяемые существенные утверждения с актуальными первичными источниками;
- определить влияние непроверенного источника через блокирующую проверку уровня 4.

- [ ] **Step 4: Уточнить пять критериев уровня 4**

В `04-content-quality.md`:

- добавить результат понятного объяснения как проверяемое свойство, а не шаблон разделов;
- добавить таблицу диагностических границ уровня 3, полноты, понятности, перегруженности и избыточности;
- требовать доказательное описание `FAIL` понятности;
- классифицировать отдельный термин или переход как понятность, а совокупность полезных деталей, скрывающую модель, как перегруженность;
- требовать фактически открыть применимый первичный источник для изменяемого существенного утверждения;
- вернуть блокирующий `NOT CHECKED`, если проверка невозможна.

- [ ] **Step 5: Уточнить редактирование уровня 5**

В `05-editing.md`:

- добавить минимальную правку названия и уровней заголовков только после подтверждённого `FAIL`;
- определить исправление поверхностности, справочной сухости и перегруженности через их первичные причины;
- добавить временную карту смысла при риске потери самостоятельного полезного аспекта;
- не превращать карту в блок заметки.

- [ ] **Step 6: Проверить отсутствие параллельных критериев**

```powershell
rg -n 'пять (основных )?критериев|техническая корректность|полнота|понятность|перегруженность|избыточность' _templates/note-rules/04-content-quality.md
rg -n 'шест(ой|ого).*критер' _templates/note-rules/03-content-distribution.md _templates/note-rules/04-content-quality.md
rg -n 'блокирующ|карта смысла|Доказательность нарушения понятности|Ясность и грамматическая корректность названия|Диагностические границы' _templates/note-rules
```

Expected: остаются ровно пять критериев; новые уточнения встроены в существующие уровни.

- [ ] **Step 7: Проверить и закоммитить quality gates**

```powershell
git diff --check -- _templates/note-rules/00-workflow.md _templates/note-rules/03-content-distribution.md _templates/note-rules/04-content-quality.md _templates/note-rules/05-editing.md
git add -- _templates/note-rules/00-workflow.md _templates/note-rules/03-content-distribution.md _templates/note-rules/04-content-quality.md _templates/note-rules/05-editing.md
git commit -m "docs: strengthen note quality rules"
```

Expected: коммит содержит четыре канонических файла без изменений заметок.

---

### Task 3: Добавить маршруты создания и повседневной работы

**Files:**
- Create: `_templates/note-rules/README.md`
- Create: `_templates/note-rules/new-note-workflow.md`
- Modify: `_templates/note-rules/00-workflow.md`

**Interfaces:**
- Consumes: канонические уровни `00`–`05`, страницы разделов и репозиторные инварианты.
- Produces: ненормативную короткую точку входа и предварительный маршрут новой заметки.

- [ ] **Step 1: Создать короткий README**

`README.md` должен содержать:

- ссылку на `00-workflow.md` как канонический процесс;
- маршрут создания новой заметки через `new-note-workflow.md`;
- маршрут проверки существующей или мигрируемой заметки через уровни 1–5;
- предупреждение, что README не создаёт новых требований.

- [ ] **Step 2: Создать `new-note-workflow.md`**

Маршрут должен последовательно определить:

- вход: заданная тема либо явно разрешённый поиск пробелов в ограниченной области;
- предварительную проверку дублей и пересечений;
- самостоятельную границу темы и выбор раздела;
- место ссылки в README раздела;
- не менее двух исходящих связей и кандидата для входящей связи;
- предварительное исследование по первичным источникам;
- временный смысловой план целевой структуры;
- сборку через `1 → 2 → 3 BUILD`;
- передачу заполненной версии в `00-workflow.md`;
- форматы `CREATION STOP`, блокирующего `NOT CHECKED` и итогового отчёта.

- [ ] **Step 3: Связать маршрут с канонической картой файлов**

В `00-workflow.md` добавить `new-note-workflow.md` и `README.md` в карту файлов как ненормативные точки входа, явно указав, что они не являются уровнями.

- [ ] **Step 4: Проверить внутренние ссылки маршрутов**

```powershell
$broken = @()
Get-ChildItem _templates/note-rules -File -Filter '*.md' | ForEach-Object {
  $file = $_
  $text = Get-Content -Raw -Encoding utf8 -LiteralPath $file.FullName
  [regex]::Matches($text, '\]\(<([^>#]+)(?:#[^>]*)?>\)') | ForEach-Object {
    $target = $_.Groups[1].Value
    if ($target -notmatch '^[a-z]+:') {
      $destination = [System.IO.Path]::GetFullPath((Join-Path $file.DirectoryName $target))
      if (-not (Test-Path -LiteralPath $destination)) { $broken += "$($file.Name) -> $target" }
    }
  }
}
if ($broken.Count) { $broken; exit 1 }
```

Expected: код 0 без вывода сломанных ссылок.

- [ ] **Step 5: Проверить и закоммитить маршруты**

```powershell
git diff --check -- _templates/note-rules
git add -- _templates/note-rules/README.md _templates/note-rules/new-note-workflow.md _templates/note-rules/00-workflow.md
git commit -m "docs: add new note creation workflow"
```

Expected: коммит добавляет два маршрута и только ссылочное изменение канонического workflow.

---

### Task 4: Разделить правила страницы и репозитория

**Files:**
- Delete: `_templates/GitHub Note Style.md`
- Create: `_templates/repository-rules.md`

**Interfaces:**
- Consumes: `note-rules/`, `scripts/generate_navigation.py`, `scripts/check_notes.py`, корневой и секционные README.
- Produces: единственный репозиторный контракт без второго шаблона страницы.

- [ ] **Step 1: Создать `repository-rules.md`**

Файл должен определить:

- `note-rules/` как канонический источник структуры и качества страницы;
- целевой стандарт для новых, мигрируемых и мигрированных заметок;
- временное сохранение legacy-заметок до явной миграции;
- правила главной страницы и страниц разделов;
- запрет ручного изменения автоматически управляемой навигации;
- минимум две исходящие и одну входящую тематическую связь;
- существование целей внутренних ссылок;
- команды:

```bash
python scripts/generate_navigation.py
python scripts/generate_navigation.py --check
python scripts/check_notes.py
```

- [ ] **Step 2: Удалить конкурирующий шаблон**

Удалить `_templates/GitHub Note Style.md`, потому что он задаёт старые блоки `Ключевая схема`, `Развернутый ответ`, `Пример` и `Частые ошибки` как альтернативный стандарт.

- [ ] **Step 3: Проверить единственность стандарта**

```powershell
if (Test-Path -LiteralPath '_templates/GitHub Note Style.md') { exit 1 }
rg -n 'Ключевая схема|Развернутый ответ|## Частые ошибки' _templates
rg -n 'generate_navigation.py|check_notes.py|note-rules/' _templates/repository-rules.md
```

Expected: старых нормативных блоков в `_templates` нет; команды и ссылка на канонические правила присутствуют.

- [ ] **Step 4: Проверить и закоммитить репозиторные правила**

```powershell
git diff --check -- _templates
git add -A -- '_templates/GitHub Note Style.md' '_templates/repository-rules.md'
git commit -m "docs: define repository rules for notes"
```

Expected: один файл удалён, один добавлен; содержимое `notes/` не изменено.

---

### Task 5: Провести полный регрессионный аудит

**Files:**
- Verify: `_templates/note-rules/*.md`
- Verify: `_templates/repository-rules.md`
- Verify: `scripts/generate_navigation.py`
- Verify: `scripts/check_notes.py`
- Verify: `notes/**/*.md`

**Interfaces:**
- Consumes: результаты Tasks 1–4.
- Produces: проверенный комплект правил и чистое рабочее дерево после коммитов.

- [ ] **Step 1: Проверить остаточные карточечные требования**

```powershell
$obsolete = rg -n 'CARD-NAV|двухзначного номера|номер страницы темы|номер файла|Дополнительные вопросы|## Вопрос' _templates/note-rules _templates/repository-rules.md
if ($LASTEXITCODE -ne 1) { $obsolete; exit 1 }
```

Expected: код 0 внешней проверки, потому что `rg` возвращает 1 и совпадений нет.

- [ ] **Step 2: Проверить внутренние ссылки всех правил**

Повторить проверку внутренних Markdown-ссылок из Task 3 для `_templates/note-rules/*.md` и отдельно подтвердить существование `_templates/repository-rules.md`.

- [ ] **Step 3: Проверить отсутствие массовой миграции**

```powershell
$changedNotes = git diff HEAD~4..HEAD --name-only -- notes
if ($changedNotes) { $changedNotes; exit 1 }
```

Expected: файлы в `notes/` не перечислены.

- [ ] **Step 4: Запустить штатные проверки**

```powershell
python scripts/generate_navigation.py --check
python scripts/check_notes.py
git diff --check
```

Expected:

```text
Navigation is up to date: 286 Markdown files.
Notes check passed: 262 notes in 23 sections.
```

`git diff --check` завершается с кодом 0.

- [ ] **Step 5: Проверить состав истории и статус**

```powershell
git log -5 --oneline
git status --short
```

Expected: видны отдельные коммиты структуры, quality gates, маршрутов и репозиторных правил; рабочее дерево чистое.
