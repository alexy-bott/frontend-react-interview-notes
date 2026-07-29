# Event delegation capture bubble

<!-- NOTE-NAV-TOP:START -->
[← Main thread long tasks и responsiveness](<./Main thread long tasks и responsiveness.md>) · [↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Memory leaks и profiling →](<./Memory leaks и profiling.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

При отправке (dispatch) DOM-событие проходит по пути распространения (event path). Сначала фаза перехвата (capture) идёт от верхних узлов к целевому элементу, затем выполняются его обработчики, после чего всплывающее событие (bubbling event) поднимается к предкам. `event.target` указывает исходную цель, а `event.currentTarget` — объект, обработчик которого выполняется сейчас.

Event delegation, или делегирование событий, использует всплытие: один listener на контейнере обрабатывает события его потомков и через `closest()` определяет смысловой элемент. Это уменьшает количество listeners и автоматически работает для динамически добавленных элементов.

Делегирование подходит не каждому событию и требует проверки границы контейнера. `stopPropagation()` не отменяет действие браузера, `preventDefault()` не останавливает распространение, а passive listener сообщает браузеру, что не будет отменять прокрутку или другое действие по умолчанию.

## Что происходит при клике

Упрощённый путь взаимодействия указателем:

1. Основной процесс браузера получает ввод от операционной системы и направляет его нужному процессу рендеринга.
2. Браузер выполняет hit testing — определяет элемент под координатами указателя.
3. Для DOM-события строится путь через предков целевого элемента.
4. Выполняются listeners фазы capture.
5. Выполняются listeners на целевом элементе.
6. Для всплывающего события выполняются listeners предков снизу вверх.
7. Если действие по умолчанию не отменено, браузер может, например, перейти по ссылке или переключить checkbox. Точный момент действия зависит от конкретного события; модель «после всплытия» является упрощением.
8. Изменения DOM или состояния могут привести к подготовке нового кадра после завершения текущей задачи.

Конкретный набор pointer-, mouse- и click-событий зависит от устройства и действия. Один пользовательский жест способен породить несколько DOM-событий.

## Фазы распространения

```text
Window
  ↓ capture
Document
  ↓
container
  ↓
target
  ↑ bubble
container
  ↑
Document
  ↑
Window
```

Listener фазы перехвата включается через `{ capture: true }`:

```js
container.addEventListener("click", handleCapture, {
  capture: true,
});

container.addEventListener("click", handleBubble);
```

На целевом элементе capture-listeners выполняются перед обычными listeners. `event.eventPhase` позволяет узнать текущую фазу, но прикладному коду обычно достаточно `target` и `currentTarget`.

## `target` и `currentTarget`

```html
<button data-action="save">
  <span>Сохранить</span>
</button>
```

При клике по `<span>`:

- `event.target` — вложенный элемент, по которому пришёлся клик;
- `event.currentTarget` — контейнер, чей listener сейчас выполняется.

Вне выполняющегося listener значение `currentTarget` равно `null`, поэтому его не следует читать позже из сохранённого объекта события. Нужное значение сохраняют сразу.

## Делегирование событий

```js
list.addEventListener("click", event => {
  if (!(event.target instanceof Element)) {
    return;
  }

  const button = event.target.closest("[data-action]");

  if (!button || !list.contains(button)) {
    return;
  }

  const item = button.closest("[data-item-id]");

  if (!item || !list.contains(item)) {
    return;
  }

  if (button.dataset.action === "remove") {
    removeItem(item.dataset.itemId);
  }
});
```

`closest()` нужен, потому что `target` может быть иконкой или текстовой обёрткой внутри кнопки. `contains()` проверяет, что найденный элемент принадлежит нужному контейнеру: `closest()` способен найти подходящего внешнего предка.

Делегирование особенно полезно для таблиц, меню, деревьев и больших списков. Для нескольких постоянных элементов отдельные обработчики могут быть проще; сокращение количества listeners не является самоцелью.

## Какие события не делегируются обычным способом

Не все события всплывают:

- `focus` и `blur` не всплывают; для делегирования используют всплывающие события `focusin` и `focusout` либо фазу capture;
- `mouseenter` и `mouseleave` не всплывают; иногда подходят `mouseover` и `mouseout`, но у них другая семантика при переходе между потомками;
- `load` для отдельных ресурсов и некоторые события медиаэлементов имеют собственные правила.

Перед делегированием проверяют свойство `bubbles` конкретного типа события, а не запоминают один список навсегда.

## Распространение и действие по умолчанию

| API | Результат |
| --- | --- |
| `preventDefault()` | отменяет действие по умолчанию, если событие допускает отмену |
| `stopPropagation()` | останавливает путь к следующим узлам |
| `stopImmediatePropagation()` | также блокирует следующие listeners на текущем узле |

```js
link.addEventListener("click", event => {
  event.preventDefault();
  openInApplication(link.href);
});
```

`preventDefault()` имеет эффект только для отменяемого события. Проверить это можно через `event.cancelable`.

Остановка распространения внутри переиспользуемого компонента может незаметно сломать обработку клика снаружи, аналитику, управление фокусом и горячие клавиши выше по дереву. Сначала лучше проверить источник события и условия обработки.

## Passive listeners

```js
window.addEventListener("touchmove", updateMetrics, {
  passive: true,
});
```

`passive: true` сообщает браузеру, что listener не отменит прокрутку через `preventDefault()`. В подходящих сценариях браузер может начать прокрутку, не ожидая завершения JavaScript.

Passive listener не делает обработчик быстрым: тяжёлая функция всё равно занимает основной поток. Вызов `preventDefault()` внутри него не отменит действие и обычно вызовет предупреждение в консоли. Если действие по умолчанию нужно отменить, listener не должен быть passive.

Для управляемого cleanup удобно передать `AbortSignal`:

```js
const controller = new AbortController();

window.addEventListener("resize", handleResize, {
  signal: controller.signal,
});

controller.abort();
```

Вызов `abort()` удалит listeners, которым передан этот `signal`. Это удобно, когда жизненный цикл нескольких обработчиков заканчивается одновременно.

## Shadow DOM

Shadow DOM создаёт границу инкапсуляции. Событие должно иметь `composed: true`, чтобы выйти за пределы shadow tree. При выходе `target` может быть заменён на host-элемент, чтобы не раскрывать внешнему коду внутреннее устройство компонента. Это поведение называют retargeting.

`event.composedPath()` возвращает путь события с учётом Shadow DOM в пределах доступной вызывающему коду информации. Для Web Components это надёжнее предположения, что обычная цепочка `parentNode` совпадает с путём события.

## React и нативные DOM events

React предоставляет обёртку `SyntheticEvent` и использует делегирование внутри своей системы событий. Начиная с React 17 основные listeners привязаны к React root, а не к `document`. Смешивание React-обработчиков и ручных нативных listeners требует проверки порядка выполнения и границ root.

События React-компонента внутри Portal всплывают по дереву React, хотя DOM-узел Portal находится в другой части документа. Это важное отличие от нативного DOM-пути.

`event.nativeEvent` даёт исходное браузерное событие, однако использовать его следует только когда возможностей `SyntheticEvent` недостаточно.

## Ключевые уточнения

- Путь события описывает распространение по дереву, `target` сохраняет исходную цель, а `currentTarget` меняется вместе с выполняемым listener.
- Делегирование опирается на распространение события; для невсплывающих событий выбирают всплывающий аналог или фазу capture.
- `preventDefault()` управляет действием браузера, а `stopPropagation()` — дальнейшим распространением события.
- Passive listener позволяет браузеру раньше начать действие вроде прокрутки, но тяжёлый обработчик всё равно занимает основной поток.
- Shadow DOM может скрыть внутренний `target`, а событие React Portal всплывает по дереву React; для этих случаев проверяют соответственно `composedPath()` и границы React root.

## Связанные темы

- [Архитектура браузера процессы и потоки](<./Архитектура браузера процессы и потоки.md>)
- [Main thread long tasks и responsiveness](<./Main thread long tasks и responsiveness.md>)
- [DOM events](<../JavaScript/DOM events.md>)
- [Portal](<../React/Portal.md>)
- [Radix UI](<../React/Radix UI.md>)

## Источники

- [DOM Standard: Events](https://dom.spec.whatwg.org/#events)
- [MDN: Event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)
- [MDN: EventTarget.addEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)
- [Chrome for Developers: Inside look at a modern web browser, part 4](https://developer.chrome.com/blog/inside-browser-part4)
- [React: Responding to Events](https://react.dev/learn/responding-to-events)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Main thread long tasks и responsiveness](<./Main thread long tasks и responsiveness.md>) · [↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Memory leaks и profiling →](<./Memory leaks и profiling.md>)
<!-- NOTE-NAV-BOTTOM:END -->
