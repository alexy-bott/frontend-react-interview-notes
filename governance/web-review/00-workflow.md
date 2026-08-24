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
- точный содержательный кандидат либо явно bounded structural/code postcondition;
- verification contract:
  - hash полного файла, если Codex не должен менять generated regions, пути или внутренние ссылки;
  - иначе protected-content manifest с точными Web-authored фрагментами или их hashes, явным списком generated regions и exact разрешёнными `old → new` переписываниями путей/назначений ссылок;
- применимые source checks.

`Vn` обозначает защищённое смысловое содержание вместе с его verification contract. Штатная генерация навигации, переименование файлов и разрешённое переписывание назначений ссылок не создают `Vn+1`, только если actual diff полностью соответствует contract и не меняет подписи ссылок, прозу, код или идентичность тематических целей. Любое изменение защищённого содержания либо выход за contract создаёт `Vn+1` и отменяет предыдущие semantic confirmations.

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

### 4. Primary confirmation Web-кандидата

Если Web уже сформировал exact содержательный кандидат или exact итоговую структуру, он проверяет полный `Vn` снова по применимым Levels 1–4. Положительный статус:

```text
PRIMARY WEB PASS(Vn)
```

Он недоступен при блокирующем `NOT CHECKED`.

Если выбран `BOUNDED_CODE` либо `BOUNDED_STRUCTURE` задан только как postcondition без exact итогового файла, до исполнения фиксируются защищённая проза и bounded contract. Фактический итоговый файл появляется только после Codex и проходит применимый primary review по actual GitHub result.

### 5. Fresh Web review

Для окончательной готовности каждой новой, мигрируемой или явно взятой в полное ревью заметки требуется независимый fresh review exact фактического `Vn` — даже если primary review не потребовал изменения текста. Fresh gate защищает не только от регрессии после редактирования, но и от ложного первичного `PASS`.

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

Отдельная pure mechanical задача, которая не является полным ревью заметки и доказанно не меняет protected content, может не запускать новый fresh semantic review, но требует Web-проверки структуры и actual diff. Эта льгота не позволяет объявить ранее не проверенную заметку готовой: новая, мигрируемая или явно взятая в полное ревью заметка всё равно требует `FRESH WEB PASS(Vn)`.

### 6. Codex execution

Для exact Web-кандидата или exact итоговой структуры Codex запускается после primary и fresh confirmation. Для `BOUNDED_CODE` и postcondition-only `BOUNDED_STRUCTURE` Codex запускается после утверждения protected prose и bounded contract; resulting actual file затем получает применимый primary review, а для новой, мигрируемой или полноценно ревьюируемой заметки — fresh review exact actual `Vn`.

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

Если actual result совпадает с full-file hash либо protected-content manifest и все generated/path rewrites входят в разрешённый contract, прежние primary/fresh confirmations exact Web-кандидата сохраняются: третье смысловое переписывание не требуется.

Если Codex реализовал `BOUNDED_CODE` или postcondition-only `BOUNDED_STRUCTURE`, actual result становится exact фактическим `Vn`: Web выполняет применимый primary review. Fresh review выполняется заново, если заметка новая, мигрируемая, явно взята в полное ревью либо protected semantic content изменилось. Предыдущее fresh confirmation можно сохранить только для отдельной mechanical structure-задачи, когда protected content побайтово/по manifest неизменно и задача не является полным ревью заметки.

### 8. Candidate status

Feature branch получает:

```text
CANDIDATE READY(Vn)
```

только если:

- primary и требуемый fresh review относятся к тому же `Vn`;
- actual branch соответствует утверждённому кандидату и его verification contract;
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

Codex может применить batch из нескольких exact кандидатов только если Web перечислил для каждого path, verification contract, scope и допустимые generated/path changes. Batch не превращает заметки в один общий semantic verdict.

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
