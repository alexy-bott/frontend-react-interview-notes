# Хранение токенов — XSS, CSRF и компромиссы

<!-- NOTE-NAV-TOP:START -->
[← Модель угроз фронтенда](<./01 Модель угроз фронтенда.md>) · [↑ Безопасность](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [CORS, CSP и границы безопасности браузера →](<./03 CORS, CSP и границы безопасности браузера.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Session ID, refresh token и долгоживущие credentials не следует хранить в `localStorage` или `sessionStorage`: любой JavaScript в origin может их прочитать, а одна XSS-уязвимость позволяет унести credential и использовать вне браузера. Для first-party web app предпочтительна серверная session или BFF с cookie `HttpOnly; Secure; SameSite`.

`HttpOnly` запрещает чтение cookie через `document.cookie`, но не обезвреживает XSS: вредный код может выполнять запросы в текущей сессии. Поскольку cookie отправляется браузером автоматически, state-changing запросы дополнительно защищают от CSRF через `SameSite`, CSRF token и проверку `Origin`/`Referer` по выбранному протоколу.

Если OAuth-архитектура требует access token в JavaScript, его обычно держат кратковременно в памяти и ограничивают audience, scope и lifetime. Перезагрузка и несколько вкладок тогда требуют отдельного refresh/session flow. Универсального места нет, но Web Storage для authentication tokens не является безопасным вариантом по умолчанию.

## Модели сессии

| Модель | Где credential | Основные свойства |
| --- | --- | --- |
| Server session | opaque session ID в HttpOnly cookie | сервер хранит session state и revoke |
| BFF | browser общается с Backend for Frontend через cookie | OAuth tokens остаются на серверной стороне |
| JS OAuth client | краткий access token в memory | сложнее reload/multi-tab, XSS действует в текущем контексте |
| Web Storage token | `localStorage`/`sessionStorage` | credential читается любым script origin; не рекомендуется для session IDs/tokens |

Opaque token — непонятный клиенту случайный идентификатор без встроенных claims. BFF (Backend for Frontend) — серверный слой, созданный под frontend: он держит tokens и обращается к downstream API от имени browser session.

## XSS и место хранения

XSS означает выполнение чужого JavaScript в origin приложения. Такой код получает права обычного frontend: читает Web Storage, DOM и JS-доступные tokens, вызывает API, меняет форму и отправляет данные наружу в пределах browser policies.

HttpOnly cookie уменьшает переносимость украденной сессии: script не может прочитать её значение. Но пока XSS исполняется на странице, browser приложит cookie к разрешённому запросу. Поэтому storage policy дополняется предотвращением XSS, CSP, короткими sessions, чувствительным re-auth и server-side authorization.

In-memory token исчезает при reload и не лежит в persistent storage. Это уменьшает окно кражи после завершения страницы, но не защищает token от XSS, исполняющегося в тот же момент.

## CSRF при cookie-based auth

CSRF использует автоматическую отправку browser credentials, чтобы инициировать запрос от имени пользователя. Same-origin policy может скрыть ответ атакующему, но не всегда препятствует отправке запроса.

Комбинация защиты зависит от архитектуры:

- `SameSite=Lax` или `Strict` ограничивает cross-site cookie requests;
- непредсказуемый CSRF token связывается с session и передаётся способом, который чужой сайт не может воспроизвести;
- server проверяет `Origin`, а при его отсутствии — допустимый `Referer` по строгому allowlist;
- state-changing операции не выполняются через `GET`;
- CORS разрешает credentialed requests только доверенным точным origins, но не заменяет CSRF-защиту.

`SameSite=None` требуется для некоторых cross-site сценариев и допускается только вместе с `Secure`; такой flow нуждается в особенно явной CSRF-модели. Subdomains являются same-site, поэтому компрометация соседнего поддомена тоже учитывается.

## Cookie attributes

```http
Set-Cookie: __Host-session=<opaque-id>; Path=/; HttpOnly; Secure; SameSite=Lax
```

| Attribute | Что даёт |
| --- | --- |
| `HttpOnly` | скрывает значение от `document.cookie` |
| `Secure` | отправляет cookie только по HTTPS, кроме специальных browser exceptions для localhost |
| `SameSite` | ограничивает отправку в cross-site context |
| `Path` | ограничивает путь отправки, но не является надёжной границей чтения |
| `Domain` | расширяет cookie на subdomains; отсутствие делает cookie host-only |
| `Max-Age`/`Expires` | задаёт persistence, но server revoke остаётся отдельным механизмом |

Prefix `__Host-` требует `Secure`, `Path=/` и отсутствия `Domain`, поэтому снижает риск подмены cookie с subdomain. Имя не заменяет остальные свойства session.

## JWT и refresh

Подписанный JWT обеспечивает целостность claims, но payload обычно только Base64URL-encoded и читается клиентом. В него не помещают secrets и лишнюю PII. Server проверяет signature, допустимый algorithm, issuer, audience, expiration и authorization для конкретного resource.

Короткий access token ограничивает время злоупотребления, но не отменяет revoke для критических сценариев. Refresh token имеет более широкую ценность и защищается rotation, reuse detection, server-side revoke и ограничениями lifetime. Refresh, logout, password change и account recovery являются чувствительными endpoints и получают CSRF/authorization/monitoring controls.

## Практический выбор

| Ситуация | Базовое решение |
| --- | --- |
| First-party SPA + собственный backend | BFF или server session в HttpOnly cookie |
| Next.js SSR | server-readable session cookie, без передачи refresh token client code |
| Публичный OAuth client без BFF | Authorization Code + PKCE и краткий token in memory по актуальному OAuth guidance |
| Несколько вкладок | server session или координация refresh без раскрытия долгоживущего token |
| Logout/компрометация | server invalidate/revoke + очистка browser state |

Конкретное решение зависит от identity provider, доменов, SSR и API, поэтому security flow документируют end-to-end: login, refresh, concurrent requests, expiration, logout, revoke и восстановление после ошибки.

## Ключевые уточнения

- Web Storage доступен JavaScript и не подходит для session IDs и долгоживущих authentication tokens по умолчанию.
- HttpOnly защищает конфиденциальность cookie, а не все действия открытой session при XSS.
- Cookie-based authentication требует явной CSRF-модели для изменяющих состояние запросов.
- SameSite снижает риск, но его режим выбирают вместе с domain architecture и дополнительными controls.
- JWT signature не шифрует payload и не заменяет server-side authorization.
- BFF сохраняет OAuth tokens на серверной стороне и даёт браузеру только session cookie.

## Связанные темы

- [Cookie и авторизация](<../Основы веб-платформы/11 Cookie и авторизация.md>)
- [Процесс авторизации и refresh-токены](<../Основы веб-платформы/12 Процесс авторизации и refresh-токены.md>)
- [XSS](<../Основы веб-платформы/14 XSS.md>)
- [CSRF](<../Основы веб-платформы/15 CSRF.md>)
- [CORS](<../Основы веб-платформы/13 CORS.md>)
- [Модель угроз фронтенда](<./01 Модель угроз фронтенда.md>)

## Источники

- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP: Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP: HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)
- [MDN: Secure cookie configuration](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Cookies)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Модель угроз фронтенда](<./01 Модель угроз фронтенда.md>) · [↑ Безопасность](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [CORS, CSP и границы безопасности браузера →](<./03 CORS, CSP и границы безопасности браузера.md>)
<!-- NOTE-NAV-BOTTOM:END -->
