---
aliases:
  - rAF
  - requestAnimationFrame
  - requestIdleCallback
  - rIC
---

#### Быстрый ответ

`requestAnimationFrame` планирует одноразовый callback перед одной из следующих отрисовок страницы. Его используют для JavaScript-анимаций и объединения визуальных обновлений DOM по кадрам.

`requestIdleCallback` просит браузер выполнить низкоприоритетную работу в свободное время основного потока. Callback получает `IdleDeadline` и должен завершиться, пока `timeRemaining()` показывает оставшийся бюджет времени.

Эти API решают разные задачи: rAF привязан к сроку подготовки ближайшего кадра, а rIC использует свободное время между более важной работой. Ни один из них не ускоряет тяжёлое вычисление. Большую задачу нужно дробить с явной передачей управления браузеру или переносить в Web Worker.

`requestIdleCallback` поддерживается не всеми основными браузерами, поэтому перед использованием проверяют наличие API и предусматривают запасной вариант. Обязательная бизнес-логика не должна зависеть от появления свободного периода.

#### Ключевая схема

```text
задача → микрозадачи → возможность отрисовки
                    ├─ requestAnimationFrame callbacks
                    ├─ style / layout
                    └─ paint

свободное время основного потока
→ requestIdleCallback
→ короткая часть некритичной работы
```

Это учебная модель. Браузер сам решает, будет ли возможность отрисовки и сколько свободного времени доступно; rAF не гарантирует отдельный paint после каждого callback.

#### `requestAnimationFrame`

Вызов регистрирует callback и сразу возвращает числовой id. Callback вызывается один раз; для продолжения анимации следующий кадр нужно запросить снова.

```js
let frameId;
let startedAt;

function animate(timestamp) {
  startedAt ??= timestamp;

  const progress = Math.min((timestamp - startedAt) / 500, 1);
  box.style.transform = `translateX(${progress * 200}px)`;

  if (progress < 1) {
    frameId = requestAnimationFrame(animate);
  }
}

frameId = requestAnimationFrame(animate);

function stopAnimation() {
  cancelAnimationFrame(frameId);
}
```

Параметр `timestamp` использует время высокой точности и одинаков для всех rAF-callbacks одного кадра. Анимацию рассчитывают из прошедшего времени, а не прибавляют фиксированное расстояние при каждом вызове. Тогда скорость не зависит от частоты монитора и пропущенных кадров.

В фоновой вкладке и для невидимых iframe браузер обычно сильно ограничивает или приостанавливает rAF. Поэтому прошедшее время нужно определять по `timestamp`, а не по числу кадров.

#### Почему rAF подходит визуальным изменениям

Браузер группирует визуальную работу вокруг подготовки кадра. rAF даёт приложению точку для обновления состояния перед пересчётом стилей, layout и paint, что уменьшает количество лишних обновлений между кадрами.

События `pointermove` или `scroll` могут приходить чаще, чем обновляется экран. Вместо изменения DOM на каждое событие можно сохранить последнее значение и применить его один раз в rAF:

```js
let latestY = 0;
let framePending = false;

window.addEventListener("scroll", () => {
  latestY = window.scrollY;

  if (framePending) {
    return;
  }

  framePending = true;
  requestAnimationFrame(() => {
    framePending = false;
    progress.style.transform = `scaleX(${latestY / maxScroll})`;
  });
}, { passive: true });
```

Этот приём ограничивает записи в DOM одним callback на кадр. Он не уменьшает стоимость самой записи и не исправит тяжёлое синхронное вычисление внутри rAF.

Для простых переходов `transform` и `opacity` CSS transition или animation обычно лучше ручного JavaScript-цикла: браузер получает больше возможностей оптимизировать выполнение, а код проще поддерживать.

#### Частые принудительные пересчёты layout

Чтение геометрии после изменения стилей может заставить браузер синхронно пересчитать style и layout, чтобы вернуть актуальное значение.

```js
element.style.width = "200px";
const width = element.offsetWidth;
```

В цикле чередование записей в DOM и чтения геометрии создаёт принудительные синхронные пересчёты layout. Работу группируют: сначала читают нужные размеры, затем выполняют записи.

```js
const widths = items.map((item) => item.offsetWidth);

items.forEach((item, index) => {
  item.style.transform = `translateX(${widths[index]}px)`;
});
```

rAF сам по себе не гарантирует отсутствие повторных пересчётов. Важен порядок операций внутри callback и взаимодействие с другими callbacks того же кадра.

#### `requestIdleCallback`

`requestIdleCallback` планирует необязательную работу, которую можно отложить. Callback получает объект `IdleDeadline`:

- `timeRemaining()` оценивает оставшийся бюджет текущего свободного периода;
- `didTimeout` показывает, что callback вызван из-за указанного `timeout`, а не из-за свободного времени.

