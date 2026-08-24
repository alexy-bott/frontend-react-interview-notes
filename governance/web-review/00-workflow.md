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

### 5. Codex execution

Для exact Web-кандидата или exact итоговой структуры Codex запускается после `PRIMARY WEB PASS(Vn)`. Для `BOUNDED_CODE` и postcondition-only `BOUNDED_STRUCTURE` Codex запускается после утверждения protected prose и bounded contract.

Fresh Web confirmation не является предварительным условием записи в изолированную feature branch. Исполнение Codex только создаёт actual GitHub candidate для независимой проверки. Оно не даёт заметке `CANDIDATE READY` и не заменяет обязательный fresh review.

Web выбирает режим из [`../codex-execution.md`](<../codex-execution.md>):

- `EXACT_NOTE_CANDIDATE` — проза и готовый текст;
- `BOUNDED_STRUCTURE` — детерминированная разметка;
- `BOUNDED_CODE` — ограниченный код;
- `REPOSITORY_MAINTENANCE` — генераторы, нумерация и ссылки.

Одна Web-инструкция означает один semantic execution pass. Codex не выполняет внутренний цикл `review → rewrite → review`.

### 6. Web verification actual branch

После push Web читает:

- actual branch HEAD;
- changed paths;
- actual файлы и diff;
- результаты CI/checks;
- соответствие Web-authored части exact `Vn`;
- generated regions и repository invariants отдельно.

Если actual result совпадает с full-file hash либо protected-content manifest и все generated/path rewrites входят в разрешённый contract, `PRIMARY WEB PASS(Vn)` exact Web-кандидата сохраняется. Actual candidate commit становится единственным объектом последующего fresh review; повторное смысловое переписывание только из-за переноса текста в feature branch не требуется.

Если Codex реализовал `BOUNDED_CODE` или postcondition-only `BOUNDED_STRUCTURE`, actual result становится exact фактическим `Vn`. Web выполняет применимый primary review по actual GitHub result. Только версия, получившая `PRIMARY WEB PASS(Vn)` на exact содержании либо подтверждённая по verification contract, может быть передана на fresh review.

После проверки Web фиксирует отдельно для каждой заметки:

- exact candidate commit SHA;
- repository path;
- candidate version `Vn`;
- соответствие verification contract;
- repository status.

### 7. Independent Fresh lane

Для окончательной готовности каждой новой, мигрируемой или явно взятой в полное ревью заметки требуется независимый Web-review actual GitHub candidate после Web verification feature branch. Независимая lane защищает как от регрессии исполнения, так и от ложного первичного `PASS`.

#### Initial Fresh

Первый независимый review конкретного path выполняется как полный Initial Fresh review exact фактического `Vn`.

Initial Fresh:

- выполняется в отдельной top-level сессии ChatGPT Web, изолированной от primary review;
- получает repository, exact candidate commit SHA, exact path или список paths и governance ref SHA;
- может читать секционный `README.md`, связанные заметки и другой необходимый current context непосредственно из указанного GitHub commit;
- не получает primary verdict, список primary `FAIL`, rationale, change design, старую версию текста, diff или отчёт Codex как подсказку;
- самостоятельно выполняет complete Levels 1–4 и применимые source checks;
- работает read-only;
- не проектирует и не исполняет исправление.

Одна independent Fresh lane может последовательно проверять несколько разных заметок и batches. Отдельная top-level сессия для каждой заметки не требуется.

Каждая заметка остаётся самостоятельной единицей review. Для каждого path отдельно фиксируются:

- exact candidate commit SHA;
- candidate version `Vn`;
- Levels 1–4;
- применимые source checks;
- `FRESH WEB PASS(Vn)`, `FAIL` или блокирующий `NOT CHECKED`.

Общий verdict на batch не заменяет отдельных verdicts по его заметкам.

Полный Initial Fresh создаёт fresh-owned baseline evidence даже если итоговый verdict — `FAIL`: независимая lane может сохранить собственные положительные результаты для тех semantic units и под-проверок, которые она действительно проверила и не пометила `FAIL` или `NOT CHECKED`.

