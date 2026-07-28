---
aliases:
  - CORS
  - Cross-Origin Resource Sharing
  - preflight
  - Access-Control-Allow-Origin
  - cross-origin request
---

#### Быстрый ответ

CORS (Cross-Origin Resource Sharing) — протокол HTTP-заголовков, через который сервер разрешает JavaScript в браузере читать определённые ответы с другого origin. Он ослабляет конкретную сетевую границу Same-Origin Policy, а не отключает её целиком.

Origin состоит из схемы, хоста и порта. Если frontend и API имеют разные origins, браузер добавляет `Origin` и проверяет `Access-Control-Allow-Origin` в ответе. Для запроса за пределами списка простых разрешённых параметров браузер сначала отправляет предварительный запрос (preflight) `OPTIONS` с желаемым методом и заголовками.

CORS не является аутентификацией, авторизацией или защитой от CSRF. Запрос может дойти до сервера, даже если браузер не отдаст ответ JavaScript-коду. Сервер всегда проверяет учётные данные, права, источник изменяющих запросов с cookie и входные данные.

#### Same-origin и cross-origin

```text
https://app.example.com:443
└scheme┘ └────host─────┘port
```

| URL относительно `https://app.example.com` | Same-origin |
| --- | --- |
| `https://app.example.com/profile` | да |
| `https://api.example.com` | нет: другой host |
| `http://app.example.com` | нет: другая scheme |
| `https://app.example.com:8443` | нет: другой port |

Same-Origin Policy ограничивает чтение и взаимодействие между origins, но не запрещает всю cross-origin активность. Браузер умеет переходить по внешней ссылке, отправлять HTML-форму и загружать некоторые ресурсы с другого origin. CORS определяет, когда скрипт получает доступ к ответу через `fetch`, XHR и связанные API.

#### Запрос без preflight

CORS-safelisted request, то есть запрос из ограниченного списка «простых», использует:

- метод `GET`, `HEAD` или `POST`;
- только разрешённые заголовки запроса с допустимыми значениями;
- для вручную заданного `Content-Type` только `application/x-www-form-urlencoded`, `multipart/form-data` или `text/plain`.

```http
GET /catalog HTTP/1.1
Origin: https://app.example.com
```

Сервер разрешает чтение ответа:

```http
Access-Control-Allow-Origin: https://app.example.com
```

Отсутствие preflight не означает отсутствие CORS. Основной запрос сразу отправляется, а затем браузер проверяет заголовки ответа. Если разрешения нет, серверная операция уже могла произойти, но JavaScript получит CORS error вместо доступного ответа.

#### Preflight

Preflight требуется, например, для `PUT`, `PATCH`, `DELETE`, `Authorization`, пользовательских заголовков или `Content-Type: application/json`.

```http
OPTIONS /orders/42 HTTP/1.1
Origin: https://app.example.com
Access-Control-Request-Method: PATCH
Access-Control-Request-Headers: content-type, authorization
```

Разрешающий ответ:

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, PATCH
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 600
Vary: Origin
```

После успешной проверки браузер отправляет настоящий `PATCH`. `Access-Control-Allow-Methods` и `Access-Control-Allow-Headers` в preflight-ответе должны покрывать запрошенные значения; они не заставляют backend реализовать endpoint и не заменяют проверку аутентификации и прав.

`Access-Control-Max-Age` разрешает кешировать результат preflight. Этот кеш отделён от обычного кеша HTTP-ответов, а браузер может ограничить максимальный срок независимо от большего значения сервера.

Frontend не отправляет `OPTIONS` вручную и не устанавливает `Origin`: это делает браузер. Если приложение сначала само делает `OPTIONS`, настоящий запрос всё равно проходит собственную CORS-проверку.

#### Credentials

Режим credentials включает cookie, HTTP-аутентификацию и клиентские сертификаты. Для cross-origin запроса с cookie:

```js
await fetch("https://api.example.com/me", {
  credentials: "include",
});
```

Response должен содержать:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
```

`Access-Control-Allow-Origin: *` нельзя использовать для ответа, который JavaScript запрашивает с credentials. Сервер возвращает один конкретный разрешённый origin, а не строку со списком origins.

