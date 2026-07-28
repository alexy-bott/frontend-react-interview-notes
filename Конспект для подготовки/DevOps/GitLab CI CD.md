---
aliases:
  - GitLab CI/CD
  - GitLab pipeline
  - gitlab-ci.yml
  - CI CD frontend
---

#### Ответ на 60 секунд

GitLab CI/CD автоматизирует проверку и доставку изменений: install, lint, typecheck, test, build, docker image, deploy. Pipeline описывается в `.gitlab-ci.yml`. Внутри есть stages, jobs, scripts, rules, variables, cache, artifacts и runners. Stage задаёт порядок крупных этапов, job выполняет конкретную работу, runner запускает job на машине или в контейнере.

Для frontend pipeline должен быстро ловить ошибки до deploy: поставить зависимости по lockfile, проверить формат/линт, прогнать TypeScript, unit-тесты, собрать production bundle, сохранить build artifacts или собрать Docker image, а затем деплоить только из нужных веток/tags. Рабочий pipeline не просто “зелёный”, а воспроизводимый, быстрый и безопасный.

#### Ключевая схема

| GitLab CI/CD сущность | Роль |
| --- | --- |
| `.gitlab-ci.yml` | конфигурация pipeline |
| `stages` | порядок этапов |
| `job` | конкретная задача |
| `script` | команды job |
| `rules` | условия запуска job |
| `runner` | среда выполнения job |
| `cache` | ускорение зависимостей |
| `artifacts` | передача результата между stages |
| `variables` | конфигурация и секреты |

#### Развернутый ответ

Stage задаёт порядок крупных этапов pipeline: quality, build, package, deploy. Job выполняет конкретную работу внутри stage: `lint`, `typecheck`, `test`, `build_app`. Jobs одного stage обычно могут выполняться параллельно, а следующий stage стартует после успешного завершения предыдущего.

`rules` управляют тем, когда запускать job: merge request, default branch, tag, schedule, manual deploy. Это отделяет быстрые проверки MR от release/deploy сценариев и не тратит runner time на лишние jobs.

Runner выполняет jobs в конкретной среде: shell, Docker executor, Kubernetes executor. Для frontend часто используют Docker executor с Node image, чтобы install/build/test запускались предсказуемо и не зависели от локальной машины runner-а.

MR pipeline обычно является quality gate: install по lockfile, lint, typecheck, unit/integration tests, production build. Deploy запускают из protected branch/tag, с protected variables и понятным правилом approval, чтобы feature branch не получила production credentials.

После успешной сборки можно собрать Docker image и запушить его в GitLab Container Registry. Tags должны включать commit SHA, branch slug или release tag. Это связывает deploy с конкретным commit и делает rollback диагностируемым.

> [!faq]+ Уточнения
> - Stage задаёт порядок, job выполняет конкретную задачу.
> - Jobs одного stage могут идти параллельно.
> - `rules` разделяют MR checks, default branch, tags, schedules и manual deploy.
> - Runner задаёт среду выполнения job.
> - Production deploy связывают с protected refs, protected variables и versioned image/artifact.

#### Пример

```yaml
stages:
  - quality
  - build
  - package

default:
  image: node:22-alpine
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - .npm/
  before_script:
    - npm ci --cache .npm --prefer-offline

lint:
  stage: quality
  script:
    - npm run lint

typecheck:
  stage: quality
  script:
    - npm run typecheck

test:
  stage: quality
  script:
    - npm test -- --ci

build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
```

#### Частые ошибки

- Не запускать typecheck в CI.
- Делать deploy из любой ветки.
- Использовать `npm install` без lockfile-дисциплины.
- Путать cache и artifacts.
- Печатать секреты в logs.
- Не сохранять build output как artifact там, где он нужен следующему stage.
- Использовать только `latest` tag для Docker image.

#### Связанные темы

- [[Конспект для подготовки/DevOps/Artifacts cache variables]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/Testing/Frontend testing]]
- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]

#### Источники

- [GitLab Docs: CI/CD YAML syntax reference](https://docs.gitlab.com/ci/yaml/)
- [GitLab Docs: Get started with GitLab CI/CD](https://docs.gitlab.com/ci/)
- [GitLab Docs: Use Docker to build Docker images](https://docs.gitlab.com/ci/docker/using_docker_build/)
