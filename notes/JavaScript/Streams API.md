# Streams API

<!-- NOTE-NAV-TOP:START -->
[← requestAnimationFrame и requestIdleCallback](<./requestAnimationFrame и requestIdleCallback.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [postMessage и BroadcastChannel →](<./postMessage и BroadcastChannel.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Web Streams API обрабатывает данные порциями (`chunks`) по мере поступления, не дожидаясь полной загрузки в память. `ReadableStream` является источником, `WritableStream` - приёмником, а `TransformStream` принимает порции и выдаёт преобразованные.

Потребитель читает поток через reader, асинхронную итерацию или `pipeTo`. Пока reader захватил поток, другой reader получить его не может: поток заблокирован (`locked`). После чтения или ошибки блокировку освобождают, а ненужный источник отменяют.

Backpressure (обратное давление) сообщает производителю, что потребитель не успевает обрабатывать данные. Очередь потока и доступный размер позволяют замедлить производство вместо бесконтрольного накопления порций в памяти.

`fetch` предоставляет тело ответа как `ReadableStream`. Методы `json()` и `text()` полностью потребляют его; для постепенной обработки нужно читать порции и самостоятельно определять границы отдельных сообщений.

## Ключевая схема

```text
производитель
→ ReadableStream queue
→ TransformStream
→ WritableStream
→ потребитель

потребитель работает медленнее
→ backpressure
→ производитель создаёт данные реже
```

```js
await readable
  .pipeThrough(transform)
  .pipeTo(writable);
```

## Чтение `ReadableStream`

```js
const response = await fetch("/large-file");

if (!response.ok || !response.body) {
  throw new Error(`HTTP ${response.status}`);
}

const reader = response.body.getReader();

try {
  while (true) {
    const { value, done } = await reader.read();

    if (done) {
      break;
    }

    processChunk(value); // обычно Uint8Array
  }
} finally {
  reader.releaseLock();
}
```

`read()` возвращает Promise с объектом, похожим на результат итератора. `done: true` означает нормальное закрытие. Ошибка источника отклоняет Promise от `read()`.

`releaseLock()` освобождает reader, но не отменяет источник. Если данные больше не нужны, вызывают `reader.cancel(reason)` или отменяют `fetch` через `AbortSignal`.

После начала чтения тело `Response` считается использованным. Получить второй reader или вызвать `response.json()` для того же тела нельзя.

## Декодирование текста по порциям

Один символ UTF-8 может быть разделён между сетевыми порциями. Поэтому каждую порцию нельзя независимо декодировать без сохранения состояния декодера.

```js
const decoder = new TextDecoder();
let text = "";

while (true) {
  const { value, done } = await reader.read();
  if (done) break;

  text += decoder.decode(value, { stream: true });
}

text += decoder.decode();
```

Удобнее построить конвейер через `TextDecoderStream`, если его поддерживают целевые браузеры:

```js
const textStream = response.body.pipeThrough(
  new TextDecoderStream(),
);
```

Текстовый поток всё ещё не задаёт границы сообщений. Сетевые порции не обязаны совпадать со строками, JSON-объектами или прикладными записями.

## Границы сообщений

Один большой JSON-документ нельзя передать в `JSON.parse` до получения всего текста. Для постепенной обработки протокол должен задавать границы записей. Например, в NDJSON каждая строка содержит отдельный JSON-объект.

Парсер хранит незавершённый остаток между порциями:

```text
chunk 1: {"id":1}\n{"id"
chunk 2: :2}\n
```

Первая запись готова после первой порции, а вторая собирается из обеих. Простое разделение каждой порции по `\n` без сохранения остатка потеряет границу сообщения.

Альтернативы: бинарный протокол с длиной сообщения в заголовке, формат SSE, multipart или потоковый JSON-парсер. Формат выбирают вместе с backend.

## `TransformStream`

```js
const uppercase = new TransformStream({
  transform(chunk, controller) {
    controller.enqueue(chunk.toUpperCase());
  },
});
```

Transform получает порцию на записываемой стороне и добавляет результаты через `enqueue` на читаемую сторону. Он может хранить промежуточное состояние между порциями и обработать остаток в `flush()`.

Конвейер автоматически распространяет нормальное закрытие и обычно передаёт ошибки или отмену по цепочке:

```js
await source
  .pipeThrough(new TextDecoderStream())
  .pipeThrough(splitLines())
  .pipeTo(createRecordSink());
```

Пользовательское преобразование должно ограничивать внутренний буфер. Если разделитель никогда не приходит, накопление остатка может исчерпать память; протокол должен задавать максимальный размер записи.

## `WritableStream`

```js
const writable = new WritableStream({
  async write(chunk) {
    await persistChunk(chunk);
  },
  close() {
    finalize();
  },
  abort(reason) {
    rollbackTemporaryState(reason);
  },
});
```

Writer предоставляет `write`, `close`, `abort` и Promise `ready`, связанный с backpressure. `close` означает нормальное завершение, а `abort` - аварийное прекращение с очисткой ресурсов.

Как и reader, активный writer блокирует поток до `releaseLock()`.

## Backpressure

Без backpressure быстрый производитель создавал бы порции быстрее, чем потребитель их обрабатывает, и очередь росла бы до исчерпания памяти.

Контроллер `ReadableStream` использует `desiredSize`: положительное значение означает свободное место в очереди, а нулевое или отрицательное - производитель должен ждать следующего `pull`, а не продолжать бесконтрольный `enqueue`.

`pipeTo` передаёт обратное давление от потребителя к источнику. Но если пользовательский источник игнорирует `desiredSize` и бесконечно добавляет данные, API не сможет остановить внешнего производителя без корректной реализации паузы или отмены.

Backpressure регулирует поток данных, но не ускоряет медленного потребителя. Узкое место всё равно нужно измерять и оптимизировать.

## `tee()` и clone Response

`readable.tee()` создаёт две ветви. `Response.clone()` использует похожее разделение тела ответа.

Если одна ветвь читается медленно или вообще не читается, данные могут буферизоваться для неё. Поэтому клонирование большого ответа не является бесплатным и способно увеличить расход памяти.

Обычно тело читают один раз и передают разобранный прикладной результат нескольким потребителям. `tee()` применяют, когда действительно нужны независимые потоковые потребители с понятной скоростью.

## Отмена и ошибки

```js
const controller = new AbortController();

const response = await fetch(url, {
  signal: controller.signal,
});

controller.abort("screen closed");
```

`AbortSignal` отменяет `fetch` и может прервать чтение тела. `reader.cancel()` сообщает источнику, что потребителю больше не нужны данные, но не гарантирует откат серверной операции.

Ошибка в конвейере должна закрыть или отменить связанные ресурсы. `pipeTo` имеет настройки распространения закрытия и отмены, но менять их стоит только при ясном распределении ответственности.

## Поток или полная загрузка

| Сценарий | Выбор |
| --- | --- |
| Маленький JSON для UI | `response.json()` |
| Загрузка или обработка большого файла | поток |
| Постепенная обработка NDJSON или SSE | поток + парсер границ сообщений |
| Нужен произвольный доступ ко всему набору | полностью загрузить или индексировать |
| Тяжёлое преобразование | поток + Worker при необходимости |

Поток добавляет машину состояний, отдельные пути ошибок и отмены, а также работу с границами порций. Для ответа в несколько килобайт полное чтение обычно проще и безопаснее.

## Где применяется во frontend

- Постепенный рендеринг больших результатов по отдельным записям.
- Конвейер загрузки или отправки с отображением прогресса.
- Декодирование текста или порций бинарного протокола.
- Сжатие, распаковка и конвейеры преобразований.
- Service Worker передаёт поток ответа без полной буферизации.
- Worker обрабатывает тяжёлые порции, пока основной поток остаётся отзывчивым.

## Ключевые уточнения

- Поток обрабатывает порции, но они не равны прикладным сообщениям без протокола определения границ.
- Reader или writer блокирует поток; освобождение блокировки и отмена источника являются разными действиями.
- `json()`/`text()` полностью потребляют body и несовместимы с повторным чтением.
- Состояние `TextDecoder` нужно сохранять, если символ разделён между байтовыми порциями.
- Backpressure ограничивает рост очереди только при корректном участии производителя.
- `tee()` или `Response.clone()` может буферизовать данные медленной ветви.
- Поток оправдан для больших данных и постепенной обработки, но усложняет жизненный цикл по сравнению с полной загрузкой.

## Связанные темы

- [Fetch и работа с API](<./Fetch и работа с API.md>)
- [AbortController](<./AbortController.md>)
- [Итераторы и генераторы](<./Итераторы и генераторы.md>)
- [ArrayBuffer TypedArray DataView](<./ArrayBuffer TypedArray DataView.md>)
- [Web Workers](<../../Конспект для подготовки/Web Basics/Web Workers.md>)

## Источники

- [WHATWG Streams Standard](https://streams.spec.whatwg.org/)
- [WHATWG Fetch Standard: Bodies](https://fetch.spec.whatwg.org/#bodies)
- [MDN: Streams API](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API)
- [MDN: Using readable streams](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← requestAnimationFrame и requestIdleCallback](<./requestAnimationFrame и requestIdleCallback.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [postMessage и BroadcastChannel →](<./postMessage и BroadcastChannel.md>)
<!-- NOTE-NAV-BOTTOM:END -->