CORS-разрешение не заставляет cookie отправиться. Она отдельно проходит `Domain`, `Path`, `Secure`, `SameSite`, политику сторонних cookie и разделение хранилища (storage partitioning). Cross-origin и cross-site — разные сравнения: два поддомена могут быть cross-origin, но same-site.

#### Доступ к заголовкам ответа

JavaScript всегда видит ограниченный набор CORS-safelisted заголовков ответа. Чтобы открыть пользовательский заголовок, сервер перечисляет его:

```http
Access-Control-Expose-Headers: X-Request-Id, Content-Disposition
```

Это не относится к `Set-Cookie`: браузер никогда не предоставляет этот заголовок ответа frontend-коду. Cookie обрабатывается отдельным механизмом.

#### Динамический список разрешённых origins и кеш

Сервер не отражает любой входящий `Origin` автоматически. Сначала он сравнивает значение с точным списком разрешённых origins, затем возвращает его:

```text
Origin received
  -> точная проверка по списку разрешённых origins
  -> Access-Control-Allow-Origin: <allowed origin>
  -> Vary: Origin
```

Проверка через `endsWith("example.com")` опасна: строка `evil-example.com` тоже заканчивается так. Origin разбирают как URL или сравнивают с заранее нормализованным множеством полных значений.

`Vary: Origin` нужен, когда ответ зависит от входящего `Origin`. Без него CDN может сохранить разрешение для одного сайта и отдать те же заголовки запросу другого. При этом политику кеширования чувствительных данных всё равно проектируют отдельно.

#### `no-cors` не отключает CORS

```js
const response = await fetch(url, { mode: "no-cors" });
```

Режим `no-cors` ограничивает методы и заголовки и возвращает непрозрачный ответ (opaque response): JavaScript не видит его status, headers и body. Режим нужен отдельным сценариям загрузки, но не позволяет прочитать чужой API.

Отключение web security в локальном браузере также не является исправлением. У реального пользователя политика останется, а проблема серверных заголовков сохранится.

#### Почему Postman работает

Postman, `curl` и backend-to-backend client не являются скриптом браузерной страницы и не обязаны применять Same-Origin Policy. Они могут получить ответ без CORS-заголовков.

Это не означает, что браузерный запрос «не дошёл». На панели Network отдельно проверяют preflight, основной запрос и ответ. Console часто намеренно скрывает детали ответа, чтобы запрещённые данные не утекали через текст ошибки.

#### Диагностика

1. Сравнить origins frontend и API полностью: scheme, host, port.
2. Найти в Network `OPTIONS` и проверить, был ли отправлен основной запрос.
3. Сверить `Origin` и точное значение `Access-Control-Allow-Origin`.
4. Сопоставить запрошенные метод и заголовки с `Allow-Methods` и `Allow-Headers`.
5. Для cookie проверить `credentials`, `Allow-Credentials` и cookie attributes.
6. Проверить перенаправления: preflight и конечный ответ должны пройти применимые правила.
7. Если есть CDN, проверить `Vary: Origin` и cache key.

Dev proxy создаёт same-origin URL только локально и способен скрыть production CORS. Маршрутизацию и заголовки production проверяют в реальном окружении.

#### Ключевые уточнения

- CORS разрешает браузерному скрипту читать ответ другого origin и не является общей сетевой защитой API.
- Safelisted request идёт без preflight, но его ответ всё равно проходит CORS-проверку.
- Preflight проверяет разрешение до основного запроса вне safelist, а не выполняет бизнес-операцию вместо него.
- Credentials требуют конкретного allowed origin и отдельного прохождения cookie policy.
- `no-cors`, Postman и dev proxy не доказывают правильность production CORS-конфигурации.

#### Связанные темы

- [[Конспект для подготовки/Security/CORS CSP и browser security boundaries]]
- [[Конспект для подготовки/Web Basics/CSRF]]
- [[Конспект для подготовки/Web Basics/Cookies и авторизация]]
- [[Конспект для подготовки/Web Basics/Auth flow и refresh tokens]]
- [[Конспект для подготовки/Web Basics/HTTP запрос]]
- [[Конспект для подготовки/JavaScript/Fetch и работа с API]]

#### Источники

- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [MDN: Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [MDN: Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
