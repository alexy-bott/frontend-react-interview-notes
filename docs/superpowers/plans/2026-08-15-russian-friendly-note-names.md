# Russian-Friendly Note Names Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Переименовать разделы и все 262 темы в естественной для русскоязычного фронтенд-разработчика форме и отразить смысловой маршрут каждого раздела двухзначными префиксами файлов.

**Architecture:** Смысловой порядок остаётся задан секционными `README.md`, а общий модуль `scripts/note_paths.py` предоставляет единый разбор имени и отображаемого заголовка. `scripts/renumber_notes.py` синхронизирует префиксы и относительные ссылки; генератор навигации скрывает номера; `check_notes.py` проверяет новый контракт. Массовая смена названий выполняется одноразовым проверяемым скриптом по полному целевому маршруту из приложения A.

**Tech Stack:** Markdown, Python 3.12 standard library, PowerShell, GitHub Actions, существующие `scripts/generate_navigation.py` и `scripts/check_notes.py`.

## Global Constraints

- Механический перевод всех английских слов не используется.
- Сохраняются оригинальные имена технологий, библиотек, стандартов, API и кодовых сущностей.
- В русскоязычных названиях используются формы `фронтенд`, `бэкенд`, `рендеринг`, `кеширование`, `профилирование`, `паттерны`.
- Страница темы имеет имя `<NN> <Название темы>.md`, где `NN` — непрерывный двухзначный номер от `01` внутри раздела.
- Числовой префикс не входит в H1, подписи ссылок и автоматически создаваемую навигацию.
- Каталоги разделов и `README.md` не получают числовых префиксов.
- Порядок страниц задаётся секционным `README.md`; имя файла материализует этот порядок.
- Основной текст заметок не переписывается, кроме названий навигационных сущностей и подписей внутренних ссылок.
- Новые зависимости не добавляются.
- Исторические документы в `docs/superpowers/` задним числом не переписываются.

---

## Карта файлов

- Create: `scripts/note_paths.py` — разбор префиксов, отображаемые названия, порядок раздела и безопасное переписывание относительных Markdown-ссылок.
- Create: `scripts/renumber_notes.py` — проверка и синхронизация числовых префиксов с маршрутами разделов.
- Modify: `scripts/generate_navigation.py` — использование общего порядка и подписей без номеров.
- Modify: `scripts/check_notes.py` — проверка формата, непрерывности, порядка и совпадения H1.
- Modify: `_templates/note-rules/01-file-structure.md` — обязательный префикс и его границы.
- Modify: `_templates/repository-rules.md` — источник порядка, команды перенумерации и проверки.
- Modify: `.github/workflows/check-notes.yml` — запуск проверки префиксов в CI.
- Modify: `README.md`, `notes/*/README.md`, `notes/**/*.md` — новые разделы, имена тем, H1 и внутренние ссылки.
- Temporary create/delete: `scripts/_migrate_note_names.py` — одноразовая атомарная миграция по приложению A; в итоговый коммит не входит.

---

### Task 1: Единый контракт имён и инструмент перенумерации

**Files:**
- Create: `scripts/note_paths.py`
- Create: `scripts/renumber_notes.py`
- Modify: `scripts/generate_navigation.py:10-93`

**Interfaces:**
- Produces: `parse_numbered_name(path: Path) -> tuple[int, str]` — строгий разбор `<NN> <title>.md`.
- Produces: `display_title(path: Path) -> str` — заголовок без префикса; до миграции допускает старое имя без номера.
- Produces: `numbered_filename(position: int, title: str) -> str`.
- Produces: `section_order(readme: Path) -> list[Path]` — существующий порядок ссылок, вынесенный без изменения поведения.
- Produces: `rewrite_internal_links(text: str, current_old: Path, current_new: Path, path_moves: Mapping[Path, Path], display_names: Mapping[Path, str]) -> str`.
- Produces: `planned_moves(notes_root: Path) -> dict[Path, Path]` и CLI `renumber_notes.py (--check | --write)`.
- Consumes: структура `notes/<Раздел>/README.md` и обычные/угловые Markdown-ссылки текущего репозитория.

- [ ] **Step 1: Зафиксировать красную проверку отсутствующего контракта**

Run:

```powershell
python -c "from pathlib import Path; from scripts.note_paths import display_title, numbered_filename; assert display_title(Path('07 Цикл событий (Event Loop).md')) == 'Цикл событий (Event Loop)'; assert numbered_filename(7, 'Promise') == '07 Promise.md'"
```

