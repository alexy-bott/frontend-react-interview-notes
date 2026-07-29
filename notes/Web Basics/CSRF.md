# CSRF

<!-- NOTE-NAV-TOP:START -->
[← XSS](<./XSS.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [CSP и security headers →](<./CSP и security headers.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

CSRF (Cross-Site Request Forgery, межсайтовая подделка запроса) — атака, при которой чужой сайт заставляет браузер пользователя отправить изменяющий запрос доверенному приложению. Сервер видит автоматически приложенную cookie сессии и может принять запрос за намеренное действие пользователя.

Атакующему не обязательно читать ответ. Достаточно вызвать перевод, смену email или logout через HTML-форму, navigation или другой разрешённый браузерный запрос. Same-Origin Policy и CORS в первую очередь ограничивают чтение, поэтому сами по себе не подтверждают намерение пользователя.

Защита сочетает явный CSRF-токен, подходящий `SameSite`, проверку `Origin`/`Referer` или Fetch Metadata, корректные HTTP-методы и дополнительное подтверждение критичных операций. Конкретный набор зависит от того, какие учётные данные браузер отправляет автоматически.

## Условия атаки

```text
пользователь авторизован на bank.example
  -> открывает evil.example
  -> evil.example создаёт POST на bank.example/transfer
  -> браузер автоматически добавляет подходящую cookie сессии
  -> сервер не проверяет источник и CSRF-токен
  -> операция выполняется
```

Для классического CSRF нужны:

1. Автоматически прикладываемые учётные данные (ambient credentials) — cookie, клиентский сертификат или другое значение, которое браузер добавляет без участия кода доверенного приложения.
2. State-changing endpoint, вызываемый доступным cross-site способом.
3. Отсутствие непредсказуемого доказательства, доступного только доверенному frontend.
4. Возможность составить достаточно данных запроса.

Response может остаться недоступным атакующему из-за Same-Origin Policy. Для атаки на состояние это не препятствие.

## Пример уязвимого запроса

Если endpoint принимает обычную HTML-form:

```html
<form method="post" action="https://bank.example/transfer">
  <input name="recipient" value="attacker" />
  <input name="amount" value="1000" />
</form>

<script>
  document.forms[0].submit();
</script>
```

Браузер способен отправить форму cross-site. Отсутствие CORS-заголовков помешает `evil.example` прочитать ответ через JavaScript, но не откатит уже выполненный перевод.

## SameSite

`SameSite` управляет отправкой cookie в cross-site контексте:

- `Strict` сильнее всего ограничивает cross-site requests, но может нарушить вход по внешней ссылке;
- `Lax` разрешает ограниченные top-level navigations с safe method и блокирует многие cross-site subrequests/POST;
- `None` разрешает cross-site cookie и требует `Secure`.

SameSite является важной baseline-защитой, но не единственным контролем для критичных действий. Browser behavior, legacy clients и архитектура продукта могут отличаться.

Site не равен origin. `app.example.com` и скомпрометированный `blog.example.com` могут быть same-site, хотя имеют разные origins. SameSite не отделяет их так, как Origin check или секретный token.

## Synchronizer token

Сервер создаёт непредсказуемый токен, связывает его с сессией и передаёт доверенному frontend. Для небезопасного метода, меняющего состояние, клиент возвращает токен в теле или пользовательском заголовке:

```http
POST /transfer HTTP/1.1
Cookie: __Host-session=abc123
X-CSRF-Token: random-session-bound-value
Content-Type: application/json

{"recipient":"user-42","amount":1000}
```

Сервер проверяет токен до бизнес-операции. Чужой сайт может отправить cookie, но не знает токен из ответа или DOM другого origin.

Token должен быть непредсказуемым, привязанным к session и не попадать в URL. Query string и URL могут сохраниться в history, logs и referrer.

Пользовательский заголовок удобен для SPA и API. HTML-форма не может добавить произвольный заголовок, а cross-origin `fetch` с ним требует preflight. Однако сервер всё равно проверяет токен, а не полагается только на факт preflight.

## Double-submit cookie

При double-submit сервер отправляет CSRF cookie, доступную JavaScript. Frontend копирует значение в тело или заголовок, а сервер сравнивает два значения.

Простое равенство cookie и заголовка уязвимо, если атакующий способен внедрить cookie через контролируемый поддомен или другой путь. Более надёжный вариант подписывает токен и связывает его с текущей сессией. Cookie сессии при этом остаётся `HttpOnly`, а CSRF cookie намеренно доступна JavaScript.

Префикс cookie `__Host-`, отсутствие `Domain`, `Secure` и строгий список разрешённых origins уменьшают возможность внедрения cookie, но не заменяют криптографическую связь там, где она требуется моделью угроз.

## Проверка `Origin` и `Referer`

Запрос, меняющий состояние, обычно содержит `Origin`. Сервер сравнивает полное нормализованное значение со списком разрешённых origins:

```text
https://app.example.com
```

Нельзя проверять подстроку или suffix без URL parsing. `https://app.example.com.evil.test` не является доверенным origin.

Если `Origin` отсутствует по допустимой причине, сервер может использовать `Referer` по явно выбранной политике. Оба заголовка контролируются браузером, но настройки proxy и приватности влияют на наличие данных. Для высокорисковой операции неизвестный источник обычно отклоняют, а исключения проектируют отдельно.

## Fetch Metadata

Современные браузеры добавляют `Sec-Fetch-Site`, `Sec-Fetch-Mode` и связанные заголовки Fetch Metadata. Сервер может отклонять неожиданные cross-site запросы, меняющие состояние, до обработки:

```text
Sec-Fetch-Site: cross-site
```

Это хороший дополнительный слой и способ защитить endpoints, где token трудно внедрить. Поддержку клиентов и необходимые cross-site integrations учитывают явно; один Fetch Metadata check не заменяет всю модель.

## HTTP-методы и подтверждение

`GET`, `HEAD` и другие безопасные методы не изменяют бизнес-состояние. Ссылки, изображения, crawlers, prefetch и browser navigation способны вызывать `GET` без намерения совершить mutation.

`POST` сам по себе не защищает от CSRF: HTML-форма умеет его отправлять. Метод только отделяет изменяющую операцию и позволяет применить обязательные серверные middleware.

Для смены password, MFA, payout details и крупного платежа полезна re-authentication или transaction confirmation. CSRF token подтверждает происхождение запроса, но украденная открытая сессия и социальная инженерия требуют дополнительных мер.

## Bearer token в заголовке

Если access token хранится у доверенного frontend и вручную добавляется в `Authorization`, чужой сайт не знает значение и не может поставить заголовок простой HTML-формой. Это существенно уменьшает классический риск CSRF.

Риск возвращается, если сервер также принимает auth cookie, токен в URL или запасные учётные данные. Кроме того, доступный JavaScript токен повышает последствия XSS: скрипт внутри origin может прочитать его и использовать вне текущей вкладки.

Выбор между cookie и хранением bearer token рассматривает XSS и CSRF вместе, а не объявляет один вариант полностью безопасным.

## CORS и CSRF

Строгий CORS может не позволить атакующему отправить JSON-запрос вне safelist с пользовательским заголовком, потому что preflight не пройдёт. Но он не останавливает safelisted запрос через форму, navigation и другие способы, а ошибочная конфигурация origin открывает путь снова.

Поэтому CORS рассматривают как браузерный протокол разрешения чтения и дополнительное ограничение способов запроса. CSRF-защита отдельно доказывает, что изменяющая операция пришла из разрешённого контекста с ожидаемым токеном.

## XSS и CSRF

XSS выполняет JavaScript внутри доверенного origin и часто может прочитать CSRF token или вызвать легитимную функцию приложения. Поэтому предотвращение XSS является необходимой частью CSRF-защиты.

Разница остаётся важной: CSRF приходит извне и использует ambient credentials, а XSS уже исполняется внутри security boundary приложения. Механизмы уменьшают разные пути атаки.

## Какие endpoints защищать

CSRF-проверка нужна не только transfer:

- изменение профиля, email, password и MFA;
- refresh, logout и привязка identity provider;
- создание API key;
- изменение permissions;
- upload/import;
- административные операции;
- login, если login CSRF способен привязать жертву к аккаунту атакующего.

Middleware удобен, но endpoint inventory проверяют отдельно: нестандартный content type, старый route или GraphQL mutation может обойти общий фильтр.

## Ключевые уточнения

- CSRF использует учётные данные, которые браузер прикладывает автоматически; чтение ответа атакующему обычно не требуется.
- SameSite уменьшает cross-site отправку cookie, но same-site subdomain и критичные операции требуют дополнительных проверок.
- CSRF-токен подтверждает доступ доверенного frontend к значению, связанному с сессией, а пользовательский заголовок сам по себе не является секретом.
- CORS ограничивает cross-origin доступ браузера и часть форм запросов, но не заменяет проверку источника изменяющей операции.
- Bearer token в заголовке снижает классический CSRF, тогда как XSS может украсть доступный JavaScript токен; угрозы оценивают вместе.

## Связанные темы

- [XSS](<./XSS.md>)
- [Cookies и авторизация](<./Cookies и авторизация.md>)
- [Auth flow и refresh tokens](<./Auth flow и refresh tokens.md>)
- [CORS](<./CORS.md>)
- [HTTP методы](<./HTTP методы.md>)
- [Token storage XSS CSRF tradeoffs](<../../Конспект для подготовки/Security/Token storage XSS CSRF tradeoffs.md>)

## Источники

- [OWASP: Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN: CSRF](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF)
- [web.dev: Protect your resources from web attacks with Fetch Metadata](https://web.dev/articles/fetch-metadata)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← XSS](<./XSS.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [CSP и security headers →](<./CSP и security headers.md>)
<!-- NOTE-NAV-BOTTOM:END -->
