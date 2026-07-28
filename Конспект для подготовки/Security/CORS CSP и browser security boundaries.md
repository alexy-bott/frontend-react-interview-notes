---
aliases:
  - browser security boundaries
  - same-origin policy
  - CORS vs CSP
  - security headers
---

#### Быстрый ответ

Same-origin policy, CORS и CSP регулируют разные границы. Origin состоит из scheme, host и port. Same-origin policy ограничивает, как JavaScript одного origin читает данные другого. CORS позволяет server через response headers дать выбранным origins доступ к cross-origin response. CSP ограничивает ресурсы и направления соединений самой страницы.

CORS не является authentication или authorization: `curl`, mobile app и backend не обязаны соблюдать browser CORS. Более того, некоторые cross-origin requests browser отправляет без preflight, но не отдаёт response вызывающему JavaScript. Поэтому API всё равно проверяет session, permissions, validation и CSRF.

CSP снижает вероятность и ущерб XSS, разрешая scripts по nonce/hash и ограничивая `connect-src`, `frame-ancestors`, `object-src`, `base-uri` и другие источники. Она дополняет безопасные DOM API и sanitization, а не исправляет опасный вывод данных автоматически.

#### Границы origin

```text
origin = scheme + host + port
```

`https://app.example.com` и `https://api.example.com` имеют разные hosts и разные origins. `https://example.com` и `http://example.com` различаются scheme. Path на origin не влияет.

Same-origin policy защищает главным образом чтение cross-origin данных. Web допускает некоторые cross-origin действия: переходы, загрузку ресурсов и отправку HTML forms. Из-за этого запрет чтения response сам по себе не предотвращает CSRF.

Для намеренного обмена сообщениями между windows/iframes используют `postMessage`. Получатель проверяет точный `event.origin`, ожидаемый `event.source` и структуру `event.data`; отправитель указывает конкретный `targetOrigin`, а не `*`, если данные чувствительны.

#### CORS

Server включает в response CORS headers. Browser сравнивает `Origin` запроса с `Access-Control-Allow-Origin` и только после успешной проверки открывает response JavaScript-коду.

Preflight — автоматический `OPTIONS` перед запросом, который не относится к категории CORS-safelisted. Он спрашивает разрешённые method, headers и credentials policy. Preflight не подтверждает пользователя и не заменяет проверку actual request.

Credentialed flow:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
Vary: Origin
```

```ts
await fetch("https://api.example.com/me", {
  credentials: "include",
});
```

При credentials нельзя вернуть `Access-Control-Allow-Origin: *`: нужен точный разрешённый origin. Если server динамически отражает origin, он сначала проверяет его по строгому allowlist и добавляет `Vary: Origin`, чтобы shared cache не смешал responses для разных origins.

CORS error часто скрывает JavaScript-коду детали response. Диагностика проверяет Network/Console, preflight и actual response headers, но конфиденциальную причину server не должен раскрывать чужому origin.

#### CSP

CSP передают предпочтительно HTTP-header `Content-Security-Policy`. Политика по allowlist доменов часто остаётся широкой; строгая CSP для scripts обычно использует случайный nonce для каждого response или допустимые hashes и не включает `unsafe-inline`/`unsafe-eval` без подтверждённой причины.

| Directive | Что ограничивает |
| --- | --- |
| `script-src` | JavaScript sources и inline execution |
| `connect-src` | `fetch`, XHR, WebSocket и EventSource destinations |
| `img-src`, `font-src`, `style-src` | соответствующие ресурсы |
| `frame-ancestors` | кто может встроить страницу во frame |
| `object-src` | plugin content; в строгой политике часто `'none'` |
| `base-uri` | допустимый `<base>` и подмена относительных URL |

`Content-Security-Policy-Report-Only` собирает violations без блокировки и помогает подготовить policy. Затем enforcement включают после анализа reports. Reports могут содержать URL и другие данные, поэтому endpoint также требует data minimization.

CSP не предотвращает все последствия разрешённого script. Скомпрометированный vendor на разрешённом origin выполняется с правами страницы; поэтому policy дополняют SRI, self-hosting, sandboxed iframe и сокращением third-party code.

#### Как механизмы сочетаются

| Задача | Основной механизм | Дополнение |
| --- | --- | --- |
| Frontend читает cross-origin API | CORS | authentication и authorization на API |
| Cookie отправляется cross-site | SameSite/CSRF controls | CORS для JS-readable credentialed response |
| Ограничить выполнение scripts | CSP | безопасные sinks, sanitization, SRI |
| Защитить transport | HTTPS | HSTS и все application-level controls |
| Встроить iframe | CSP `frame-ancestors`, `sandbox` | точный `postMessage` protocol |

#### Ключевые уточнения

- Same-origin policy ограничивает browser JavaScript, но допускает часть cross-origin отправок и загрузок.
- CORS определяет, может ли browser-код прочитать response; API authorization действует для любого клиента.
- Preflight проверяет CORS policy, а не личность и права пользователя.
- Credentialed CORS требует точного origin и не совместим с wildcard `*` в allow-origin.
- CSP ограничивает возможности страницы и дополняет предотвращение XSS.
- `postMessage` создаёт явный cross-origin channel и требует проверки origin, source и data schema.

#### Связанные темы

- [[Конспект для подготовки/Web Basics/CORS]]
- [[Конспект для подготовки/Web Basics/CSP и security headers]]
- [[Конспект для подготовки/Web Basics/Cookies и авторизация]]
- [[Конспект для подготовки/Web Basics/CSRF]]
- [[Конспект для подготовки/Web Basics/XSS]]
- [[Конспект для подготовки/Web Basics/HTTP vs HTTPS]]

#### Источники

- [MDN: Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
- [MDN: Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
- [OWASP: Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
