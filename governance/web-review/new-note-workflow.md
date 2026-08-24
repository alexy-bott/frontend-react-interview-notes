# Web-led маршрут создания новой заметки

Этот маршрут применяется до канонического процесса [`00-workflow.md`](<./00-workflow.md>).

## 1. Поиск тематического пробела

ChatGPT Web читает:

- root `README.md`;
- секционный `README.md`;
- соседние и связанные заметки;
- существующие названия и границы тем.

Web проверяет:

- нет ли уже отдельной заметки с тем же ядром;
- не является ли тема частью существующей страницы;
- какой раздел и место в маршруте подходят;
- какой объём принадлежит новой заметке, а какой — соседним темам.

Codex не выбирает тему, раздел или место самостоятельно.

## 2. Исследование

Web исследует материал по актуальным первичным источникам и фиксирует:

- технические факты;
- контекст версии;
- ограничения и исключения;
- practically important trade-offs;
- источники, реально использованные в итоговой заметке.

Непроверенный изменяемый факт не превращается в уверенное утверждение.

## 3. Смысловой план

Web проектирует:

- H1 и имя темы без числового префикса;
- `Быстрый ответ`;
- `Карту темы`;
- тематическое раскрытие;
- применимость `Мини-задачи`;
- `Где применяется во frontend`;
- `Ключевые уточнения`;
- связанные темы;
- источники;
- точное место ссылки в секционном README.

## 4. Candidate

Web создаёт exact Web-authored содержание заметки по Levels 1–4. Generated navigation может быть оставлена штатному механизму репозитория, но Web фиксирует verification contract: exact protected content, generated regions, planned final path и разрешённые path/link-destination rewrites.

Exact Web-authored candidate получает `PRIMARY WEB PASS(Vn)` до передачи Codex. После push Web подтверждает actual feature branch по verification contract, а отдельная fresh-сессия проверяет exact actual `Vn` непосредственно из GitHub. Если Codex должен создать bounded code, до исполнения утверждаются проза и code contract, а actual resulting `Vn` после push сначала проходит применимый primary review и затем fresh review.

## 5. Execution

Codex получает:

- exact analysis-base;
- section и точное место в маршруте;
- exact Web-authored note content;
- allowed paths;
- разрешение `EXACT_NOTE_CANDIDATE` + `REPOSITORY_MAINTENANCE`;
- full-file hash либо protected-content manifest;
- exact planned path map и разрешённые переписывания назначений ссылок;
- protected соседние заметки, подписи ссылок, проза и код;
- команды checks.

Codex:

1. создаёт заметку и изменяет ручную часть секционного README;
2. запускает `python scripts/renumber_notes.py --write`;
3. запускает `python scripts/generate_navigation.py`;
4. проверяет, что actual diff соответствует protected-content manifest, generated regions и approved path map;
5. подтверждает, что вне generated regions изменены только разрешённые назначения ссылок, а их подписи, проза, код и semantic targets сохранены;
6. запускает tests/checks;
7. публикует feature branch только по инструкции.

Codex не добавляет новые тематические разделы и не расширяет содержание.

## 6. Web verification

Web читает actual GitHub diff и проверяет:

- путь и итоговый номер;
- точное положение в секционном маршруте;
- Web-authored содержание по full-file hash либо protected-content manifest;
- generated navigation;
- соответствие всех переименований exact planned path map;
- переписанные назначения внутренних ссылок без изменений подписей, окружающей прозы, кода и semantic targets;
- отсутствие посторонних переименований;
- CI/repository checks.

После Web verification exact actual `Vn` передаётся отдельной fresh-сессии по candidate commit SHA и итоговому repository path. Только после `FRESH WEB PASS(Vn)` и выполнения остальных gates применяется `CANDIDATE READY → publication → READY` из `00-workflow.md`.
