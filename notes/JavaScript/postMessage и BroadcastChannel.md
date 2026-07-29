# postMessage и BroadcastChannel

<!-- NOTE-NAV-TOP:START -->
[← Streams API](<./Streams API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Garbage collection →](<./Garbage collection.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`postMessage` передаёт данные между контекстами JavaScript без общей ссылки на объект. Окно, iframe, Worker и `MessagePort` используют похожую модель сообщений, но имеют разные границы безопасности и сигнатуры методов.

Данные проходят structured clone (структурное клонирование): поддерживаемые значения копируются, а transferable-ресурсы, например `ArrayBuffer` и `MessagePort`, можно передать с переносом владения.

Для `window.postMessage` отправитель указывает точный `targetOrigin`, а получатель проверяет `event.origin`, при необходимости `event.source` и структуру `event.data` во время выполнения. Само получение сообщения не делает его данные доверенными.

`BroadcastChannel` рассылает сообщения между объектами канала одного origin в совместимой storage partition, например для выхода из аккаунта или синхронизации вкладок. Он не хранит историю, не гарантирует доставку закрытой или спящей вкладке и закрывается через `channel.close()`.

## Ключевая схема

```text
значение отправителя
→ structured clone / transfer
→ очередь сообщений браузера
→ событие message у получателя
→ проверка source/origin/структуры
→ выполнение прикладного действия
```

| Механизм | Связь |
| --- | --- |
| `window.postMessage` | Window ↔ iframe, opener или другая ссылка на Window |
| `Worker.postMessage` | основной контекст ↔ dedicated/shared Worker |
| `MessageChannel` | два связанных `MessagePort` |
| `BroadcastChannel` | контексты одного origin и storage partition с одинаковым именем канала |

## `window.postMessage`

Родительское окно отправляет сообщение в iframe:

```js
iframe.contentWindow.postMessage(
  { type: "theme:set", theme: "dark" },
  "https://widget.example",
);
```

Iframe проверяет сообщение:

```js
window.addEventListener("message", (event) => {
  if (event.origin !== "https://app.example") {
    return;
  }

  if (event.source !== window.parent) {
    return;
  }

  const message = parseParentMessage(event.data);

  if (message.type === "theme:set") {
    setTheme(message.theme);
  }
});
```

`targetOrigin` ограничивает, при каком текущем origin целевое окно может получить сообщение. Строка `"*"` разрешает любой origin и не подходит для секретов или команд с полномочиями, если точный origin известен.

Получатель не должен доверять одному полю `type`. Данные может отправить любой скрипт с доступной ссылкой на окно; поэтому проверяются origin, source и структура данных.

Origin включает протокол, хост и порт. Путь в `event.origin` не входит.

## Смена адреса целевого окна

Ссылка на `Window` может остаться той же после перехода окна на другой origin. Точный `targetOrigin` не даст случайно отправить секрет странице, которая теперь открыта в этом окне.

```js
popup.postMessage(message, expectedOrigin);
```

Для долгоживущего протокола канала часто выполняют handshake (начальное согласование) и проверяют идентификатор сессии или канала, но он не заменяет браузерную проверку origin.

## Structured clone

Сообщение не передаёт общую ссылку между изолированными контекстами. Structured clone поддерживает циклические ссылки и многие встроенные типы, но не функции, DOM-узлы и произвольную семантику прототипов классов.

```js
worker.postMessage({
  date: new Date(),
  map: new Map([["key", 1]]),
});
```

Получатель получает независимый граф данных. Изменение исходного объекта после `postMessage` не меняет уже отправленное сообщение.

Валидация всё равно нужна: structured clone проверяет возможность клонирования, а не соответствие прикладному контракту.

## Transferable objects

```js
const buffer = new ArrayBuffer(1024 * 1024);

worker.postMessage({ buffer }, [buffer]);
console.log(buffer.byteLength); // 0, buffer detached
```

Перенос позволяет не копировать большой ресурс, но отправитель теряет к нему доступ. Это передача владения, а не общая память.

`MessagePort` также можно перенести, чтобы передать конечную точку другому контексту. Передаваемый объект после успешного переноса нельзя продолжать использовать как прежде.

Для настоящей общей памяти нужен `SharedArrayBuffer`, синхронизация через `Atomics` и выполнение дополнительных требований безопасности.

## Worker messages

```js
const worker = new Worker("./worker.js", { type: "module" });

worker.postMessage({ type: "calculate", input });

worker.addEventListener("message", (event) => {
  const result = parseWorkerResult(event.data);
  renderResult(result);
});
```

Объект dedicated Worker уже является конкретной конечной точкой, поэтому `targetOrigin`, как у `Window`, здесь нет. Но схема данных, идентификатор запроса, формат ошибок и жизненный цикл по-прежнему нужны.

Если несколько запросов идут одновременно, сообщение включает correlation id - идентификатор, связывающий запрос с ответом:

```js
{ type: "result", requestId: "r42", value: 10 }
```

Без идентификатора поздний результат может обновить не тот сценарий интерфейса.

## `MessageChannel`

```js
const channel = new MessageChannel();

channel.port1.addEventListener("message", handleMessage);
channel.port1.start();

worker.postMessage(
  { type: "connect", port: channel.port2 },
  [channel.port2],
);
```

`MessageChannel` создаёт два связанных порта. Это удобно для отдельного двустороннего протокола без глобального обработчика `message` на `window`.

Порты закрывают через `port.close()` и снимают обработчики. Переданный порт является полномочием на связь по каналу, поэтому его не передают недоверенному коду без необходимости.

## `BroadcastChannel`

```js
const authChannel = new BroadcastChannel("auth");

authChannel.postMessage({ type: "logout" });

authChannel.addEventListener("message", (event) => {
  const message = parseAuthMessage(event.data);

  if (message.type === "logout") {
    clearLocalSession();
  }
});
```

Другие объекты `BroadcastChannel` того же origin, storage partition и с тем же именем канала получают сообщение. Отправивший объект не получает собственное сообщение, но другой экземпляр канала в том же контексте может его получить.

Канал не хранит сообщения: вкладка, открытая позже, не увидит прошлое событие выхода. При старте она должна проверить фактическое состояние сессии, а `BroadcastChannel` только ускоряет синхронизацию открытых контекстов.

Доставка сообщения не заменяет отзыв токена или сессии на backend. Вкладка должна корректно обработать следующий `401`, даже если сообщение было пропущено.

## BroadcastChannel или storage event

Изменение `localStorage` вызывает событие `storage` в других документах того же origin, но не в документе, который сделал запись. Это старый способ передать сигнал между вкладками, одновременно сохранив пару ключ-значение.

`BroadcastChannel` передаёт сообщение напрямую и поддерживает structured-clone данные. `localStorage` полезен, если одновременно нужно сохранить небольшое состояние, но синхронное хранилище не используют как высокочастотную шину.

Service Worker может координировать подконтрольные страницы и фоновые события, но имеет отдельный жизненный цикл и решает более широкую задачу, чем канал между вкладками.

## Protocol design

```ts
type Message =
  | { type: "theme:set"; theme: "light" | "dark" }
  | { type: "logout" }
  | { type: "search:result"; requestId: string; items: Item[] };
```

Устойчивый протокол содержит:

- версию или обратно совместимое развитие формата;
- discriminant `type`;
- проверку данных во время выполнения;
- correlation id для request/response;
- явное сообщение об ошибке;
- ограничения размера и частоты сообщений;
- правила закрытия и отмены.

Объединение типов TypeScript помогает внутри одной сборки, но другой iframe, вкладка или старый Service Worker может отправить несовместимые данные во время выполнения.

## Где применяется во frontend

- Родительская страница и встроенный виджет обмениваются командами с точной проверкой origin.
- Worker получает вычислительную задачу и возвращает результат по идентификатору запроса.
- `MessageChannel` выдаёт плагину отдельный порт связи.
- `BroadcastChannel` синхронизирует выход из аккаунта или тему между открытыми вкладками.
- `ArrayBuffer` передаётся Worker через transfer list без большой копии.

## Ключевые уточнения

- Сообщение передаёт клонированные данные, а не общую ссылку на объект.
- `window.postMessage` требует точный `targetOrigin`; получатель проверяет origin, source и схему данных.
- `"*"` не подходит чувствительным данным, если target origin можно указать.
- Передаваемый ресурс меняет владельца и отсоединяется на стороне отправителя.
- Сообщения Worker не имеют `targetOrigin`, но всё равно требуют протокола, формата ошибок и связи запросов с ответами.
- `BroadcastChannel` работает для живых контекстов одного origin и совместимой storage partition, но не хранит историю.
- Уведомление между вкладками не заменяет фактическое состояние сессии на backend.

## Связанные темы

- [Web Workers](<../Web Basics/Web Workers.md>)
- [ArrayBuffer TypedArray DataView](<./ArrayBuffer TypedArray DataView.md>)
- [Копирование объектов](<./Копирование объектов.md>)
- [CORS CSP и browser security boundaries](<../Security/CORS CSP и browser security boundaries.md>)
- [Observer PubSub и события](<../Patterns/Observer PubSub и события.md>)

## Источники

- [WHATWG HTML Standard: Cross-document messaging](https://html.spec.whatwg.org/multipage/web-messaging.html#web-messaging)
- [WHATWG HTML Standard: BroadcastChannel](https://html.spec.whatwg.org/multipage/web-messaging.html#broadcasting-to-other-browsing-contexts)
- [MDN: Window.postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [MDN: BroadcastChannel](https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Streams API](<./Streams API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Garbage collection →](<./Garbage collection.md>)
<!-- NOTE-NAV-BOTTOM:END -->