Expected: FAIL с `ModuleNotFoundError: No module named 'scripts.note_paths'`.

- [ ] **Step 2: Создать минимальные функции имени в `scripts/note_paths.py`**

Добавить следующий контракт:

```python
from __future__ import annotations

import os
import re
from collections.abc import Mapping
from pathlib import Path


NUMBERED_NOTE_RE = re.compile(r"^(?P<number>\d{2}) (?P<title>.+)\.md$")
INVALID_TITLE_RE = re.compile(r'[<>:"/\\|?*]')


def parse_numbered_name(path: Path) -> tuple[int, str]:
    match = NUMBERED_NOTE_RE.fullmatch(path.name)
    if not match:
        raise ValueError(f"expected '<NN> <title>.md': {path.name}")
    return int(match.group("number")), match.group("title")


def display_title(path: Path) -> str:
    match = NUMBERED_NOTE_RE.fullmatch(path.name)
    return match.group("title") if match else path.stem


def numbered_filename(position: int, title: str) -> str:
    if not 1 <= position <= 99:
        raise ValueError(f"position must be between 1 and 99: {position}")
    if not title or INVALID_TITLE_RE.search(title):
        raise ValueError(f"invalid note title: {title!r}")
    return f"{position:02d} {title}.md"
```

- [ ] **Step 3: Повторить проверку функций имени**

Run: команда из Step 1.

Expected: PASS, exit code 0.

- [ ] **Step 4: Вынести `section_order` и операции со ссылками**

Перенести из `generate_navigation.py` в `note_paths.py` без изменения регулярного выражения и проверки полноты маршрута:

```python
def section_order(readme: Path) -> list[Path]: ...

def markdown_destination(current_file: Path, destination: Path) -> str: ...

def rewrite_internal_links(
    text: str,
    current_old: Path,
    current_new: Path,
    path_moves: Mapping[Path, Path],
    display_names: Mapping[Path, str],
) -> str: ...
```

`rewrite_internal_links` обязан оставлять без изменений внешние URL, `mailto:`, якорные ссылки и содержимое fenced code blocks; для внутренней ссылки он разрешает старую цель относительно `current_old`, применяет `path_moves`, строит новый относительный путь от `current_new`, сохраняет `#fragment` и заменяет подпись только при наличии цели в `display_names`.

- [ ] **Step 5: Переключить генератор на общий контракт**

В `scripts/generate_navigation.py` импортировать `display_title`, `markdown_destination` и `section_order`. В `note_navigation` заменить `previous.stem` и `following.stem`:

```python
parts.append(f"[← {display_title(previous)}]({markdown_destination(note, previous)})")
...
parts.append(f"[{display_title(following)} →]({markdown_destination(note, following)})")
```

Удалить перенесённые дублирующиеся функции и импорты.

- [ ] **Step 6: Проверить отсутствие регрессии на старом корпусе**

Run:

```powershell
python scripts/generate_navigation.py --check
python scripts/check_notes.py
```

Expected:

```text
Navigation is up to date: 286 Markdown files.
Notes check passed: 262 notes in 23 sections.
```

- [ ] **Step 7: Создать `scripts/renumber_notes.py`**

Реализовать:

```python
def planned_moves(notes_root: Path) -> dict[Path, Path]:
    moves: dict[Path, Path] = {}
    for section in sorted(path for path in notes_root.iterdir() if path.is_dir()):
        ordered = section_order(section / "README.md")
        for position, source in enumerate(ordered, start=1):
            target = source.with_name(numbered_filename(position, display_title(source)))
            if source != target:
                moves[source.resolve()] = target.resolve()
    return moves


def validate_moves(moves: Mapping[Path, Path], notes_root: Path) -> None: ...
def apply_moves(moves: Mapping[Path, Path], notes_root: Path) -> None: ...
def main() -> int: ...
```

`validate_moves` проверяет, что все абсолютные исходные и итоговые пути находятся внутри разрешённого `notes_root`, итоговые пути уникальны, а существующая цель либо сама входит в набор исходных путей, либо блокирует операцию. `apply_moves` сначала читает и переписывает Markdown, затем использует уникальные временные имена внутри конкретных каталогов, после чего выполняет финальные перемещения и запись. CLI требует ровно один режим: `--check` не пишет и возвращает 1 при рассогласовании; `--write` применяет валидированный план.

