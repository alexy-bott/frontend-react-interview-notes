---
aliases:
  - GitLab CI/CD
  - GitLab pipeline
  - gitlab-ci.yml
  - CI CD frontend
---

#### Быстрый ответ

GitLab CI/CD запускает автоматические проверки и delivery по событиям repository. Конфигурация `.gitlab-ci.yml` описывает, когда создать pipeline, какие jobs в него включить, в какой среде их выполнить и какие результаты передать дальше. Runner получает job и запускает её commands, например в изолированном Docker container.

Для frontend merge request обычно проходит dependency install по lockfile, lint, typecheck, tests и production build. Delivery использует конкретный artifact или image, а production credentials выдаются только доверенному deploy job. `workflow: rules` управляет созданием pipeline, job-level `rules` — присутствием job, `needs` — её реальными зависимостями и ранним запуском.

#### Ключевая схема

```text
push / merge request / tag / schedule
-> workflow: rules     создаёт или отклоняет pipeline
-> job rules           формируют набор jobs
-> runner              выполняет scripts в заданной среде
-> needs / stages      задают зависимости и порядок
-> artifacts / reports передают и показывают результат
-> environment         фиксирует deployment
```

| Сущность | За что отвечает |
| --- | --- |
| `workflow: rules` | существует ли pipeline для события |
| `job` + `script` | конкретная единица работы |
| `rules` | входит ли job в созданный pipeline |
| `stage` | общий барьер между группами jobs |
| `needs` | точная DAG-зависимость между jobs |
| `runner` | execution environment и доступные ресурсы |

#### Базовая модель

Без `needs` stages работают как последовательные барьеры: все успешные jobs текущего stage завершаются до следующего. Jobs внутри stage выполняются параллельно при наличии runners. `needs` создаёт directed acyclic graph (DAG): job запускается сразу после перечисленных dependencies и не ждёт несвязанные jobs предыдущего stage.

`workflow: rules` вычисляется раньше jobs. Поэтому job rule не может вернуть job в pipeline, создание которого запретил workflow. Разделение полезно для типичной проблемы GitLab: один push в branch с открытым merge request может создать одновременно branch и MR pipelines. Workflow должен явно определить, какие pipeline sources допустимы.

Runner является частью trust boundary. Job получает source code, variables и network access, разрешённые проектом. Shared, project и protected runners имеют разный уровень доверия; используемый image тоже входит в supply chain. Поэтому deploy job выполняют на контролируемом runner и не выдают production secrets непроверенному MR-коду.

#### Развернутый ответ

**CI.** Continuous Integration даёт раннюю обратную связь: lockfile воспроизводится, типы согласованы, tests проходят, production build собирается. Независимые lint/typecheck/test jobs можно выполнять параллельно, чтобы ошибка появилась быстрее.

**CD.** Continuous Delivery подготавливает проверенный release к deploy, а Continuous Deployment автоматически отправляет прошедшее изменение в production. Конкретный процесс команды может оставлять manual approval перед production; это не отменяет автоматизацию сборки, проверок и фиксации release.

**Rules.** Условия связывают job с pipeline source, branch, tag, изменёнными paths или manual action. Не следует без необходимости смешивать legacy `only/except` и `rules`: у них разные defaults, и конфигурация становится труднее предсказуемой.

**Reproducibility.** Node/package-manager version, lockfile и build command должны быть одинаковыми локально и в CI. Container image tag удобен, но tag может быть обновлён владельцем registry; для строгой воспроизводимости фиксируют точную версию или digest и планируют обновления безопасности.

**Security.** Protected/masked variables снижают вероятность случайной утечки, но любой job с доступом к secret способен его использовать. Изменения `.gitlab-ci.yml`, included templates и build scripts проходят review как executable code. Deploy permissions, environments и runners ограничивают отдельно от обычных test jobs.

#### Пример

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
    - if: $CI_COMMIT_TAG

stages:
  - quality
  - build

default:
  # В проекте tag согласуют с поддерживаемой Node version и обновляют явно.
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
  script: npm run lint

typecheck:
  stage: quality
  script: npm run typecheck

test:
  stage: quality
  script: npm test -- --ci

build:
  stage: build
  needs: [lint, typecheck, test]
  script: npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
```

Workflow запускает MR pipeline, но подавляет дублирующий branch pipeline, когда для branch уже открыт MR. Это один конкретный policy: для tag releases, schedules или parent/child pipelines правила расширяют согласно процессу проекта.

#### Ключевые уточнения

- `workflow: rules` выбирает pipelines, job `rules` — jobs внутри них.
- Stage задаёт общий порядок, `needs` — фактические зависимости и более ранний старт.
- Зелёный pipeline полезен только при воспроизводимой среде и meaningful quality gates.
- Build artifact или image связывают с commit SHA/release tag; один `latest` недостаточен для диагностики и rollback.
- Runner и CI configuration входят в security boundary, потому что исполняют код и получают variables.
- Production deploy ограничивают protected environment/ref, доверенным runner и минимальными credentials.

#### Связанные темы

- [[Конспект для подготовки/DevOps/Artifacts cache variables]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/Testing/Frontend testing]]
- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]

#### Источники

- [GitLab Docs: Get started with GitLab CI/CD](https://docs.gitlab.com/ci/)
- [GitLab Docs: CI/CD YAML syntax](https://docs.gitlab.com/ci/yaml/)
- [GitLab Docs: Workflow](https://docs.gitlab.com/ci/yaml/workflow/)
- [GitLab Docs: Job rules](https://docs.gitlab.com/ci/jobs/job_rules/)
- [GitLab Docs: needs](https://docs.gitlab.com/ci/yaml/needs/)
