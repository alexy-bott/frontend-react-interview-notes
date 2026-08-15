# CORS, CSP и границы безопасности браузера

<!-- NOTE-NAV-TOP:START -->
[← Хранение токенов — XSS, CSRF и компромиссы](<./02 Хранение токенов — XSS, CSRF и компромиссы.md>) · [↑ Безопасность](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Цепочка поставок, секреты и сторонние скрипты →](<./04 Цепочка поставок, секреты и сторонние скрипты.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Same-origin policy, CORS и CSP регулируют разные browser security boundaries, то есть разные границы безопасности браузера.

| Механизм | Что контролирует | Чего не контролирует |
| --- | --- | --- |
| Same-origin policy, или SOP | Может ли JavaScript одного origin читать данные и объекты другого origin | Права пользователя на сервере |
| CORS | Может ли JavaScript прочитать cross-origin HTTP-response | Возможность вызвать API из `curl`, backend или mobile application |
| CSP | Какие scripts и ресурсы может загрузить страница и куда она может подключаться | Корректность authorization и безопасную обработку данных |
| SameSite и CSRF-защита | Когда browser отправляет автоматически прикладываемые cookies | Доступ JavaScript к cross-origin response |
| HTTPS и HSTS | Используется ли защищённое сетевое соединение | XSS, CSRF и ошибки проверки прав |

Origin, или источник документа, для обычного HTTP(S)-адреса определяется сочетанием:

```text
origin = scheme + host + effective port
```

Например:

```text
https://app.example.com
https://api.example.com
```

имеют разные origins, потому что у них разные hosts.

Same-origin policy по умолчанию не позволяет JavaScript страницы свободно читать DOM, storage и HTTP-ответы другого origin.

CORS позволяет server ослабить это ограничение и явно разрешить выбранному frontend-origin прочитать HTTP-response.

CSP ограничивает возможности самой страницы:

- откуда разрешено загружать JavaScript;
- к каким API и WebSocket endpoints можно подключаться;
- кто может встроить страницу в iframe;
- куда разрешено отправлять HTML forms.

CORS не является authentication или authorization. Даже правильно настроенный CORS не освобождает API от проверки:

- кто выполняет запрос;
- имеет ли пользователь право на действие;
- корректны ли переданные данные;
- не является ли запрос CSRF-атакой.

CSP не исправляет XSS автоматически. Она уменьшает вероятность выполнения внедрённого кода и ограничивает часть его возможностей, но приложение всё равно должно безопасно работать с недоверенными данными.

## Границы origin

Для обычного HTTP(S)-адреса origin состоит из:

```text
scheme + host + effective port
```

**Scheme**, или схема, определяет используемый протокол:

```text
http
https
```

**Host** — имя сервера:

```text
example.com
api.example.com
```

**Effective port**, или фактический порт, — явно указанный порт либо порт по умолчанию для схемы:

```text
http  → 80
https → 443
```

Разные origins:

```text
http://example.com
https://example.com
```

Различается scheme.

```text
https://app.example.com
https://api.example.com
```

Различается host.

```text
https://example.com
https://example.com:8443
```

Различается port.

Адреса:

```text
https://example.com
https://example.com:443
```

имеют один effective port и относятся к одному origin.

Path, query и fragment на origin не влияют:

```text
https://example.com/users
https://example.com/orders?page=2#active
```

Оба адреса относятся к origin:

```text
https://example.com
```

### Origin и site — не одно и то же

Origin является строгой границей и учитывает scheme, host и port.

Site является более широкой группировкой, которую браузер использует, например, для правил `SameSite` cookies.

Упрощённо:

```text
https://app.example.com
https://api.example.com
```

обычно являются:

```text
cross-origin
```

потому что hosts различаются, но:

```text
same-site
```

потому что относятся к одному основному домену `example.com` и используют одинаковую схему `https`.

Поэтому возможна ситуация:

- cookie считается same-site и отправляется;
- JavaScript-запрос остаётся cross-origin;
- для чтения response требуется CORS.

### Что ограничивает same-origin policy

Same-origin policy, или политика одного источника, мешает коду одного origin произвольно получать доступ к данным другого origin.

Она в первую очередь ограничивает cross-origin reads, то есть чтение чужих данных.

Например, JavaScript страницы:

```text
https://evil.example
```

не должен свободно прочитать:

```text
https://bank.example/account
```

иначе любой сайт мог бы получать личные данные пользователя из других открытых сессий.

Однако browser разрешает некоторые cross-origin-действия.

Упрощённо их можно разделить на три группы:

| Действие | Типичное поведение |
| --- | --- |
| Cross-origin read | Обычно ограничено |
| Cross-origin write | Часто разрешено |
| Cross-origin embed | Часто разрешено с дополнительными правилами |

### Cross-origin writes

Cross-origin write означает отправку данных или запуск навигации на другой origin.

Например, браузер позволяет:

- перейти по внешней ссылке;
- отправить обычную HTML form;
- открыть другой сайт через `window.location`;
- отправить часть запросов без CORS preflight.

```html
<form
  method="post"
  action="https://bank.example/transfer"
>
  <input name="amount" value="1000">
</form>
```

Same-origin policy не гарантирует, что такой запрос не будет отправлен.

Она может запретить атакующей странице прочитать response, но операция на сервере уже могла выполниться.

Именно поэтому SOP и CORS сами по себе не защищают от CSRF.

### Cross-origin embeds

Браузер разрешает встраивать некоторые ресурсы другого origin:

```html
<img src="https://cdn.example/image.png">

<script src="https://cdn.example/library.js"></script>

<iframe src="https://widget.example"></iframe>
```

Правила доступа зависят от типа ресурса.

Например, страницу можно встроить в cross-origin iframe, но parent page не получает свободный доступ к DOM этого iframe.

Cross-origin script после загрузки выполняется с правами страницы, которая его подключила.

Это важное отличие:

```text
script загружен с vendor.example
→ выполняется внутри app.example
→ получает доступ к DOM и browser APIs app.example
```

Поэтому подключение third-party script означает передачу ему значительной части полномочий страницы.

### Cross-origin reads

JavaScript обычно не может:

- прочитать DOM cross-origin iframe;
- получить содержимое чужого `localStorage`;
- прочитать body cross-origin Fetch response без CORS;
- получить большинство свойств cross-origin `Window`.

При этом некоторые ограниченные операции с cross-origin `Window` разрешены, например отправка сообщения через `postMessage`.

### Почему `no-cors` не обходит SOP

Режим:

```ts
const response = await fetch(url, {
  mode: "no-cors",
});
```

не отключает same-origin policy и не открывает JavaScript доступ к чужому API.

Frontend получает opaque response, или непрозрачный ответ.

Из него нельзя нормально прочитать:

- HTTP status;
- response body;
- большинство response headers.

```ts
const response = await fetch(
  "https://api.example.com/data",
  {
    mode: "no-cors",
  },
);

console.log(response.type); // "opaque"
```

`no-cors` используется браузером для ограниченных типов запросов, но не является способом обойти CORS.

### Cross-origin обмен через `postMessage`

Для намеренного обмена данными между:

- parent page и iframe;
- страницей и popup;
- двумя окнами;

используют `window.postMessage()`.

SOP запрещает напрямую читать DOM другого origin, но `postMessage` создаёт явный канал передачи структурированных сообщений.

Отправитель указывает данные и ожидаемый origin получателя:

```ts
const widgetOrigin = "https://widget.example";

iframe.contentWindow?.postMessage(
  {
    type: "profile.request",
    version: 1,
  },
  widgetOrigin,
);
```

`targetOrigin` определяет, какому origin разрешено получить сообщение.

Если target window к моменту доставки находится на другом origin, browser отбросит сообщение.

Для чувствительных данных нельзя без необходимости использовать:

```text
*
```

Потому что сообщение сможет получить документ с любым текущим origin.

Получатель проверяет три вещи:

1. `event.origin` — origin отправителя.
2. `event.source` — конкретное окно, отправившее сообщение.
3. `event.data` — структуру и содержимое сообщения.

```ts
const appOrigin = "https://app.example.com";

window.addEventListener("message", (event) => {
  if (event.origin !== appOrigin) {
    return;
  }

  if (event.source !== window.parent) {
    return;
  }

  const message = event.data;

  if (
    typeof message !== "object" ||
    message === null ||
    message.type !== "profile.request" ||
    message.version !== 1
  ) {
    return;
  }

  sendProfile();
});
```

Проверка только `event.origin` может быть недостаточной, если с одного разрешённого origin открыто несколько окон.

`event.source` позволяет убедиться, что сообщение пришло от ожидаемого окна.

`event.data` является внешними данными. TypeScript type не проверяет данные во время выполнения, поэтому перед использованием нужна runtime validation, то есть фактическая проверка структуры.

При загрузке iframe parent page может отправить сообщение слишком рано, когда iframe ещё не установил обработчик.

Для этого используют readiness handshake:

```text
iframe загрузился
→
iframe отправил сообщение ready
→
parent проверил origin и source
→
parent начал отправлять данные
```

## CORS

CORS (Cross-Origin Resource Sharing) — механизм, через который server разрешает browser JavaScript одного origin читать HTTP-response другого origin.

CORS не открывает сервер для запросов вообще. Он определяет, получит ли frontend-код доступ к response.

Рассмотрим:

```text
Frontend:
https://app.example.com

API:
https://api.example.com
```

Origins различаются, поэтому запрос является cross-origin.

Frontend выполняет:

```ts
const response = await fetch(
  "https://api.example.com/users",
);
```

Браузер добавляет request header:

```http
Origin: https://app.example.com
```

Server разрешает этому origin читать response:

```http
Access-Control-Allow-Origin: https://app.example.com
```

Браузер получает response, проверяет CORS headers и только после успешной проверки открывает response JavaScript-коду.

Упрощённо:

```text
JavaScript вызывает fetch
→
browser добавляет Origin
→
server возвращает CORS headers
→
browser проверяет policy
→
JavaScript получает или не получает response
```

### Почему CORS является browser-механизмом

CORS соблюдает browser.

Он не ограничивает:

- `curl`;
- Postman;
- mobile application;
- desktop application;
- другой backend;
- самостоятельно написанный HTTP client.

Такой клиент может отправить запрос независимо от CORS headers.

Поэтому API всегда само проверяет:

- authentication — кто выполняет запрос;
- authorization — имеет ли пользователь право;
- validation — допустимы ли входные данные;
- rate limit — не превышена ли допустимая частота;
- CSRF — не используется ли автоматически приложенная cookie злоумышленником.

### Запросы без preflight

Не каждый cross-origin request требует предварительной проверки.

Browser может сразу отправить request, если он соответствует ограниченному безопасному для совместимости набору методов, headers и content types.

Такой запрос часто называют simple request, хотя в Fetch Standard используется понятие CORS-safelisted request.

Типичные разрешённые methods:

```text
GET
HEAD
POST
```

Разрешены только определённые request headers и ограниченные значения `Content-Type`, например:

```text
application/x-www-form-urlencoded
multipart/form-data
text/plain
```

Упрощённый поток:

```text
actual request
→
server response
→
CORS-проверка response
```

Важно: safelisted означает не «безопасный для бизнеса», а «совместимый с запросами, которые Web исторически умел отправлять через HTML forms».

Такой `POST` может изменить server state.

Следовательно:

```text
нет preflight
≠
операция безопасна
```

и:

```text
нет preflight
≠
CSRF невозможен
```

### Preflight

Preflight, или предварительный CORS-запрос, — автоматический `OPTIONS`, которым browser спрашивает server, разрешено ли отправить основной запрос с указанными method и headers.

Например, frontend хочет отправить:

```http
PATCH /users/42
Content-Type: application/json
Authorization: Bearer <token>
```

Такой request не соответствует CORS safelist.

Сначала browser отправляет:

```http
OPTIONS /users/42
Origin: https://app.example.com
Access-Control-Request-Method: PATCH
Access-Control-Request-Headers: authorization, content-type
```

Headers означают:

- `Origin` — какой frontend хочет выполнить запрос;
- `Access-Control-Request-Method` — какой method будет у основного запроса;
- `Access-Control-Request-Headers` — какие дополнительные headers он содержит.

Server отвечает:

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: PATCH
Access-Control-Allow-Headers: Authorization, Content-Type
```

После успешной проверки browser отправляет основной request.

```text
preflight OPTIONS
→
CORS-разрешение
→
actual PATCH
→
CORS-проверка actual response
```

Успешный preflight означает только:

```text
server сообщает browser,
что понимает и разрешает такой cross-origin request
```

Preflight не проверяет:

- пользователя;
- его бизнес-права;
- request body;
- существование ресурса;
- допустимость изменения;
- баланс счёта;
- принадлежность заказа.

Все эти проверки выполняются при обработке основного запроса.

Preflight обычно не содержит пользовательскую cross-origin cookie. Поэтому нельзя проектировать CORS так, чтобы `OPTIONS` требовал обычную пользовательскую аутентификацию.

### Кеширование preflight

Server может разрешить browser временно сохранить успешный результат preflight:

```http
Access-Control-Max-Age: 600
```

Значение указывается в секундах.

В течение этого времени browser может не отправлять повторный `OPTIONS` для подходящего сочетания:

- origin;
- URL;
- method;
- request headers.

Preflight cache является специальным внутренним кешем браузера и отличается от обычного HTTP cache.

Browser может ограничить максимальное время хранения независимо от значения server.

### Основные CORS response headers

**`Access-Control-Allow-Origin`**

Определяет origin, которому разрешено читать response:

```http
Access-Control-Allow-Origin: https://app.example.com
```

Либо разрешает любой origin в подходящем запросе без credentials:

```http
Access-Control-Allow-Origin: *
```

Header не принимает список origins:

```http
Access-Control-Allow-Origin:
  https://a.example, https://b.example
```

Такой формат некорректен.

Если server поддерживает несколько frontend origins, он:

1. Получает `Origin`.
2. Сравнивает его со строгим allowlist.
3. Возвращает одно совпавшее значение.

Нельзя без проверки отражать любой входящий `Origin`.

Опасная логика:

```text
получили Origin
→
безусловно вернули его в Access-Control-Allow-Origin
```

фактически разрешает любому сайту читать response.

Сравнивать нужно полный origin:

```text
scheme + host + port
```

Проверка:

```ts
origin.endsWith("example.com")
```

небезопасна, потому что может разрешить:

```text
https://notexample.com
https://evil-example.com
```

**`Access-Control-Allow-Methods`**

Используется в preflight response и сообщает разрешённые methods:

```http
Access-Control-Allow-Methods:
  GET, POST, PATCH, DELETE
```

Это CORS-разрешение для browser, а не замена server-side routing и authorization.

**`Access-Control-Allow-Headers`**

Сообщает, какие дополнительные request headers разрешены:

```http
Access-Control-Allow-Headers:
  Authorization, Content-Type, X-Request-Id
```

Если frontend хочет передать header, которого нет в разрешённом списке, preflight не пройдёт.

**`Access-Control-Allow-Credentials`**

Разрешает frontend-коду получить credentialed response:

```http
Access-Control-Allow-Credentials: true
```

Credentials — данные, которыми browser подтверждает контекст пользователя, например cookies или HTTP authentication information.

Значение должно быть:

```text
true
```

При credentialed request недостаточно только этого header: нужен также точный `Access-Control-Allow-Origin`.

**`Access-Control-Expose-Headers`**

Даже после успешного CORS JavaScript по умолчанию видит только ограниченный набор response headers.

Чтобы открыть собственный header:

```http
X-Request-Id: 01HXYZ
Access-Control-Expose-Headers: X-Request-Id
```

Frontend сможет прочитать:

```ts
response.headers.get("X-Request-Id");
```

`Set-Cookie` нельзя открыть JavaScript-коду через `Access-Control-Expose-Headers`.

Browser обрабатывает его самостоятельно, а Fetch API не позволяет прочитать его как обычный response header.

**`Access-Control-Max-Age`**

Задаёт время хранения успешного preflight result:

```http
Access-Control-Max-Age: 600
```

**`Vary: Origin`**

Если server возвращает разный `Access-Control-Allow-Origin` в зависимости от request `Origin`, response должен сообщить HTTP-кешу, что это разные варианты:

```http
Vary: Origin
```

Без `Vary` shared cache может:

- вернуть CORS header для другого frontend;
- отдать response без нужного разрешения;
- в худшем случае смешать варианты, рассчитанные на разные origins.

### Credentialed CORS и cookies

По умолчанию cross-origin `fetch` не отправляет cookies в режиме `include`.

Для credentialed request frontend указывает:

```ts
const response = await fetch(
  "https://api.example.com/me",
  {
    credentials: "include",
  },
);
```

Server возвращает:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
Vary: Origin
```

При credentials нельзя использовать:

```http
Access-Control-Allow-Origin: *
```

Нужен точный разрешённый origin.

`credentials: "include"` не заставляет browser отправить любую существующую cookie.

Cookie дополнительно должна соответствовать своим атрибутам:

- `Domain` или host-only scope;
- `Path`;
- `Secure`;
- `SameSite`;
- срок действия;
- partitioning;
- browser privacy policy.

Например, cookie с:

```text
SameSite=Strict
```

может не отправиться в cross-site context, даже если Fetch использует `credentials: "include"`.

CORS и cookie policy отвечают на разные вопросы:

```text
Cookie policy
→ будет ли credential отправлен

CORS
→ сможет ли JavaScript прочитать response
```

### CORS и CSRF

CORS не является CSRF-защитой.

CSRF использует тот факт, что browser может автоматически приложить cookie к запросу.

Атакующему часто не нужно читать response. Ему достаточно вызвать изменяющую операцию.

Защита от CSRF может включать:

- `SameSite` cookies;
- CSRF token;
- проверку `Origin`;
- проверку `Referer` в подходящей модели;
- запрет изменяющих операций через `GET`;
- повторное подтверждение чувствительной операции;
- корректную проверку прав на server.

Preflight может усложнить часть атак, но его нельзя считать единственной CSRF-защитой.

### CORS errors

Для JavaScript CORS failure обычно выглядит как общая network error.

Frontend может не получить:

- HTTP status;
- body;
- response headers;
- точную server-side-причину.

Но возможны два принципиально разных сценария.

**Preflight не прошёл**

```text
OPTIONS отправлен
→
CORS-разрешение не получено
→
actual request не отправлен
```

В этом случае основная операция обычно не выполнялась.

**Actual request был обработан**

```text
actual request отправлен
→
server выполнил операцию
→
response не прошёл CORS-проверку
→
JavaScript получил network error
```

В этом случае данные уже могли измениться.

Поэтому нельзя автоматически повторять неидемпотентный request только потому, что frontend получил CORS/network error.

Например, повторная отправка может дважды:

- создать заказ;
- провести платёж;
- отправить сообщение;
- запустить фоновую задачу.

Для критичных операций дополнительно используют idempotency key, то есть уникальный идентификатор операции, по которому server распознаёт повтор.

### Диагностика CORS

При диагностике проверяют:

1. Origin страницы.
2. Полный URL API.
3. Был ли отправлен preflight `OPTIONS`.
4. Какие method и headers запросил browser.
5. CORS headers preflight response.
6. CORS headers actual response.
7. Redirects.
8. Настройки reverse proxy, gateway и CDN.
9. Режим `credentials`.
10. Атрибуты cookie.
11. `Vary: Origin`.
12. Добавляются ли CORS headers к error responses.

Важно проверять response в DevTools Network и сообщения browser Console.

CORS headers должны добавляться не только к успешному `200`, но и к `401`, `403`, `404`, `422` и другим ответам, если frontend должен иметь возможность прочитать ошибку.

При этом server не должен раскрывать чужому origin чувствительные сведения только ради удобной диагностики.

### CORS и WebSocket

WebSocket не использует обычный CORS protocol и не проверяет `Access-Control-Allow-Origin`.

Во время browser WebSocket handshake передаётся:

```http
Origin: https://app.example.com
```

WebSocket server самостоятельно сравнивает его с allowlist.

Это особенно важно при cookie-аутентификации: иначе вредоносная страница может попытаться открыть соединение от имени уже вошедшего пользователя.

Проверка `Origin` не заменяет authentication и authorization. Небраузерный client способен самостоятельно сформировать этот header.

## CSP

CSP (Content Security Policy) — политика, которая ограничивает возможности документа и загруженного в него кода.

Основная цель CSP — уменьшить вероятность выполнения внедрённого JavaScript и ограничить направления, в которых страница может загружать или отправлять данные.

Например, CSP может определить:

- откуда разрешено загружать scripts;
- какие inline scripts можно выполнить;
- к каким API и WebSocket endpoints можно подключаться;
- откуда разрешены изображения, стили и шрифты;
- кто может встроить страницу в iframe;
- куда можно отправить HTML form.

CSP предпочтительно передают через HTTP response header:

```http
Content-Security-Policy: default-src 'self'
```

Policy можно частично передать через `<meta>`:

```html
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'self'"
>
```

Но HTTP header надёжнее:

- действует до обработки HTML;
- защищает ресурсы, загружаемые в начале документа;
- поддерживает больше directives;
- позволяет использовать report-only policy.

Например, `frame-ancestors` не работает из CSP, переданной через `<meta>`.

### Source expressions

В directives используются source expressions, то есть правила, описывающие разрешённые источники.

Частые значения:

| Значение | Смысл |
| --- | --- |
| `'self'` | текущий origin |
| `'none'` | ничего не разрешено |
| `https:` | любой HTTPS-origin |
| `https://cdn.example.com` | конкретный origin |
| `'nonce-...'` | script или style с подходящим одноразовым значением |
| `'sha256-...'` | содержимое с подходящим cryptographic hash |

`'self'` означает именно origin, а не весь site.

Если страница открыта на:

```text
https://app.example.com
```

то `'self'` не включает автоматически:

```text
https://api.example.com
```

### Основные CSP directives

| Directive | Что ограничивает |
| --- | --- |
| `default-src` | источник по умолчанию для многих типов загружаемых ресурсов |
| `script-src` | JavaScript и inline script execution |
| `style-src` | CSS и inline styles |
| `img-src` | изображения |
| `font-src` | шрифты |
| `media-src` | audio и video |
| `connect-src` | Fetch, XHR, WebSocket, EventSource и Beacon |
| `worker-src` | Worker и Service Worker scripts |
| `frame-src` | какие iframe может загрузить текущая страница |
| `frame-ancestors` | кто может встроить текущую страницу |
| `form-action` | куда разрешено отправлять HTML forms |
| `object-src` | plugin content через `object` и `embed` |
| `base-uri` | допустимые значения элемента `<base>` |

Пример:

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self';
  img-src 'self' https://cdn.example.com data:;
  font-src 'self' https://fonts.example.com;
  connect-src 'self' https://api.example.com wss://realtime.example.com;
  frame-src https://widget.example;
  frame-ancestors 'none';
  form-action 'self';
  object-src 'none';
  base-uri 'none'
```

Эта policy:

- по умолчанию разрешает ресурсы текущего origin;
- разрешает изображения с CDN;
- разрешает обращения к API и WebSocket;
- разрешает загрузить определённый iframe;
- запрещает другим страницам встраивать текущую страницу;
- разрешает forms только на текущий origin;
- запрещает plugin content;
- запрещает изменение base URL.

### `default-src`

`default-src` является fallback, то есть правилом по умолчанию, для многих directives загрузки.

```http
Content-Security-Policy:
  default-src 'self'
```

Если отдельно не указан `img-src`, изображения будут проверяться по `default-src`.

Но `default-src` не заменяет некоторые directives.

Например, отдельно задают:

```text
frame-ancestors
form-action
base-uri
```

Policy:

```http
Content-Security-Policy:
  default-src 'none'
```

сама по себе не запрещает другим сайтам встраивать страницу.

Для этого нужен:

```http
frame-ancestors 'none'
```

### `script-src`

`script-src` управляет загрузкой и выполнением JavaScript.

Простая policy:

```http
Content-Security-Policy:
  script-src 'self'
```

разрешает scripts текущего origin.

Но `'self'` не гарантирует безопасность, если на текущий origin можно загрузить пользовательский `.js` либо существует endpoint, возвращающий управляемый атакующим JavaScript.

Строгая script policy чаще строится на nonce или hash.

### Nonce

Nonce — случайное одноразовое значение, создаваемое server для конкретного HTML-response.

Header:

```http
Content-Security-Policy:
  script-src 'nonce-random-value'
```

HTML:

```html
<script nonce="random-value">
  startApplication();
</script>
```

Browser выполнит script только при совпадении nonce.

Nonce должен быть:

- создан криптографически безопасным генератором;
- достаточно длинным;
- непредсказуемым;
- новым для каждого response;
- добавлен только к доверенным scripts.

Нельзя использовать постоянный nonce:

```text
nonce="frontend"
```

Если атакующий знает значение, он сможет добавить его к внедрённому script.

Server-side template также не должен автоматически копировать nonce на HTML, полностью управляемый пользователем.

Nonce обычно удобен для HTML, который формируется динамически на server.

### Hash

Hash разрешает script с точно определённым содержимым.

Policy:

```http
Content-Security-Policy:
  script-src 'sha256-<base64-hash>'
```

HTML:

```html
<script>
  startApplication();
</script>
```

Browser вычисляет hash содержимого script и сравнивает его со значением policy.

Если script изменится, hash перестанет совпадать.

Hash удобен для небольшого стабильного inline script.

При изменении:

- кода;
- пробелов;
- переносов строк;

значение может потребовать обновления.

### Nonce и hash — в чём разница

| Механизм | Что подтверждает | Когда удобен |
| --- | --- | --- |
| Nonce | Script получил одноразовое разрешение текущего response | Динамический server-rendered HTML |
| Hash | Содержимое script совпадает с ожидаемым | Стабильный неизменяемый script |

Оба подхода лучше широкой политики, разрешающей любой inline JavaScript.

### `strict-dynamic`

`'strict-dynamic'` — дополнительное правило для `script-src`.

Оно означает, что script, которому уже доверяют через nonce или hash, может программно загрузить другие scripts, и это доверие распространится на них.

```http
Content-Security-Policy:
  script-src 'nonce-random-value' 'strict-dynamic'
```

Например, разрешённый bootstrap script создаёт:

```ts
const script = document.createElement("script");
script.src = "/chunks/app.js";
document.head.append(script);
```

При `strict-dynamic` такой script может быть разрешён как загруженный доверенным bootstrap-кодом.

Преимущество — не нужно заранее перечислять каждый dynamic chunk в allowlist.

Риск — доверенный script не должен строить `src` из непроверенных данных:

```ts
script.src = untrustedUrl;
```

Иначе атакующий может заставить уже разрешённый code загрузить вредоносный script.

`strict-dynamic` является продвинутым механизмом. Его применяют после понимания того, как приложение создаёт и загружает scripts.

### `unsafe-inline` и `unsafe-eval`

Без подтверждённой необходимости избегают:

```text
'unsafe-inline'
'unsafe-eval'
```

`'unsafe-inline'` разрешает широкий класс inline-кода, например:

```html
<script>
  run();
</script>
```

и inline event handlers:

```html
<button onclick="deleteUser()">
  Удалить
</button>
```

Это ослабляет защиту от XSS, потому что внедрённый inline script тоже может стать исполняемым.

`'unsafe-eval'` разрешает выполнение строк как JavaScript через механизмы вроде:

```ts
eval(code);
new Function(code);
```

Development-сборка или отдельная библиотека иногда может требовать такие послабления, но production policy должна содержать только действительно необходимые исключения.

### `connect-src`

`connect-src` ограничивает сетевые destinations, к которым JavaScript страницы может подключаться.

Он применяется к:

- `fetch`;
- `XMLHttpRequest`;
- WebSocket;
- EventSource;
- `navigator.sendBeacon()`.

```http
Content-Security-Policy:
  connect-src
    'self'
    https://api.example.com
    wss://realtime.example.com
```

Даже если CORS разрешает frontend читать API, CSP может заблокировать сам запрос, если API отсутствует в `connect-src`.

И наоборот, разрешённый `connect-src` не отменяет CORS.

```text
CSP connect-src
→ разрешено ли странице начать соединение

CORS
→ разрешено ли JavaScript прочитать cross-origin response
```

`connect-src` также не является authorization. API всё равно проверяет пользователя и его права.

### `frame-src` и `frame-ancestors`

Эти directives решают противоположные задачи.

`frame-src` определяет, какие страницы может встроить текущий документ:

```http
Content-Security-Policy:
  frame-src https://widget.example
```

`frame-ancestors` определяет, кто может встроить текущую страницу:

```http
Content-Security-Policy:
  frame-ancestors 'none'
```

Упрощённо:

```text
frame-src
→ что могу встроить я

frame-ancestors
→ кто может встроить меня
```

`frame-ancestors 'none'` помогает защищаться от clickjacking.

Clickjacking — атака, при которой страницу помещают в невидимый или замаскированный iframe и заставляют пользователя нажать на реальный элемент, не показывая его настоящий контекст.

`frame-ancestors` нужно передавать HTTP-header. Оно не работает в CSP, объявленной через `<meta>`.

### `form-action`

`form-action` ограничивает destinations HTML forms:

```http
Content-Security-Policy:
  form-action 'self'
```

Это важно, потому что `connect-src` не контролирует обычную отправку form.

Внедрённый `<form>` не должен иметь возможность отправить данные на произвольный чужой адрес.

### `object-src`

`object-src` ограничивает устаревший plugin content через:

```html
<object>
<embed>
```

В современной строгой policy обычно используют:

```http
object-src 'none'
```

### `base-uri`

HTML-элемент:

```html
<base href="https://example.com/">
```

меняет базовый URL для относительных ссылок.

Если атакующий сможет внедрить `<base>`, относительные URLs scripts, forms и links могут начать указывать на неожиданный origin.

Поэтому строгая policy часто содержит:

```http
base-uri 'none'
```

или:

```http
base-uri 'self'
```

### CSP и безопасная работа с DOM

CSP не заменяет безопасные DOM APIs.

Опасный пример:

```ts
container.innerHTML = userContent;
```

Если `userContent` не прошёл корректную sanitization, атакующий может внедрить HTML и попытаться использовать доступные XSS-векторы.

Для обычного текста используют:

```ts
container.textContent = userContent;
```

Если приложению действительно нужен пользовательский HTML, его очищают проверенным sanitizer, то есть инструментом, удаляющим опасные элементы, attributes и URLs.

CSP является дополнительным барьером:

```text
безопасные DOM APIs и sanitization
→ предотвращают внедрение

CSP
→ мешает внедрённому коду выполниться или связаться с запрещённым адресом
```

### Third-party scripts

Third-party script — JavaScript, который контролируется другой организацией или загружается из внешнего источника.

Например:

```html
<script src="https://analytics.example/sdk.js"></script>
```

После загрузки script выполняется с правами страницы.

Он потенциально может:

- читать доступный DOM;
- читать browser storage;
- изменять интерфейс;
- отслеживать действия пользователя;
- отправлять запросы на разрешённые адреса;
- выполнять действия от имени пользователя через доступные API.

Если CSP разрешает:

```http
script-src https://analytics.example
```

она доверяет scripts с этого origin.

Если vendor скомпрометирован или разрешённый origin позволяет публиковать чужие scripts, CSP allowlist не предотвратит выполнение такого кода.

Поэтому CSP дополняют другими мерами.

**Self-hosting**

Self-hosting означает размещение копии зависимости на инфраструктуре приложения.

Преимущества:

- приложение контролирует момент обновления;
- внешний vendor не может незаметно изменить уже раздаваемый файл;
- уменьшается количество внешних сетевых соединений;
- CSP становится проще.

Но приложение берёт на себя:

- обновление зависимости;
- исправление уязвимостей;
- соблюдение лицензии;
- контроль целостности сборки.

**Subresource Integrity**

SRI (Subresource Integrity, контроль целостности подресурса) позволяет зафиксировать ожидаемый cryptographic hash внешнего script или stylesheet.

```html
<script
  src="https://cdn.example/library.js"
  integrity="sha384-..."
  crossorigin="anonymous"
></script>
```

Browser:

1. Загружает resource.
2. Вычисляет его hash.
3. Сравнивает с `integrity`.
4. Выполняет resource только при совпадении.

Если CDN или attacker подменит файл, hash не совпадёт и resource будет заблокирован.

Для cross-origin SRI resource должен корректно участвовать в CORS-проверке, поэтому часто нужен:

```html
crossorigin="anonymous"
```

SRI защищает от неожиданного изменения содержимого файла, но не ограничивает полномочия script после успешной проверки.

Если ожидаемый script сам является вредоносным или уязвимым, SRI не исправит его.

**Sandboxed iframe**

Недоверенный widget можно запускать не как script внутри основной страницы, а в отдельном iframe с `sandbox`.

```html
<iframe
  src="https://widget.example"
  sandbox="allow-scripts"
></iframe>
```

Без дополнительных tokens sandbox ограничивает многие возможности:

- scripts;
- forms;
- navigation;
- popup;
- обычный origin;
- доступ к части browser APIs.

В примере `allow-scripts` возвращает возможность выполнять scripts, но остальные ограничения сохраняются.

Permissions добавляют минимально, исходя из задачи.

Следует осторожно сочетать:

```text
allow-scripts
allow-same-origin
```

Если iframe имеет тот же origin, что и parent, эта комбинация может позволить ему получить доступ к parent DOM, удалить `sandbox` attribute и перезагрузиться без ограничений.

Взаимно недоверенный контент безопаснее размещать на отдельном origin.

Для связи с sandboxed iframe используют `postMessage` и проверяют origin, source и data.

### CSP Report-Only

Новую policy удобно сначала запустить в режиме наблюдения:

```http
Content-Security-Policy-Report-Only:
  default-src 'self';
  script-src 'self'
```

Browser сообщает о нарушениях, но не блокирует resources.

Это помогает обнаружить:

- inline scripts;
- внешние CDN;
- analytics;
- WebSocket endpoints;
- динамические styles;
- scripts browser extensions;
- забытые resources.

После анализа policy включают через:

```http
Content-Security-Policy
```

Report-only не защищает страницу. Он только показывает, что было бы заблокировано.

CSP reports могут содержать:

- URL документа;
- адрес заблокированного resource;
- название directive;
- строку и файл script;
- другие данные о контексте нарушения.

URL иногда содержит чувствительные identifiers или параметры. Поэтому reporting endpoint применяет data minimization, то есть собирает только необходимые данные и хранит их ограниченное время.

Reports приходят от клиента и считаются недоверенными данными.

Endpoint должен использовать:

- ограничение размера request;
- безопасный parser;
- rate limit;
- защиту журналов;
- ограниченный срок хранения;
- фильтрацию чувствительных параметров.

Reports также могут быть неполными: browser, extension, network policy или privacy settings могут не отправить их.

### Что CSP не предотвращает

CSP не является полной защитой от XSS и не исправляет:

- unsafe DOM injection;
- неправильную sanitization;
- уязвимость разрешённого script;
- скомпрометированный vendor;
- server-side authorization bug;
- утечку через разрешённый API;
- передачу секрета в уже разрешённую analytics system.

Если вредоносный code уже находится в разрешённом script, CSP может считать его доверенным.

Поэтому CSP является defense in depth, а не единственной линией защиты.

## Как механизмы сочетаются

| Задача | Основной механизм | Дополнение |
| --- | --- | --- |
| Запретить JavaScript читать данные другого origin | Same-origin policy | CORS для намеренного доступа |
| Разрешить frontend читать cross-origin API | CORS | authentication и authorization |
| Ограничить отправку cookie cross-site | `SameSite` | CSRF token и server-side-проверки |
| Ограничить выполнение scripts | CSP | безопасные DOM APIs и sanitization |
| Зафиксировать содержимое внешнего script | SRI | CSP и контроль vendor |
| Изолировать недоверенный widget | iframe `sandbox` | отдельный origin и `postMessage` |
| Запретить встраивание страницы | CSP `frame-ancestors` | безопасный интерфейс |
| Ограничить Fetch и WebSocket destinations | CSP `connect-src` | CORS и server authorization |
| Защитить данные в сети | HTTPS | HSTS и application security |
| Обмениваться данными между iframe и parent | `postMessage` | проверка origin, source и data |

### HTTPS и HSTS

HTTPS защищает трафик между browser и TLS endpoint:

- шифрует данные;
- защищает от незаметного изменения в пути;
- подтверждает сервер через certificate.

HTTPS не защищает от JavaScript, который уже легально выполняется внутри страницы.

HSTS (HTTP Strict Transport Security) — response header, которым сайт сообщает browser:

```text
в дальнейшем обращайся ко мне только через HTTPS
```

Пример:

```http
Strict-Transport-Security:
  max-age=31536000;
  includeSubDomains
```

`max-age` задаёт срок действия policy в секундах.

`includeSubDomains` распространяет правило на поддомены.

После получения HSTS policy browser автоматически преобразует попытки обращения по HTTP в HTTPS и не позволяет пользователю обойти ошибку certificate обычным подтверждением.

HSTS помогает против downgrade-сценариев, где пользователя пытаются оставить на HTTP.

Но при первом посещении browser ещё может не знать policy. HSTS preload позволяет заранее включить подходящий домен в список браузера, однако это требует отдельной осторожной настройки и готовности всех поддоменов работать через HTTPS.

HSTS не заменяет:

- CSP;
- CORS;
- CSRF-защиту;
- server authorization;
- безопасную работу с DOM.

### Пример: frontend и API на разных origins

```text
Frontend:
https://app.example.com

API:
https://api.example.com
```

Frontend выполняет:

```ts
await fetch("https://api.example.com/me", {
  credentials: "include",
});
```

Полный поток может выглядеть так:

1. CSP страницы проверяет, разрешён ли `https://api.example.com` в `connect-src`.
2. Browser проверяет, подходит ли cookie по `Domain`, `Path`, `Secure`, `SameSite` и другим правилам.
3. Если request требует preflight, browser отправляет `OPTIONS`.
4. API возвращает CORS-разрешение для `https://app.example.com`.
5. Browser отправляет actual request.
6. API проверяет session и права пользователя.
7. API возвращает response и CORS headers.
8. Browser проверяет CORS policy.
9. JavaScript получает response.
10. SOP продолжает запрещать frontend произвольный доступ к другим неразрешённым origins.

Каждый механизм выполняет только свою часть.

### Пример: внешний analytics script

Страница подключает:

```html
<script
  src="https://analytics.example/sdk.js"
  integrity="sha384-..."
  crossorigin="anonymous"
></script>
```

Защита распределяется так:

1. HTTPS защищает загрузку по сети.
2. SRI проверяет, что файл совпадает с ожидаемым hash.
3. CSP решает, разрешён ли этот script source.
4. После выполнения script получает полномочия страницы.
5. `connect-src` ограничивает destinations его сетевых запросов.
6. Server APIs продолжают проверять права пользователя.
7. Полный отказ от ненужного third-party code уменьшает поверхность атаки сильнее, чем одна дополнительная policy.

## Ключевые уточнения

- Origin состоит из scheme, host и effective port.
- Path, query и fragment не входят в origin.
- Поддомены обычно имеют разные origins.
- Same-origin policy в первую очередь ограничивает чтение cross-origin данных.
- SOP может разрешить отправку запроса, но запретить JavaScript читать response.
- Поэтому SOP и CORS сами по себе не предотвращают CSRF.
- `no-cors` возвращает opaque response и не является обходом SOP.
- `postMessage` создаёт явный cross-origin-канал.
- При `postMessage` проверяют `targetOrigin`, `event.origin`, `event.source` и структуру `event.data`.
- CORS определяет, может ли browser JavaScript прочитать cross-origin response.
- CORS не ограничивает `curl`, backend и другие небраузерные clients.
- CORS не заменяет authentication, authorization и validation.
- Request без preflight всё равно может изменить server state.
- Preflight проверяет origin, method и request headers, но не бизнес-права пользователя.
- Успешный preflight не отменяет проверку actual request и actual response.
- Credentialed CORS требует точного `Access-Control-Allow-Origin`.
- При credentials нельзя использовать `Access-Control-Allow-Origin: *`.
- `credentials: "include"` не отменяет cookie attributes и browser privacy policy.
- При динамическом разрешении origin обычно нужен `Vary: Origin`.
- `Access-Control-Expose-Headers` открывает JavaScript дополнительные response headers.
- `Set-Cookie` нельзя прочитать через Fetch.
- CORS error не доказывает, что server не обработал actual request.
- WebSocket не использует обычные CORS response headers; server проверяет `Origin` самостоятельно.
- CSP ограничивает resources и возможности страницы.
- CSP предпочтительно передавать HTTP-header.
- `default-src` не заменяет `frame-ancestors`, `form-action` и `base-uri`.
- CSP nonce должен быть непредсказуемым и новым для каждого response.
- CSP hash привязан к конкретному содержимому script.
- `'unsafe-inline'` и `'unsafe-eval'` заметно ослабляют script policy.
- `connect-src` ограничивает Fetch, XHR, WebSocket и EventSource.
- `frame-src` определяет, что может встроить страница.
- `frame-ancestors` определяет, кто может встроить страницу.
- `form-action` ограничивает destinations HTML forms.
- CSP не заменяет sanitization и безопасные DOM APIs.
- Разрешённый third-party script выполняется с полномочиями страницы.
- SRI проверяет содержимое resource, но не ограничивает его полномочия после выполнения.
- Self-hosting увеличивает контроль, но переносит ответственность за обновление зависимости на приложение.
- Iframe `sandbox` ограничивает возможности недоверенного документа.
- CSP Report-Only помогает подготовить policy, но ничего не блокирует.
- CSP reports могут содержать чувствительные данные и считаются недоверенным input.
- HTTPS защищает transport, а HSTS заставляет browser использовать HTTPS в будущих обращениях.
- Ни один отдельный механизм не заменяет остальные уровни защиты.

## Связанные темы

- [CORS](<../Основы веб-платформы/13 CORS.md>)
- [CSP и заголовки безопасности](<../Основы веб-платформы/16 CSP и заголовки безопасности.md>)
- [Cookie и авторизация](<../Основы веб-платформы/11 Cookie и авторизация.md>)
- [CSRF](<../Основы веб-платформы/15 CSRF.md>)
- [XSS](<../Основы веб-платформы/14 XSS.md>)
- [HTTP и HTTPS](<../Основы веб-платформы/03 HTTP и HTTPS.md>)

## Источники

- [WHATWG Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [WHATWG HTML Standard: Origins](https://html.spec.whatwg.org/multipage/browsers.html#origins)
- [WHATWG HTML Standard: Cross-document messaging](https://html.spec.whatwg.org/multipage/web-messaging.html)
- [WHATWG HTML Standard: The iframe element](https://html.spec.whatwg.org/multipage/iframe-embed-object.html#the-iframe-element)
- [W3C: Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [W3C: Subresource Integrity](https://www.w3.org/TR/sri-2/)
- [RFC 6797: HTTP Strict Transport Security](https://www.rfc-editor.org/rfc/rfc6797)
- [MDN: Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
- [MDN: Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
- [OWASP: Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Хранение токенов — XSS, CSRF и компромиссы](<./02 Хранение токенов — XSS, CSRF и компромиссы.md>) · [↑ Безопасность](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Цепочка поставок, секреты и сторонние скрипты →](<./04 Цепочка поставок, секреты и сторонние скрипты.md>)
<!-- NOTE-NAV-BOTTOM:END -->