- [ ] **Step 8: Подтвердить диагностический результат до миграции**

Run:

```powershell
python scripts/renumber_notes.py --check
```

Expected: exit code 1 и сводка `262 note paths need renumbering`; файлы не изменены.

- [ ] **Step 9: Повторно проверить действующий корпус и diff**

Run:

```powershell
python scripts/generate_navigation.py --check
python scripts/check_notes.py
git diff --check
```

Expected: две штатные проверки PASS; `git diff --check` без вывода.

- [ ] **Step 10: Закоммитить инфраструктуру**

```powershell
git add scripts/note_paths.py scripts/renumber_notes.py scripts/generate_navigation.py
git commit -m "feat: add semantic note renumbering"
```

---

### Task 2: Атомарная миграция разделов и 262 тем

**Files:**
- Temporary create/delete: `scripts/_migrate_note_names.py`
- Rename/Modify: `notes/*/README.md`
- Rename/Modify: `notes/**/*.md`
- Modify: `README.md`
- Modify: `_templates/note-rules/01-file-structure.md:60-105`
- Modify: `_templates/repository-rules.md:69-123`

**Interfaces:**
- Consumes: функции из `scripts/note_paths.py` и полный `TARGET_ROUTES` из приложения A.
- Produces: 23 раздела, 262 пронумерованные страницы, новые H1 и синхронные внутренние ссылки.
- Produces: правила, в которых числовой префикс обязателен и не считается частью отображаемого названия.

- [ ] **Step 1: Создать одноразовый скрипт миграции**

Создать `scripts/_migrate_note_names.py` со следующими интерфейсами и скопировать в `TARGET_ROUTES` приложение A без изменения порядка и формулировок:

```python
TARGET_ROUTES: dict[str, tuple[str, tuple[str, ...]]] = {
    # old_section: (new_section, final_titles_in_current_readme_order)
}


def build_migration(root: Path) -> tuple[dict[Path, Path], dict[Path, str]]: ...
def validate_migration(path_moves: Mapping[Path, Path], display_names: Mapping[Path, str]) -> None: ...
def apply_migration(path_moves: Mapping[Path, Path], display_names: Mapping[Path, str]) -> None: ...
def main() -> int: ...
```

`build_migration` сопоставляет текущие страницы и целевые названия строго по позиции в каждом секционном `README.md`; включает перемещения 14 каталогов, всех `README.md` разделов и 262 страниц. `display_names` содержит новые подписи для страниц и разделов. `validate_migration` требует ровно 23 раздела и 262 страницы, равную длину текущего и целевого маршрутов, отсутствие повторов, коллизий и недопустимых Windows-символов.

`apply_migration` до первого перемещения читает все действующие Markdown-файлы. Затем через временные уникальные пути перемещает файлы и каталоги, заменяет первый H1 страницы или секционного `README.md`, переписывает пути и подписи внутренних ссылок функцией `rewrite_internal_links` и не меняет остальные абзацы.

CLI:

```text
python scripts/_migrate_note_names.py --plan
python scripts/_migrate_note_names.py --write
```

`--plan` только печатает полную таблицу `старый путь -> новый путь` и сводку; `--write` повторно валидирует тот же план перед записью.

- [ ] **Step 2: Получить полную таблицу и проверить её размер**

Run:

```powershell
python scripts/_migrate_note_names.py --plan
```

Expected: exit code 0, `23 sections`, `14 renamed sections`, `262 notes`, `0 collisions`. В каждой строке присутствуют и старый, и итоговый путь.

- [ ] **Step 3: Проверить контрольные точки таблицы до записи**

В выводе `--plan` подтвердить точные строки:

```text
notes/Accessibility/Semantics ARIA и accessible name.md -> notes/Доступность/01 Семантика, ARIA и доступное имя.md
notes/JavaScript/Event Loop.md -> notes/JavaScript/35 Цикл событий (Event Loop).md
notes/React/useEffect vs useLayoutEffect.md -> notes/React/12 useEffect и useLayoutEffect.md
notes/Web Basics/Critical Render Path.md -> notes/Основы веб-платформы/20 Критический путь рендеринга (Critical Render Path).md
notes/Workflow/Jira.md -> notes/Процессы разработки/02 Jira.md
```

Expected: все пять соответствий присутствуют; ни один итоговый заголовок не содержит служебный номер.

