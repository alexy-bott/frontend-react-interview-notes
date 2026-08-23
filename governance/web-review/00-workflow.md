# Web-led workflow заметок

**Канонический файл:** [`00-workflow.md`](<./00-workflow.md>).

Этот документ определяет роли и порядок работы. Levels 1–5 — логические зоны ответственности, а не автономные Codex-агенты.

## Источники истины

- опубликованный default branch GitHub — factual source of truth;
- exact SHA, на котором ChatGPT Web проводил анализ, — analysis-base;
- actual feature branch и её diff — evidence результата исполнения;
- отчёт Codex сам по себе не доказывает корректность содержимого.

## Роли

### Пользователь

- задаёт цель и приоритет;
- принимает только действительно новые semantic/product решения;
- не обязан вручную проверять каждое предложение или переносить длинные логи.

### ChatGPT Web

- читает actual repository state;
- определяет, относится ли заметка к legacy или явно взята в миграцию;
- выполняет Levels 1 → 2 → 3 → 4;
- проверяет актуальные технические утверждения по первичным источникам;
- владеет решениями `PASS`, `FAIL` и `NOT CHECKED`;
- проектирует Level 5 change-set;
- формулирует окончательную прозу;
- задаёт Codex точный base, режим, scope и проверки;
- после push читает actual GitHub branch и diff;
- подтверждает `CANDIDATE READY` и `READY`.

### Codex

- ограниченный исполнитель;
- не проводит обычное смысловое ревью заметки вместо Web;
- не решает, понятен ли текст и достаточно ли материала;
- не расширяет semantic scope;
- применяет Web-кандидат, выполняет разрешённую структуру/код и штатное обслуживание;
- возвращает `STOP`, когда требуется новое смысловое решение или изменился base.

### GitHub и CI

- фиксируют опубликованное состояние;
- подтверждают branch, HEAD, diff и механические проверки;
- не заменяют смысловой Web-review.

## Граница постепенной миграции

Новая содержательная модель обязательна для:

- новой заметки;
- существующей заметки, явно взятой в миграцию или полное ревью;
- заметки, уже приведённой к активной модели.

Остальной корпус остаётся legacy до отдельной обработки. Изменение governance не запускает массовую автоматическую переработку `notes/**` и не разрешает Codex самостоятельно нормализовать все страницы.

## Версия кандидата

Для каждой заметки Web фиксирует candidate version `Vn`:

- exact repository path либо ожидаемое новое положение;
- точный содержательный кандидат;
- hash полного файла, если generated regions не меняются;
- либо hash Web-authored содержимого вне `NOTE-NAV-*`, когда навигация будет сформирована штатным генератором;
- применимые source checks.

Любое содержательное изменение создаёт `Vn+1` и отменяет предыдущие semantic confirmations.

## Существующая заметка

### 1. Baseline

Web:

1. проверяет live `main`;
2. фиксирует analysis-base SHA;
3. читает заметку целиком, секционный `README.md`, связанные страницы и применимую governance;
4. не использует dirty local worktree как source of truth.

### 2. Primary Web review

Web последовательно выполняет:

```text
Level 1 — внешний каркас
Level 2 — блоки и Markdown/HTML
Level 3 — состав и распределение материала
Level 4 — техническое и текстовое качество
```

`FAIL` раннего уровня не прекращает остальные доступные проверки. Невозможная под-проверка получает локальный `NOT CHECKED` с причиной.

Level 4 обязательно включает:

1. техническую корректность;
2. полноту;
3. глобальную понятность;
4. локальную прозрачность значимых предложений и коротких фрагментов;
5. перегруженность;
6. избыточность.

Пункты 3–6 реализуют пять канонических критериев Level 4: локальная прозрачность является под-проверкой понятности, а не шестым критерием.

### 3. Level 5 — Web change design

При подтверждённых `FAIL` ChatGPT Web применяет [`05-change-design.md`](<./05-change-design.md>) и создаёт bounded execution specification.

Для изменения прозы Web по умолчанию формулирует exact итоговый текст до Codex.

### 4. Primary confirmation exact Web-кандидата

Если Web уже сформировал exact содержательный кандидат, он проверяет полный `Vn` снова по применимым Levels 1–4. Положительный статус:

```text
PRIMARY WEB PASS(Vn)
```

