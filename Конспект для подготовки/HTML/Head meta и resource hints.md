---
aliases:
  - HTML head
  - meta viewport
  - resource hints
  - SEO meta
---

#### Быстрый ответ

`<head>` содержит metadata и связи документа с внешними ресурсами: кодировку, viewport, `<title>`, description, canonical URL, stylesheets, scripts, icons и resource hints. Эти данные влияют на разбор документа, mobile layout, название вкладки, поисковое представление и порядок обнаружения ресурсов, хотя большая их часть не отображается как содержимое страницы.

Resource hints сообщают браузеру о вероятно важных соединениях или файлах. `preconnect` заранее готовит соединение с origin, `preload` рано загружает конкретный ресурс текущей страницы, а `prefetch` предлагает ресурс для возможного будущего перехода. Подсказки конкурируют за сеть, поэтому их добавляют после проверки waterfall и с корректными `as`, `type` и CORS-настройками.

#### Ключевая схема

| Элемент | Назначение | Существенная граница |
| --- | --- | --- |
| `<!doctype html>` | включает standards mode | находится перед `<html>`, а не внутри `<head>` |
| `<meta charset>` | задаёт декодирование документа | размещается как можно раньше |
| `meta viewport` | связывает layout viewport с устройством | не следует запрещать user zoom |
| `<title>` | имя документа и вкладки | уникален и отражает текущую страницу |
| `description` | описание содержимого | поисковик может выбрать другой snippet |
| `canonical` | указывает предпочтительный URL | является сигналом, а не безусловной командой |
| `preconnect` | заранее создаёт соединение | нужен только важному внешнему origin |
| `preload` | начинает загрузку известного ресурса | не выполняет и не применяет ресурс сам по себе |

#### Базовая модель

Browser начинает читать `<head>` до основного содержимого, поэтому порядок влияет на ранние решения. `meta charset="utf-8"` помещают в начало документа, `meta viewport` задаёт ожидаемую mobile-геометрию, а stylesheet и scripts формируют critical rendering path.

`<link rel="stylesheet">` обычно блокирует render, пока CSS не загружен и не разобран. Обычный classic script без `async`/`defer` блокирует HTML parser на загрузку и выполнение. `defer` загружает внешний classic script параллельно и выполняет после parsing в порядке документа; `async` выполняет после загрузки без гарантии порядка относительно других async scripts. Module script откладывается по умолчанию подобно `defer`.

Resource hint не меняет смысл ресурса. Preloaded stylesheet всё ещё нужно подключить как stylesheet, а preloaded font должен реально использоваться CSS. Браузер может не получить пользы от hint, если будущий запрос отличается по URL, destination или CORS mode.

#### Развернутый ответ

**Viewport.** Базовое `width=device-width, initial-scale=1` делает CSS viewport соответствующим ширине устройства. `user-scalable=no` и жёсткое ограничение `maximum-scale` мешают увеличению и создают проблему доступности.

**Metadata для поиска.** `<title>` и description должны описывать конкретную страницу, а `canonical` помогает объединять дублирующие URL. Ни один тег не гарантирует позицию или точный snippet: поисковая система учитывает доступный контент, HTTP-ответ, ссылки и собственные правила.

**Preconnect.** Подсказка заранее выполняет DNS, TCP и при необходимости TLS setup для origin. Она экономит время только если соединение скоро понадобится. Большой список preconnect открывает лишние sockets; для менее уверенного случая существует более дешёвый `dns-prefetch`.

**Preload.** Указывает ресурс текущей навигации и его destination через `as`. Font обычно требует `as="font"`, MIME `type` и `crossorigin`, включая многие same-origin случаи из-за CORS-режима font fetch. Responsive image preload согласуют с `imagesrcset` и `imagesizes`, чтобы не загрузить неподходящий candidate.

**Prefetch.** Предназначен для вероятного будущего использования и имеет меньшую срочность, но браузер сам решает, выполнять ли подсказку. Для модулей текущей страницы существует `modulepreload`, который подготавливает module script и его зависимости в соответствии с browser implementation.

#### Пример

```html
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Заказы - Панель управления</title>
    <meta
      name="description"
      content="Поиск, фильтрация и обработка заказов."
    >
    <link rel="canonical" href="https://example.com/orders">

    <link rel="preconnect" href="https://static.example-cdn.com" crossorigin>
    <link
      rel="preload"
      href="/fonts/interface-latin.woff2"
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

Font preload оправдан только если этот точный файл используется на первом экране. Module script не требует дополнительного `defer`; его зависимостям можно дать `modulepreload` только после измерения реальной задержки.

#### Ключевые уточнения

- Metadata описывает документ и влияет на browser/tooling, но не заменяет содержательный и семантический HTML.
- `defer`, `async` и module script имеют разные правила выполнения; выбор зависит от порядка и зависимости от DOM.
- `preload` запускает получение ресурса, но ресурс всё равно нужно применить обычным механизмом.
- Resource hint приносит пользу только при совпадении с будущим запросом и реальной критичности; лишние hints расходуют сеть.
- Viewport configuration должна поддерживать responsive layout, не запрещая пользователю масштабирование.

#### Связанные темы

- [[Конспект для подготовки/HTML/HTML]]
- [[Конспект для подготовки/HTML/Изображения и responsive media]]
- [[Конспект для подготовки/Web Basics/Critical Render Path]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]
- [[Конспект для подготовки/JavaScript/async и defer]]
- [[Конспект для подготовки/React/SSR и SSG]]

#### Источники

- [WHATWG HTML: Document metadata](https://html.spec.whatwg.org/multipage/semantics.html#semantics)
- [MDN: What's in the head?](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content/Webpage_metadata)
- [MDN: script element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script)
- [MDN: rel=preload](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/preload)
- [web.dev: Resource hints](https://web.dev/learn/performance/resource-hints)
