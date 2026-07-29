---
aliases:
  - Nginx frontend
  - static serving
  - SPA Nginx
  - nginx.conf frontend
---

#### Быстрый ответ

Nginx может отдавать собранную SPA как static files: `index.html`, hashed JS/CSS и media. Для client-side routing он сначала ищет реальный file, а для неизвестного route возвращает `index.html`; API и assets должны иметь отдельные locations, чтобы отсутствующий script или `/api` не маскировался HTML-ответом.

HTML и versioned assets кешируют по-разному. `index.html` допускают хранить только с обязательной revalidation, потому что он ссылается на текущие chunks. Content-hashed assets кешируют надолго. Security headers и compression проверяют на фактических responses: Nginx `add_header` имеет особенности inheritance, из-за которых header верхнего уровня может исчезнуть при добавлении другого header внутри `location`.

#### Ключевая схема

```text
request
-> API/proxy location? -> upstream
-> real asset?         -> file + asset cache
-> known SPA route?    -> index.html + revalidation
-> client router       -> screen/not-found
```

| Задача | Механизм | Проверка |
| --- | --- | --- |
| Static files | `root`, `try_files` | status, MIME, body |
| SPA fallback | `/index.html` | refresh nested route |
| Asset cache | content hash + long `max-age` | повторный request/cache hit |
| HTML freshness | `no-cache`/revalidation | после deploy виден новый manifest |
| Compression | gzip/Brotli или precompressed files | `Content-Encoding`, `Vary` |
| Security | headers по policy приложения | каждый response/location |

#### Базовая модель

URL `/settings/profile` не обязан существовать как file: после загрузки SPA его понимает client router. `try_files $uri $uri/ /index.html` возвращает shell, но catch-all нельзя ставить перед real assets/API. Иначе запрос отсутствующего `app.abc.js` получит status 200 и HTML, а browser покажет misleading MIME/syntax error.

`Cache-Control: no-cache` не запрещает хранение: browser может сохранить response, но обязан revalidate перед повторным использованием. `no-store` запрещает хранение и часто избыточен для публичного `index.html`. Hashed asset не меняет content под тем же URL, поэтому `max-age=31536000, immutable` безопасен при сохранении старых files на время жизни открытых clients.

Nginx выбирает наиболее подходящий `location`, и directives наследуются по собственным правилам. В частности, если текущий level содержит хотя бы один `add_header`, headers предыдущего level по обычной модели не наследуются. Поэтому security/cache headers удобно вынести в snippet и явно подключать там, где задаются location-level headers.

#### Развернутый ответ

**Deploy.** Открытая вкладка со старым runtime может позже запросить старый lazy chunk. Atomic upload и retention прежних hashed assets предотвращают `ChunkLoadError`. Очистка CDN сразу после публикации нового HTML ломает long-lived sessions.

**SSR.** Nginx может завершать TLS, отдавать static assets и proxy-ровать остальные requests в Node process. `try_files ... /index.html` для SSR route неверен: HTML должен создать application server, а не статический shell.

**Headers.** CSP строится по реальным script/style/connect sources и сначала проверяется в Report-Only mode. HSTS включают только на HTTPS origin с осознанным scope. `nosniff`, Referrer-Policy и Permissions-Policy также являются security contracts, а не набором строк для копирования.

**Compression.** Server выбирает representation по `Accept-Encoding` и отвечает соответствующим `Content-Encoding`; shared cache различает варианты через `Vary: Accept-Encoding`. Сжатие уже compressed images обычно не даёт пользы, а HTML/CSS/JS/JSON сжимаются хорошо.

#### Пример

```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  location = /index.html {
    add_header Cache-Control "no-cache" always;
    include /etc/nginx/snippets/frontend-security.conf;
  }

  # Контракт Vite-подобной сборки: все files здесь content-hashed.
  location /assets/ {
    try_files $uri =404;
    add_header Cache-Control "public, max-age=31536000, immutable" always;
    include /etc/nginx/snippets/frontend-security.conf;
  }

  location / {
    try_files $uri $uri/ /index.html;
    include /etc/nginx/snippets/frontend-security.conf;
  }
}
```

`frontend-security.conf` содержит согласованные headers и копируется в image рядом с server config. API location или reverse proxy добавляется до SPA catch-all. Конфиг проверяют `nginx -t` и HTTP-тестами для `/`, nested route, missing asset и cache headers.

#### Ключевые уточнения

- SPA fallback применяется routes, но отсутствующий asset/API должен сохранить корректный `404` или upstream response.
- `no-cache` требует revalidation, а `no-store` запрещает хранение; это разные политики.
- Immutable caching требует content hashes и retention старых chunks после deploy.
- Location-level `add_header` способен отменить inheritance server-level headers, поэтому проверяют каждый тип response.
- Nginx static serving не выполняет SSR; в server-rendered приложении он обычно proxy перед runtime.

#### Связанные темы

- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/Web Basics/HTTP caching]]
- [[Конспект для подготовки/Web Basics/CSP и security headers]]
- [[Конспект для подготовки/Performance/Bundle size и loading strategy]]
- [[Конспект для подготовки/React/React Router]]

#### Источники

- [NGINX: Serving Static Content](https://docs.nginx.com/nginx/admin-guide/web-server/serving-static-content/)
- [NGINX: Core module and try_files](https://nginx.org/en/docs/http/ngx_http_core_module.html#try_files)
- [NGINX: Headers module](https://nginx.org/en/docs/http/ngx_http_headers_module.html)
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