Fresh-сессия может позже впервые проверять path, который ранее только встречался ей как repository context, если она не получала по нему primary/change materials и не выносила самостоятельный semantic verdict.

#### Follow-up после semantic correction

Semantic `Vn+1` после Initial Fresh `FAIL` не требует автоматически нового fresh-поколения и полного rereview всей заметки.

Та же независимая Fresh lane может выполнить Follow-up review, используя только собственную предыдущую review history:

```text
previous Fresh-reviewed blob
→ current actual candidate blob
→ changed semantic units
→ dependency cone
→ whole-note consistency scan
````

В Follow-up lane разрешено самостоятельно сравнивать свой previous reviewed blob с current candidate. Это сравнение является частью собственного independent review evidence и не считается передачей Primary diff.

Follow-up не получает:

* primary verdict по новой версии;
* primary rationale;
* primary change design;
* Codex report;
* объяснение того, какие именно правки Primary считал достаточными.

Если та же top-level Fresh-сессия продолжает lane, она использует собственные прежние findings и source evidence. Если valid fresh-owned baseline невозможно доказательно восстановить, incremental mode недоступен и выполняется полный независимый review.

#### Semantic units

Fresh reviewer выбирает минимальную самостоятельно проверяемую единицу, которая сохраняет смысл. Обычно это:

* отдельный абзац;
* список или таблица;
* code block вместе с непосредственно объясняющим его текстом;
* самостоятельный фрагмент внутри тематического H2/H3;
* стандартизированный смысловой блок, если его части зависят друг от друга;
* набор source entries, относящийся к одному изменяемому claim или API.

Byte-identical semantic units могут наследовать только собственное previous Fresh evidence. Primary evidence таким способом не наследуется.

#### Dependency cone

Incremental Follow-up обязан проверять не только изменённую строку.

Минимальный impact cone определяется так:

| Тип изменения                                | Что повторно проверяется                                                                        |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Локальная формулировка                       | изменённая unit, соседний контекст и summary/clarification, если они повторяют тот же смысл     |
| Техническое утверждение                      | изменённая unit, зависимые пример/таблица/code fragment и применимый current primary source     |
| Новый или уточнённый термин                  | место определения и все зависимые использования термина в заметке                               |
| Source-only correction                       | применимость нового source и соответствие source тому claim/API, который он должен подтверждать |
| Удаление или перенос материала               | затронутые исходный и итоговый блоки, completeness, distribution и redundancy                   |
| Изменение keyboard/state/data-flow механизма | все локальные примеры, таблицы и ключевые уточнения, которые используют тот же механизм         |

После dependency cone всегда выполняется короткий whole-note consistency scan. Он проверяет, что correction:

* не создала противоречие с byte-identical материалом;
* не оставила старую формулировку того же механизма в другом месте;
* не нарушила терминологическую согласованность;
* не создала новый существенный пробел;
* не создала локальную перегруженность или дублирование;
* не нарушила обязательный внешний и внутренний каркас заметки.

#### Source evidence в Follow-up

Изменённый или зависимый technical claim проверяется заново по актуальному применимому primary source.

Byte-identical claims могут наследовать собственное Fresh source evidence и не требуют полного повторного исследования на каждом cycle.

Fresh reviewer обязан переоткрыть unchanged evidence, если:

* source или API materially изменились;
* предыдущее evidence стало явно устаревшим;
* current correction меняет интерпретацию зависимого claim;
* whole-note consistency scan выявляет возможное противоречие;
* reviewer больше не может доказательно считать старое evidence применимым.

#### Escalation в FULL Follow-up

Incremental mode прекращается и Follow-up выполняется как полный Levels 1–4 review current candidate, если выполняется хотя бы одно условие:

* изменены filename, H1 или identity темы;
* materially изменена центральная учебная модель или основной механизм заметки;
* substantially переписан `Быстрый ответ` так, что изменился contract всей заметки;
* добавлен новый самостоятельный механизм или новый существенный аспект темы;
* material перемещён между тематическими блоками так, что требуется заново оценивать content distribution;
* изменено больше трёх независимых content semantic units, не считая source entries, которые только документируют уже существующие claims;
* одновременно существенно перестроено несколько тематических H2/H3;
* изменена semantic criteria identity Levels 1–4;
* relevant previous review имел блокирующий `NOT CHECKED`;
* dependency cone невозможно доказательно ограничить;
* consistency scan обнаружил возможную регрессию вне первоначального cone.

FULL Follow-up может выполнять та же независимая Fresh lane: она остаётся независимой от Primary, но заново выполняет complete Levels 1–4 и применимые current source checks.

Новое fresh-поколение само по себе не требуется только потому, что появился `Vn+1`. Новая top-level independent lane требуется, если текущая lane получила primary/change materials, потеряла доказуемую независимость либо valid fresh-owned review lineage недоступна.

Review в primary-беседе не может называться Fresh или Follow-up independent review.

#### Follow-up verdict

Положительный Follow-up status:

```text
FOLLOW-UP WEB PASS(Vn)
```

Он допустим только если:

* существует complete Initial Fresh baseline для этого path;
* все previous Fresh findings, относящиеся к current lineage, закрыты или доказанно больше не применимы;
* changed units и dependency cone получили применимые проверки;
* whole-note consistency scan дал `PASS`;
* нет блокирующих `NOT CHECKED`;
* current candidate остаётся независимым от Primary review lane.

Для incremental PASS не требуется повторять полный отчёт Levels 1–4. Достаточно зафиксировать:

```text
Path
Candidate version
Mode: INCREMENTAL
Reviewed changed units
Dependency cone
Inherited Fresh evidence
Source checks
Whole-note consistency
Open findings
FOLLOW-UP WEB PASS(Vn)
```

При `FAIL`, `NOT CHECKED` или `Mode: FULL` reviewer сообщает применимые детали достаточно полно, чтобы было ясно, какая проверка не пройдена.

#### Mechanical corrections

Pure mechanical correction, которая доказанно не меняет protected semantic content, не создаёт новую semantic version и может сохранить существующий `FRESH WEB PASS(Vn)` или `FOLLOW-UP WEB PASS(Vn)` после Web verification actual diff, verification contract и repository invariants.

Эта льгота не позволяет объявить ранее не проверенную заметку готовой: initial independent full review остаётся обязательным для новой, мигрируемой или явно взятой в полное ревью заметки.

### 8. Candidate status

Feature branch получает:

```text
CANDIDATE READY(Vn)
```

только если:

- `PRIMARY WEB PASS(Vn)` относится к current `Vn`, а independent gate закрыт либо `FRESH WEB PASS(Vn)`, либо `FOLLOW-UP WEB PASS(Vn)` с complete Initial Fresh lineage и закрытыми previous Fresh findings;
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

Используется [`new-note-workflow.md`](<./new-note-workflow.md>), затем тот же процесс `primary → execution → Web verification → Initial Fresh / применимый Follow-up → candidate status → publication`.

## Работа с несколькими заметками

Corpus review выполняется последовательно по заметкам. Для каждой заметки отдельно фиксируются path, `Vn`, primary status, fresh status и repository status.

Codex может применить batch из нескольких exact кандидатов только если Web перечислил для каждого path:

- candidate version;
- verification contract;
- allowed scope;
- допустимые generated/path changes;
- task-specific checks.

Batch не превращает заметки в один общий semantic verdict.

Одна fresh-сессия может проверить actual GitHub batch из нескольких заметок. Она самостоятельно читает каждую заметку и возвращает отдельный verdict для каждого path.

Если после Initial Fresh `FAIL` несколько заметок получили новые semantic versions, их можно накопить и передать одним Follow-up batch той же independent Fresh lane. Для каждого path отдельно определяются changed units, dependency cone, необходимость escalation в FULL и итоговый independent status.

## Статусы

Локальные:

```text
PASS / FAIL / NOT CHECKED по Levels 1–4
PRIMARY WEB PASS(Vn)
FRESH WEB PASS(Vn)
FOLLOW-UP WEB PASS(Vn)
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