```js
let idleId;

function processQueue(deadline) {
  let processedAtLeastOne = false;

  while (
    queue.length > 0 &&
    (deadline.timeRemaining() > 1 || !processedAtLeastOne)
  ) {
    processItem(queue.shift());
    processedAtLeastOne = true;
  }

  if (queue.length > 0) {
    idleId = requestIdleCallback(processQueue, { timeout: 2000 });
  }
}

idleId = requestIdleCallback(processQueue, { timeout: 2000 });

function cancelBackgroundWork() {
  cancelIdleCallback(idleId);
}
```

Цикл обрабатывает небольшую порцию и повторно планирует остаток. Даже при истёкшем тайм-ауте выполняется только ограниченная часть, иначе «фоновая» работа сама создаст долгую задачу (`Long Task`).

Тайм-аут не означает, что появится свободный бюджет. Он просит браузер запустить callback после указанного максимального ожидания, даже если это ухудшит отзывчивость страницы. Поэтому объём работы всё равно ограничивают.

#### Ограничения rIC

Свободный период может долго не появляться на загруженной странице, а в фоновой вкладке поведение дополнительно ограничивается. `requestIdleCallback` не является Baseline API во всех основных браузерах, поэтому нужен запасной способ планирования.

Запасной вариант не обязан имитировать `IdleDeadline`. Для простой очереди можно планировать короткие порции через `setTimeout`, передавая рабочей функции собственный бюджет:

```js
function scheduleChunk(task) {
  if ("requestIdleCallback" in window) {
    return {
      kind: "idle",
      id: requestIdleCallback(task, { timeout: 2000 }),
    };
  }

  return {
    kind: "timer",
    id: setTimeout(() => {
      task({
        didTimeout: true,
        timeRemaining: () => 0,
      });
    }, 0),
  };
}
```

Такой объект только унифицирует форму callback. `setTimeout` не знает реального свободного бюджета и не становится эквивалентом rIC.

#### `scheduler.postTask`

`scheduler.postTask()` позволяет поставить задачу с приоритетом `user-blocking`, `user-visible` или `background` и возвращает Promise. Это более явная модель приоритетов, но API также поддерживается не всеми браузерами.

```js
if (globalThis.scheduler?.postTask) {
  await scheduler.postTask(updateIndex, {
    priority: "background",
  });
} else {
  setTimeout(updateIndex, 0);
}
```

Приоритет `background` не делает большой callback прерываемым. Если `updateIndex` занимает сотни миллисекунд, работу всё равно нужно разделить на части или выполнить в Worker.

#### Что выбрать

| Задача | Механизм | Граница |
| --- | --- | --- |
| Обновление DOM перед кадром | `requestAnimationFrame` | callback должен быть коротким |
| CSS transition/animation | CSS | подходит не любой вычисляемой анимации |
| Некритичная отложенная работа | `requestIdleCallback` | ограниченная поддержка, запуск может задержаться |
| Задача с явным приоритетом | `scheduler.postTask` | ограниченная поддержка, callback не прерывается автоматически |
| Разделить работу и уступить event loop | короткие порции в отдельных задачах | нужно вручную хранить прогресс |
| Тяжёлое вычисление вне основного потока | Web Worker | данные передаются сообщениями |
| Продолжение Promise | микрозадача | браузер не сможет отрисовать кадр между бесконечными шагами |

#### Ключевые уточнения

- rAF вызывается перед возможной отрисовкой, но не гарантирует отдельный paint для каждого callback.
- rAF одноразовый; продолжение и отмена управляются явно.
- Анимацию рассчитывают по `timestamp`, чтобы она не зависела от частоты обновления экрана.
- rAF синхронизирует момент визуальной работы, но не уменьшает стоимость тяжёлого кода.
- rIC предназначен для некритичной работы и должен учитывать `timeRemaining()`.
- Тайм-аут rIC может запустить callback без свободного бюджета, поэтому объём работы всё равно ограничивают.
- rIC и `scheduler.postTask` требуют проверки поддержки; запасной механизм имеет другую семантику.
- Микрозадача не уступает управление рендерингу: длинная цепочка микрозадач способна задержать кадр.

#### Связанные темы

- [[Конспект для подготовки/JavaScript/Event Loop]]
- [[Конспект для подготовки/JavaScript/Debounce и throttle]]
- [[Конспект для подготовки/JavaScript/Оптимизация фронтенда]]
- [[Конспект для подготовки/Web Basics/Critical Render Path]]
- [[Конспект для подготовки/Web Basics/Web Workers]]

#### Источники

- [WHATWG HTML Standard: Animation frames](https://html.spec.whatwg.org/multipage/imagebitmap-and-animations.html#animation-frames)
- [MDN: requestAnimationFrame](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)
- [MDN: requestIdleCallback](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback)
- [MDN: Scheduler.postTask](https://developer.mozilla.org/en-US/docs/Web/API/Scheduler/postTask)
