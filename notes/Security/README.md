# Security

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Frontend threat model.md>)

Заметок в разделе: **4**
<!-- SECTION-NAV:END -->

## Маршрут изучения

Раздел идёт от системной модели угроз к browser session, ограничениям origin и цепочке поставки кода.

### 1. Активы и границы доверия

- [Frontend threat model](<./Frontend threat model.md>)

### 2. Session, XSS и CSRF

- [Token storage XSS CSRF tradeoffs](<./Token storage XSS CSRF tradeoffs.md>)

### 3. Browser security boundaries

- [CORS CSP и browser security boundaries](<./CORS CSP и browser security boundaries.md>)

### 4. Dependencies, build и third-party code

- [Supply chain secrets и third-party scripts](<./Supply chain secrets и third-party scripts.md>)

Дополнительные карточки XSS, CSRF, cookies, CORS, CSP и OWASP находятся в [Web Basics](<../Web Basics/README.md>). Сначала для риска определяется угроза и авторитетный слой защиты, затем выбираются конкретные browser и server controls.
