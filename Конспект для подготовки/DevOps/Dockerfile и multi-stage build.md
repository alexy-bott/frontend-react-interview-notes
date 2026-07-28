---
aliases:
  - Dockerfile frontend
  - multi-stage build
  - Docker multi-stage
  - frontend Dockerfile
---

#### Ответ на 60 секунд

Multi-stage build позволяет разделить сборку и runtime. Для frontend это особенно полезно: в первом stage берём Node.js, устанавливаем зависимости и собираем приложение; во втором stage берём маленький runtime image, например Nginx, и копируем туда только готовые статические файлы. Так production image получается меньше, быстрее и безопаснее.

Качество Dockerfile сильно зависит от порядка слоёв. Сначала копируют lockfile и `package.json`, ставят зависимости, потом копируют исходники и запускают build. Тогда Docker может переиспользовать layer с зависимостями, если код изменился, но lockfile остался прежним. `.dockerignore` дополняет это: он не даёт лишним файлам попадать в build context.

#### Ключевая схема

```text
builder stage
-> install dependencies
-> run tests or build
-> produce dist

runtime stage
-> copy dist only
-> serve files
```

| Инструкция | Роль |
| --- | --- |
| `FROM` | выбрать base image или stage |
| `WORKDIR` | задать рабочую директорию |
| `COPY` | скопировать файлы в image |
| `RUN` | выполнить команду при сборке |
| `ARG` | build-time параметр |
| `ENV` | переменная окружения внутри image/container |
| `EXPOSE` | документировать порт |
| `CMD` | команда запуска container |

#### Развернутый ответ

Multi-stage build отделяет инструменты сборки от runtime. Один stage часто оставляет в production image исходники, dev-зависимости, package manager cache и build tools. Multi-stage переносит только результат: `dist` для SPA или server output для SSR.

Порядок `COPY` влияет на Docker cache. Сначала копируют `package.json` и lockfile, выполняют `npm ci`, а исходники копируют после этого. Тогда изменение компонента не инвалидирует layer с установкой зависимостей, если lockfile не изменился.

В CI и Docker build используют lockfile-дисциплину. `npm ci` устанавливает зависимости строго по lockfile и падает, если `package.json` с ним не согласован. Это делает сборку воспроизводимой и помогает ловить случайные изменения зависимостей.

`ARG` и `ENV` живут в разных фазах. `ARG` доступен во время build. `ENV` попадает в image/container runtime. Для frontend всё, что встраивается в bundle на build-time, становится публичным JavaScript. Поэтому public API URL допустим, а secrets - нет.

Build secrets используют для приватных package registry tokens и похожих значений, которые нужны только во время build. Обычный `ARG` или копирование `.env` может оставить секрет в metadata, layer history или итоговом image.

Для Next.js SSR финальный stage обычно Node-based: копируется standalone output, static assets и запускается server. Для статической SPA финальный stage может быть Nginx-only.

> [!faq]+ Уточнения
> - Multi-stage уменьшает production image и отделяет build tools от runtime.
> - Lockfile копируют до исходников, чтобы кешировать установку зависимостей.
> - `npm ci` подходит для CI/Docker, потому что следует lockfile.
> - `ARG` - build-time, `ENV` - runtime container environment.
> - Secrets передают через build secrets/CI, а не через обычный `ARG` или `.env` в image.

#### Пример

```dockerfile
# syntax=docker/dockerfile:1

FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Для Next.js SSR такой финальный stage обычно будет Node-based, а не Nginx-only.

#### Частые ошибки

- Делать production image на полном Node stage без необходимости.
- Копировать весь проект до `npm ci` и ломать кеш зависимостей.
- Не использовать lockfile.
- Передавать секреты через `ARG` и оставлять их в истории сборки.
- Не фиксировать major/minor base image и неожиданно получать несовместимые обновления.
- Забывать, что `EXPOSE` не публикует порт сам по себе.

#### Связанные темы

- [[Конспект для подготовки/DevOps/Docker для frontend]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/Web Basics/HTTP caching]]

#### Источники

- [Docker Docs: Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Docs: Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Docker Docs: Build cache](https://docs.docker.com/build/cache/)
- [Docker Docs: Build secrets](https://docs.docker.com/build/building/secrets/)
