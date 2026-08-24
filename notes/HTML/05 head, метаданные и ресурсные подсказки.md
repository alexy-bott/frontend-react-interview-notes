# head, метаданные и ресурсные подсказки

<!-- NOTE-NAV-TOP:START -->
[← Формы](<./04 Формы.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Изображения и адаптивные медиа →](<./06 Изображения и адаптивные медиа.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`<head>` содержит метаданные документа и объявления ресурсов: кодировку, viewport, `<title>`, description, canonical URL, стили, скрипты, иконки и resource hints. Эти данные обычно не являются видимым содержимым страницы, но влияют на разбор HTML, mobile layout, название вкладки, поисковое представление и момент обнаружения ресурсов.

Resource hints позволяют заранее сообщить браузеру о ресурсе или origin, который, вероятно, скоро понадобится. `preconnect` просит раньше установить соединение с origin, `preload` заранее получает конкретный ресурс текущей навигации, `prefetch` предлагает получить ресурс для вероятной будущей навигации, а `modulepreload` заранее получает модуль и помещает его во внутреннее хранилище загруженных модулей (module map).

Подсказка полезна только тогда, когда будущий запрос действительно совпадает с ней. Лишние preconnect и preload расходуют сетевые и системные ресурсы и могут конкурировать с более важной загрузкой.

## Карта темы

| Элемент или механизм | Что делает | Важная граница |
| --- | --- | --- |
| `<!doctype html>` | включает standards mode | находится перед `<html>`, а не внутри `<head>` |
| `<meta charset="utf-8">` | объявляет кодировку HTML | должен целиком находиться в первых 1024 байтах документа |
| `meta viewport` | задаёт параметры layout viewport на мобильных устройствах | не должен лишать пользователя необходимого zoom |
| `<title>` | задаёт название документа | обычно отображается во вкладке и используется внешними системами |
| `meta description` | даёт краткое описание страницы | поисковая система может построить snippet из другого текста |
| `rel="canonical"` | указывает предпочтительный URL | поисковая система может выбрать другой canonical |
| `preconnect` | заранее готовит соединение с origin | имеет смысл только для origin, который скоро понадобится |
| `preload` | заранее получает ресурс текущей навигации | `as`, CORS mode и другие параметры должны совпасть с реальным запросом |
| `prefetch` | предлагает заранее получить ресурс для будущей навигации | браузер может отложить или пропустить такую загрузку |
| `modulepreload` | заранее получает модуль в module map | модуль не выполняется только из-за `modulepreload` |

## Метаданные документа

`<head>` представляет коллекцию метаданных документа. Один из первых элементов обычно объявляет кодировку:

```html
<meta charset="utf-8">
```

HTML Standard требует, чтобы элемент с декларацией кодировки целиком находился в первых 1024 байтах документа. Чем раньше браузер узнает правильную кодировку, тем меньше риск повторного разбора уже прочитанных байтов.

Базовая viewport-настройка для адаптивной страницы выглядит так:

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

Она сообщает мобильному браузеру, что layout viewport должен учитывать ширину устройства. Не следует без необходимости запрещать масштабирование через `user-scalable=no` или ограничивать `maximum-scale` ниже значения, позволяющего пользователю увеличить содержимое.

`<title>` задаёт название документа. `meta name="description"` может использоваться поисковой системой как описание результата, но не гарантирует конкретный snippet. Например, Google в первую очередь формирует snippet из содержимого страницы и использует meta description только когда она лучше описывает результат.

`rel="canonical"` указывает предпочтительный URL для текущего документа:

```html
<link rel="canonical" href="https://example.com/orders">
```

Для Google это сильный сигнал canonicalization, но не безусловная команда: поисковая система может выбрать другой URL, если остальные сигналы указывают на него.

## Стили и скрипты в `head`

Применимый `<link rel="stylesheet">` обычно участвует в блокировке первого рендеринга, потому что браузеру нужны стили для корректного отображения найденного содержимого.

Обычный внешний classic script без `async` и `defer` может остановить HTML-парсер до загрузки и выполнения скрипта.

```html
<script src="/legacy.js"></script>
```

`defer` позволяет загружать classic script параллельно с HTML и выполнить его после завершения parsing, сохраняя порядок между deferred scripts:

```html
<script defer src="/app.js"></script>
```

`async` также загружается параллельно, но выполняется после готовности без гарантии порядка относительно других async scripts:

```html
<script async src="/analytics.js"></script>
```

Модульный скрипт без `async` уже имеет отложенную модель выполнения, поэтому дополнительный `defer` ему не нужен:

```html
<script type="module" src="/app.js"></script>
```

Подробные различия вынесены в заметку [«async и defer»](<../JavaScript/33 async и defer.md>).

## Resource hints

### `preconnect`

```html
<link rel="preconnect" href="https://static.example-cdn.com" crossorigin>
```

`preconnect` сообщает браузеру, что соединение с указанным origin (схема, host и port), вероятно, скоро понадобится. User agent может выполнить полный или частичный handshake либо пропустить предварительное соединение, если ресурсов устройства или сети недостаточно.

Поэтому preconnect не является гарантией уже готового соединения. Большой список таких подсказок может расходовать ресурсы без пользы.

### `preload`

```html
<link
  rel="preload"
  href="/fonts/interface.woff2"
  as="font"
  type="font/woff2"
  crossorigin
>
```

`preload` заранее получает ресурс, который нужен текущей навигации. Чтобы браузер смог переиспользовать результат, будущий запрос должен совпасть по URL, destination, request mode и credentials mode. Для font preload это обычно означает корректные `as="font"`, `type` и `crossorigin`.

Сам `preload` не применяет ресурс. Например, preloaded stylesheet всё равно должен быть подключён как stylesheet, а preloaded font — реально запрошен из CSS.

### `prefetch` и `modulepreload`

`prefetch` предназначен для ресурса или same-site документа, который, вероятно, понадобится при будущей навигации. Браузер может отложить такой запрос, чтобы не мешать ресурсам текущей страницы.

```html
<link rel="prefetch" href="/next-page-data.json">
```

`modulepreload` предназначен для JavaScript modules. Он заранее получает модуль и помещает результат в module map — внутреннее хранилище уже загруженных модулей; браузер также может заранее получить часть его зависимостей.

```html
<link rel="modulepreload" href="/app.js">
```

Это подготавливает модуль к последующему использованию, но само по себе не выполняет его.

## Пример

```html
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Заказы — Панель управления</title>
    <meta
      name="description"
      content="Поиск, фильтрация и обработка заказов."
    >
    <link rel="canonical" href="https://example.com/orders">

    <link rel="preconnect" href="https://static.example-cdn.com" crossorigin>
    <link
      rel="preload"
      href="https://static.example-cdn.com/fonts/interface.woff2"
      as="font"
      type="font/woff2"
      crossorigin
    >

    <link rel="stylesheet" href="/styles.css">
    <script type="module" src="/app.js"></script>
  </head>
  <body>...</body>
</html>
```

Font preload оправдан только если этот файл действительно нужен достаточно рано, чтобы ранняя загрузка дала выигрыш. Module script не требует `defer`, потому что его обычная модель выполнения уже отложена относительно HTML parsing.

## Где применяется во frontend

- При настройке базового HTML-документа: кодировка, viewport и title должны быть известны браузеру до основной части страницы.
- При SEO-настройке: description и canonical помогают описать страницу и предпочитаемый URL, но поисковая система принимает окончательное решение сама.
- При подключении CSS и JavaScript: расположение и атрибуты ресурсов влияют на HTML parsing и первый рендер.
- При оптимизации LCP и шрифтов: `preload` используют только для действительно критичного ресурса, который иначе обнаружился бы поздно.
- При работе с внешним CDN или API: `preconnect` может убрать часть задержки установления соединения, если запрос действительно скоро произойдёт.
- При code splitting: `modulepreload` может заранее подготовить модуль до момента его выполнения.

## Ключевые уточнения

- `<head>` содержит метаданные и объявления ресурсов, а не основное видимое содержимое страницы.
- Декларация `<meta charset="utf-8">` должна целиком находиться в первых 1024 байтах HTML.
- `defer`, `async` и module script имеют разные правила выполнения; `type="module"` уже отложен по умолчанию.
- `preload` относится к текущей навигации, а `prefetch` — к вероятному будущему использованию.
- Preload переиспользуется только при совместимых параметрах будущего запроса.
- `preconnect` и другие resource hints являются оптимизационными подсказками и не должны добавляться массово без реальной потребности.
- Meta description и canonical влияют на сигналы для поисковых систем, но не гарантируют конкретный snippet или выбранный canonical URL.

## Связанные темы

- [HTML](<./01 HTML.md>)
- [Изображения и адаптивные медиа](<./06 Изображения и адаптивные медиа.md>)
- [Критический путь рендеринга (Critical Render Path)](<../Основы веб-платформы/20 Критический путь рендеринга (Critical Render Path).md>)
- [Core Web Vitals](<../Основы веб-платформы/21 Core Web Vitals.md>)
- [async и defer](<../JavaScript/33 async и defer.md>)
- [SSR и SSG](<../React/27 SSR и SSG.md>)

## Источники

- [HTML Standard: Document metadata](https://html.spec.whatwg.org/multipage/semantics.html#semantics)
- [HTML Standard: Link types](https://html.spec.whatwg.org/multipage/links.html)
- [HTML Standard: Scripting](https://html.spec.whatwg.org/multipage/scripting.html)
- [Google Search Central: Canonicalization](https://developers.google.com/search/docs/crawling-indexing/canonicalization)
- [Google Search Central: Control your snippets](https://developers.google.com/search/docs/appearance/snippet)
- [W3C WAI: Meta viewport allows for zoom](https://www.w3.org/WAI/standards-guidelines/act/rules/b4f0c3/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Формы](<./04 Формы.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Изображения и адаптивные медиа →](<./06 Изображения и адаптивные медиа.md>)
<!-- NOTE-NAV-BOTTOM:END -->
