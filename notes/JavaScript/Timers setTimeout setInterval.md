# Timers setTimeout setInterval

<!-- NOTE-NAV-TOP:START -->
[← Event Loop](<./Event Loop.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Promise →](<./Promise.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`setTimeout` и `setInterval` - браузерные Web API для планирования задач таймера. `setTimeout` планирует один вызов не раньше указанной задержки, а `setInterval` повторяет вызов приблизительно с заданным интервалом.

Задержка не является точным временем выполнения. Когда таймер созрел, браузер делает его задачу доступной для event loop. Callback начнёт выполняться только после освобождения основного потока и завершения более ранней работы.

`setTimeout(fn, 0)` поэтому не вызывает `fn` немедленно и не создаёт микрозадачу. Он переносит callback как минимум в будущую задачу, которая сможет выполниться после текущего кода и накопившихся микрозадач.

Для polling (периодических запросов) часто лучше рекурсивный `setTimeout`: следующий запуск планируется после завершения предыдущей асинхронной операции. `setInterval` не ждёт Promise из `async`-callback и может начать следующий запрос до окончания предыдущего.

## Ключевая схема

```text
setTimeout(callback, delay)
→ браузер ждёт не меньше delay
→ задача таймера становится готова
→ event loop сможет выбрать её для выполнения
→ callback ждёт свободный основной поток
→ выполняется с новым стеком вызовов
```

```js
setTimeout(() => console.log("timer"), 0);
Promise.resolve().then(() => console.log("microtask"));
console.log("sync");

// sync
// microtask
// timer
```

## `setTimeout`

```js
const timeoutId = setTimeout(() => {
  showNotification();
}, 1000);

clearTimeout(timeoutId);
```

Вызов возвращает идентификатор, по которому ожидающий таймер можно отменить. После выполнения одноразовый таймер больше не планирует callback.

Дополнительные аргументы можно передать после задержки, но функция-обёртка обычно читается понятнее и позволяет вызвать метод через нужный объект:

```js
setTimeout(showMessage, 1000, "Saved");
setTimeout(() => userSession.refresh(), 1000);
```

Передача `userSession.refresh` без обёртки отделяет метод от объекта, поэтому он потеряет прежний `this`.

## Минимальная, а не точная задержка

```js
const startedAt = performance.now();

setTimeout(() => {
  console.log(performance.now() - startedAt);
}, 50);

const end = performance.now() + 100;
while (performance.now() < end) {
  // main thread занят
}
```

Callback выполнится только после цикла, то есть примерно через `100 ms` или позже. Значение `50` означает «не запускать callback раньше», а не «запустить ровно через 50 ms».

После нескольких вложенных таймеров HTML Standard увеличивает слишком маленькую задержку как минимум примерно до `4 ms`. Браузер может ограничивать таймеры ещё сильнее в фоновой вкладке, на неактивной странице или в энергосберегающем режиме.

Таймеры не являются механизмом реального времени и не подходят для точного измерения длительности.

## `setInterval`

```js
const intervalId = setInterval(() => {
  updateClock();
}, 1000);

clearInterval(intervalId);
```

`setInterval` удобен для короткой независимой повторяемой работы. Если основной поток занят, callback задержится. Пропущенное время автоматически не компенсируется, а фактические промежутки зависят от нагрузки и ограничений браузера.

Асинхронный callback создаёт отдельную проблему:

```js
setInterval(async () => {
  await loadStatus();
}, 1000);
```

Timer API не ожидает возвращённый Promise. Через следующую секунду может начаться новый `loadStatus`, хотя предыдущий Promise всё ещё находится в состоянии `pending`. JavaScript-части callbacks не выполняются одновременно в одном потоке, но сетевые операции могут перекрываться во времени.

## Рекурсивный `setTimeout`

Polling обычно должен дождаться ответа, вычислить новую задержку (`backoff`) и только затем запланировать следующий запуск:

```js
function startPolling({ signal, delay = 1000 }) {
  let timeoutId;

  async function poll() {
    try {
      await loadStatus({ signal });
    } catch (error) {
      if (!signal.aborted) {
        reportError(error);
      }
    } finally {
      if (!signal.aborted) {
        timeoutId = setTimeout(poll, delay);
      }
    }
  }

  poll();

  signal.addEventListener("abort", () => {
    clearTimeout(timeoutId);
  }, { once: true });
}
```

Следующий таймер создаётся после завершения текущей операции, поэтому один планировщик не запускает перекрывающиеся запросы. Сигнал нужно передать и в реальный `fetch`, иначе отменится только следующий запуск, но не текущий запрос.

В production polling дополнительно учитывает экспоненциальное увеличение задержки (`exponential backoff`), случайный разброс (`jitter`), отсутствие сети, заголовок `Retry-After`, видимость страницы и максимальное число ошибок.

## Накопление погрешности таймера

Timer drift - расхождение между ожидаемым и фактическим временем запусков. Если обратный отсчёт просто уменьшает число при каждом срабатывании `setInterval`, задержки постепенно накапливают ошибку:

```js
let seconds = 60;
setInterval(() => {
  seconds -= 1;
}, 1000);
```

Надёжнее хранить конечный момент времени (`deadline`) и заново вычислять остаток:

```js
const deadline = Date.now() + 60_000;

const intervalId = setInterval(() => {
  const remaining = Math.max(0, deadline - Date.now());
  renderCountdown(Math.ceil(remaining / 1000));

  if (remaining === 0) {
    clearInterval(intervalId);
  }
}, 250);
```

Таймер определяет только частоту обновления интерфейса, а само значение рассчитывается как разница времени. Для срока сессии или аукциона достоверный `deadline` должен приходить с backend; при расчёте также учитывают расхождение часов клиента и сервера.

## Отмена и жизненный цикл

Пока таймер зарегистрирован, браузер удерживает callback. Callback через замыкание может удерживать props, данные, DOM-узлы и другие значения.

```js
function mountBanner() {
  const timeoutId = setTimeout(hideBanner, 5000);

  return () => clearTimeout(timeoutId);
}
```

Отмена нужна, если владелец может завершить работу раньше таймера. Одноразовый `setTimeout` после выполнения освобождает регистрацию, но интервал живёт до `clearInterval` или завершения страницы.

Идентификаторы `setTimeout` и `setInterval` берутся из общего набора, поэтому оба метода очистки технически способны отменять оба вида таймеров. В коде всё равно используют соответствующую пару, чтобы жизненный цикл читался однозначно.

## Timers и rendering

Таймер не синхронизирован с отрисовкой кадра. Для JavaScript-анимации используют `requestAnimationFrame`, который вызывается при подготовке кадра и передаёт его временную метку.

`setTimeout(fn, 0)` позволяет разбить вычисление на задачи и дать браузеру возможность обработать пользовательский ввод и рендеринг между частями. Каждая порция должна быть короткой, а минимальная задержка вложенных таймеров увеличивается браузером.

Микрозадача Promise для такой передачи управления не подходит: event loop очищает всю очередь микрозадач до следующей возможности рендеринга, поэтому длинная цепочка продолжит блокировать кадр.

## Где применяется во frontend

- Debounce переносит `setTimeout` при каждом новом событии.
- Polling использует рекурсивный `setTimeout`, увеличиваемую задержку и `AbortSignal`.
- Toast автоматически закрывается, но таймер очищается при ручном закрытии и размонтировании компонента.
- Обратный отсчёт вычисляет значение из `deadline`, а таймер только инициирует перерисовку.
- Вычисление дробится на короткие задачи, если Worker не подходит.
- Анимация использует `requestAnimationFrame`, а не интервал, чтобы учитывать частоту отрисовки кадров.

## Ключевые уточнения

- Таймер принадлежит браузерному Web API, а не стандарту ECMAScript.
- Задержка задаёт минимальное ожидание; занятый основной поток увеличивает фактическое время.
- `setTimeout(..., 0)` создаёт будущую задачу, а не синхронный вызов и не микрозадачу.
- `setInterval` не ждёт `async`-callback и может запускать перекрывающиеся асинхронные операции.
- Рекурсивный `setTimeout` подходит, когда следующий запуск зависит от завершения предыдущего.
- Обратный отсчёт рассчитывают по времени, а не по количеству вызовов callback.
- Таймер удерживает callback до выполнения или отмены, поэтому его нужно связать с жизненным циклом владельца.
- Для анимации используют `requestAnimationFrame`; тяжёлый код разбивают на короткие части или переносят в Worker.

## Связанные темы

- [Event Loop](<./Event Loop.md>)
- [Debounce и throttle](<./Debounce и throttle.md>)
- [AbortController](<./AbortController.md>)
- [requestAnimationFrame и requestIdleCallback](<./requestAnimationFrame и requestIdleCallback.md>)
- [Page lifecycle visibility и background tabs](<../Browser Internals/Page lifecycle visibility и background tabs.md>)

## Источники

- [WHATWG HTML Standard: Timers](https://html.spec.whatwg.org/multipage/timers-and-user-prompts.html#timers)
- [MDN: setTimeout](https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout)
- [MDN: setInterval](https://developer.mozilla.org/en-US/docs/Web/API/Window/setInterval)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Event Loop](<./Event Loop.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Promise →](<./Promise.md>)
<!-- NOTE-NAV-BOTTOM:END -->
