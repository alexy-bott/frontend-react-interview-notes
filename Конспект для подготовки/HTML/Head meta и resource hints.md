---
aliases:
  - HTML head
  - meta viewport
  - resource hints
  - SEO meta
---

#### Ответ на 60 секунд

`<head>` содержит служебную информацию о документе: кодировку, viewport, заголовок страницы, meta description, ссылки на CSS, scripts, icons, canonical URL, Open Graph-данные и resource hints. Пользователь обычно не видит `<head>` напрямую, но он влияет на загрузку, SEO, шаринг в соцсетях, доступность и корректное отображение на мобильных.

Базовый минимум для современной страницы: `<!doctype html>`, `lang` на `<html>`, `meta charset="utf-8"`, `meta name="viewport"`, уникальный `<title>`, осмысленный `meta description`, корректные CSS/scripts и аккуратные hints. `preload` и `preconnect` добавляют точечно: они меняют приоритеты загрузки и могут как помочь LCP, так и ухудшить его.

#### Ключевая схема

| Элемент | Зачем нужен |
| --- | --- |
| `<!doctype html>` | включает standards mode |
| `<html lang="ru">` | язык документа для accessibility и SEO |
| `charset` | корректная кодировка |
| `viewport` | адаптивное отображение на мобильных |
| `<title>` | заголовок вкладки и поисковой выдачи |
| `description` | краткое описание страницы |
| `canonical` | основной URL при дублях |
| `preconnect` | заранее установить соединение |
| `preload` | заранее загрузить критичный ресурс |

#### Развернутый ответ

`meta viewport` нужен для мобильной верстки. Без него браузер может использовать виртуальную desktop-ширину и показывать страницу уменьшенной. Значение `width=device-width, initial-scale=1` связывает CSS viewport с шириной устройства и делает responsive CSS предсказуемым.

Resource hints - это подсказки браузеру о ресурсах и соединениях. `dns-prefetch` заранее резолвит DNS, `preconnect` заранее открывает соединение к origin, `preload` загружает конкретный ресурс текущей страницы с высоким приоритетом, `prefetch` подходит для вероятных будущих переходов. Неправильный hint может ухудшить приоритеты загрузки.

`preload` используют для действительно критичных ресурсов текущей страницы: LCP-image, важный font, critical script/style. Если preload поставить на всё подряд, браузер начнёт качать лишнее раньше нужного и может задержать ресурс, который пользователь должен увидеть первым.

Scripts в `<head>` влияют на parsing и rendering. `defer` загружает script параллельно с HTML, выполняет после парсинга и сохраняет порядок. `async` выполняет script сразу после загрузки и не гарантирует порядок. Основной app-bundle обычно подключают через `defer`, независимую аналитику - через `async`.

SEO зависит не только от meta tags. На индексацию и сниппеты влияют семантический HTML, уникальный title, description, canonical, корректные headings, доступность, быстрый LCP, отсутствие блокирующих ошибок рендера и серверная отдача контента там, где поисковику нужен готовый HTML.

> [!faq]+ Уточнения
> - `meta viewport` делает mobile layout предсказуемым для responsive CSS.
> - `preconnect` готовит соединение, `preload` грузит конкретный ресурс текущей страницы.
> - `prefetch` подходит для вероятного будущего перехода, а не для критичного ресурса текущего экрана.
> - `defer` сохраняет порядок и ждёт parsing, `async` выполняется сразу после загрузки.
> - `description` не гарантирует текст сниппета, но помогает поисковику понять страницу.

#### Пример

```html
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Каталог товаров</title>
    <meta name="description" content="Каталог товаров с фильтрами и поиском." />
    <link rel="canonical" href="https://example.com/catalog" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="preload" as="image" href="/hero.webp" fetchpriority="high" />
    <link rel="stylesheet" href="/styles.css" />
    <script defer src="/app.js"></script>
  </head>
  <body>
    <main>...</main>
  </body>
</html>
```

#### Частые ошибки

- Забывать `meta viewport` и получать сломанную мобильную верстку.
- Делать одинаковый `<title>` на всех страницах.
- Использовать `preload` для большого числа ресурсов.
- Ставить основной app-script без `defer` в `<head>`.
- Не указывать `lang` на документе.
- Считать meta description гарантированным текстом сниппета, а не подсказкой поисковику.

#### Связанные темы

- [[Конспект для подготовки/HTML/HTML]]
- [[Конспект для подготовки/HTML/Семантическая верстка]]
- [[Конспект для подготовки/Web Basics/Critical Render Path]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]
- [[Конспект для подготовки/JavaScript/async и defer]]
- [[Конспект для подготовки/React/SSR и SSG]]

#### Источники

- [MDN: What's in the head?](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content/Webpage_metadata)
- [MDN: Viewport meta tag](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Viewport_meta_element)
- [MDN: HTML script element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script)
- [MDN: rel=preload](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/preload)
- [web.dev: Optimize resource loading](https://web.dev/learn/performance/optimize-resource-loading)
