---
aliases:
  - responsive images
  - srcset
  - sizes
  - lazy loading
  - изображения в HTML
---

#### Быстрый ответ

Responsive image позволяет браузеру выбрать подходящий файл для размеров layout, плотности пикселей и поддерживаемого формата. `<img>` задаёт fallback, текстовую альтернативу и геометрию, `srcset` перечисляет candidates, `sizes` описывает ожидаемую CSS-ширину, а `<picture>` добавляет art direction или выбор формата.

Для производительности задают корректные `width`/`height`, не lazy-loadят LCP-изображение и откладывают media ниже первого экрана. Для доступности `alt` передаёт назначение изображения в текущем контексте; декоративный image получает пустой `alt`.

#### Ключевая схема

| Механизм | Что сообщает браузеру |
| --- | --- |
| `src` | fallback и базовый URL изображения |
| `srcset` с `w` | candidates разной intrinsic width |
| `sizes` | предполагаемая ширина элемента в layout |
| `srcset` с `x` | candidates для разной pixel density |
| `<picture><source>` | media condition, формат или другое кадрирование |
| `width`/`height` | intrinsic aspect ratio для резервирования места |
| `loading="lazy"` | возможность отложить некритичную загрузку |

#### Базовая модель

При width descriptors браузер использует `srcset`, `sizes`, viewport и device pixel ratio, чтобы самостоятельно выбрать candidate. `sizes` описывает layout до загрузки CSS-результата; это не список размеров файлов. Если фактическая ширина карточки 400 px, а `sizes` утверждает `100vw`, browser может скачать лишний большой asset.

Density descriptors `1x`, `2x` применяют, когда CSS-размер изображения известен и отличаются только варианты по плотности. В одном `srcset` не смешивают `w` и `x`. Для большинства responsive layouts с изменяемой шириной удобнее width descriptors.

`<picture>` перебирает `<source>` сверху вниз и выбирает первое подходящее условие `media`/`type`; вложенный `<img>` остаётся обязательным fallback и владельцем `alt`, размеров и общих атрибутов. Art direction означает смену композиции, например широкий desktop-кадр и крупный mobile crop.

#### Развернутый ответ

**Геометрия.** `width` и `height` на `<img>` позволяют вычислить aspect ratio до загрузки. Responsive CSS может задать `max-width: 100%; height: auto`, сохранив пропорции. Если разные `<source>` имеют разное кадрирование, их размеры нужно согласовать с фактическими assets, чтобы резерв не создавал новый shift.

**Alt-текст.** Текст зависит от функции изображения. Ссылка-логотип может иметь `alt="На главную"`, график требует передачи вывода или данных рядом, а декоративная текстура - `alt=""`. `figcaption` подписывает figure для всех пользователей, но не всегда заменяет краткий `alt`, необходимый в месте изображения.

**Lazy loading.** `loading="lazy"` позволяет browser отложить изображения вне viewport. Точная дистанция и момент загрузки являются browser heuristic. Критичное LCP image оставляют eager и при необходимости дают `fetchpriority="high"`; этот hint не гарантирует выбранный порядок и не используется массово.

**Формат.** `<picture>` может предложить AVIF/WebP и оставить совместимый fallback. Формат выбирают по реальному размеру и качеству; порядок `<source>` выражает предпочтение. Для простого выбора размера в одном формате отдельный `<picture>` не нужен.

**CSS background.** Фоновое изображение уместно для декора, но не имеет `alt` и обнаруживается после CSS. Содержательное image лучше представить `<img>`, чтобы сохранить семантику, responsive selection и раннее обнаружение.

#### Пример

`<picture>` меняет кадрирование на узком экране, а каждый вариант остаётся responsive:

```html
<picture>
  <source
    media="(max-width: 640px)"
    srcset="/team-mobile-480.avif 480w, /team-mobile-800.avif 800w"
    sizes="100vw"
  >
  <source
    srcset="/team-wide-960.avif 960w, /team-wide-1440.avif 1440w"
    sizes="(max-width: 1200px) 100vw, 1200px"
  >
  <img
    src="/team-wide-960.jpg"
    width="1200"
    height="675"
    alt="Команда разработки обсуждает макет интерфейса"
  >
</picture>
```

Mobile files должны иметь соотношение сторон, совместимое с зарезервированной геометрией, либо соответствующие размеры у `<source>` в поддерживающих browsers. Если меняется только разрешение, достаточно одного `<img srcset sizes>` без art direction.

#### Ключевые уточнения

- `srcset` перечисляет files, а `sizes` описывает layout width; browser сам выбирает candidate и может учитывать cache.
- `<picture>` нужен для art direction или форматов, но не является обязательной оболочкой каждого responsive image.
- `alt` описывает функцию и смысл в контексте, а не механически перечисляет всё видимое на картинке.
- `loading="lazy"` является browser hint и не применяется к LCP image.
- Размеры предотвращают CLS только при соответствии реальному соотношению сторон выбранного asset.

#### Связанные темы

- [[Конспект для подготовки/HTML/Accessibility]]
- [[Конспект для подготовки/Performance/Images fonts и resource priority]]
- [[Конспект для подготовки/CSS/Responsive design и media queries]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]
- [[Конспект для подготовки/Web Basics/Critical Render Path]]

#### Источники

- [WHATWG HTML: Images](https://html.spec.whatwg.org/multipage/images.html)
- [MDN: img element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img)
- [MDN: Responsive images](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images)
- [web.dev: Optimize Largest Contentful Paint](https://web.dev/articles/optimize-lcp)