- [ ] **Step 4: Применить миграцию**

Run:

```powershell
python scripts/_migrate_note_names.py --write
```

Expected: `Migration applied: 23 sections, 262 notes`; отсутствуют частично перемещённые каталоги и временные имена.

- [ ] **Step 5: Пересобрать служебную навигацию**

Run:

```powershell
python scripts/generate_navigation.py
python scripts/generate_navigation.py --check
python scripts/renumber_notes.py --check
python scripts/check_notes.py
```

Expected:

```text
Navigation is up to date: 286 Markdown files.
Note numbering is up to date: 262 notes in 23 sections.
Notes check passed: 262 notes in 23 sections.
```

- [ ] **Step 6: Обновить правило имени файла**

В `_templates/note-rules/01-file-structure.md` заменить прежний запрет на нормативный блок:

```text
Имя репозиторного файла страницы темы состоит из двухзначного числового префикса, пробела, читаемого названия темы и расширения `.md`:

01 Название темы.md

Префикс отражает положение страницы в маршруте секционного README.md. Он не входит в название темы, H1 и подписи навигационных ссылок. H1 согласуется с частью имени файла после удаления префикса и расширения.
```

В описании достоверности имени сохранить существующие ограничения для вложений и временных файлов.

- [ ] **Step 7: Обновить репозиторные правила**

В `_templates/repository-rules.md` зафиксировать:

```text
- порядок ссылок в секционном README.md является источником смыслового маршрута;
- scripts/renumber_notes.py --write синхронизирует имена файлов и внутренние ссылки;
- scripts/renumber_notes.py --check подтверждает непрерывность и соответствие маршруту;
- scripts/generate_navigation.py обслуживает только блоки NOTE-NAV-* и SECTION-NAV-* и скрывает служебные номера.
```

Добавить `python scripts/renumber_notes.py --check` в обязательный набор финальных команд.

- [ ] **Step 8: Удалить одноразовый скрипт**

Удалить `scripts/_migrate_note_names.py` через `apply_patch`. Проверить:

```powershell
Test-Path scripts/_migrate_note_names.py
```

Expected: `False`.

- [ ] **Step 9: Проверить миграционный diff**

Run:

```powershell
git diff --check
git diff --summary
git status --short
```

Expected: нет whitespace errors; Git показывает перемещения каталогов и файлов, а не 262 независимых удаления без новых файлов; временный скрипт отсутствует.

- [ ] **Step 10: Закоммитить миграцию и правила**

```powershell
git add README.md notes _templates/note-rules/01-file-structure.md _templates/repository-rules.md
git commit -m "docs: localize and order note names"
```

---

### Task 3: Репозиторные инварианты и CI

**Files:**
- Modify: `scripts/check_notes.py:8-149`
- Modify: `.github/workflows/check-notes.yml`

**Interfaces:**
- Consumes: `parse_numbered_name`, `display_title`, `section_order` из `scripts/note_paths.py`.
- Produces: ошибки `invalid numeric prefix`, `non-contiguous numbering`, `README order differs from numeric order`, `H1 differs from filename`.
- Produces: CI, запускающий генератор, перенумерацию в режиме проверки и полную проверку заметок.

- [ ] **Step 1: Зафиксировать красную проверку несовпадения H1**

Временно вызвать ещё не существующую чистую функцию:

```powershell
python -c "from pathlib import Path; from scripts.check_notes import note_identity_errors; assert note_identity_errors(Path('01 Promise.md'), '# Другое название\n') == ['H1 differs from filename: expected Promise']"
```

Expected: FAIL с `ImportError`.

- [ ] **Step 2: Добавить чистые проверки идентичности и порядка**

В `scripts/check_notes.py` добавить:

```python
def note_identity_errors(note: Path, visible: str) -> list[str]:
    errors: list[str] = []
    try:
        _, expected_title = parse_numbered_name(note)
    except ValueError:
        return [f"invalid numeric prefix: {note.name}"]
    headings = re.findall(r"^# ([^#].*)$", visible, flags=re.MULTILINE)
    if len(headings) == 1 and headings[0] != expected_title:
        errors.append(f"H1 differs from filename: expected {expected_title}")
    return errors


def section_numbering_errors(readme: Path, ordered: list[Path]) -> list[str]:
    numbers = [parse_numbered_name(path)[0] for path in ordered]
    expected = list(range(1, len(ordered) + 1))
    errors: list[str] = []
    if numbers != expected:
        errors.append(f"README order differs from numeric order: {numbers}")
    if sorted(numbers) != expected:
        errors.append(f"non-contiguous numbering: {sorted(numbers)}")
    return errors
```

