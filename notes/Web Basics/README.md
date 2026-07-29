# Web Basics

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./URL в адресной строке.md>)

Заметок в разделе: **26**
<!-- SECTION-NAV:END -->

## Маршрут изучения

Раздел идёт от устройства URL и сетевых протоколов к HTTP/API, данным и авторизации, browser security, загрузке приложения и realtime-возможностям.

### 1. URL и сетевые протоколы

- [URL в адресной строке](<./URL в адресной строке.md>)
- [Web protocols](<./Web protocols.md>)
- [HTTP vs HTTPS](<./HTTP vs HTTPS.md>)

Подробный путь от DNS до первого render вынесен в [Что происходит после ввода URL](<../Browser Internals/Что происходит после ввода URL.md>).

### 2. HTTP request и response

- [HTTP запрос](<./HTTP запрос.md>)
- [HTTP методы](<./HTTP методы.md>)
- [HTTP status codes и ошибки API](<./HTTP status codes и ошибки API.md>)

### 3. Проектирование и описание API

- [REST](<./REST.md>)
- [API pagination filtering sorting](<./API pagination filtering sorting.md>)
- [OpenAPI и Swagger](<./OpenAPI и Swagger.md>)

### 4. Данные, cookies и authentication

- [Хранение данных в браузере](<./Хранение данных в браузере.md>)
- [Cookies и авторизация](<./Cookies и авторизация.md>)
- [Auth flow и refresh tokens](<./Auth flow и refresh tokens.md>)

### 5. Browser security

- [CORS](<./CORS.md>)
- [XSS](<./XSS.md>)
- [CSRF](<./CSRF.md>)
- [CSP и security headers](<./CSP и security headers.md>)
- [OWASP Top 10](<./OWASP Top 10.md>)

Общая модель угроз и хранение token глубже разобраны в [Frontend threat model](<../Security/Frontend threat model.md>) и [Token storage XSS CSRF tradeoffs](<../Security/Token storage XSS CSRF tradeoffs.md>).

### 6. Доставка и производительность приложения

- [HTTP caching](<./HTTP caching.md>)
- [Bundlers и code splitting](<./Bundlers и code splitting.md>)
- [Critical Render Path](<./Critical Render Path.md>)
- [Core Web Vitals](<./Core Web Vitals.md>)

Механика browser rendering продолжается в [Rendering pipeline reflow repaint composite](<../Browser Internals/Rendering pipeline reflow repaint composite.md>) и [Main thread long tasks и responsiveness](<../Browser Internals/Main thread long tasks и responsiveness.md>).

### 7. Realtime и фоновые возможности

- [Realtime transports](<./Realtime transports.md>)
- [WebSocket](<./WebSocket.md>)
- [SSE](<./SSE.md>)
- [Web Workers](<./Web Workers.md>)
- [Service Workers и PWA](<./Service Workers и PWA.md>)
