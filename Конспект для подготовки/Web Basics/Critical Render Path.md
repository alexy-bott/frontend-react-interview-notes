---
aliases:
  - Critical Render Path
  - CRP
  - критический путь рендеринга
  - render-blocking resources
---

#### Быстрый ответ

Critical Render Path (CRP), или критический путь рендеринга, — цепочка работы и ресурсов, от которой зависит первый полезный кадр страницы. Браузер получает HTML, строит DOM, получает необходимые стили и CSSOM, формирует внутреннее представление рендеринга, рассчитывает layout и создаёт кадр.

Внешний CSS с подходящим `media` обычно блокирует рендеринг, потому что позднее правило может изменить вид уже найденного HTML. Обычный классический скрипт без `async` или `defer` блокирует HTML parser, потому что способен изменить ещё разбираемый документ. Приложение с клиентским рендерингом дополнительно зависит от загрузки и выполнения JavaScript, который создаст полезный DOM.

Оптимизация CRP сокращает не «все файлы вообще», а зависимости конкретного первого экрана: время HTML-ответа, блокирующий рендеринг CSS, блокирующие parser скрипты, позднее обнаружение LCP-ресурса и лишнюю работу main thread до кадра.

#### Базовая последовательность

```text
HTML bytes -> DOM
CSS bytes  -> CSSOM
DOM + CSSOM -> rendering representation
             -> layout
             -> paint records
             -> rasterization/composite
             -> first useful frame
```

Это модель зависимостей, а не строго последовательный waterfall. HTML разбирается потоково, preload scanner заранее находит ресурсы, сеть загружает несколько файлов одновременно, а браузер может нарисовать часть страницы до окончания всех запросов.

Детали layout, paint и composite разобраны отдельно в [[Конспект для подготовки/Browser Internals/Rendering pipeline reflow repaint composite]]. В этой карточке важен путь первоначального документа до видимого результата.

#### HTML и обнаружение ресурсов

HTML parser создаёт DOM по мере поступления bytes. Встречая `<link>`, `<script>`, `<img>` и другие элементы, браузер начинает обнаруживать зависимости. Дополнительный preload scanner продолжает искать URL впереди основного parser, когда тот остановлен скриптом.

Ресурс, которого нет в раннем HTML, обнаруживается позже. Например, background image из внешнего CSS станет известен только после загрузки и разбора stylesheet. LCP-image, добавленная JavaScript после hydration, ждёт ещё и bundle execution.

Поэтому главный ресурс первого экрана желательно выразить в исходном HTML или дать браузеру корректную раннюю подсказку. Это не означает preload каждого asset: лишние высокоприоритетные requests конкурируют за сеть.

#### Почему CSS блокирует рендеринг

CSS использует каскад: правило в конце stylesheet способно изменить стиль элемента, найденного раньше. Браузер обычно ждёт CSSOM для подходящих render-blocking stylesheets, чтобы не показать страницу с заведомо промежуточным оформлением.

```html
<link rel="stylesheet" href="/styles.css" />
```

Stylesheet с media query, которая сейчас не совпадает, не блокирует текущий рендер тем же образом, хотя файл всё ещё может загружаться:

```html
<link
  rel="stylesheet"
  href="/print.css"
  media="print"
/>
```

Способы сократить задержку:

- уменьшить CSS, необходимый первому экрану;
- удалить неиспользуемые правила;
- встроить небольшой critical CSS, если измерение оправдывает дополнительную сложность;
- загружать некритичные стили отдельно и без вспышки неправильного layout;
- кэшировать stylesheet и не создавать лишнюю цепочку `@import`.

Inline critical CSS ускоряет первый render только при правильном размере и CSP. Он увеличивает HTML, может дублировать внешний stylesheet и хуже переиспользуется кэшем, поэтому не является универсальным правилом.

#### Как scripts влияют на parser

```html
<script src="/app.js"></script>
```

Classic script без атрибутов останавливает HTML parsing до загрузки и выполнения. Это необходимо, потому что script может вызвать `document.write`, добавить DOM или запросить текущее состояние документа.

```html
<script defer src="/app.js"></script>
```

`defer` загружается параллельно с HTML, выполняется после завершения parsing, сохраняет порядок относительно других deferred scripts и завершается до `DOMContentLoaded`.

```html
<script async src="/analytics.js"></script>
```

`async` загружается параллельно и выполняется сразу после готовности, временно останавливая parser. Порядок нескольких async scripts не гарантирован, поэтому вариант подходит независимому коду.