В `main()` добавлять эти сообщения с текущим относительным путём. Некорректный префикс не должен приводить к необработанному исключению в проверке раздела.

- [ ] **Step 3: Повторить локальную проверку идентичности**

Run: команда из Step 1.

Expected: PASS, exit code 0.

- [ ] **Step 4: Проверить весь корпус новым контрактом**

Run:

```powershell
python scripts/check_notes.py
```

Expected: `Notes check passed: 262 notes in 23 sections.`

- [ ] **Step 5: Добавить проверку нумерации в GitHub Actions**

Итоговый порядок шагов `.github/workflows/check-notes.yml`:

```yaml
      - run: python scripts/generate_navigation.py --check
      - run: python scripts/renumber_notes.py --check
      - run: python scripts/check_notes.py
```

- [ ] **Step 6: Исключить старые пути из действующего корпуса**

Run:

```powershell
rg -n "notes/(Accessibility|Algorithms|Architecture|Browser Internals|Forms|Frontend System Design|Patterns|Performance|Principles|Security|Testing|Tooling|Web Basics|Workflow)/" README.md notes scripts _templates .github
```

Expected: no matches. Исторический каталог `docs/superpowers/` намеренно не входит в поиск.

- [ ] **Step 7: Проверить формат всех страниц и отсутствие номеров в H1**

Run:

```powershell
python -c "from pathlib import Path; import re; notes=[p for p in Path('notes').rglob('*.md') if p.name != 'README.md']; assert len(notes)==262; assert all(re.fullmatch(r'\d{2} .+\.md', p.name) for p in notes); assert all(not re.match(r'^# \d{2} ', p.read_text(encoding='utf-8')) for p in notes)"
```

Expected: PASS, exit code 0.

- [ ] **Step 8: Выполнить полную автоматическую проверку**

Run:

```powershell
python scripts/generate_navigation.py --check
python scripts/renumber_notes.py --check
python scripts/check_notes.py
git diff --check
```

Expected: три проверки PASS; `git diff --check` без вывода.

- [ ] **Step 9: Вручную проверить навигационную выборку**

Открыть и проверить H1, верхнюю и нижнюю навигацию, подписи без номеров и существование целей:

```text
notes/JavaScript/01 Типы данных.md
notes/JavaScript/35 Цикл событий (Event Loop).md
notes/JavaScript/51 Оптимизация фронтенда.md
notes/React/01 Преимущества React.md
notes/React/19 HOC и React.memo.md
notes/React/37 Правила хуков.md
notes/Основы веб-платформы/01 URL в адресной строке.md
notes/Основы веб-платформы/26 Service Workers и PWA.md
```

Expected: номера видны только в файловых путях; H1 и подписи ссылок используют названия из приложения A.

- [ ] **Step 10: Закоммитить проверки**

```powershell
git add scripts/check_notes.py .github/workflows/check-notes.yml
git commit -m "ci: enforce semantic note numbering"
```

- [ ] **Step 11: Выполнить финальную проверку после коммита**

Run:

```powershell
python scripts/generate_navigation.py --check
python scripts/renumber_notes.py --check
python scripts/check_notes.py
git diff --check
git status --short
```

Expected: три проверки PASS; две команды Git без вывода.

---

## Приложение A: целевые маршруты

Порядок строк внутри каждого раздела является окончательным номером файла. Название раздела после стрелки является итоговым именем каталога и H1 секционного `README.md`.

### Accessibility → Доступность

1. Семантика, ARIA и доступное имя
2. Клавиатурная навигация и управление фокусом
3. Доступность диалогов, выпадающих элементов и оверлеев
4. Доступность форм и сообщений об ошибках

### Algorithms → Алгоритмы

1. Big O и сложность алгоритмов
2. Сложность методов массивов
3. Выбор структуры данных — Map, Set или Object
4. Типовые алгоритмические задачи во фронтенде

### Architecture → Архитектура

1. Архитектура фронтенда
2. Feature-Sliced Design (FSD)
3. Управление состоянием
4. API-слой и контракты
5. Обработка ошибок и наблюдаемость
6. Флаги функциональности (Feature Flags)
7. Микрофронтенды