Он недоступен при блокирующем `NOT CHECKED`.

Если выбран `BOUNDED_CODE` и фактический код ещё должен создать Codex, до исполнения фиксируются Web-approved prose и code contract, но окончательный `Vn` возникает только после чтения actual GitHub result. Такой `Vn` проходит primary review после исполнения.

### 5. Fresh Web review

Для окончательной готовности заметки с изменённым содержанием требуется независимый fresh review exact фактического `Vn`.

Fresh review:

- выполняется в новой top-level сессии ChatGPT Web;
- получает одну заметку, её path/контекст и активную governance;
- не получает primary verdict, список предыдущих `FAIL`, rationale, change design или diff как подсказку;
- самостоятельно выполняет Levels 1–4 и применимые source checks;
- работает read-only;
- не проектирует и не исполняет исправление.

Review в той же primary-беседе не может называться fresh.

Положительный статус:

```text
FRESH WEB PASS(Vn)
```

Pure mechanical change, которое доказанно не меняет Web-authored содержание заметки, не требует нового fresh semantic review, но требует Web-проверки структуры и actual diff.

### 6. Codex execution

Для exact Web-кандидата Codex запускается после primary и fresh confirmation. Для `BOUNDED_CODE` Codex запускается после утверждения prose и code contract; resulting actual file затем получает новый primary и fresh review.

Web выбирает режим из [`../codex-execution.md`](<../codex-execution.md>):

- `EXACT_NOTE_CANDIDATE` — проза и готовый текст;
- `BOUNDED_STRUCTURE` — детерминированная разметка;
- `BOUNDED_CODE` — ограниченный код;
- `REPOSITORY_MAINTENANCE` — генераторы, нумерация и ссылки.

Одна Web-инструкция означает один semantic execution pass. Codex не выполняет внутренний цикл `review → rewrite → review`.

### 7. Web verification actual branch

После push Web читает:

- actual branch HEAD;
- changed paths;
- actual файлы и diff;
- результаты CI/checks;
- соответствие Web-authored части exact `Vn`;
- generated regions и repository invariants отдельно.

Совпадение exact candidate не требует третьего смыслового переписывания. Если Codex реализовал `BOUNDED_CODE`, actual result становится новым exact `Vn`: Web выполняет полный primary review и отдельный fresh review до `CANDIDATE READY`.

### 8. Candidate status

Feature branch получает:

```text
CANDIDATE READY(Vn)
```

только если:

- primary и требуемый fresh review относятся к тому же `Vn`;
- actual branch соответствует утверждённому кандидату;
- нет блокирующих `NOT CHECKED`;
- repository checks дали `REPO PASS`;
- base и scope подтверждены.

`CANDIDATE READY` не означает, что результат уже опубликован в `main`.

### 9. Publication

Публикация — отдельная операция.

Перед ней Web повторно проверяет live `main`. Если SHA изменился, Codex возвращает `STOP`; он не выполняет rebase/merge/cherry-pick самостоятельно.

После безопасной публикации Web читает actual default branch. Только неизменённый опубликованный `Vn` может получить:

```text
READY(Vn)
```

## Создание новой заметки

Используется [`new-note-workflow.md`](<./new-note-workflow.md>), затем тот же primary/fresh/execution/publication процесс.

## Работа с несколькими заметками

Corpus review выполняется последовательно по заметкам. Для каждой заметки отдельно фиксируются path, `Vn`, primary status, fresh status и repository status.

Codex может применить batch из нескольких exact кандидатов только если Web перечислил каждый path, hash, scope и допустимые generated changes. Batch не превращает заметки в один общий semantic verdict.

## Статусы

Локальные:

```text
PASS / FAIL / NOT CHECKED по Levels 1–4
PRIMARY WEB PASS(Vn)
FRESH WEB PASS(Vn)
```

Репозиторные:

```text
REPO PASS
REPO FAIL
REPO NOT CHECKED
```

Готовность:

```text
CANDIDATE READY(Vn) — проверенная feature branch
READY(Vn) — та же версия опубликована и проверена в main
```

## Защита от бесконечного цикла

Если правила конфликтуют, необходимых данных нет или новый проход повторяет то же состояние без прогресса, Web фиксирует `UNRESOLVED` и останавливает автоматический цикл. Codex не выбирает, какое правило игнорировать.
