# Web Workers

<!-- NOTE-NAV-TOP:START -->
[← SSE](<./24 SSE.md>) · [↑ Основы веб-платформы](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Service Workers и PWA →](<./26 Service Workers и PWA.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Web Worker — браузерный API для выполнения JavaScript в отдельном контексте воркера, потенциально параллельно main thread. Он помогает сохранить отзывчивость интерфейса при тяжёлой вычислительной работе: разборе большого файла, обработке изображений, сжатии, локальном поиске или сложных расчётах.

Worker не имеет доступа к DOM. Main thread и worker обмениваются сообщениями через `postMessage`; значения обычно копируются алгоритмом структурированного клонирования (structured clone algorithm), а большие буферы можно передать как Transferable — с переносом владения вместо копирования содержимого.

Worker не ускоряет любую функцию автоматически. Создание контекста, загрузка скрипта, сериализация данных и координация имеют цену. Если проблема находится в сети, layout, обновлении DOM или слишком частом React render, перенос вычисления в worker не устраняет исходное ограничение.

## Что меняется в модели выполнения

```text
main thread
  - DOM, события, координация style/layout/paint
  - отправляет задачу и данные
             |
             | postMessage
             v
контекст worker
  - отдельные global scope и event loop
  - выполняет вычисление
             |
             | postMessage
             v
main thread применяет небольшой результат к UI
```

JavaScript страницы обычно выполняет одну задачу за раз на main thread. Долгое синхронное вычисление задерживает обработчики ввода и подготовку следующего frame. Worker создаёт отдельный agent с собственным event loop; браузер может выполнить его на другом потоке ОС и использовать несколько ядер CPU.

Параллельность не гарантирует неограниченные ресурсы. Браузер управляет планированием потоков, фоновыми вкладками и ограничениями устройства. Если создать десятки workers, они будут конкурировать за CPU и память, а UI может стать медленнее.

## Что доступно в worker

В worker нет `window`, `document` и DOM-узлов. Есть собственный `WorkerGlobalScope`, timers, `fetch`, WebSocket, IndexedDB, часть Cache API, Web Crypto и другие API, поддерживаемые конкретным контекстом worker.

DOM изменяет main thread. Worker вычисляет компактный результат: массив координат, разобранные записи, image bitmap, операции diff или результаты поиска. Если отправить обратно огромный объект и затем синхронно построить тысячи DOM-узлов, main thread всё равно получит long task.

`OffscreenCanvas` позволяет перенести часть рендеринга canvas в worker, если браузер и используемые API это поддерживают. Это отдельная возможность, а не общий доступ worker к DOM-элементу canvas.

## Dedicated и Shared Worker

| Вид | Владение и связь | Когда подходит |
| --- | --- | --- |
| `Worker` (Dedicated Worker) | связан с создавшим его document или worker | вычисление для одной страницы или функции приложения |
| `SharedWorker` | один worker может обслуживать несколько same-origin contexts через ports | общая координация нескольких вкладок при доступной поддержке браузеров |
| Service Worker | event-driven proxy для origin/scope, не принадлежит одной странице | перехват сети, offline и push; это отдельная модель |

Обычно начинают с Dedicated Worker: у него проще жизненный цикл и владение. Shared Worker нужен нечасто и имеет более сложную координацию ports и совместимость с браузерами.

## Classic и module worker

Современная сборка может создать module worker:

```ts
const worker = new Worker(
  new URL("./image.worker.ts", import.meta.url),
  { type: "module" },
);
```

`new URL(..., import.meta.url)` позволяет сборщику найти entry-файл worker и собрать отдельный chunk. Конкретный синтаксис зависит от настройки Vite, Webpack или Next.js; его проверяют в production-сборке, а не только на dev server.

Module worker использует ES modules и правила загрузки модулей. CSP `worker-src` и заголовки ответа со скриптом worker тоже должны разрешать загрузку и выполнение.

## Structured clone

`postMessage` не передаёт обычный объект по общей ссылке. Structured clone создаёт независимую копию поддерживаемого графа значений, включая многие `Array`, plain objects, `Map`, `Set`, `Date`, `ArrayBuffer` и typed arrays.

Не клонируются функции и DOM-узлы. Прототип пользовательского класса и дескрипторы свойств также не сохраняются как при обычной работе с исходным экземпляром. На границе сообщений лучше передавать явные data objects и проверять их схему.

Копирование большого графа объектов потребляет время и память в обоих контекстах. Worker может убрать вычисление с main thread, но дорогое клонирование при отправке и получении всё равно создаст заметные паузы.

## Transferable objects

Transferable переносит владение базовым ресурсом вместо копирования. Для `ArrayBuffer` после передачи исходный буфер становится detached и больше не содержит байтов:

```ts
const worker = new Worker(
  new URL("./decode.worker.js", import.meta.url),
  { type: "module" },
);

const buffer = await file.arrayBuffer();

worker.postMessage(
  { type: "decode", buffer },
  [buffer],
);

console.log(buffer.byteLength); // 0: владение передано worker
```

Объект должен находиться и в сообщении, и в transfer list. Не все значения являются transferable: например, передают `typedArray.buffer`, а не сам `Uint8Array`.

Передача владения подходит, если отправитель больше не использует ресурс. Если обеим сторонам одновременно нужны данные, обычное клонирование может быть правильнее несмотря на цену.

## Shared memory

`SharedArrayBuffer` позволяет нескольким agents обращаться к одной памяти. Это уже настоящая concurrency: операции могут пересекаться, поэтому для координации нужны `Atomics` и корректный protocol доступа.

Доступ в браузере обычно требует изолированного от других origins документа, настроенного через заголовки COOP/COEP. Такая изоляция влияет на popup-окна и сторонние ресурсы, поэтому её не включают только ради «ускорения» без проверки архитектуры.

Shared memory оправдана для специализированных high-performance задач, например WebAssembly или больших numeric workloads. Для обычной формы сообщений `postMessage` безопаснее и проще рассуждать.

## Гранулярность задачи

Worker полезен, когда блок вычисления достаточно крупный, чтобы выигрыш превысил стоимость коммуникации. Измеряют:

- длительность main-thread task;
- объём данных в обе стороны;
- частоту вызовов;
- время запуска worker и размер его кода;
- задержку до результата;
- CPU/memory на целевых devices.

Маленькие операции не отправляют по одной. Их объединяют в batch. Большую задачу также можно stream/partition, чтобы показывать progress и поддерживать cancellation.

Worker не всегда единственный вариант. Если calculation можно разбить на короткие chunks и результат нужен постепенно, cooperative scheduling на main thread может оказаться проще. Если bottleneck — layout thrashing, сначала уменьшают DOM reads/writes.

## Protocol, ошибки и отмена

Для нескольких параллельных задач сообщения связывают через request ID:

```ts
type WorkerRequest = {
  type: "parse";
  requestId: string;
  buffer: ArrayBuffer;
};

type WorkerResponse =
  | { type: "progress"; requestId: string; processed: number }
  | { type: "result"; requestId: string; rows: unknown[] }
  | { type: "error"; requestId: string; code: string; message: string };
```

Прикладное сообщение об отмене работает, только если worker периодически отдаёт управление event loop или сам проверяет состояние отмены между chunks. Один длинный синхронный цикл не обработает новое сообщение до завершения.

`worker.terminate()` немедленно останавливает Dedicated Worker, но не даёт ему завершить cleanup. Это крайний способ завершения принадлежащего странице worker. Для ошибок подписываются на `error` и `messageerror`, отклоняют ожидающие promises и не оставляют запрос навсегда в состоянии загрузки.

## Worker pool

Если задачи приходят часто, worker переиспользуют или создают небольшой pool вместо нового worker на каждую операцию. Размер пула связывают с характером задач и ограничениями устройства; `navigator.hardwareConcurrency` является только подсказкой о числе логических processors, а не готовым размером пула.

Вычислительно тяжёлые workers конкурируют с рендерингом браузера и другими вкладками за ядра CPU. Оставить main thread свободным логически недостаточно: загрузка всех ядер всё равно влияет на отзывчивость и расход батареи.

## Ключевые уточнения

- Worker переносит JavaScript calculation из main thread, но DOM остаётся на main thread.
- Structured clone копирует поддерживаемые данные; Transferable переносит владение ресурсом и отсоединяет его у отправителя.
- Worker улучшает responsiveness, а не обязательно уменьшает общее CPU time.
- Протокол сообщений нуждается в type, request ID, проверке данных, ошибках и семантике отмены.
- `SharedArrayBuffer` вводит shared-memory concurrency и обычно требует cross-origin isolation.
- Service Worker называется worker, но решает сетевые и offline-задачи и имеет другой жизненный цикл.

## Подходящие задачи

| Сценарий | Что отдавать worker |
| --- | --- |
| Импорт большого CSV/XLSX | parsing, normalization, предварительную validation |
| Image editor | decoding, filters, pixel transforms, thumbnails |
| Локальный поиск | построение index и scoring большого набора документов |
| Code editor | syntax parsing, linting, diff |
| Compression/crypto | CPU-heavy преобразование chunks |
| Карта/визуализация | геометрические расчёты и aggregation, но не обычный DOM |

## Связанные темы

- [Service Workers и PWA](<./26 Service Workers и PWA.md>)
- [Цикл событий (Event Loop)](<../JavaScript/35 Цикл событий (Event Loop).md>)
- [Главный поток, долгие задачи и отзывчивость](<../Устройство браузера/04 Главный поток, долгие задачи и отзывчивость.md>)
- [Оптимизация фронтенда](<../JavaScript/51 Оптимизация фронтенда.md>)
- [Core Web Vitals](<./21 Core Web Vitals.md>)
- [CSP и заголовки безопасности](<./16 CSP и заголовки безопасности.md>)

## Источники

- [MDN: Using Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)
- [MDN: Worker](https://developer.mozilla.org/en-US/docs/Web/API/Worker)
- [MDN: Structured clone algorithm](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm)
- [MDN: Transferable objects](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)
- [MDN: `crossOriginIsolated` in workers](https://developer.mozilla.org/en-US/docs/Web/API/WorkerGlobalScope/crossOriginIsolated)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← SSE](<./24 SSE.md>) · [↑ Основы веб-платформы](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Service Workers и PWA →](<./26 Service Workers и PWA.md>)
<!-- NOTE-NAV-BOTTOM:END -->
