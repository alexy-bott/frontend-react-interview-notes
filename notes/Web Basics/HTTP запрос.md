# HTTP запрос

<!-- NOTE-NAV-TOP:START -->
[← HTTP vs HTTPS](<./HTTP vs HTTPS.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [HTTP методы →](<./HTTP методы.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

HTTP-запрос — сообщение клиента серверу. Его смысл задают метод и целевой URL, заголовки передают метаданные, а необязательное тело содержит данные операции. Например, `POST /api/users` с `Content-Type: application/json` сообщает, куда направлен запрос, как сервер должен интерпретировать тело и какие данные переданы.

В HTTP/1.1 сообщение в текстовом представлении состоит из строки запроса (request line), заголовков, пустой строки и тела. HTTP/2 и HTTP/3 кодируют сообщения в бинарные frames и используют псевдозаголовки (pseudo-headers), но наблюдаемая модель для приложения остаётся прежней: метод, URL, заголовки и тело.

Браузер формирует часть запроса самостоятельно. Frontend-код не может произвольно задать `Host`, `Cookie`, `Content-Length` и некоторые другие контролируемые заголовки. Для межсайтового запроса дополнительно действуют CORS и политика cookie.

## Структура сообщения

```http
POST /api/users?notify=true HTTP/1.1
Host: example.com
Accept: application/json
Content-Type: application/json
Authorization: Bearer token

{"name":"Ann"}
```

| Часть | Что означает |
| --- | --- |
| `POST` | HTTP-метод и семантика операции |
| `/api/users?notify=true` | путь и строка запроса (query string) |
| `HTTP/1.1` | версия текстового протокола в request line |
| Headers | метаданные запроса и представления |
| Body | данные, если контракт операции допускает тело |

Фрагмент URL после `#`, например `#reviews`, в запрос не входит. Он используется браузером внутри уже полученного документа. Query string после `?` входит в целевой URL и может попасть в историю, логи, аналитику и заголовок `Referer`, поэтому секреты в ней не передают.

## Заголовки и тело

`Content-Type` описывает формат тела текущего сообщения. `Accept` сообщает, какие форматы ответа клиент предпочитает получить:

```http
Accept: application/json
Content-Type: application/json
```

Если отправляется `FormData`, браузер сам создаёт `Content-Type: multipart/form-data` с уникальным параметром `boundary`. Задавать этот заголовок вручную не следует: без согласованной границы сервер не сможет корректно разделить части тела.

`Authorization` обычно передаёт access token или другую схему авторизации. Cookie хранится браузером и при подходящих атрибутах добавляется в заголовок `Cookie` автоматически; JavaScript не собирает этот заголовок вручную.

`Content-Length` либо разбиение потока на части определяются средой и протоколом. В браузерном `fetch` разработчик передаёт данные через `body`, а их фактическое кодирование и низкоуровневые заголовки формирует браузер.

## URL и HTTP/2 или HTTP/3

HTTP/2 и HTTP/3 не отправляют текстовую request line. Её роль выполняют pseudo-headers:

```text
:method    POST
:scheme    https
:authority example.com
:path      /api/users?notify=true
```

Обычный JavaScript не задаёт эти поля напрямую. Они формируются из метода и URL запроса. В Network panel DevTools браузер показывает удобное логическое представление, хотя данные на проводе закодированы иначе.

## Запрос через `fetch`

```js
await fetch("/api/users?notify=true", {
  method: "POST",
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ name: "Ann" }),
});
```

`fetch` не преобразует объект в JSON автоматически: объект явно сериализуется через `JSON.stringify`, а формат указывается в `Content-Type`. Для `URLSearchParams`, `Blob`, `FormData` и streams правила формирования тела отличаются.

Fetch API запрещает тело у `GET` и `HEAD`. На уровне HTTP содержание GET-запроса также не имеет общепринятой семантики и может быть отвергнуто промежуточными компонентами. Параметры чтения передают в path или query либо выбирают другой метод согласно API-контракту.

## Cookies и межсайтовый запрос

По умолчанию `fetch` отправляет credentials только для same-origin запроса. Для cookie-запроса к другому origin требуется `credentials: "include"`:

```js
await fetch("https://api.example.com/profile", {
  credentials: "include",
});
```

Этого недостаточно само по себе. Cookie должна подходить по атрибутам `Domain`, `Path`, `Secure` и `SameSite`, а сервер должен разрешить credentialed CORS request для конкретного origin. `Access-Control-Allow-Origin: *` с credentials не подходит.

Заголовки вроде `Authorization` и `Content-Type: application/json` делают многие межсайтовые запросы предварительно проверяемыми. Браузер сначала отправляет CORS preflight через `OPTIONS`, а основной запрос выполняет только после разрешающего ответа.

## Условный запрос и кэш

Для повторной проверки кэшированного ресурса браузер или клиент может отправить валидатор:

```http
If-None-Match: "users-v7"
```

Если представление не изменилось, сервер отвечает `304 Not Modified` без нового тела, и клиент использует сохранённый ответ. `If-Modified-Since` и `Last-Modified` решают похожую задачу на основе времени, но `ETag` обычно точнее выражает версию представления.

## Диагностика в DevTools

На панели Network проверяют:

1. Request URL, метод и наличие перенаправлений.
2. Query parameters и request payload.
3. Заголовки, которые фактически добавил браузер.
4. Наличие preflight и его ответ.
5. Cookies вместе с причиной, по которой конкретная cookie была заблокирована.
6. Timing: ожидание соединения, отправку, ожидание ответа и загрузку тела.

## Ключевые уточнения

- Метод и URL задают цель запроса, headers описывают контекст, а body передаёт данные согласно контракту операции.
- `Content-Type` относится к телу текущего сообщения, а `Accept` — к предпочитаемому формату ответа.
- Query string отправляется серверу и часто сохраняется инфраструктурой; URL fragment остаётся в браузере.
- Браузер сам формирует защищённые заголовки и низкоуровневое представление HTTP/2 или HTTP/3.
- `credentials: "include"` только разрешает браузеру учитывать credentials; cookie policy и CORS сервера всё равно должны разрешить запрос.

## Связанные темы

- [HTTP методы](<./HTTP методы.md>)
- [HTTP status codes и ошибки API](<./HTTP status codes и ошибки API.md>)
- [HTTP caching](<./HTTP caching.md>)
- [CORS](<./CORS.md>)
- [Cookies и авторизация](<./Cookies и авторизация.md>)
- [Fetch и работа с API](<../JavaScript/Fetch и работа с API.md>)

## Источники

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [MDN: HTTP messages](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages)
- [MDN: Using the Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
- [Fetch Standard: Headers](https://fetch.spec.whatwg.org/#terminology-headers)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← HTTP vs HTTPS](<./HTTP vs HTTPS.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [HTTP методы →](<./HTTP методы.md>)
<!-- NOTE-NAV-BOTTOM:END -->
