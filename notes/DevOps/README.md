# DevOps

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Docker для frontend.md>)

Заметок в разделе: **7**
<!-- SECTION-NAV:END -->

## Темы

- [Docker для frontend](<./Docker для frontend.md>)
- [Dockerfile и multi-stage build](<./Dockerfile и multi-stage build.md>)
- [Nginx и static serving](<./Nginx и static serving.md>)
- [Env variables и секреты](<./Env variables и секреты.md>)
- [Artifacts cache variables](<./Artifacts cache variables.md>)
- [GitLab CI CD](<./GitLab CI CD.md>)
- [Frontend pipeline](<./Frontend pipeline.md>)

## Связанные разделы

- [Deployment env Docker](<../Next.js/Deployment env Docker.md>)
- [Vite](<../Tooling/Vite.md>)
- [Webpack](<../Tooling/Webpack.md>)
- [Воспроизводимые версии в команде](<../Tooling/Воспроизводимые версии в команде.md>)
- [Git для frontend](<../Git/Git для frontend.md>)
- [Jira](<../Workflow/Jira.md>)

## Маршрут

1. Понять runtime-модель Docker: image, container, registry, filesystem, network и volumes.
2. Собрать воспроизводимый frontend image: build context, layers, multi-stage build, cache и build secrets.
3. Разделить static SPA и SSR: fallback, cache policy, headers, old chunks и reverse proxy.
4. Провести границы конфигурации: build-time/runtime и public/secret.
5. Различить cache, artifacts и variables, затем проследить передачу конкретного build в deploy.
6. Разобрать GitLab pipeline: workflow, jobs, rules, stages, `needs`, runners и security boundary.
7. Собрать полный delivery flow: quality gates, build once/promote, smoke checks, observability и rollback.
