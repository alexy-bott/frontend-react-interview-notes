# Core Web Vitals LCP INP CLS

<!-- NOTE-NAV-TOP:START -->
[← Performance диагностика и профилирование](<./Performance диагностика и профилирование.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Bundle size и loading strategy →](<./Bundle size и loading strategy.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Core Web Vitals - набор полевых метрик пользовательского опыта: Largest Contentful Paint (LCP) оценивает скорость появления основного содержимого, Interaction to Next Paint (INP) - отзывчивость страницы на взаимодействия, Cumulative Layout Shift (CLS) - визуальную стабильность.

Хорошими считаются `LCP ≤ 2.5 s`, `INP ≤ 200 ms` и `CLS ≤ 0.1`. Оценка строится по 75-му перцентилю реальных посещений, отдельно для mobile и desktop: не менее 75% посещений должны попадать в хороший диапазон. Метрика указывает на вид проблемы, а причина определяется разбором конкретного элемента, взаимодействия или layout shift.

## Ключевая схема

| Метрика | Пользовательский вопрос | Составляющие или источник |
| --- | --- | --- |
| LCP | когда появилось основное содержимое? | TTFB, resource load delay/duration, render delay |
| INP | как быстро страница показала следующий кадр после взаимодействия? | input delay, обработчики, presentation delay |
| CLS | насколько неожиданно двигался уже видимый контент? | размер сдвига и доля затронутого viewport |

| Диапазон | LCP | INP | CLS |
| --- | --- | --- | --- |
| Хороший | `≤ 2.5 s` | `≤ 200 ms` | `≤ 0.1` |
| Требует улучшения | `> 2.5 s` и `≤ 4 s` | `> 200 ms` и `≤ 500 ms` | `> 0.1` и `≤ 0.25` |
| Плохой | `> 4 s` | `> 500 ms` | `> 0.25` |

## Базовая модель

**LCP** фиксирует момент, когда крупнейший подходящий текстовый или графический элемент в viewport был отрисован. Кандидат может меняться по мере загрузки страницы, поэтому сначала в DevTools находят фактический LCP element, а не предполагают, что им всегда является hero image.

**INP** наблюдает взаимодействия на протяжении жизни страницы и выбирает показатель, близкий к самому медленному с поправкой на количество взаимодействий. Одно взаимодействие может включать несколько событий, например `pointerup` и `click`. Его latency складывается из ожидания начала обработки (input delay), выполнения обработчиков и ожидания следующего paint (presentation delay).

**CLS** оценивает неожиданные перемещения видимых элементов без соответствующего действия пользователя. Браузер группирует близкие shifts в session windows, а итоговым значением становится окно с наибольшей суммой. Поэтому длительно открытая страница не накапливает все сдвиги в один бесконечно растущий score.

## Развернутый ответ

**Диагностика LCP.** Полное время делят на четыре части: Time to First Byte (TTFB), задержку до начала загрузки LCP-ресурса, длительность загрузки и задержку от получения ресурса до render элемента. Если изображение мало, но URL появляется только после выполнения JavaScript, сжатие файла почти не исправит задержку его обнаружения.

LCP-ресурс должен обнаруживаться как можно раньше, критичное изображение не lazy-loadят, а его приоритет при необходимости повышают через `fetchpriority="high"`. Высокий TTFB исправляют на серверной и cache-границе; render delay ищут в блокирующих стилях, JavaScript, hydration и long tasks.

**Диагностика INP.** Если велик input delay, main thread был занят до запуска обработчика. Большая processing duration указывает на тяжёлый handler или синхронные callbacks. Большая presentation delay возникает, когда после обработчика браузер выполняет React render, style/layout и paint. Debounce не является общим лечением: для click он может лишь отложить реакцию ещё сильнее.

**Диагностика CLS.** Для изображений и iframe резервируют геометрию через `width`/`height` или `aspect-ratio`; место для banner, error message и skeleton планируют до появления содержимого. Web font может изменить размеры текста, поэтому важны стратегия загрузки и совместимый fallback. Не каждый сдвиг штрафуется: изменение, ожидаемо связанное с недавним пользовательским input, обрабатывается иначе, но интерфейс всё равно должен оставаться понятным.

**Lab и field.** Lighthouse и локальный trace помогают воспроизвести причину, а Chrome UX Report или собственный RUM показывают реальный 75-й перцентиль. Field-данные нужно сегментировать: хороший desktop не компенсирует плохой mobile, а быстрый landing page - медленный route приложения.

## Пример

Критичное изображение присутствует в исходном HTML, не использует lazy loading и заранее резервирует место:

```html
<img
  src="/hero-1200.avif"
  srcset="/hero-640.avif 640w, /hero-1200.avif 1200w"
  sizes="(max-width: 768px) 100vw, 1200px"
  width="1200"
  height="640"
  fetchpriority="high"
  alt="Интерфейс панели управления"
>
```

`srcset` и `sizes` помогают выбрать подходящий файл, размеры задают aspect ratio для layout, а `fetchpriority` подсказывает браузеру повысить приоритет. Атрибут нужен только вероятному LCP-изображению; массовое назначение высокого приоритета уничтожает саму приоритизацию.

## Ключевые уточнения

- Core Web Vitals являются field-метриками; Lighthouse даёт диагностический lab-результат, а не статистику реальных посещений.
- LCP оптимизируют по его фактическим четырём составляющим. Уменьшение файла не помогает, если время уходит до начала загрузки или после её завершения.
- INP охватывает input delay, обработчики и подготовку следующего кадра; React render является только одной из возможных частей.
- CLS относится к неожиданным сдвигам и рассчитывается по группам близких shifts, а не как простая сумма за всё время жизни страницы.
- Улучшение одной метрики проверяют вместе с остальными: перенос большого JavaScript с загрузки на первое действие способен улучшить LCP и ухудшить INP.

## Связанные темы

- [Core Web Vitals](<../Web Basics/Core Web Vitals.md>)
- [Critical Render Path](<../Web Basics/Critical Render Path.md>)
- [Performance диагностика и профилирование](<./Performance диагностика и профилирование.md>)
- [Images fonts и resource priority](<./Images fonts и resource priority.md>)
- [Main thread long tasks и responsiveness](<../Browser Internals/Main thread long tasks и responsiveness.md>)
- [Hydration](<../React/Hydration.md>)

## Источники

- [web.dev: How the Core Web Vitals thresholds were defined](https://web.dev/articles/defining-core-web-vitals-thresholds)
- [web.dev: Optimize Largest Contentful Paint](https://web.dev/articles/optimize-lcp)
- [web.dev: Interaction to Next Paint](https://web.dev/articles/inp)
- [web.dev: Optimize Cumulative Layout Shift](https://web.dev/articles/optimize-cls)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Performance диагностика и профилирование](<./Performance диагностика и профилирование.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Bundle size и loading strategy →](<./Bundle size и loading strategy.md>)
<!-- NOTE-NAV-BOTTOM:END -->
