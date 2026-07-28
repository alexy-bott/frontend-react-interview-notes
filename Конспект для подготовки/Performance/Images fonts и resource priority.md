---
aliases:
  - image performance
  - font performance
  - resource priority
  - preload
  - fetchpriority
---

#### Ответ на 60 секунд

Изображения, шрифты и resource priorities часто напрямую влияют на LCP и CLS. Если главный hero image обнаруживается поздно, грузится в тяжёлом формате или конкурирует с менее важными ресурсами, LCP ухудшается. Если изображения, iframe или embeds не имеют размеров, layout может прыгать и ухудшать CLS. Если web font загружается поздно и меняет метрики текста, пользователь видит сдвиги или задержку отображения текста.

Для изображений важны формат, размер под viewport, `srcset/sizes`, lazy loading для некритичных изображений, явные `width/height` или `aspect-ratio`, корректный `alt` и приоритет для LCP-картинки через `fetchpriority` или `preload` по ситуации. Для шрифтов важны subset, preload только критичных font files, `font-display`, fallback с похожими метриками и отсутствие лишних начертаний.

Resource hints - это подсказки, а не магия. `preload` нужен для ресурса, который точно нужен очень рано. `preconnect` полезен для важного внешнего origin. Если подсказок слишком много, они начинают конкурировать с реальными критичными ресурсами и могут ухудшить waterfall.

#### Ключевая схема

| Ресурс | Риск | Что делать |
| --- | --- | --- |
| Hero image | поздний LCP | правильный размер, формат, priority |
| Below-fold images | лишняя ранняя загрузка | `loading="lazy"` |
| Images без размеров | CLS | `width/height` или `aspect-ratio` |
| Web fonts | FOIT/FOUT/CLS | subset, `font-display`, preload critical |
| Third-party origin | latency | точечный `preconnect` |
| Preload | конкуренция ресурсов | только действительно critical |

#### Развернутый ответ

Главную картинку первого экрана нельзя оптимизировать как обычную декоративную картинку. Браузер должен обнаружить её рано, получить правильный приоритет и скачать подходящий размер. Если LCP image задаётся через CSS background, появляется поздно после JS или спрятана за client render, браузер может начать загрузку слишком поздно.

`srcset` и `sizes` нужны, чтобы не отдавать мобильному viewport desktop-изображение. Форматы вроде AVIF/WebP часто уменьшают размер, но итог зависит от качества, контента и поддержки. `decoding="async"` может помочь не блокировать main thread декодированием, но для LCP-картинки приоритет загрузки важнее, чем механическое добавление всех атрибутов.

Fonts влияют не только на внешний вид. Если текст сначала скрывается до загрузки font, страдает perceived performance. Если fallback и web font имеют разные метрики, после подмены может появиться layout shift. Поэтому используют `font-display`, ограничивают количество начертаний, делают subset и подбирают fallback ближе по метрикам.

Preload и preconnect нужно применять точечно. Preload второстепенных images, fonts или scripts может отобрать bandwidth у LCP-ресурса. Preconnect к каждому внешнему домену тоже стоит денег, потому что открывает соединения заранее.

#### Где применяется во frontend

| Ситуация | Что проверить | Решение |
| --- | --- | --- |
| Hero долго появляется | когда стартует загрузка image | preload/fetchpriority, убрать позднее обнаружение |
| Mobile грузит huge image | responsive image config | `srcset/sizes`, CDN resizing |
| Карточки прыгают | размеры media | aspect-ratio или width/height |
| Текст мигает/двигается | font strategy | `font-display`, fallback metrics, subset |
| Сторонний CDN медленный | connection setup | `preconnect` только для важного origin |

> [!faq]+ Уточнения
> - `loading="lazy"` не ставят на LCP image.
> - `preload` для всего подряд ухудшает приоритеты.
> - `width/height` у изображения помогают браузеру зарезервировать место.
> - CSS background для LCP image часто сложнее оптимизировать, чем `<img>`.
> - Fonts могут влиять и на LCP, и на CLS.

#### Пример

```html
<link rel="preconnect" href="https://cdn.example.com" crossorigin>
<link rel="preload" as="image" href="/hero-1200.avif" fetchpriority="high">

<img
  src="/hero-1200.avif"
  srcset="/hero-640.avif 640w, /hero-1200.avif 1200w"
  sizes="(max-width: 768px) 100vw, 1200px"
  width="1200"
  height="640"
  fetchpriority="high"
  alt="Dashboard overview"
>
```

#### Частые ошибки

- Lazy-load главной картинки первого экрана.
- Не задавать размеры images/iframe.
- Preload-ить все fonts и images без приоритизации.
- Отдавать одинаковое большое изображение всем viewport.
- Использовать слишком много font weights/styles.
- Делать LCP image через JS, который выполняется поздно.

#### Связанные темы

- [[Конспект для подготовки/Performance/Core Web Vitals LCP INP CLS]]
- [[Конспект для подготовки/HTML/Изображения и responsive media]]
- [[Конспект для подготовки/HTML/Head meta и resource hints]]
- [[Конспект для подготовки/Web Basics/Critical Render Path]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]
- [[Конспект для подготовки/CSS/Responsive design и media queries]]

#### Источники

- [web.dev: Optimize LCP](https://web.dev/articles/optimize-lcp)
- [web.dev: Optimize CLS](https://web.dev/articles/optimize-cls)
- [MDN: Responsive images](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images)
