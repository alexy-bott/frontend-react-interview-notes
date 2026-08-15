# Debounce и throttle

<!-- NOTE-NAV-TOP:START -->
[← Fetch и работа с API](<./41 Fetch и работа с API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [DOM API — innerHTML и layout →](<./43 DOM API — innerHTML и layout.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Debounce и throttle ограничивают частоту выполнения функции при частом потоке событий.

Debounce ждёт паузу: каждый новый вызов переносит выполнение ещё на заданную задержку. Он подходит для поиска после остановки ввода, проверки поля и автосохранения.

Throttle сохраняет регулярный отклик: функция выполняется не чаще одного раза за интервал, пока события продолжаются. Он подходит для перетаскивания, `pointermove`, индикатора прокрутки и других сценариев, где важны промежуточные обновления.

Короткий критерий выбора: если нужен итог после тишины - debounce; если нужны промежуточные результаты с ограниченной частотой - throttle. Для визуального обновления раз в кадр часто лучше `requestAnimationFrame`.

## Ключевая схема

Пусть события приходят в моменты `0`, `50`, `100` и `300` мс, а ограничение равно `200` мс.

```text
events:            ●──●──●────────●

debounce trailing:             ●──────●
                               300     500 мс

throttle:          ●────────●────────●
                   0        200      400 мс
```

Точный результат throttle зависит от настроек `leading` и `trailing`, но главное различие сохраняется: debounce ищет паузу, throttle ограничивает темп.

## Как работает debounce

Debounced-функция хранит таймер. Каждый вызов отменяет предыдущий таймер и создаёт новый. Исходная функция выполняется только тогда, когда между вызовами прошло не меньше `delay`.

```js
function debounce(fn, delay) {
  let timerId;

  function debounced(...args) {
    const context = this;

    clearTimeout(timerId);
    timerId = setTimeout(() => {
      timerId = undefined;
      fn.apply(context, args);
    }, delay);
  }

  debounced.cancel = () => {
    clearTimeout(timerId);
    timerId = undefined;
  };

  return debounced;
}
```

Обычная функция-обёртка и `fn.apply(context, args)` сохраняют объект, через который была вызвана функция. Стрелочная обёртка брала бы `this` из внешней области видимости и могла бы изменить поведение метода.

`cancel()` нужен при завершении жизненного цикла: например, закрытое модальное окно не должно запускать отложенное сохранение. В готовых утилитах также встречается `flush()`, который немедленно выполняет ожидающий trailing-вызов.

## Как работает throttle

Throttled-функция запоминает момент последнего выполнения. Если интервал уже прошёл, вызов выполняется сразу. Иначе сохраняются последние аргументы и планируется trailing-вызов в конце временного окна.

```js
function throttle(fn, interval) {
  let lastTime = -Infinity;
  let timerId;
  let lastArgs;
  let lastContext;

  function invoke(time) {
    lastTime = time;
    const args = lastArgs;
    const context = lastContext;
    lastArgs = undefined;
    lastContext = undefined;
    fn.apply(context, args);
  }

  function throttled(...args) {
    const now = performance.now();
    const remaining = interval - (now - lastTime);

    lastArgs = args;
    lastContext = this;

    if (remaining <= 0) {
      clearTimeout(timerId);
      timerId = undefined;
      invoke(now);
    } else if (timerId === undefined) {
      timerId = setTimeout(() => {
        timerId = undefined;
        invoke(performance.now());
      }, remaining);
    }
  }

  throttled.cancel = () => {
    clearTimeout(timerId);
    timerId = undefined;
    lastTime = -Infinity;
    lastArgs = undefined;
    lastContext = undefined;
  };

  return throttled;
}
```

Этот вариант выполняет первый вызов сразу и сохраняет последний вызов внутри интервала. Готовые библиотеки дают явные настройки и тщательнее обрабатывают повторный вход, возвращаемое значение и исключения. Для общего кода проекта надёжнее использовать одну проверенную утилиту.

## `leading`, `trailing` и `maxWait`

| Настройка | Поведение |
| --- | --- |
| `leading` | выполнить в начале серии или временного окна |
| `trailing` | выполнить с последними аргументами в конце |
| `maxWait` | не откладывать debounce дольше заданного времени |

Trailing debounce подходит поиску: нужен последний запрос после паузы. Leading debounce подходит защите от двойного клика, если первый вызов должен сработать сразу, а следующие временно игнорируются.

Throttle часто использует оба края: первый вызов даёт быстрый отклик, а trailing-вызов не теряет последнее положение указателя. Если отключить trailing, последнее состояние может не попасть в интерфейс.

`maxWait` полезен для потока, который долго не прекращается. Обычный debounce в таком сценарии может не выполниться вообще; максимальное ожидание гарантирует периодический запуск.

## Debounce запроса и отмена запроса

Debounce уменьшает число новых запросов, но не останавливает `fetch`, который уже начался. Эти задачи решают вместе с `AbortController`.

```js
let controller;

const runSearch = debounce(async (query, signal) => {
  try {
    const response = await fetch(
      `/api/search?q=${encodeURIComponent(query)}`,
      { signal },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    renderResults(await response.json());
  } catch (error) {
    if (!signal.aborted) {
      showSearchError(error);
    }
  }
}, 300);

searchInput.addEventListener("input", (event) => {
  controller?.abort("query changed");
  controller = new AbortController();

  runSearch(event.currentTarget.value, controller.signal);
});
```

При каждом событии `input` предыдущий выполняющийся запрос отменяется сразу, а новый начинается только после паузы. При завершении работы также вызывают `runSearch.cancel()` и `controller?.abort()`.

В реальном коде нужно отдельно обработать сетевую ошибку и не показывать отмену как ошибку пользователю. Подробная модель находится в [AbortController](<./40 AbortController.md>).

## Throttle и `requestAnimationFrame`

Throttle по интервалу ограничивает частоту, например одним вызовом в `100` мс. Для позиции перетаскиваемого элемента или анимации при прокрутке обычно нужен максимум один update на кадр, поэтому удобен rAF-throttle:

```js
function throttleByFrame(fn) {
  let frameId;
  let lastArgs;
  let lastContext;

  function throttled(...args) {
    lastArgs = args;
    lastContext = this;

    if (frameId !== undefined) {
      return;
    }

    frameId = requestAnimationFrame(() => {
      frameId = undefined;
      const args = lastArgs;
      const context = lastContext;
      lastArgs = undefined;
      lastContext = undefined;
      fn.apply(context, args);
    });
  }

  throttled.cancel = () => {
    if (frameId !== undefined) {
      cancelAnimationFrame(frameId);
    }

    frameId = undefined;
    lastArgs = undefined;
    lastContext = undefined;
  };

  return throttled;
}
```

Он объединяет все события до ближайшего кадра и использует последние аргументы. Это не ускоряет саму работу: callback должен оставаться коротким, иначе кадр всё равно будет пропущен.

## Таймер не является точными часами

`setTimeout(delay)` задаёт минимальную задержку, а не точное время выполнения. После истечения задержки callback станет доступен event loop и будет ждать, пока освободится основной поток. В фоновой вкладке браузер может дополнительно ограничивать таймеры.

Поэтому debounce и throttle определяют частоту вызовов, но не дают гарантий реального времени. Для срока жизни сессии источником истины не должен быть один клиентский таймер.

## React

Debounced- или throttled-обёртка хранит таймер и последние аргументы, поэтому её экземпляр должен сохраняться между renders. Если создавать обёртку заново при каждом render, каждый экземпляр получит собственное состояние и единая серия вызовов распадётся.

При этом стабильная обёртка не должна навсегда захватить устаревшие props или state. Обычно её сочетают с ref на актуальный callback либо используют библиотечный hook, который сохраняет экземпляр, читает свежие данные и выполняет очистку.

При размонтировании отменяют таймер или `requestAnimationFrame` и связанную асинхронную операцию. Одна мемоизация без очистки не завершает отложенную работу.

## Практический выбор

| Сценарий | Выбор | Причина |
| --- | --- | --- |
| Поиск после остановки ввода | trailing debounce | нужен последний запрос после паузы |
| Автосохранение с длинным непрерывным вводом | debounce + `maxWait` | пауза желательна, но ждать бесконечно нельзя |
| Защита от двойной отправки | leading debounce или состояние `pending` | первый вызов нужен сразу |
| Индикатор прокрутки | throttle или rAF | нужны регулярные промежуточные обновления |
| Позиция при перетаскивании | rAF-throttle | не больше одного обновления DOM на кадр |
| Тяжёлое вычисление | разделение работы или Web Worker | ограничение частоты не уменьшает стоимость одного вызова |

## Ключевые уточнения

- Debounce выполняет после паузы, throttle сохраняет ограниченный регулярный темп.
- `leading` отвечает за начало серии, `trailing` - за последнее значение в конце.
- Debounce не отменяет уже начатый запрос; для этого нужен `AbortSignal`.
- Timer задаёт минимальную задержку и зависит от занятости event loop.
- Обёртка должна сохранять `this`, аргументы и жизненный цикл отложенного вызова.
- В React важны одновременно стабильный экземпляр функции, свежие данные и очистка.
- Для визуальных обновлений rAF-throttle обычно лучше произвольного интервала, но не делает тяжёлый callback дешёвым.

## Связанные темы

- [Цикл событий (Event Loop)](<./35 Цикл событий (Event Loop).md>)
- [AbortController](<./40 AbortController.md>)
- [requestAnimationFrame и requestIdleCallback](<./47 requestAnimationFrame и requestIdleCallback.md>)
- [Функции](<./13 Функции.md>)
- [useCallback](<../React/14 useCallback.md>)

## Источники

- [MDN: setTimeout](https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout)
- [MDN: requestAnimationFrame](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)
- [web.dev: Optimize JavaScript execution](https://web.dev/learn/performance/optimize-javascript)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Fetch и работа с API](<./41 Fetch и работа с API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [DOM API — innerHTML и layout →](<./43 DOM API — innerHTML и layout.md>)
<!-- NOTE-NAV-BOTTOM:END -->
