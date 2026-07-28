---
aliases:
  - env variables frontend
  - frontend secrets
  - Docker env
  - GitLab variables
  - runtime config
---

#### Ответ на 60 секунд

Env variables во frontend нужно делить на build-time и runtime. В обычной SPA переменные вроде `VITE_API_URL` или `REACT_APP_API_URL` часто встраиваются в bundle во время сборки. После этого они становятся частью публичного JavaScript, поэтому туда нельзя класть секреты. Секреты должны жить на backend, в CI/CD variables, secret manager или runtime окружении сервера, но не в клиентском bundle.

В Docker есть `ARG` для build-time и `ENV` для image/container runtime. В GitLab CI/CD есть variables, masked/protected settings и external secrets. Важное правило: frontend может знать публичную конфигурацию, например URL API или Sentry DSN с публичным client key, но не приватные tokens, passwords, registry credentials, private API keys и signing secrets.

#### Ключевая схема

| Вид значения | Где живёт | Видно пользователю |
| --- | --- | --- |
| Public API URL | frontend bundle или runtime config | да |
| Feature flag public snapshot | frontend config | да |
| Sentry public DSN | frontend bundle/config | обычно да |
| Backend DB password | backend env/secret manager | нет |
| NPM private token | CI secret/build secret | нет |
| Docker registry password | CI variable | нет |
| JWT signing secret | backend secret | нет |

#### Развернутый ответ

Build-time env используется во время `npm run build`. Если значение попало в JS bundle, его можно увидеть в DevTools или скачанном файле. Префиксы вроде `VITE_` и `REACT_APP_` не делают значение секретным; они только разрешают сборщику вставить его в клиентский код.

Статическая SPA после сборки не читает env variables контейнера автоматически. Если конфиг нужно менять без пересборки, используют `env.js`, JSON config endpoint, server-side template substitution или config, который отдаёт backend. Такой config всё равно считается публичным, если попадает в браузер.

SSR-приложение с Node.js может читать env variables во время обработки запроса. Но значение становится публичным, если его передали в client component, serialized props, HTML или JS bundle. Поэтому в Next.js/SSR важно разделять server-only config и public runtime config.

GitLab masked variables скрываются в logs, protected variables доступны только protected branches/tags, environment-scoped variables ограничивают окружение. Это снижает риск утечки, но не отменяет дисциплину: секреты не печатают, не кладут в artifacts и не встраивают в frontend bundle.

Docker build secrets используют для приватных package registry tokens и похожих значений во время build. Обычные `ARG` могут остаться в metadata/history или попасть в layer через команды, поэтому для секретов они не подходят.

> [!faq]+ Уточнения
> - Всё, что попало в frontend bundle, публично.
> - `VITE_*` и `REACT_APP_*` означают public build-time config, а не secret.
> - Static SPA требует отдельный runtime config mechanism, если config меняется без rebuild.
> - SSR может читать server env, но нельзя случайно сериализовать secret в client.
> - Masked/protected variables снижают риск, но не защищают от записи секрета в artifact/image.

#### Пример

Публичный runtime config для SPA:

```html
<script src="/env.js"></script>
<script type="module" src="/assets/app.js"></script>
```

```js
// env.js, генерируется при запуске container или deploy
window.__APP_CONFIG__ = {
  apiUrl: "https://api.example.com",
  release: "2026.07.15",
};
```

Использование в приложении:

```ts
const apiUrl = window.__APP_CONFIG__.apiUrl;
```

GitLab variables в pipeline:

```yaml
build:
  stage: build
  script:
    - npm ci
    - VITE_API_URL="$PUBLIC_API_URL" npm run build
```

`PUBLIC_API_URL` должен быть публичной конфигурацией, а не секретом.

#### Частые ошибки

- Считать `VITE_` или `REACT_APP_` переменную секретной.
- Класть private token в frontend `.env`.
- Передавать секрет через Docker `ARG`.
- Печатать env variables в CI logs.
- Сохранять `.env` или generated config с секретами в artifacts.
- Ожидать, что static SPA сама прочитает env container после build.
- Путать public config и secret config.

#### Связанные темы

- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/DevOps/GitLab CI CD]]
- [[Конспект для подготовки/DevOps/Artifacts cache variables]]
- [[Конспект для подготовки/Web Basics/Cookies и авторизация]]
- [[Конспект для подготовки/Web Basics/CSP и security headers]]
- [[Конспект для подготовки/Security/Supply chain secrets и third-party scripts]]
- [[Конспект для подготовки/Architecture/Feature flags]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]

#### Источники

- [Docker Docs: Build variables](https://docs.docker.com/build/building/variables/)
- [Docker Docs: Build secrets](https://docs.docker.com/build/building/secrets/)
- [GitLab Docs: CI/CD variables](https://docs.gitlab.com/ci/variables/)
- [GitLab Docs: Use external secrets in CI/CD](https://docs.gitlab.com/ci/secrets/)