### Browser Internals → Устройство браузера

1. Архитектура браузера — процессы и потоки
2. Что происходит после ввода URL
3. Конвейер рендеринга — reflow, repaint и composite
4. Главный поток, долгие задачи и отзывчивость
5. Делегирование, перехват и всплытие событий
6. Утечки памяти и профилирование
7. Жизненный цикл страницы и фоновые вкладки

### CSS → CSS

1. Каскад и наследование
2. Специфичность селекторов
3. Псевдоклассы и псевдоэлементы
4. Блочная модель (Box Model)
5. display и контексты форматирования
6. Единицы измерения
7. Flexbox
8. CSS Grid
9. Адаптивный дизайн и медиазапросы
10. Контейнерные запросы
11. Сброс и нормализация стилей
12. CSS-препроцессоры
13. SCSS
14. Модули SCSS — @use и @forward
15. Переменные, миксины и функции SCSS
16. Архитектура SCSS и вложенность
17. Центрирование
18. Позиционирование
19. Контекст наложения и z-index
20. Анимации — transform или position

### DevOps → DevOps

1. Docker для фронтенда
2. Многоэтапная сборка Dockerfile
3. Nginx и раздача статических файлов
4. Переменные окружения и секреты
5. Артефакты, кеш и переменные пайплайна
6. GitLab CI-CD
7. CI-CD-пайплайн фронтенда

### Forms → Формы

1. Формы во фронтенде
2. Управляемые и неуправляемые формы, FormData
3. React Hook Form
4. Controller и пользовательские компоненты
5. Валидация форм
6. Серверные ошибки и асинхронная валидация
7. Состояние формы и жизненный цикл отправки
8. Архитектура форм

### Frontend System Design → Системный дизайн фронтенда

1. Проектирование фронтенд-фичи
2. Таблица с фильтрацией, сортировкой и пагинацией
3. Форма с асинхронной валидацией и серверными ошибками
4. Авторизация и защищённые маршруты
5. Экран с обновлениями в реальном времени

### Git → Git

1. Git для фронтенда
2. merge, rebase, cherry-pick, revert и reset
3. Конфликты и код-ревью

### HTML → HTML

1. HTML
2. Семантическая вёрстка
3. Доступность HTML
4. Формы
5. head, метаданные и ресурсные подсказки
6. Изображения и адаптивные медиа

### JavaScript → JavaScript

1. Типы данных
2. Number, BigInt и точность вычислений
3. Строки Unicode и кодировки
4. Приведение типов
5. Сравнение через ==, === и Object.is
6. Автоупаковка (Autoboxing)
7. Опциональная цепочка и оператор нулевого слияния
8. Деструктуризация, rest и spread
9. var, let и const
10. Поднятие объявлений (hoisting) и TDZ
11. Контекст выполнения и области видимости
12. Строгий режим (strict mode)
13. Функции
14. Функции высшего порядка, каррирование и композиция
15. Замыкание
16. this
17. Чистая функция
18. Прототипы
19. Классы и наследование
20. Дескрипторы, геттеры и сеттеры
21. Проверка свойств объекта
22. Копирование объектов
23. Неизменяемость объектов
24. Proxy и Reflect
25. Сериализация JSON
26. Массивы и методы массивов
27. Map, Set, WeakMap и WeakSet
28. Итераторы и генераторы
29. Date и Intl
30. Регулярные выражения
31. ArrayBuffer, TypedArray и DataView
32. ES-модули
33. async и defer
34. Обработка ошибок
35. Цикл событий (Event Loop)
36. Таймеры — setTimeout и setInterval
37. Promise
38. Комбинаторы Promise
39. async и await
40. AbortController
41. Fetch и работа с API
42. Debounce и throttle
43. DOM API — innerHTML и layout
44. События DOM
45. CustomEvent, EventTarget и dispatchEvent
46. Observer API
47. requestAnimationFrame и requestIdleCallback
48. Streams API
49. postMessage и BroadcastChannel
50. Сборка мусора
51. Оптимизация фронтенда

### Next.js → Next.js

1. Next.js 14
2. App Router
3. Серверные и клиентские компоненты
4. SSR, SSG, ISR и Streaming
5. Получение данных, кеш и ревалидация
6. Server Actions и Route Handlers
7. Деплой, переменные окружения и Docker

### Patterns → Паттерны

