# DevOps

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./01 Docker для фронтенда.md>)

Заметок в разделе: **7**
<!-- SECTION-NAV:END -->

## Темы

- [Docker для фронтенда](<./01 Docker для фронтенда.md>)
- [Многоэтапная сборка Dockerfile](<./02 Многоэтапная сборка Dockerfile.md>)
- [Nginx и раздача статических файлов](<./03 Nginx и раздача статических файлов.md>)
- [Переменные окружения и секреты](<./04 Переменные окружения и секреты.md>)
- [Артефакты, кеш и переменные пайплайна](<./05 Артефакты, кеш и переменные пайплайна.md>)
- [GitLab CI-CD](<./06 GitLab CI-CD.md>)
- [CI-CD-пайплайн фронтенда](<./07 CI-CD-пайплайн фронтенда.md>)

## Связанные разделы

- [Деплой, переменные окружения и Docker](<../Next.js/07 Деплой, переменные окружения и Docker.md>)
- [Vite](<../Инструменты разработки/10 Vite.md>)
- [Webpack](<../Инструменты разработки/11 Webpack.md>)
- [Воспроизводимые версии в команде](<../Инструменты разработки/05 Воспроизводимые версии в команде.md>)
- [Git для фронтенда](<../Git/01 Git для фронтенда.md>)
- [Jira](<../Процессы разработки/02 Jira.md>)

## Маршрут

1. Понять runtime-модель Docker: image, container, registry, filesystem, network и volumes.
2. Собрать воспроизводимый frontend image: build context, layers, multi-stage build, cache и build secrets.
3. Разделить static SPA и SSR: fallback, cache policy, headers, old chunks и reverse proxy.
4. Провести границы конфигурации: build-time/runtime и public/secret.
5. Различить cache, artifacts и variables, затем проследить передачу конкретного build в deploy.
6. Разобрать GitLab pipeline: workflow, jobs, rules, stages, `needs`, runners и security boundary.
7. Собрать полный delivery flow: quality gates, build once/promote, smoke checks, observability и rollback.
