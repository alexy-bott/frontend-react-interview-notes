---
aliases:
  - performance profiling
  - performance diagnostics
  - DevTools Performance
  - RUM
  - lab vs field
---

#### Быстрый ответ

Диагностика производительности начинается с конкретного пользовательского симптома и измеримой метрики, а не с заранее выбранной оптимизации. Сначала фиксируют исходный результат в воспроизводимом сценарии, затем по network waterfall и performance trace определяют, где уходит время: в сети, выполнении JavaScript, React render, layout, paint, декодировании ресурсов или backend.

Лабораторные измерения (lab data) помогают воспроизвести проблему в контролируемых условиях. Полевые данные (field data) получают от реальных посещений; сбор таких измерений называют Real User Monitoring (RUM). После точечного изменения повторяют тот же lab-сценарий и проверяют production-сегменты, чтобы подтвердить улучшение и обнаружить побочные регрессии.

#### Ключевая схема

```text
симптом
-> сценарий и метрика
-> воспроизводимый baseline
-> trace и узкое место
-> одна проверяемая гипотеза
-> точечное изменение
-> повторный lab-замер
-> field/RUM после релиза
```

| Симптом | Первый сигнал | Инструмент для причины |
| --- | --- | --- |
| Медленно появляется основной контент | LCP и его составляющие | Network + Performance |
| Интерфейс поздно отвечает на ввод | INP, long tasks | Performance trace |
| Контент неожиданно сдвигается | CLS | Performance/Layout Shift track |
| Долго открывается маршрут | resource timing, chunk waterfall | Network + bundle analyzer |
| React-экран дорого обновляется | commit duration | React DevTools Profiler |
| Память растёт после повторения сценария | heap size и retained objects | Memory snapshots |

#### Базовая модель

**Загрузка (loading performance)** охватывает путь от навигации до полезного содержимого: HTML, TTFB, CSS, JavaScript, изображения, шрифты, cache и начальный render. **Работа после загрузки (runtime performance)** охватывает клики, ввод, прокрутку, route transitions, обновления данных, React render и работу браузерного main thread.

Chrome DevTools Performance показывает задачи main thread, вызовы функций, style/layout, paint и screenshots на общей временной шкале. Network показывает момент обнаружения ресурса, приоритет, цепочку инициаторов, cache, переданный размер и длительность. React Profiler показывает только работу React; дорогой layout после commit нужно искать в browser trace.

Один инструмент не отвечает на все вопросы. Lighthouse даёт стандартизированный lab-аудит страницы, но не воспроизводит произвольный сценарий внутри приложения и не представляет всех пользователей. Bundle analyzer показывает состав chunks, но не доказывает, что именно они задерживают наблюдаемое действие.

#### Развернутый ответ

**Фиксация сценария.** Записывают route, данные, действие, устройство или CPU throttling, сеть, состояние cache и production build. Сравнение dev-сборки с production или warm cache с cold cache не позволяет приписать разницу изменению кода.

**Поиск узкого места.** Сначала выбирают самый крупный вклад в задержку. Для LCP это может быть TTFB, позднее обнаружение ресурса, его загрузка или задержка render. Для взаимодействия - ожидание свободного main thread, обработчик, React update, layout и paint. Оптимизация меньшей части не изменит итоговую метрику заметно.

**Проверка гипотезы.** Изменяют одну причину и повторяют замер несколько раз в тех же условиях. Важна не единичная лучшая цифра, а устойчивое изменение распределения. Одновременно проверяют соседние метрики: перенос работы с загрузки на первый клик может улучшить LCP и ухудшить INP.

**Field/RUM.** Реальные данные сегментируют по route, версии приложения, типу устройства, сети и другим признакам, которые не раскрывают личность пользователя. Агрегат по всему сайту способен скрыть регрессию одного тяжёлого экрана. Для Core Web Vitals ориентируются на 75-й перцентиль, а не на среднее значение.

**Performance budgets.** Ограничения на initial JavaScript, размер отдельных ресурсов или длительность ключевого сценария помогают ловить известные классы регрессий в CI. Budget не заменяет профилирование: допустимый размер bundle не гарантирует быстрый runtime.

#### Диагностика

| Наблюдение | Что проверить сначала | Следующая проверка |
| --- | --- | --- |
| LCP-изображение начинает грузиться поздно | есть ли URL в исходном HTML и не включён ли lazy loading | initiator chain и приоритет |
| Обработчик клика стартует с задержкой | long task перед событием | источник scripting и сторонний код |
| React commit короткий, экран всё равно тормозит | layout и paint после commit | размер DOM и forced layout |
| Chunk скачан быстро, route открывается поздно | parse/execute и цепочку динамических imports | CPU trace на слабом устройстве |
| Heap растёт после закрытия экрана | повторить сценарий и сравнить snapshots | retaining path для listener, timer или DOM |

#### Пример

User Timing API помечает границы прикладного сценария в performance trace:

```js
performance.mark("orders-filter:start");

applyFilters();

performance.mark("orders-filter:end");
performance.measure(
  "orders-filter",
  "orders-filter:start",
  "orders-filter:end",
);
```

Так измеряется только синхронная работа `applyFilters`. Если визуальный результат появляется после React update и paint, одной этой длительности недостаточно: её сопоставляют с trace или измерением до фактического завершения нужного этапа.

#### Ключевые уточнения

- Baseline включает условия измерения, а не только число. Без одинакового build, cache, данных и throttling сравнение ненадёжно.
- Размер переданного JavaScript не показывает стоимость parse, compile и execute; эти этапы особенно заметны на слабом CPU.
- React Profiler локализует React render, но не заменяет Network, browser layout и paint analysis.
- Lab объясняет воспроизводимый случай, field показывает распределение реального опыта. Для решения production-проблем нужны оба вида данных.
- Оптимизация считается подтверждённой после повторного измерения целевой и соседних метрик, а не после изменения кода.

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
- [React: Profiler](https://react.dev/reference/react/Profiler)
