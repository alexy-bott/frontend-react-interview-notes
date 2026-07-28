---
aliases:
  - performance profiling
  - performance diagnostics
  - DevTools Performance
  - RUM
  - lab vs field
---

#### Ответ на 60 секунд

Performance-работа начинается с диагностики, а не с набора случайных оптимизаций. Сначала нужно понять, что именно плохо: загрузка, отзывчивость, стабильность layout, размер bundle, память, конкретный экран или конкретное действие пользователя. Потом выбирают инструмент: Lighthouse/PageSpeed для первичного lab-сигнала, Chrome DevTools Performance для trace, Network/Coverage для загрузки ресурсов, React DevTools Profiler для render-проблем, Memory panel для утечек, RUM для реальной картины у пользователей.

Lab и field отвечают на разные вопросы. Lab помогает воспроизвести и найти причину в контролируемой среде. Field/RUM показывает, что происходит у реальных пользователей на разных устройствах, сетях и маршрутах. Хороший процесс: измерить baseline, найти bottleneck, внести точечное изменение, повторить замер в тех же условиях и затем смотреть production-метрики.

На собеседовании сильный ответ звучит так: “Я сначала привяжу проблему к метрике и сценарию, потом сниму trace, найду основной вклад: network, JS, render, layout, React commit, image/font, cache или backend TTFB. После фикса проверю, что метрика улучшилась и не ухудшились соседние”.

#### Ключевая схема

```text
symptom -> metric -> trace -> bottleneck -> targeted fix -> lab check -> RUM monitoring
```

| Симптом | Где смотреть | Возможная причина |
| --- | --- | --- |
| Медленный первый экран | Lighthouse, Network, LCP breakdown | TTFB, LCP image, render-blocking CSS/JS |
| Клик реагирует поздно | Performance trace, INP, Long Tasks | main thread, handler, React render |
| Layout прыгает | CLS debug, Performance screenshots | images/fonts/ads без reserved space |
| Большой старт | Coverage, bundle analyzer, Network | initial JS, dependencies, chunks |
| Экран тормозит после данных | React Profiler, Performance panel | дорогой render, layout, таблица |
| Память растёт | Memory snapshots | listeners, timers, detached DOM, cache |

#### Развернутый ответ

Сначала нужно отделить loading performance от runtime performance. Loading - это путь до полезного первого экрана: HTML, CSS, JS, fonts, images, cache, TTFB, hydration. Runtime - это работа уже открытого приложения: input, scroll, filters, forms, charts, websocket updates, React renders, layout/paint и memory leaks.

Chrome DevTools Performance помогает увидеть timeline: tasks, long tasks, event handlers, scripting, rendering, painting, screenshots и Web Vitals markers. Для загрузки полезны Network waterfall, initiator, priority, cache, compression и размер transferred/resource. Для bundle полезны Coverage и bundle analyzer: можно увидеть не только размер файла, но и реально использованный код.

React DevTools Profiler нужен, когда trace показывает, что время уходит в React render/commit или конкретный экран ререндерится слишком часто. Там смотрят, какие компоненты обновлялись, сколько занял render, почему они обновились и помогают ли memoization/state split/context split/virtualization.

RUM нужен, потому что один Lighthouse-прогон не равен production. Реальные пользователи отличаются CPU, сетью, viewport, кешем, географией, маршрутом и данными. Поэтому performance regression лучше ловить через web-vitals, собственные marks/measures, analytics, error monitoring и performance budgets в CI.

#### Где применяется во frontend

| Ситуация | Диагностика | Следующий шаг |
| --- | --- | --- |
| “Главная долго грузится” | LCP + Network waterfall | найти LCP element и его путь загрузки |
| “Фильтр в таблице лагает” | Performance trace + React Profiler | main thread, render, virtualization |
| “После релиза стало хуже” | RUM diff по версии | сравнить bundle, route, device segment |
| “Lighthouse зелёный, пользователи жалуются” | field data + slow devices | проверить INP/Long Tasks в production |
| “Память растёт” | heap snapshots после повторяемого сценария | найти retained objects |

> [!faq]+ Уточнения
> - Lighthouse полезен, но не заменяет RUM.
> - Performance trace нужно снимать под конкретный сценарий: загрузка, клик, ввод, scroll, route transition.
> - Один общий bundle size редко объясняет всю проблему; важны initial JS, parse/compile/execute и waterfall.
> - React Profiler отвечает на вопрос про React-работу, но не показывает всю стоимость браузерного layout/paint.
> - Оптимизацию стоит считать завершённой только после повторной проверки метрик.

#### Пример

```js
performance.mark("filter:start");

applyFilters();

performance.mark("filter:end");
performance.measure("filter", "filter:start", "filter:end");
```

Такой mark помогает связать пользовательский сценарий с trace и RUM, если аналогичное измерение отправляется в аналитику.

#### Частые ошибки

- Начинать с memoization, не понимая bottleneck.
- Сравнивать замеры при разных throttling/device/cache условиях.
- Смотреть только transferred size и игнорировать parse/execute cost.
- Исправлять LCP, но ухудшать INP большим client-side JS.
- Проверять только локальный dev build вместо production artifact.

#### Связанные темы

- [[Конспект для подготовки/Performance/Core Web Vitals LCP INP CLS]]
- [[Конспект для подготовки/Performance/Bundle size и loading strategy]]
- [[Конспект для подготовки/Performance/React performance profiling]]
- [[Конспект для подготовки/Browser Internals/Main thread long tasks и responsiveness]]
- [[Конспект для подготовки/Browser Internals/Memory leaks и profiling]]
- [[Конспект для подготовки/JavaScript/Оптимизация фронтенда]]

#### Источники

- [Chrome DevTools: Performance features reference](https://developer.chrome.com/docs/devtools/performance/reference)
- [web.dev: Web Vitals](https://web.dev/articles/vitals)
- [React docs: Profiler](https://react.dev/reference/react/Profiler)
