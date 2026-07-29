# Auth flow и refresh tokens

<!-- NOTE-NAV-TOP:START -->
[← Cookies и авторизация](<./Cookies и авторизация.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [CORS →](<./CORS.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Поток аутентификации (auth flow) во frontend — жизненный цикл сессии: начальная проверка, вход, добавление учётных данных к API-запросу, ограниченное обновление access token, обработка потери сессии и выход. UI должен различать `unknown`, `authenticated` и `unauthenticated`, чтобы не показывать защищённый экран до завершения начальной проверки.

Распространённая схема использует короткоживущий access token в памяти и более защищённый refresh token в cookie с атрибутами `HttpOnly; Secure`. После подходящего `401` API-слой запускает один запрос на обновление, остальные запросы ждут тот же Promise, затем исходная операция повторяется не более одного раза. Явное отклонение refresh token завершает локальную сессию, а временный сетевой сбой обрабатывается отдельно.

Это один вариант, а не универсальный стандарт. Session cookie без access token, OAuth/OIDC Authorization Code with PKCE и backend-for-frontend используют другие потоки. Выбор зависит от архитектуры backend, модели угроз (threat model), SSR, нескольких клиентов и требований к отзыву сессии.

## Состояния сессии

```text
unknown
  -> bootstrap success -> authenticated
  -> no session        -> unauthenticated

unauthenticated
  -> login success     -> authenticated

authenticated
  -> refresh success   -> authenticated
  -> refresh rejected  -> unauthenticated
  -> logout            -> unauthenticated
```

`unknown` не равен `unauthenticated`. При reload access token в memory потерян, но `HttpOnly` refresh/session cookie ещё может быть действительна. Пока `/auth/refresh` или `/me` не ответил, redirect на login создаёт мигание и способен потерять исходный маршрут.

Auth bootstrap обычно выполняется один раз до принятия решения protected route. Сетевую ошибку следует отличать от отсутствующей сессии: offline пользователь не обязательно выполнил logout.

## Access и refresh token

**Access token** предъявляется серверу ресурсов и живёт недолго. Короткий TTL ограничивает окно использования украденного значения, но требует механизма продолжения сессии.

**Refresh token** позволяет получить новый access token. Он живёт дольше, поэтому является более чувствительным credential. Backend хранит связанное с ним серверное состояние или возможность проверить и отозвать всё семейство токенов.

```text
login
  -> refresh token in HttpOnly cookie
  -> access token in memory
  -> Authorization: Bearer <access>
```

Frontend может декодировать JWT claims для предварительного UX, например показать срок, но не подтверждает подпись и не использует эти данные как серверную проверку доступа. Решение об authorization принимает API.

## Login

При собственной password auth браузер отправляет credentials по HTTPS, сервер проверяет их и создаёт session/refresh state. Ответ устанавливает cookie и, в рассматриваемой схеме, возвращает access token:

```http
Set-Cookie: __Host-refresh=...; Path=/; HttpOnly; Secure; SameSite=Lax
Content-Type: application/json

{"accessToken":"..."}
```

`Set-Cookie` не читается JavaScript. Браузер сохраняет его сам, а frontend проверяет JSON-ответ, сохраняет access token в памяти, загружает `/me` и очищает кеши предыдущего пользователя.

При OAuth 2.0/OpenID Connect публичное браузерное приложение обычно использует Authorization Code flow с PKCE. Оно не может безопасно хранить client secret: любой секрет в бандле доступен пользователю. Identity provider возвращает authorization code через redirect, а code verifier связывает обмен с начавшим его клиентом. Детали redirect URI, `state`, `nonce` и обмена токенами являются отдельным протоколом и не заменяются самодельной передачей пароля приложению.

## Reactive refresh после `401`

```text
подходящий API-запрос -> 401
  -> refresh already running? wait
  -> otherwise POST /auth/refresh
  -> success: store new access token
  -> один раз повторить исходный запрос
  -> failure: clear session
```

Refresh запускают только для запросов, которые действительно используют истёкший access token. Не перехватывают `401` самого login/refresh endpoint, запрос с заведомо неверными credentials или public operation, где refresh не имеет смысла.

`403` обычно не исправляется refresh: сервер понял identity, но отказал в действии. UI показывает access denied или актуализирует permissions, не создавая token loop.

## Single-flight refresh

Если пять API-requests одновременно получили `401`, пять refresh calls способны конфликтовать с rotation. Single-flight хранит общий Promise: первый запрос запускает refresh, остальные ждут тот же результат.

```ts
let accessToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;

function isTokenResponse(value: unknown): value is { accessToken: string } {
  return (
    typeof value === "object" &&
    value !== null &&
    "accessToken" in value &&
    typeof value.accessToken === "string"
  );
}

async function refreshAccessToken() {
  refreshPromise ??= fetch("/auth/refresh", {
    method: "POST",
    credentials: "include",
  })
    .then(async response => {
      if (response.status === 401 || response.status === 403) {
        return null;
      }

      if (!response.ok) {
        throw new Error("Refresh service is unavailable");
      }

      const data: unknown = await response.json();

      if (!isTokenResponse(data)) {
        return null;
      }

      accessToken = data.accessToken;
      return data.accessToken;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}
```

Проверка формы ответа не доказывает криптографическую валидность JWT — это обязанность сервера ресурсов. Она защищает frontend от неожиданной структуры данных API.

## Повтор исходного запроса

```ts
async function authRequest(
  input: RequestInfo,
  init: RequestInit = {},
) {
  const execute = (token: string | null) => {
    const headers = new Headers(init.headers);

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    return fetch(input, { ...init, headers });
  };

  const response = await execute(accessToken);

  if (response.status !== 401) {
    return response;
  }

  const nextToken = await refreshAccessToken();

  if (!nextToken) {
    throw new Error("Unauthenticated");
  }

  return execute(nextToken);
}
```

Пример повторяет запрос ровно один раз, потому что второй ответ возвращается без рекурсии. В production дополнительно проверяют, разрешено ли обновление для этого endpoint и можно ли воспроизвести тело запроса.

Строку, `Blob` или заново созданное JSON-тело можно отправить повторно. Уже прочитанный `ReadableStream`, источник upload progress и некоторые объекты `Request` повторить нельзя без фабрики, создающей новое тело. Для платежа и другой mutation также нужен контракт идемпотентности, иначе сетевой retry способен повторить бизнес-операцию.

## Proactive и reactive refresh

**Proactive refresh** пытается обновить токен незадолго до `exp`. Он уменьшает число `401`, но зависит от расхождения часов сервера и клиента, замедленных фоновых timers и состояния нескольких вкладок.

**Reactive refresh** реагирует на `401` и остаётся необходимым fallback: сервер мог отозвать token раньше срока, изменить session version или отвергнуть его по другой причине.

Практический вариант проверяет срок перед новым API-запросом, но не полагается на один глобальный timer. После возвращения из фоновой вкладки время пересчитывается заново.

## Rotation и reuse detection

При refresh token rotation сервер выдаёт новый refresh token и инвалидирует использованный. Если старый token появляется повторно, это может означать кражу или гонку; backend отзывает token family и требует новый login.

Ротация требует атомарности на сервере. Короткое допустимое окно (grace window) иногда разрешает почти одновременный повтор из-за сети или нескольких вкладок, но увеличивает окно риска. Эту политику определяет сервер аутентификации, а frontend предотвращает лишние параллельные refresh-запросы.

Несколько вкладок имеют отдельную memory. Они могут координировать logout и обновление auth state через `BroadcastChannel`, но передавать access token между вкладками следует только после отдельной оценки угроз. Server-side session остаётся источником истины.

## CSRF и CORS

Refresh cookie отправляется браузером автоматически, поэтому refresh endpoint является CSRF-целью. Защита может сочетать:

- `SameSite` по архитектуре sites;
- проверку `Origin`;
- CSRF token;
- `POST` вместо изменения через safe method;
- ограниченный список разрешённых CORS-origins;
- rotation и привязку refresh state.

Если frontend и API имеют разные origins, `fetch` использует `credentials: "include"`, сервер разрешает конкретный origin и `Access-Control-Allow-Credentials: true`, а cookie должна пройти политики SameSite и браузера.

CORS управляет чтением ответа JavaScript-кодом. Он не проверяет пользователя и не заменяет CSRF-защиту endpoint.

## Logout

Полный logout состоит из серверной и клиентской частей:

1. Сервер отзывает session/refresh token family.
2. Сервер удаляет cookie теми же `Path`/`Domain` attributes.
3. Frontend очищает access token и identity state.
4. Query caches и персональные persistent data удаляются.
5. Другие вкладки получают событие logout.
6. In-flight requests больше не восстанавливают старую сессию.

Простое удаление access token из memory не отзывает `HttpOnly` refresh cookie. Простое удаление cookie на клиенте невозможно для `HttpOnly`, и даже обычная cookie может не удалиться при несовпавшем `Path`.

## Ключевые уточнения

- `unknown` является состоянием bootstrap, а не синонимом гостя; protected UI ждёт подтверждения сессии.
- Refresh запускается только для подходящего `401`, выполняется single-flight и не применяется как лечение `403`.
- Повтор запроса ограничен одной попыткой и требует воспроизводимого тела и безопасной семантики операции.
- Rotation и reuse detection реализует backend, а frontend уменьшает гонки между запросами и вкладками.
- Logout должен отозвать серверные учётные данные и очистить все клиентские уровни пользовательского состояния.

## Связанные темы

- [Cookies и авторизация](<./Cookies и авторизация.md>)
- [HTTP status codes и ошибки API](<./HTTP status codes и ошибки API.md>)
- [CORS](<./CORS.md>)
- [CSRF](<./CSRF.md>)
- [XSS](<./XSS.md>)
- [Fetch и работа с API](<../JavaScript/Fetch и работа с API.md>)
- [postMessage и BroadcastChannel](<../JavaScript/postMessage и BroadcastChannel.md>)
- [Auth flow и protected routes](<../Frontend System Design/Auth flow и protected routes.md>)

## Источники

- [OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [RFC 7636: Proof Key for Code Exchange](https://www.rfc-editor.org/rfc/rfc7636)
- [MDN: `Set-Cookie`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [OWASP: OAuth 2.0 Protocol Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html)
- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Cookies и авторизация](<./Cookies и авторизация.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [CORS →](<./CORS.md>)
<!-- NOTE-NAV-BOTTOM:END -->
