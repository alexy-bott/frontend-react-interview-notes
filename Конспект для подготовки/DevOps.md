#### Темы

- [[Конспект для подготовки/DevOps/Docker для frontend]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/DevOps/Artifacts cache variables]]
- [[Конспект для подготовки/DevOps/GitLab CI CD]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]

#### Связанные разделы

- [[Конспект для подготовки/Next.js/Deployment env Docker]]
- [[Конспект для подготовки/Tooling/Vite]]
- [[Конспект для подготовки/Tooling/Webpack]]
- [[Конспект для подготовки/Tooling/Воспроизводимые версии в команде]]
- [[Конспект для подготовки/Git/Git для frontend]]
- [[Конспект для подготовки/Workflow/Jira]]

#### Маршрут

1. Понять runtime-модель Docker: image, container, registry, filesystem, network и volumes.
2. Собрать воспроизводимый frontend image: build context, layers, multi-stage build, cache и build secrets.
3. Разделить static SPA и SSR: fallback, cache policy, headers, old chunks и reverse proxy.
4. Провести границы конфигурации: build-time/runtime и public/secret.
5. Различить cache, artifacts и variables, затем проследить передачу конкретного build в deploy.
6. Разобрать GitLab pipeline: workflow, jobs, rules, stages, `needs`, runners и security boundary.
7. Собрать полный delivery flow: quality gates, build once/promote, smoke checks, observability и rollback.
