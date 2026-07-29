---
aliases:
  - Dockerfile frontend
  - multi-stage build
  - Docker multi-stage
  - frontend Dockerfile
---

#### Быстрый ответ

Multi-stage Dockerfile разделяет environment сборки и environment запуска. Builder stage содержит Node.js, package manager, dependencies и source; runtime stage получает только `dist` для SPA либо минимальный server output для SSR. Build tools и исходники не попадают в финальный image.

Для эффективного cache сначала копируют manifests и lockfile, выполняют воспроизводимую установку, затем добавляют source. Изменение source переиспользует dependency layer, а изменение lockfile корректно его инвалидирует. Build secrets передают через BuildKit secret mounts, а не `ARG`, `ENV` или `COPY`.

#### Ключевая схема

```text
deps stage: manifests + lockfile -> npm ci
build stage: dependencies + source -> npm run build -> dist
runtime stage: server config + dist -> container command
```

| Инструкция | Фаза | Смысл |
| --- | --- | --- |
| `FROM ... AS` | build | создаёт именованный stage |
| `COPY` | build | создаёт layer из context/предыдущего stage |
| `RUN` | build | выполняет команду и сохраняет результат layer |
| `ARG` | build | параметр сборки, не secret storage |
| `ENV` | image/runtime | default environment container |
| `EXPOSE` | metadata | документирует port, но не публикует его |
| `CMD` | runtime | default command container |

#### Базовая модель

Каждая инструкция использует результат предыдущих layers и inputs. Cache hit возможен, когда instruction и её dependencies не изменились. Если `COPY . .` стоит до `npm ci`, изменение любого source file инвалидирует установку dependencies.

`npm ci` следует `package-lock.json`, удаляет существующий `node_modules` и падает при несогласованности manifest/lockfile. Это делает dependency graph проверяемым. Для pnpm/yarn используют соответствующий frozen/immutable mode и правильный lockfile.

Multi-stage `COPY --from=build` переносит только выбранные files, но секрет, записанный в build output, всё равно попадёт в runtime. Разделение stages уменьшает поверхность, а не заменяет контроль содержимого artifact.

#### Развернутый ответ

**Build cache mount.** `RUN --mount=type=cache,target=/root/.npm npm ci` сохраняет скачанные package archives между builds без добавления cache directory в image layer. Build обязан давать тот же результат и при пустом cache.

**Secrets.** Private registry token нужен только команде установки. `RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci` временно монтирует файл на время instruction. `ARG NPM_TOKEN` может появиться в history/provenance и влияет на cache; он не предназначен для credentials.

**Build-time public config.** `ARG VITE_API_URL` допустим как публичный input, но значение встраивается в bundle и остаётся видимым. Изменение arg инвалидирует соответствующий build layer и создаёт другой artifact; это важно для стратегии «build once, promote».

**Runtime stage.** Static image содержит Nginx/config/assets. SSR image содержит production server files и production dependencies, запускается не-root user при поддержке output и корректно обрабатывает signals. Конкретный layout зависит от framework output.

**Base images.** Floating major tag упрощает обновления, но build меняется без source diff. Pin digest даёт точность, но требует регулярного automated update. Для production выбирают поддерживаемую Node/Nginx version и фиксируют policy; версии примера не являются рекомендацией навсегда.

#### Пример

```dockerfile
# syntax=docker/dockerfile:1

FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Это SPA-вариант. В репозитории base images фиксируют по утверждённой версии/digest, а CI запускает built image и проверяет отдачу `index.html` до публикации.

#### Ключевые уточнения

- Multi-stage исключает ненужные build files только тогда, когда runtime stage копирует узкий список outputs.
- Порядок instructions определяет область invalidation cache; manifests идут до часто меняющегося source.
- Cache mount ускоряет build, но не является dependency или частью обязательного результата.
- `ARG` и `ENV` не подходят secrets; BuildKit secret доступен только нужной `RUN` instruction.
- SPA runtime и SSR runtime различаются, поэтому один Nginx Dockerfile нельзя механически использовать для server-rendered приложения.

#### Связанные темы

- [[Конспект для подготовки/DevOps/Docker для frontend]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]

#### Источники

- [Docker: Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Docker: Build cache](https://docs.docker.com/build/cache/)
- [Docker: Build secrets](https://docs.docker.com/build/building/secrets/)
