# Images fonts и resource priority

<!-- NOTE-NAV-TOP:START -->
[← React performance profiling](<./React performance profiling.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Изображения и web fonts влияют на загрузку, LCP, CLS и объём трафика. Для изображения выбирают подходящие размеры и формат, позволяют браузеру рано обнаружить LCP-ресурс, резервируют геометрию и откладывают только некритичные изображения. Для шрифта сокращают набор файлов и символов, определяют поведение текста во время загрузки и подбирают близкий fallback.

Приоритет ресурсов сначала формируется браузером по типу и месту обнаружения. `fetchpriority`, `preload` и `preconnect` являются подсказками, а не гарантией ускорения. Их добавляют точечно после проверки waterfall: лишний ресурс с высоким приоритетом конкурирует с действительно критичными CSS, изображением и шрифтом.

## Ключевая схема

| Задача | Механизм | Что проверять |
| --- | --- | --- |
| Не загружать лишние пиксели | `srcset` + `sizes`, image CDN | какой candidate реально выбран |
| Стабилизировать layout | `width`/`height` или `aspect-ratio` | совпадает ли зарезервированное соотношение сторон |
| Рано начать LCP image | HTML discovery, `fetchpriority`, иногда `preload` | resource load delay |
| Отложить below-the-fold media | `loading="lazy"` | не является ли элемент LCP |
| Сократить font cost | WOFF2, subset, нужные weights | число и размер font requests |
| Управлять показом текста | `font-display` и metric-compatible fallback | FOIT, FOUT и layout shift |

## Базовая модель

Responsive image позволяет браузеру выбрать файл под layout и плотность экрана. `srcset` перечисляет candidates, а `sizes` сообщает ожидаемую ширину изображения до расчёта CSS. Если `sizes` неверен, браузер может выбрать слишком большой файл, даже когда набор `srcset` задан правильно.

Атрибуты `width` и `height` задают intrinsic aspect ratio. При responsive CSS изображение может менять фактический размер, но браузер заранее резервирует пропорциональное место и уменьшает CLS. Если реальный asset имеет другое соотношение сторон, резерв окажется неверным.

Web font загружается как отдельный ресурс. До его получения браузер либо временно скрывает текст, либо показывает fallback и затем заменяет его. Эти эффекты называют Flash of Invisible Text (FOIT) и Flash of Unstyled Text (FOUT). `font-display` выбирает стратегию показа, а совместимые метрики fallback уменьшают сдвиг при замене.

## Развернутый ответ

**LCP-изображение.** URL должен быть доступен в исходном HTML или preload, а `loading="lazy"` для него не используют. `fetchpriority="high"` повышает подсказанный приоритет, но не исправляет высокий TTFB, слишком большой файл или render delay после загрузки. Обычно одному главному image достаточно высокого приоритета.

**Некритичные изображения.** `loading="lazy"` откладывает загрузку media, находящегося дальше от viewport. Это экономит сеть на длинной странице, но большое число изображений при приближении к viewport всё равно может создать конкуренцию. Для карточек дополнительно задают размеры, обработку ошибки и осмысленный `alt`; декоративное изображение получает пустой `alt=""`.

**Формат и качество.** AVIF и WebP часто уменьшают размер по сравнению со старыми форматами, но выбор подтверждают на конкретном контенте: encoding settings влияют на качество, CPU-декодирование и размер. SVG подходит логотипам и векторной графике, но не является автоматической заменой фотографии.

**Шрифты.** Загружают только используемые families, weights и subsets. Preload применяют к конкретному критичному WOFF2-файлу, который точно используется на первом экране; для font preload указывают `as="font"`, правильный `type` и `crossorigin`, иначе возможна повторная загрузка. Слишком много preloaded начертаний отнимает bandwidth.

**Metric-compatible fallback.** CSS descriptors `size-adjust`, `ascent-override`, `descent-override` и `line-gap-override` позволяют приблизить метрики fallback к web font. Это уменьшает CLS, но значения рассчитывают для конкретной пары шрифтов, а не копируют произвольно.

**Resource hints.** `preconnect` заранее устанавливает соединение с важным внешним origin и оправдан, когда ресурс с него скоро понадобится. `preload` запускает загрузку известного ресурса текущей страницы раньше обычного обнаружения. Для responsive image preload должен согласовываться с `imagesrcset` и `imagesizes`, иначе можно загрузить не тот candidate.

## Диагностика

| Симптом | Что посмотреть в Network/Performance | Возможное исправление |
| --- | --- | --- |
| LCP image стартует поздно | initiator и resource load delay | сделать URL доступным в HTML или точечно preload |
| Mobile скачивает desktop asset | выбранный `currentSrc`, `srcset`, `sizes` | исправить candidates и layout size |
| Карточки сдвигаются после image load | зарезервированный размер | добавить корректный aspect ratio |
| Текст долго невидим | font request и `font-display` | изменить display strategy, subset и caching |
| Текст сдвигается после font swap | метрики fallback/web font | подобрать fallback и metric overrides |
| Preload не используется | warning DevTools и совпадение URL/type/CORS | исправить атрибуты или удалить hint |

## Пример

Критичное responsive image обнаруживается из HTML и получает только необходимые подсказки:

```html
<img
  src="/dashboard-1200.avif"
  srcset="/dashboard-640.avif 640w, /dashboard-1200.avif 1200w"
  sizes="(max-width: 768px) 100vw, 1200px"
  width="1200"
  height="640"
  fetchpriority="high"
  alt="Обзор заказов в панели управления"
>
```

Такой `<img>` обычно не требует дополнительного preload, потому что browser preload scanner уже видит его в HTML. Preload добавляют, если trace показывает реальную задержку обнаружения, например когда LCP-ресурс задан в CSS, и согласуют его с responsive candidates.

## Ключевые уточнения

- `loading="lazy"` экономит загрузку некритичных изображений, но задерживает LCP image и потому для него не используется.
- `width` и `height` резервируют соотношение сторон; они предотвращают CLS только при соответствии реальному asset и layout.
- `fetchpriority="high"` является подсказкой браузеру. Несколько ресурсов с высоким приоритетом начинают конкурировать друг с другом.
- `font-display: swap` быстро показывает текст, но не гарантирует отсутствие CLS; важны метрики fallback.
- Preload полезен только для заранее известного критичного ресурса и должен совпасть с будущим запросом по URL, типу и CORS-режиму.

## Связанные темы

- [Core Web Vitals LCP INP CLS](<./Core Web Vitals LCP INP CLS.md>)
- [Изображения и responsive media](<../HTML/Изображения и responsive media.md>)
- [Head meta и resource hints](<../HTML/Head meta и resource hints.md>)
- [Critical Render Path](<../Web Basics/Critical Render Path.md>)
- [Core Web Vitals](<../Web Basics/Core Web Vitals.md>)
- [Responsive design и media queries](<../CSS/Responsive design и media queries.md>)

## Источники

- [web.dev: Optimize Largest Contentful Paint](https://web.dev/articles/optimize-lcp)
- [web.dev: Optimize Cumulative Layout Shift](https://web.dev/articles/optimize-cls)
- [web.dev: Optimize web fonts](https://web.dev/articles/font-best-practices)
- [MDN: Responsive images](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images)
- [MDN: rel=preload](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/preload)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← React performance profiling](<./React performance profiling.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-BOTTOM:END -->
