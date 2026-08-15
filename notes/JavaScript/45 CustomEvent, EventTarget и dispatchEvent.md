# CustomEvent, EventTarget и dispatchEvent

<!-- NOTE-NAV-TOP:START -->
[← События DOM](<./44 События DOM.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Observer API →](<./46 Observer API.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`EventTarget` - интерфейс Web API для объектов, которые принимают обработчики и отправляют события через `addEventListener`, `removeEventListener` и `dispatchEvent`. Его реализуют `Window`, `Document`, DOM-элементы, `AbortSignal`, Worker и многие другие браузерные объекты.

`CustomEvent` создаёт пользовательское событие и передаёт данные в `event.detail`. По умолчанию такое событие не всплывает, не пересекает границу Shadow DOM и не отменяется; нужные свойства `bubbles`, `composed` и `cancelable` задают явно.

`dispatchEvent` выполняет обработчики синхронно в текущем стеке вызовов. Он не создаёт отдельную задачу и не делает событие настоящим пользовательским вводом: `event.isTrusted` для события, отправленного из JavaScript, остаётся `false`.

Пользовательские события полезны для связи Web Components и независимых виджетов. Внутри обычного приложения прямой callback, хранилище состояния или типизированный сервис часто дают более явный контракт.

## Ключевая схема

```js
const event = new CustomEvent("user:selected", {
  detail: { userId: "u1" },
  bubbles: true,
  composed: true,
  cancelable: true,
});

const accepted = element.dispatchEvent(event);
```

```text
создать событие
→ dispatchEvent(target)
→ синхронно пройти capture/target/bubble
→ обработчики читают event/detail
→ проверить отмену действия
→ dispatchEvent возвращает false, если отменяемое событие отменено
```

## `EventTarget`

Можно использовать отдельный `EventTarget` как локальный источник событий:

```js
const bus = new EventTarget();

function onSaved(event) {
  console.log(event.detail.id);
}

bus.addEventListener("document:saved", onSaved);
bus.dispatchEvent(new CustomEvent("document:saved", {
  detail: { id: "doc-1" },
}));
bus.removeEventListener("document:saved", onSaved);
```

Жизненный цикл обработчика совпадает с обычными DOM-событиями. Для удаления нужна та же ссылка на функцию и то же значение `capture`, либо общий `AbortSignal`:

```js
const controller = new AbortController();

bus.addEventListener("document:saved", onSaved, {
  signal: controller.signal,
});

controller.abort();
```

`EventTarget` не хранит историю событий. Подписчик, добавленный после отправки, не получит старое состояние. Если новый потребитель должен сразу прочитать текущее значение, нужно хранилище или наблюдаемое состояние, а не только event bus.

## `CustomEvent.detail`

```js
const event = new CustomEvent("cart:item-added", {
  detail: {
    productId: "p1",
    quantity: 2,
  },
});
```

`detail` передаётся по ссылке внутри одной среды JavaScript. `CustomEvent` не выполняет structured clone (структурное клонирование), поэтому обработчик может изменить переданный объект:

```js
event.detail.quantity = 10;
```

Если данные должны оставаться неизменяемыми, передают доступный только для чтения снимок по соглашению, создают защитную копию или проектируют API так, чтобы обработчик не получал изменяемый предметный объект.

Generic-параметр TypeScript для карты событий улучшает контракт во время компиляции, но код во время выполнения всё равно может отправить событие с неверным `detail`. Данные из недоверенного источника проверяют как `unknown`.

## Опции события

| Настройка | По умолчанию | Что меняет |
| --- | --- | --- |
| `bubbles` | `false` | поднимается ли событие по пути предков |
| `cancelable` | `false` | может ли `preventDefault()` отменить операцию |
| `composed` | `false` | может ли событие выйти из Shadow DOM |

```js
const event = new CustomEvent("dialog:before-close", {
  cancelable: true,
  detail: { reason: "escape" },
});

if (dialog.dispatchEvent(event)) {
  dialog.close();
}
```

Обработчик может вызвать `event.preventDefault()`. Для отменяемого события `dispatchEvent` тогда вернёт `false`, и владелец отменит собственную операцию.

Это протокол приложения, а не встроенное действие браузера по умолчанию: создатель события сам решает, что означает отмена и что делать с результатом.

## Синхронный dispatch

```js
console.log("before");
target.dispatchEvent(event);
console.log("after");
```

Все обработчики выполняются между `before` и `after`, если распространение не остановлено. Долгий обработчик блокирует вызывающий код и основной поток.

`dispatchEvent` не ожидает Promise, созданный обработчиком:

```js
target.addEventListener("save", async () => {
  await persist();
});

target.dispatchEvent(new Event("save"));
// dispatchEvent уже завершён, persist может быть pending.
```

Если вызывающий код должен дождаться асинхронного результата, отправка события не выражает такой контракт. Лучше вызвать `async`-функцию, собрать Promise явно или использовать командный API.

Исключение обработчика не становится обычным `throw` из `dispatchEvent` для вызывающего кода: браузер сообщает его как необработанную ошибку. Поэтому событие не подходит как скрытый синхронный вызов с ожидаемым результатом и ошибкой.

## `isTrusted`

Событие, созданное браузером из пользовательского ввода, в предусмотренных платформой случаях имеет `isTrusted === true`. Событие, отправленное через `dispatchEvent`, имеет `isTrusted === false`.

Это помогает отличить синтетическое событие, но не является границей авторизации. Действие, связанное с безопасностью, всё равно проверяется по правам и сессии на backend. Автоматизация браузера может создавать доверенные взаимодействия по правилам платформы.

Программная отправка `click` запускает обработчики и предусмотренное элементом поведение, но не превращается в физическое действие пользователя и не обходит требования user activation у API вроде буфера обмена или всплывающих окон.

## Web Components и Shadow DOM

Пользовательский элемент обычно отправляет наружу семантическое событие:

```js
this.dispatchEvent(new CustomEvent("value-change", {
  detail: { value: this.value },
  bubbles: true,
  composed: true,
}));
```

`bubbles` позволяет событию всплыть к предку, а `composed` - пересечь границу Shadow DOM. Наружу лучше отправлять предметное событие `value-change`, а не раскрывать внутренний клик конкретной кнопки.

Данные события должны быть минимальной и стабильной частью публичного API компонента. Внутренний DOM остаётся деталью реализации.

## Custom event или другой механизм

| Требование | Механизм |
| --- | --- |
| Дочерний Web Component сообщает предку | всплывающий `CustomEvent` |
| Вызывающий код ожидает результат или ошибку | функция или Promise |
| Много потребителей читают текущее состояние | хранилище или наблюдаемое состояние |
| Связь между вкладками | `BroadcastChannel` или событие `storage` |
| Связь с окном или iframe | `postMessage` с проверкой origin |
| Владелец передаёт callback дочернему коду | функция обратного вызова |

Глобальная шина событий со строковыми именами скрывает связи между модулями, допускает конфликты имён и усложняет трассировку. Если она нужна, имена событий, схемы данных, владельцев и очистку документируют как публичный контракт.

## Ключевые уточнения

- `EventTarget` отправляет события и управляет обработчиками, но не хранит текущее или прошлое состояние.
- `CustomEvent.detail` передаётся по ссылке и не клонируется автоматически.
- Пользовательское событие по умолчанию не всплывает, не отменяется и не пересекает Shadow DOM.
- `dispatchEvent` работает синхронно и не ждёт Promise из асинхронного обработчика.
- `false` от `dispatchEvent` означает вызов `preventDefault()` у отменяемого события, а не возвращаемое значение обработчика.
- Синтетическое событие имеет `isTrusted === false` и не заменяет реальную user activation или проверку безопасности.
- Если нужен асинхронный результат, явная функция или Promise понятнее протокола событий.

## Связанные темы

- [События DOM](<./44 События DOM.md>)
- [postMessage и BroadcastChannel](<./49 postMessage и BroadcastChannel.md>)
- [Observer, Pub-Sub и события](<../Паттерны/03 Observer, Pub-Sub и события.md>)
- [AbortController](<./40 AbortController.md>)

## Источники

- [WHATWG DOM Standard: EventTarget](https://dom.spec.whatwg.org/#interface-eventtarget)
- [WHATWG DOM Standard: CustomEvent](https://dom.spec.whatwg.org/#interface-customevent)
- [MDN: EventTarget.dispatchEvent](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/dispatchEvent)
- [MDN: CustomEvent](https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← События DOM](<./44 События DOM.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Observer API →](<./46 Observer API.md>)
<!-- NOTE-NAV-BOTTOM:END -->