1. Стратегия (Strategy)
2. Адаптер и фасад
3. Observer, Pub-Sub и события
4. Фабрика, одиночка и жизненный цикл
5. Compound Components и Headless UI

### Performance → Производительность

1. Диагностика и профилирование производительности
2. Core Web Vitals — LCP, INP и CLS
3. Размер бандла и стратегия загрузки
4. Профилирование производительности React
5. Изображения, шрифты и приоритет ресурсов

### Principles → Принципы разработки

1. SOLID во фронтенде
2. DRY, KISS и YAGNI
3. Композиция вместо наследования

### React → React

1. Преимущества React
2. Как работает React
3. Fiber
4. Согласование (Reconciliation)
5. Причины рендера
6. Состояние в React
7. Серверное состояние и React Query
8. key
9. Обработка ошибок через Error Boundaries
10. Хуки
11. useReducer
12. useEffect и useLayoutEffect
13. useRef
14. useCallback
15. useTransition и useDeferredValue
16. Мемоизация
17. Context
18. Управляемые и неуправляемые компоненты
19. HOC и React.memo
20. Пакетное обновление (Batching)
21. Жизненный цикл
22. Порталы
23. Redux и Flux
24. Redux Toolkit
25. RTK Query
26. Zustand
27. SSR и SSG
28. Гидратация (Hydration)
29. Suspense и lazy
30. React Router
31. Radix UI
32. React 18 и 19
33. Серверные компоненты
34. React Compiler
35. useEffectEvent
36. Activity
37. Правила хуков

### Security → Безопасность

1. Модель угроз фронтенда
2. Хранение токенов — XSS, CSRF и компромиссы
3. CORS, CSP и границы безопасности браузера
4. Цепочка поставок, секреты и сторонние скрипты

### Testing → Тестирование

1. Тестирование фронтенда
2. Стратегия тестирования фронтенда
3. Jest
4. React Testing Library
5. MSW и моки API
6. Асинхронный UI, формы и авторизация
7. E2E-тестирование
8. Нестабильные тесты (Flaky Tests)

### Tooling → Инструменты разработки

1. Файлы фронтенд-проекта
2. package.json и lock-файлы
3. Версии зависимостей и semver
4. npm, Yarn, pnpm и менеджеры пакетов
5. Воспроизводимые версии в команде
6. Файлы окружения и переменные фронтенда
7. ESLint, Prettier и конфигурация качества кода
8. .gitignore, .npmrc, README и служебные файлы
9. Анализ бандла и бюджет размера
10. Vite
11. Webpack
12. Конфигурация production-сборки

### TypeScript → TypeScript

1. Плюсы и минусы TypeScript
2. Типы данных
3. Вывод типов, widening и контекстная типизация
4. never, any и unknown
5. Утверждения типов и non-null assertion
6. Объединения, пересечения и дискриминируемые объединения
7. Type Guards
8. type и interface
9. Структурная типизация
10. Типизация функций
11. Классы — модификаторы доступа, abstract и private
12. Дженерики
13. Перегрузка функций
14. Вариантность и совместимость функций
15. Типизация Array.map
16. keyof, indexed access и mapped types
17. Utility Types
18. infer и условные типы
19. as const и satisfies
20. tsconfig и строгий режим
21. enum
22. import type и isolatedModules
23. Файлы деклараций
24. Проверка данных с бэкенда
25. Типизация React с TypeScript

### Vue → Vue

1. Options API и Composition API
2. Реактивность
3. Виртуальный DOM
4. Слоты
5. Жизненный цикл
6. Proxy

### Web Basics → Основы веб-платформы

1. URL в адресной строке
2. Веб-протоколы
3. HTTP и HTTPS
4. HTTP-запрос
5. HTTP-методы
6. Коды состояния HTTP и ошибки API
7. REST
8. Пагинация, фильтрация и сортировка API
9. OpenAPI и Swagger
10. Хранение данных в браузере
11. Cookie и авторизация
12. Процесс авторизации и refresh-токены
13. CORS
14. XSS
15. CSRF
16. CSP и заголовки безопасности
17. OWASP Top 10
18. HTTP-кеширование
19. Бандлеры и разделение кода
20. Критический путь рендеринга (Critical Render Path)
21. Core Web Vitals
22. Транспорты реального времени
23. WebSocket
24. SSE
25. Web Workers
26. Service Workers и PWA

### Workflow → Процессы разработки

1. Scrum и Agile
2. Jira
