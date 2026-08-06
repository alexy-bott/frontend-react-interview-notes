# CORS CSP и browser security boundaries

<!-- NOTE-NAV-TOP:START -->
[← Token storage XSS CSRF tradeoffs](<./Token storage XSS CSRF tradeoffs.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Supply chain secrets и third-party scripts →](<./Supply chain secrets и third-party scripts.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Same-origin policy, CORS и CSP решают разные задачи браузерной безопасности:

| Механизм | Главный вопрос |
| --- | --- |
| Same-origin policy | Может ли JavaScript одной страницы читать данные другой страницы? |
| CORS | Разрешает ли сервер JavaScript-коду другого origin прочитать HTTP-ответ? |
| CSP | Какие scripts, ресурсы и сетевые соединения разрешены самой странице? |

Origin, или источник страницы, для обычного HTTP(S)-адреса состоит из:

```text
scheme + host + port
```

Например:

```text
https://app.example.com
https://api.example.com
```

имеют разные origins, потому что различаются hosts.

Same-origin policy по умолчанию не позволяет JavaScript страницы свободно читать DOM и ответы другого origin.

CORS позволяет серверу ослабить это ограничение и явно разрешить выбранному frontend-origin читать HTTP-ответ.

CSP ограничивает возможности уже загруженной страницы: откуда она может запускать JavaScript, загружать изображения, открывать WebSocket и отправлять формы.

CORS не является authentication или authorization. Сервер всё равно обязан проверять пользователя, его права и входные данные.

CSP не исправляет XSS автоматически. Она уменьшает вероятность запуска внедрённого кода и ограничивает возможный ущерб, но приложение всё равно должно безопасно выводить недоверенные данные.

## Границы origin

```text
origin = scheme + host + effective port
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

Path на origin не влияет:

```text
https://example.com/users
https://example.com/orders
```

Оба адреса принадлежат одному origin:

```text
https://example.com
```

Same-origin policy, или политика одного источника, ограничивает доступ JavaScript одного origin к данным другого.

В первую очередь она защищает чтение:

```text
страница evil.example
не может свободно прочитать
ответ api.bank.example
```

Но некоторые cross-origin-действия браузер разрешает.

Например, страница может:

- перейти по ссылке на другой сайт;
- отправить обычную HTML-форму;
- загрузить изображение;
- подключить внешний script;
- встроить iframe.

Поэтому важно различать:

```text
отправить запрос
```

и:

```text
прочитать ответ из JavaScript
```

Same-origin policy часто запрещает второе, но не всегда запрещает первое.

Именно поэтому она сама по себе не защищает от CSRF. Вредоносная страница может отправить запрос с автоматически приложенной cookie, даже если не сможет прочитать ответ.

Режим:

```ts
fetch(url, {
  mode: "no-cors",
});
```

не отключает same-origin policy.

JavaScript получит opaque response, или непрозрачный ответ, из которого нельзя прочитать:

- тело;
- status;
- большинство заголовков.

`no-cors` не является способом получить доступ к чужому API.

Для намеренного обмена данными между страницей и cross-origin iframe используют `postMessage`.

Отправитель указывает точный origin получателя:

```ts
iframe.contentWindow?.postMessage(
  {
    type: "profile.request",
  },
  "https://widget.example",
);
```

Получатель проверяет:

- `event.origin` — от какого origin пришло сообщение;
- `event.source` — от какого окна оно пришло;
- `event.data` — соответствует ли сообщение ожидаемой структуре.

```ts
window.addEventListener("message", (event) => {
  if (event.origin !== "https://app.example.com") {
    return;
  }

  if (event.source !== window.parent) {
    return;
  }

  const message = event.data;

  if (
    typeof message !== "object" ||
    message === null ||
    message.type !== "profile.request"
  ) {
    return;
  }

  sendProfile();
});
```

Значение `targetOrigin: "*"` не используют для чувствительных данных, потому что сообщение может получить документ с неожиданным origin.

## CORS

CORS (Cross-Origin Resource Sharing) — механизм, через который сервер разрешает JavaScript-коду другого origin читать HTTP-ответ.

Frontend на:

```text
https://app.example.com
```

выполняет запрос:

```ts
const response = await fetch(
  "https://api.example.com/users",
);
```

Браузер добавляет к запросу:

```http
Origin: https://app.example.com
```

Сервер разрешает этому origin читать ответ:

```http
Access-Control-Allow-Origin: https://app.example.com
```

Браузер сравнивает origin страницы со значением `Access-Control-Allow-Origin`.

Если проверка успешна, JavaScript получает доступ к `Response`.

Если проверка не прошла, браузер скрывает ответ от JavaScript. В `fetch` это обычно выглядит как сетевая ошибка.

CORS проверяется браузером. Он не ограничивает:

- `curl`;
- Postman;
- мобильное приложение;
- другой backend;
- самостоятельно написанный HTTP-клиент.

Поэтому CORS не защищает API от прямого вызова.

API всегда самостоятельно проверяет:

- authentication — кто выполняет запрос;
- authorization — имеет ли пользователь право на операцию;
- validation — корректны ли данные;
- rate limit;
- CSRF-защиту при cookie-аутентификации.

### Запрос без preflight

Некоторые cross-origin-запросы браузер может отправить сразу.

Например, обычный `GET` или HTML-form `POST` с простым набором заголовков.

```text
actual request
→
CORS-проверка response
```

Такой запрос может изменить данные на сервере, даже если JavaScript потом не получит доступ к ответу.

Поэтому отсутствие preflight не означает, что запрос безопасен.

### Preflight

Preflight, или предварительный запрос, — автоматический `OPTIONS`, который браузер отправляет перед более сложным cross-origin-запросом.

Например, frontend хочет выполнить:

```http
PATCH /users/42
Content-Type: application/json
Authorization: Bearer <token>
```

Перед ним браузер отправит:

```http
OPTIONS /users/42
Origin: https://app.example.com
Access-Control-Request-Method: PATCH
Access-Control-Request-Headers: authorization, content-type
```

Сервер отвечает:

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: PATCH
Access-Control-Allow-Headers: Authorization, Content-Type
```

Preflight проверяет, разрешает ли сервер браузеру отправить запрос с такими:

- method;
- headers;
- origin.

Preflight не проверяет:

- личность пользователя;
- права пользователя;
- корректность body;
- бизнес-правила.

После успешного preflight сервер всё равно обязан полностью проверить основной запрос.

Результат preflight можно временно кешировать:

```http
Access-Control-Max-Age: 600
```

Это уменьшает количество повторных `OPTIONS`.

### Запросы с cookies

По умолчанию cross-origin `fetch` не отправляет cookies как credentialed-запрос.

Для их отправки используют:

```ts
const response = await fetch(
  "https://api.example.com/me",
  {
    credentials: "include",
  },
);
```

Сервер должен вернуть:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
```

При credentials нельзя использовать:

```http
Access-Control-Allow-Origin: *
```

Нужен точный origin.

Если сервер динамически разрешает несколько origins, он сначала проверяет входящий `Origin` по allowlist, а затем возвращает совпавшее значение:

```http
Access-Control-Allow-Origin: https://app.example.com
Vary: Origin
```

`Vary: Origin` сообщает HTTP-кешу, что ответ может различаться для разных origins.

Само `credentials: "include"` ещё не гарантирует отправку cookie. Браузер дополнительно проверяет:

- `Domain`;
- `Path`;
- `Secure`;
- `SameSite`;
- срок действия cookie;
- browser privacy policy.

CORS и `SameSite` решают разные задачи.

```text
CORS
→ может ли JavaScript прочитать response

SameSite
→ будет ли cookie отправлена в cross-site context
```

### Доступ к response headers

Даже после успешного CORS JavaScript по умолчанию видит не все response headers.

Чтобы открыть собственный заголовок:

```http
X-Request-Id: 01HXYZ
Access-Control-Expose-Headers: X-Request-Id
```

Тогда frontend сможет прочитать его:

```ts
response.headers.get("X-Request-Id");
```

Заголовок `Set-Cookie` JavaScript прочитать не может. Браузер обрабатывает его самостоятельно.

### Почему возникает CORS error

CORS error может возникнуть в двух разных ситуациях.

Preflight не прошёл:

```text
OPTIONS отклонён
→
основной запрос не отправлен
```

Основной запрос был отправлен:

```text
server обработал запрос
→
response не содержит правильные CORS headers
→
JavaScript не получил доступ к response
```

Поэтому ошибка CORS не всегда означает, что сервер ничего не изменил.

Особенно опасно автоматически повторять `POST`, оплату или создание заказа после такой ошибки: первая операция могла уже выполниться.

При диагностике проверяют:

1. Origin страницы.
2. URL API.
3. Был ли `OPTIONS`.
4. Какие method и headers запросил браузер.
5. Заголовки preflight response.
6. Заголовки основного response.
7. `credentials`.
8. Атрибуты cookie.
9. Redirects и proxy.
10. Добавляются ли CORS headers к ошибочным ответам.

WebSocket не использует обычный CORS-протокол.

При открытии браузер отправляет `Origin`, а WebSocket-сервер должен самостоятельно проверить его, особенно если аутентификация основана на cookies.

## CSP

CSP (Content Security Policy) — политика, которая ограничивает возможности страницы.

Она может определить:

- откуда разрешено загружать JavaScript;
- к каким API можно подключаться;
- какие изображения и стили допустимы;
- кто может встроить страницу в iframe;
- куда разрешено отправлять формы.

CSP предпочтительно передают через HTTP-header:

```http
Content-Security-Policy: default-src 'self'
```

Основные directives:

| Directive | Что ограничивает |
| --- | --- |
| `default-src` | источник по умолчанию для многих типов ресурсов |
| `script-src` | JavaScript |
| `style-src` | CSS |
| `img-src` | изображения |
| `font-src` | шрифты |
| `connect-src` | `fetch`, XHR, WebSocket и EventSource |
| `frame-src` | какие iframe может загрузить страница |
| `frame-ancestors` | кто может встроить эту страницу |
| `form-action` | куда разрешено отправлять формы |
| `object-src` | устаревший plugin content |
| `base-uri` | какие значения разрешены для `<base>` |

Пример:

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  connect-src 'self' https://api.example.com wss://realtime.example.com;
  img-src 'self' https://cdn.example.com;
  frame-ancestors 'none';
  form-action 'self';
  object-src 'none';
  base-uri 'none'
```

Такая policy разрешает ресурсы текущего origin, разрешает обращения к указанному API и WebSocket, запрещает встраивание страницы и plugin content.

### CSP для scripts

Простая policy:

```http
script-src 'self'
```

разрешает JavaScript текущего origin.

Но если атакующий может загрузить собственный `.js` на этот же origin, одного `'self'` недостаточно.

Более строгий подход разрешает конкретные scripts через nonce или hash.

Nonce — случайное одноразовое значение, созданное сервером для одного HTML-response.

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

Браузер выполнит script только при совпадении nonce.

Nonce должен быть:

- случайным;
- непредсказуемым;
- новым для каждого response;
- добавленным только доверенным scripts.

Нельзя использовать постоянное значение:

```text
nonce="frontend"
```

Атакующий сможет скопировать его в свой script.

Hash разрешает script с конкретным содержимым:

```http
Content-Security-Policy:
  script-src 'sha256-...'
```

Если script изменится, hash перестанет совпадать.

Без необходимости не используют:

```text
'unsafe-inline'
'unsafe-eval'
```

`'unsafe-inline'` разрешает inline scripts и обработчики вроде:

```html
<button onclick="deleteUser()">
```

`'unsafe-eval'` разрешает выполнение строк как JavaScript через `eval()` и похожие механизмы.

Оба значения заметно ослабляют CSP.

### Что CSP не исправляет

CSP не заменяет безопасную работу с DOM.

Опасный код:

```ts
container.innerHTML = userContent;
```

может оставаться уязвимым, особенно если policy допускает выполнение подходящего кода или имеет слишком широкие разрешения.

Поэтому CSP дополняют:

- использованием `textContent` для обычного текста;
- безопасными DOM API;
- sanitization HTML, если HTML действительно нужен;
- серверной валидацией;
- ограничением сторонних scripts.

CSP также не защищает от ошибок авторизации.

Если frontend имеет право отправлять запрос к:

```text
https://api.example.com
```

директива `connect-src` разрешит сетевое соединение. Но API всё равно должно проверить, имеет ли конкретный пользователь право читать или изменять ресурс.

### `frame-src` и `frame-ancestors`

Эти directives решают разные задачи.

```text
frame-src
→ какие iframe может загрузить текущая страница
```

```text
frame-ancestors
→ какие страницы могут встроить текущую страницу
```

Чтобы полностью запретить встраивание:

```http
Content-Security-Policy: frame-ancestors 'none'
```

Это помогает защищаться от clickjacking, когда атакующий помещает страницу в невидимый iframe и заставляет пользователя нажимать на элементы, которых он не видит.

### Проверка CSP перед включением

Политику можно сначала запустить в режиме наблюдения:

```http
Content-Security-Policy-Report-Only: ...
```

В этом режиме браузер сообщает о нарушениях, но не блокирует ресурсы.

Это помогает найти:

- inline scripts;
- внешние CDN;
- WebSocket endpoints;
- динамически загружаемые styles;
- стороннюю аналитику.

После проверки policy включают через обычный:

```http
Content-Security-Policy
```

Report-only сам по себе страницу не защищает.

## Как механизмы сочетаются

| Задача | Основной механизм | Что ещё требуется |
| --- | --- | --- |
| JavaScript читает cross-origin API | CORS | authentication и authorization |
| Cookie отправляется cross-site | `SameSite` и CSRF-защита | CORS, если JavaScript должен прочитать ответ |
| Ограничить выполнение scripts | CSP | безопасная работа с DOM |
| Защитить сетевой трафик | HTTPS | проверки прав и защита приложения |
| Запретить встраивание страницы | CSP `frame-ancestors` | безопасный UI |
| Обменяться данными с iframe | `postMessage` | проверка `origin`, `source` и данных |
| Ограничить WebSocket endpoint | CSP `connect-src` | проверка `Origin` и аутентификация на сервере |

Пример credentialed cross-origin API:

```text
Frontend:
https://app.example.com

API:
https://api.example.com
```

1. Frontend выполняет `fetch` с `credentials: "include"`.
2. Браузер решает, подходит ли cookie по `SameSite`, `Secure` и другим атрибутам.
3. При необходимости браузер выполняет preflight.
4. API проверяет сессию и права пользователя.
5. API возвращает CORS headers для frontend-origin.
6. Браузер разрешает JavaScript прочитать response.
7. CSP страницы дополнительно определяет, разрешено ли подключение к этому API через `connect-src`.

Каждый механизм отвечает только за свою часть.

## Ключевые уточнения

- Origin состоит из scheme, host и port.
- Same-origin policy в первую очередь ограничивает чтение cross-origin данных.
- Cross-origin request иногда отправляется, даже если JavaScript не сможет прочитать response.
- CORS разрешает браузерному JavaScript читать response другого origin.
- CORS не является authentication, authorization или CSRF-защитой.
- Preflight проверяет разрешённые method и headers, но не права пользователя.
- Успешный preflight не отменяет проверку основного запроса.
- CORS error не доказывает, что сервер не обработал запрос.
- Credentialed CORS требует точного `Access-Control-Allow-Origin`.
- При credentialed CORS нельзя использовать `Access-Control-Allow-Origin: *`.
- Для динамического origin обычно нужен `Vary: Origin`.
- `Access-Control-Expose-Headers` открывает frontend-коду дополнительные response headers.
- `Set-Cookie` недоступен для чтения через Fetch.
- `no-cors` не обходит same-origin policy.
- CSP ограничивает ресурсы и действия страницы.
- CSP nonce должен быть случайным и новым для каждого response.
- CSP не заменяет sanitization и безопасные DOM API.
- `frame-src` определяет загружаемые iframe, а `frame-ancestors` — кто может встроить страницу.
- `connect-src` ограничивает Fetch, WebSocket и EventSource, но не заменяет серверную авторизацию.
- `postMessage` требует точного `targetOrigin` и проверки `event.origin`, `event.source` и `event.data`.

## Связанные темы

- [CORS](<../Web Basics/CORS.md>)
- [CSP и security headers](<../Web Basics/CSP и security headers.md>)
- [Cookies и авторизация](<../Web Basics/Cookies и авторизация.md>)
- [CSRF](<../Web Basics/CSRF.md>)
- [XSS](<../Web Basics/XSS.md>)
- [HTTP vs HTTPS](<../Web Basics/HTTP vs HTTPS.md>)

## Источники

- [WHATWG Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [WHATWG HTML Standard: Origins](https://html.spec.whatwg.org/multipage/browsers.html#origins)
- [WHATWG HTML Standard: Cross-document messaging](https://html.spec.whatwg.org/multipage/web-messaging.html)
- [W3C: Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [MDN: Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
- [MDN: Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
- [OWASP: Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Token storage XSS CSRF tradeoffs](<./Token storage XSS CSRF tradeoffs.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Supply chain secrets и third-party scripts →](<./Supply chain secrets и third-party scripts.md>)
<!-- NOTE-NAV-BOTTOM:END -->
