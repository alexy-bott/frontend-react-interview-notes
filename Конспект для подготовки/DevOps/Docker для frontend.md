---
aliases:
  - Docker frontend
  - Docker для фронтенда
  - containerization frontend
  - Docker basics
---

#### Ответ на 60 секунд

Docker нужен фронтенд-разработчику, чтобы приложение собиралось и запускалось одинаково в локальной среде, CI и production. Базовые сущности: image - шаблон с файловой системой и инструкциями запуска, container - запущенный экземпляр image, Dockerfile - рецепт сборки image, registry - хранилище images, layer - слой образа, который можно кешировать и переиспользовать.

Для frontend есть два типичных сценария. SPA собирается в статические файлы и обычно отдаётся Nginx, CDN или другим static server. SSR-приложение, например Next.js в server mode, требует runtime-процесса Node.js или платформы, которая умеет выполнять серверный код. Runtime зависит от типа приложения: frontend в Docker не всегда означает Nginx-only container.

#### Ключевая схема

| Понятие | Смысл |
| --- | --- |
| Image | неизменяемый шаблон приложения |
| Container | запущенный image |
| Dockerfile | инструкция сборки image |
| Build context | файлы, которые отправляются Docker build |
| Layer | кешируемый слой image |
| Registry | место хранения images |
| Volume | внешнее хранилище данных |
| Network | связь контейнеров между собой |

#### Развернутый ответ

Image - это неизменяемый артефакт сборки: файловая система, metadata и команда запуска. Container появляется, когда image запускают. Из одного image можно поднять несколько containers с разными env, портами и настройками. Поэтому image должен быть воспроизводимым, а runtime-конфигурация - управляемой снаружи.

Для SPA типичный pipeline состоит из двух частей: Node image собирает `dist`/`build`, затем runtime image вроде `nginx:alpine` отдаёт готовые статические файлы. Production image содержит только runtime-файлы: HTML, JS, CSS, assets и Nginx config. Локальные `node_modules`, исходники, dev-зависимости и package manager cache туда не попадают.

Для SSR/Next.js server mode нужен другой runtime. Если приложение рендерит HTML на запросе, контейнер должен запускать Node process или standalone server output, иметь server entrypoint и runtime env variables. Nginx в таком сценарии может быть reverse proxy перед Node.js, но не единственным runtime.

Build context - набор файлов, который Docker отправляет в сборку. `.dockerignore` защищает context от `node_modules`, `.git`, `dist`, coverage, локальных `.env` и мусорных артефактов. Это ускоряет build и снижает риск случайно положить чувствительные данные в image layers.

После сборки image пушат в registry: GitLab Container Registry, Docker Hub, Harbor, AWS ECR или другой registry. Для deploy используют конкретный tag: commit SHA, release tag, semver. Один `latest` без версии мешает rollback и диагностике.

> [!faq]+ Уточнения
> - Image - артефакт, container - запущенный экземпляр image.
> - SPA часто собирают в Node stage и отдают через Nginx/CDN/static server.
> - Next.js SSR/server mode требует Node runtime или платформу с server execution.
> - `.dockerignore` уменьшает build context и защищает от лишних файлов.
> - Production image тегают commit SHA/release tag, а не только `latest`.

#### Пример

```bash
docker build -t registry.example.com/app/frontend:abc123 .
docker run --rm -p 8080:80 registry.example.com/app/frontend:abc123
docker push registry.example.com/app/frontend:abc123
```

Минимальная `.dockerignore`:

```dockerignore
node_modules
dist
build
.git
.env
.env.*
npm-debug.log
coverage
```

#### Частые ошибки

- Путать image и container.
- Копировать `node_modules` с локальной машины внутрь image.
- Не использовать `.dockerignore`.
- Думать, что SPA и SSR деплоятся одинаково.
- Класть секреты в frontend image или `.env`, который попадает в build context.
- Тегать production image только как `latest` без commit/release tag.

#### Связанные темы

- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/DevOps/GitLab CI CD]]
- [[Конспект для подготовки/React/SSR и SSG]]
- [[Конспект для подготовки/Next.js/Deployment env Docker]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]

#### Источники

- [Docker Docs: What is Docker?](https://docs.docker.com/get-started/docker-overview/)
- [Docker Docs: Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
