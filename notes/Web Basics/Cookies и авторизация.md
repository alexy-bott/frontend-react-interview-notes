# Cookies и авторизация

<!-- NOTE-NAV-TOP:START -->
[← Хранение данных в браузере](<./Хранение данных в браузере.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Auth flow и refresh tokens →](<./Auth flow и refresh tokens.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Cookie — небольшая запись, которую сервер устанавливает через `Set-Cookie`, а браузер автоматически отправляет в заголовке `Cookie` подходящих HTTP-запросов. Условия задают атрибуты: `Domain`, `Path`, `Expires`/`Max-Age`, `Secure`, `HttpOnly` и `SameSite`.

Для аутентификации cookie обычно хранит непрозрачный идентификатор сессии (session ID) или refresh token. `HttpOnly` запрещает чтение из JavaScript, `Secure` ограничивает отправку HTTPS-соединением, `SameSite` ограничивает часть cross-site запросов. Эти меры дополняют друг друга, но не заменяют защиту от XSS, CSRF и серверную проверку прав.

Сессия (session), JWT и cookie — разные сущности. Сессия описывает модель состояния на сервере, JWT — формат подписанного токена, cookie — способ хранения и автоматической доставки. JWT можно передавать и в cookie, и в `Authorization`, а cookie может содержать обычный случайный идентификатор сессии.

## Как cookie участвует в запросе

```text
запрос на вход
  -> сервер проверяет учётные данные
  -> заголовок ответа Set-Cookie
  -> браузер сохраняет cookie
  -> подходящий следующий запрос
  -> заголовок запроса Cookie
  -> сервер находит сессию или проверяет токен
```

```http
Set-Cookie: __Host-session=abc123; Path=/; HttpOnly; Secure; SameSite=Lax
```

Frontend JavaScript не читает `Set-Cookie` из ответа `fetch`: этот заголовок ответа недоступен скрипту. Браузер обрабатывает его самостоятельно.

Cookie отправляется только если URL и контекст подходят её attributes. Наличие записи в DevTools не означает, что она войдёт в каждый запрос.

## Attributes

| Attribute | Что определяет |
| --- | --- |
| `Domain` | hosts, которым cookie может отправляться |
| `Path` | URL-пути, для которых cookie включается в запрос |
| `Max-Age` / `Expires` | срок хранения |
| `Secure` | отправку только по защищённому соединению |
| `HttpOnly` | недоступность через `document.cookie` |
| `SameSite` | cross-site контексты, в которых cookie разрешено отправлять |
| `Partitioned` | отдельное хранение cookie по top-level site |

Если `Domain` не указан, cookie является host-only и не отправляется поддоменам. `Domain=example.com` расширяет область на подходящие subdomains и увеличивает последствия компрометации одного из них.

`Path=/admin` ограничивает отправку URL-путём, но не создаёт security boundary. Код другого path того же origin способен обратиться к `/admin`, а доступ JavaScript к cookie определяется `HttpOnly`, не `Path`.

`Max-Age` задаёт срок в секундах и при наличии имеет приоритет над `Expires`. Cookie без обоих атрибутов является session cookie, но восстановление сессии браузером способно вернуть её вместе с вкладками. Критичный logout не строят только на предположении «закрытие браузера всё удалит».

Чтобы удалить cookie, сервер задаёт истёкший срок с теми же `Path` и `Domain`, по которым она была создана:

```http
Set-Cookie: __Host-session=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax
```

## `HttpOnly`, `Secure` и XSS

`HttpOnly` не позволяет вредоносному скрипту прочитать значение через `document.cookie`. Это снижает риск вынести токен сессии и использовать его на другом устройстве.

Однако XSS выполняется внутри страницы пользователя и может отправлять разрешённые запросы, читать доступные ответы и менять UI. `HttpOnly` ограничивает последствия, но не превращает XSS в безопасный сценарий.

`Secure` запрещает отправку cookie по обычному HTTP. Он не шифрует значение отдельно: защиту канала даёт HTTPS. Без `HttpOnly` JavaScript на HTTPS-странице всё ещё может прочитать cookie.

## `SameSite`: site не равен origin

SameSite сравнивает sites, а не origins. Упрощённо site основан на схеме и registrable domain. Поэтому `https://app.example.com` и `https://api.example.com` являются разными origins, но могут быть same-site.

| Значение | Поведение |
| --- | --- |
| `Strict` | cookie не отправляется в cross-site контексте |
| `Lax` | разрешает same-site requests и ограниченный набор top-level cross-site navigations с безопасным методом |
| `None` | разрешает cross-site отправку и требует `Secure` |

`Strict` сильнее против CSRF, но способен ломать переход по внешней ссылке в уже авторизованный раздел. `Lax` часто удобнее основной session cookie, однако защищает не каждую схему. Высокорисковые изменения дополняют CSRF token, проверкой `Origin`/`Referer` и запретом state changes через safe methods.

Поведение сторонних cookie дополнительно ограничивается политиками приватности браузера. `SameSite=None` означает разрешение со стороны cookie, а не гарантию, что конкретный браузер всегда примет и отправит стороннюю cookie.

## Cookie prefixes

Префиксы добавляют проверяемые браузером ограничения:

```text
__Secure-name  -> обязательно Secure и установка из HTTPS
__Host-name    -> Secure, Path=/, отсутствует Domain
```

`__Host-` полезен для основной session cookie: поддомен не может задать Domain-cookie с тем же именем для всего родительского домена. Prefix работает только если имя и attributes точно соответствуют правилам.

`Partitioned` включает CHIPS: сторонняя cookie хранится отдельно для каждого top-level site. Это уменьшает cross-site tracking и даёт встроенному сервису изолированное состояние. Атрибут требует `Secure`; доступность и сопутствующие политики браузеров проверяют для целевых окружений.

## Session и JWT

**Server session.** Cookie содержит случайный ID, а сервер хранит пользователя, срок и состояние отзыва. Logout и немедленная блокировка просты, но session store должен быть доступен всем экземплярам backend.

**JWT access token.** Токен содержит claims и подпись. Сервер может проверить подпись без чтения session record, но всё равно часто обращается к данным прав, denylist или token version.

Payload JWT кодируется base64url и обычно читается без ключа. Подпись защищает целостность, а не конфиденциальность. Пароли, refresh secrets и лишние персональные данные в claims не кладут.

Долгий TTL JWT затрудняет немедленный revoke. Короткий access token ограничивает окно утечки, а refresh/session хранит возможность продолжить вход и требует rotation или серверного отзыва.

## Варианты хранения данных аутентификации

| Вариант | Плюсы | Основные риски и цена |
| --- | --- | --- |
| Сессия в `HttpOnly` cookie | токен недоступен JavaScript, простой отзыв на сервере | автоматическая отправка требует CSRF-дизайна |
| Access token in memory + refresh cookie | access не хранится постоянно, refresh закрыт `HttpOnly` | нужен bootstrap/refresh и защита refresh endpoint |
| Токен в Web Storage | просто переживает перезагрузку и добавляется в заголовок | XSS может прочитать и вынести токен |
| Access token в `HttpOnly` cookie | JavaScript не читает токен | каждый запрос с аутентификацией использует cookie и требует CSRF/CORS-модели |

Универсально «идеального» места нет. Решение следует из модели угроз: какие XSS/CSRF риски допустимы, нужен ли cross-origin API, как работает logout, несколько вкладок, SSR и мобильный клиент.

## Cross-origin запрос с cookie

```js
await fetch("https://api.example.com/me", {
  credentials: "include",
});
```

Для чтения cross-origin ответа сервер должен разрешить конкретный origin и credentials:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
```

Cookie дополнительно должна пройти `Domain`, `Path`, `Secure`, `SameSite` и правила приватности браузера. CORS определяет, может ли скрипт прочитать ответ; он не заменяет аутентификацию и не является общей CSRF-защитой.

## Authentication и authorization

Authentication (AuthN) устанавливает, кто пользователь. Authorization (AuthZ) проверяет, разрешено ли ему конкретное действие над конкретным ресурсом.

Frontend скрывает запрещённую кнопку для хорошего UX, но сервер проверяет авторизацию на каждом endpoint. Пользователь может вызвать HTTP-запрос без UI, а claims и состояние доступа способны измениться после загрузки страницы.

## Ключевые уточнения

- Cookie является HTTP-механизмом доставки состояния, session — серверной моделью, JWT — форматом токена.
- `HttpOnly` закрывает чтение значения через JavaScript, но XSS всё ещё может действовать внутри текущей сессии.
- `SameSite` сравнивает sites, а CORS — origins; эти границы нельзя использовать как взаимозаменяемые.
- Подпись JWT подтверждает целостность claims, но не шифрует payload и не решает отзыв автоматически.
- AuthN устанавливает identity, а AuthZ проверяет право; UI-проверка не заменяет серверную.

## Связанные темы

- [Auth flow и refresh tokens](<./Auth flow и refresh tokens.md>)
- [CSRF](<./CSRF.md>)
- [XSS](<./XSS.md>)
- [CORS](<./CORS.md>)
- [HTTP vs HTTPS](<./HTTP vs HTTPS.md>)
- [Хранение данных в браузере](<./Хранение данных в браузере.md>)
- [Token storage XSS CSRF tradeoffs](<../Security/Token storage XSS CSRF tradeoffs.md>)

## Источники

- [RFC 6265: HTTP State Management Mechanism](https://www.rfc-editor.org/rfc/rfc6265)
- [MDN: `Set-Cookie`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [MDN: Secure cookie configuration](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Cookies)
- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Хранение данных в браузере](<./Хранение данных в браузере.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Auth flow и refresh tokens →](<./Auth flow и refresh tokens.md>)
<!-- NOTE-NAV-BOTTOM:END -->
