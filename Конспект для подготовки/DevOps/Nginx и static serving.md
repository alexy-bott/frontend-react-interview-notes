---
aliases:
  - Nginx frontend
  - static serving
  - SPA Nginx
  - nginx.conf frontend
---

#### Ответ на 60 секунд

Nginx во frontend чаще всего используют как static server для собранной SPA: он отдаёт `index.html`, JS, CSS, изображения и другие assets. Для SPA важна настройка fallback: если пользователь открывает `/profile/settings`, такого файла на диске может не быть, поэтому Nginx должен вернуть `index.html`, а routing уже обработает React Router или другой client router.

Отдельно важно настроить кеширование. HTML обычно кешируют осторожно или с revalidation, потому что он указывает на актуальные версии assets. JS/CSS с content hash в имени можно кешировать долго через `immutable`. Это связывает Nginx-конфиг с frontend build-стратегией.

#### Ключевая схема

| Задача | Nginx-настройка |
| --- | --- |
| Отдать статические файлы | `root`, `index` |
| SPA fallback | `try_files $uri $uri/ /index.html` |
| Долгий cache для hashed assets | `Cache-Control: public, max-age=31536000, immutable` |
| Осторожный cache для HTML | `no-cache` или короткий TTL |
| Сжатие | gzip/brotli на уровне сервера или precompressed assets |
| Security headers | CSP, HSTS, nosniff, frame-ancestors |

#### Развернутый ответ

SPA fallback нужен из-за client-side routing. URL `/profile/settings` может не соответствовать файлу на диске. `try_files` сначала ищет файл, затем директорию, а если ничего не нашёл - отдаёт `index.html`. После этого React Router или другой client router решает, какой экран показать.

HTML и hashed assets кешируют по-разному. `index.html` должен быстро обновляться после деплоя, потому что он ссылается на актуальные JS/CSS. Если HTML закеширован надолго, пользователь может получить старые ссылки на уже удалённые assets. JS/CSS с content hash можно кешировать долго: изменилось содержимое - изменилось имя файла.

Security headers часто ставят на Nginx/CDN уровне: `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`. Значения должны соответствовать реальному приложению, сторонним scripts, analytics, fonts и API, иначе headers могут сломать загрузку ресурсов.

Для Next.js SSR Nginx часто выступает reverse proxy перед Node.js process, а не просто отдаёт `dist`. Он может завершать TLS, проксировать запросы, отдавать static assets, добавлять headers и управлять compression. Но сам SSR выполняет Node runtime.

Compression можно включать на Nginx/CDN уровне или заранее генерировать `.gz`/`.br` при build. Нужно проверить `Content-Encoding`, `Vary: Accept-Encoding` и cache headers, чтобы сервер не отдавал неправильную версию ресурса.

> [!faq]+ Уточнения
> - `try_files $uri $uri/ /index.html` защищает SPA от 404 на refresh вложенного route.
> - HTML кешируют осторожно, hashed assets - долго и immutable.
> - Security headers должны учитывать реальные third-party scripts, fonts и API.
> - Для SSR Nginx обычно reverse proxy, а Node process выполняет rendering.
> - Compression требует корректных `Content-Encoding`, `Vary` и cache headers.

#### Пример

```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
    add_header Cache-Control "no-cache";
  }

  location ~* \.(js|css|png|jpg|jpeg|gif|svg|webp|avif|woff2)$ {
    try_files $uri =404;
    add_header Cache-Control "public, max-age=31536000, immutable";
  }

  add_header X-Content-Type-Options "nosniff" always;
  add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

#### Частые ошибки

- Не настроить SPA fallback и получать 404 при refresh на nested route.
- Кешировать `index.html` так же долго, как hashed assets.
- Отдавать старые assets после deploy без стратегии invalidation.
- Использовать Nginx-only container для приложения, которому нужен SSR runtime.
- Ставить CSP без проверки analytics, fonts, API и third-party scripts.
- Не проверять cache headers в DevTools Network.

#### Связанные темы

- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/Web Basics/HTTP caching]]
- [[Конспект для подготовки/Web Basics/CSP и security headers]]
- [[Конспект для подготовки/React/SSR и SSG]]
- [[Конспект для подготовки/React/React Router]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]

#### Источники

- [NGINX Docs: Serve Static Content](https://docs.nginx.com/nginx/admin-guide/web-server/serving-static-content/)
- [NGINX Docs: ngx_http_core_module](https://nginx.org/en/docs/http/ngx_http_core_module.html)
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
