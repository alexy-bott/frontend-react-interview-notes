---
aliases:
  - frontend pipeline
  - frontend CI/CD pipeline
  - pipeline frontend
  - deploy frontend
---

#### Ответ на 60 секунд

Frontend pipeline - это цепочка автоматических проверок и доставки: установка зависимостей, lint, typecheck, tests, production build, анализ артефактов, сборка Docker image и deploy. Его задача - не просто “запустить npm scripts”, а сделать поставку воспроизводимой: один и тот же commit проходит понятные gates и превращается в конкретный artifact или image tag.

Pipeline разделяет fast feedback и delivery. В merge request нужны быстрые проверки качества. На default branch можно собирать image и деплоить staging. Production deploy обычно привязывают к protected branch/tag, manual approval или release process. Для rollback нужен версионированный artifact/image, а не только `latest`.

#### Ключевая схема

```text
merge request
-> install
-> lint
-> typecheck
-> test
-> build

main/tag
-> build Docker image
-> push registry
-> deploy staging/prod
-> monitor
```

| Этап | Что проверяет |
| --- | --- |
| install | lockfile и воспроизводимость зависимостей |
| lint | стиль и базовые ошибки |
| typecheck | TypeScript-контракты |
| test | unit/integration проверки, например Jest/RTL |
| build | production bundle компилируется |
| package | Docker image или static artifact |
| deploy | доставка в окружение |
| monitor | smoke tests, metrics, error tracking |

#### Развернутый ответ

Quality gate - набор проверок, без которых merge или deploy не проходит. Для frontend это обычно lint, typecheck, unit/integration tests и production build. E2E можно запускать на staging, nightly или по изменению критичных зон, если они тяжёлые.

Staging проверяет artifact/image в окружении, похожем на production. Production deploy должен использовать тот же artifact/image, который уже прошёл проверки. Если на deploy заново пересобирать код с другим набором env, исчезает связь между проверенной версией и тем, что реально попало пользователям.

Smoke tests после deploy проверяют минимальную жизнеспособность: HTML отдаётся, assets загружаются, API health доступен, главный route открывается, login или ключевой сценарий не сломан. Smoke не заменяет E2E, но быстро ловит проблемы доставки, конфигурации и static serving.

Rollback работает проще, когда каждый deploy связан с versioned image tag или release artifact. Commit SHA/release tag позволяют понять, какая версия запущена, и вернуть предыдущую. `latest` без версии затрудняет диагностику и откат.

Frontend pipeline может включать performance budget: bundle size, bundle analyzer report, Lighthouse CI, synthetic Web Vitals checks. Это ловит деградации до релиза, а не после жалоб пользователей.

Для Vite запускают именно `vite build`, а не dev server. Для Webpack запускают production build с release env/mode, проверяют hashed assets, sourcemaps policy, bundle size и то, что `devServer.proxy` не воспринимается как production routing.

> [!faq]+ Уточнения
> - Quality gate обычно включает lint, typecheck, tests и production build.
> - Production должен деплоить уже проверенный artifact/image.
> - Smoke tests проверяют доставку и грубую работоспособность после deploy.
> - Rollback требует versioned artifact/image tag.
> - Pipeline может проверять bundle size и performance budget.

#### Пример

```yaml
stages:
  - quality
  - build
  - package
  - deploy

build_image:
  stage: package
  image: docker:27
  services:
    - docker:27-dind
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
  variables:
    IMAGE_TAG: "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
  script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
    - docker build -t "$IMAGE_TAG" .
    - docker push "$IMAGE_TAG"

deploy_staging:
  stage: deploy
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  script:
    - echo "Deploy $CI_COMMIT_SHA to staging"
```

В реальном проекте deploy-команды зависят от инфраструктуры: Kubernetes, Helm, Docker Compose, SSH, GitOps, cloud platform или hosting provider.

#### Частые ошибки

- Пересобирать production artifact во время deploy другим набором env.
- Не запускать production build в merge request.
- Деплоить из feature branches с production secrets.
- Не иметь rollback strategy.
- Не связывать release с commit SHA.
- Не проверять, что Docker image стартует после сборки.
- Игнорировать bundle size и performance regressions.

#### Связанные темы

- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]
- [[Конспект для подготовки/Tooling/npm yarn pnpm и package managers]]
- [[Конспект для подготовки/Tooling/Воспроизводимые версии в команде]]
- [[Конспект для подготовки/Tooling/Bundle analysis и size budgets]]
- [[Конспект для подготовки/DevOps/GitLab CI CD]]
- [[Конспект для подготовки/DevOps/Artifacts cache variables]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/Architecture/Error handling и observability]]
- [[Конспект для подготовки/Testing/E2E testing]]
- [[Конспект для подготовки/Testing/Jest]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]
- [[Конспект для подготовки/Tooling/Vite]]
- [[Конспект для подготовки/Tooling/Webpack]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]

#### Источники

- [GitLab Docs: CI/CD YAML syntax reference](https://docs.gitlab.com/ci/yaml/)
- [GitLab Docs: Use Docker to build Docker images](https://docs.gitlab.com/ci/docker/using_docker_build/)
- [Docker Docs: Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