Module scripts по умолчанию ведут себя как deferred относительно HTML parsing. Атрибут `async` меняет и их порядок выполнения. Скрипт также может ждать уже обнаруженные blocking stylesheets, если браузеру нужно сохранить корректную последовательность и доступ к стилям.

`defer` не уменьшает стоимость выполнения JavaScript. Большой bundle после parsing всё равно занимает main thread и может задержать `DOMContentLoaded`, LCP или интерактивность.

#### Server-rendered и client-rendered HTML

SSR может дать браузеру полезный DOM до загрузки приложения. Hydration затем связывает существующий HTML с React-логикой. Пользователь способен видеть экран раньше, чем он станет полностью интерактивным.

В client-rendered SPA исходный HTML часто содержит только пустой root. Формально браузер может быстро его нарисовать, но полезный контент появится после JavaScript download, parse, execute, data fetch и React render. Поэтому для такого приложения JavaScript и данные входят в практический critical path.

Streaming SSR и Suspense способны отправлять готовые части раньше, но добавляют собственные границы, scripts и hydration work. Результат проверяют измерением, а не только наличием SSR.

#### LCP-ресурс

Для LCP важны четыре части пути:

1. Time to First Byte (TTFB) HTML.
2. Задержка до обнаружения LCP-ресурса.
3. Время его загрузки.
4. Задержка от готовности ресурса до render элемента.

Для главного изображения помогают корректный `src`/`srcset`, размер файла, CDN, раннее присутствие в HTML и иногда `fetchpriority="high"` или preload:

```html
<link
  rel="preload"
  as="image"
  href="/hero.webp"
  fetchpriority="high"
/>

<img
  src="/hero.webp"
  width="1200"
  height="600"
  fetchpriority="high"
  alt="Панель проекта"
/>
```

Preload должен совпадать с реально используемым ресурсом, `as`, CORS mode и responsive image selection. Несовпадение способно привести к двойной загрузке. Если browser и так рано обнаруживает `<img>`, дополнительный preload может не дать выигрыша.

`width` и `height` резервируют aspect ratio и уменьшают layout shift, но не сокращают bytes изображения. Каждая техника решает отдельную часть метрики.

#### Fonts

Текст может стать LCP-элементом. Web font добавляет загрузку и способен задержать отображение или изменить геометрию после замены fallback.

Оптимизация включает subset, современный format, self-hosting/CDN по измерению, разумный `font-display` и подбор fallback metrics. Preload используют только для шрифта, который действительно нужен первому экрану, с правильными `type` и `crossorigin`.

#### Диагностика

1. Записать Navigation trace в Performance и Network без искусственного disable cache как единственного режима.
2. Найти момент HTML response и обнаружения render-blocking ресурсов.
3. Проверить цепочки redirects и request initiators.
4. Найти фактический LCP element и его request priority.
5. Разделить network delay и main-thread render delay.
6. Изменить одну зависимость и повторить измерение на слабом CPU и сети.

Lighthouse помогает найти кандидатов, но waterfall и Performance trace объясняют причинную цепочку. Field LCP подтверждает, что проблема существует у реальных пользователей.

#### Ключевые уточнения

- CRP описывает зависимости первого полезного кадра, а rendering pipeline — этапы создания каждого кадра страницы.
- CSS блокирует рендеринг, когда его результат нужен текущему media context; размер и момент обнаружения stylesheet определяют цену.
- `defer` освобождает HTML parser, но выполнение bundle всё равно занимает основной поток до `DOMContentLoaded`.
- SSR способен показать HTML до hydration, а client-rendered SPA зависит от JavaScript для появления полезного DOM.
- Preload и высокий приоритет помогают только правильно выбранному критичному ресурсу и могут навредить при конкуренции за сеть.

#### Связанные темы

- [[Конспект для подготовки/Browser Internals/Что происходит после ввода URL]]
- [[Конспект для подготовки/Browser Internals/Rendering pipeline reflow repaint composite]]
- [[Конспект для подготовки/Browser Internals/Main thread long tasks и responsiveness]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]
- [[Конспект для подготовки/JavaScript/async и defer]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]
- [[Конспект для подготовки/React/Hydration]]

#### Источники

- [MDN: Critical rendering path](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Critical_rendering_path)
- [web.dev: Optimize Largest Contentful Paint](https://web.dev/articles/optimize-lcp)
- [HTML Living Standard: Scripting](https://html.spec.whatwg.org/multipage/scripting.html)
- [MDN: Preloading content](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/preload)
