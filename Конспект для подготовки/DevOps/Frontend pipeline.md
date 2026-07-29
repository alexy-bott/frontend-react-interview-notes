---
aliases:
  - frontend pipeline
  - frontend CI/CD pipeline
  - pipeline frontend
  - deploy frontend
---

#### Быстрый ответ

Frontend pipeline превращает commit в проверяемый и воспроизводимый release. Обычно он устанавливает dependencies по lockfile, параллельно запускает lint, typecheck и tests, создаёт production build, публикует versioned artifact или image, разворачивает его, выполняет smoke checks и связывает ошибки/метрики с release ID.

Главный delivery-инвариант — **build once, promote**: staging и production получают тот же проверенный artifact, а не независимо собранные похожие версии. Если окружениям нужны разные публичные URLs или flags, их передают runtime config отдельно от immutable application artifact. Rollback возвращает известную предыдущую версию, но требует совместимости с текущим API и данными.

#### Ключевая схема

```text
source + lockfile
-> quality gates
-> production build
-> versioned artifact/image + release metadata
-> staging deploy
-> smoke/integration checks
-> production rollout
-> monitoring
-> rollback or forward fix
```

| Этап | Проверяемый результат |
| --- | --- |
| Install | lockfile совместим с runtime/package manager |
| Lint/typecheck/test | код проходит принятые contracts |
| Build | production bundle создаётся без dev-only допущений |
| Package | artifact неизменяем и связан с commit SHA |
| Deploy | окружение запустило именно этот release |
| Verify | routes, assets, API и критичный сценарий доступны |
| Observe | errors, metrics и source maps связаны с release |

#### Базовая модель

Quality gate — обязательная проверка, которая блокирует merge или delivery при нарушении согласованного условия. Набор зависит от риска: lint и typecheck дают быстрый feedback, unit/integration tests проверяют поведение, production build ловит ошибки bundler/config, E2E проверяет целый сценарий в работающем окружении.

Artifact — идентифицируемый результат build: архив `dist`, package, container image или deployment bundle. Его маркируют commit SHA/release version и по возможности проверяют digest. Если deploy повторно запускает build, измениться могут dependencies, base image, environment values и время генерации — production получит уже не то, что прошло проверки.

Static SPA часто содержит environment-specific values прямо в bundle. Тогда staging build и production build являются **разными artifacts**, даже если source commit одинаков. Чтобы действительно promote один artifact, публичную конфигурацию выносят в runtime file/endpoint. Server-side secrets при этом остаются вне браузера.

#### Развернутый ответ

**Feedback path.** Независимые быстрые jobs выполняют параллельно. Тяжёлые E2E, visual regression и performance checks запускают там, где их сигнал оправдывает время: на staging, для critical paths, nightly либо по изменившимся областям. Это приоритизация, а не отказ от проверки.

**Packaging.** Pipeline сохраняет artifact, release manifest, commit SHA и при необходимости SBOM/provenance. Container image получает immutable tag или digest; static release публикуют в versioned directory. `latest` можно оставить удобным указателем, но не единственным идентификатором.

**Deploy.** Static files загружают atomically: новый `index.html` не должен ссылаться на chunks, которых ещё нет. Старые content-hashed chunks некоторое время сохраняют, потому что открытые вкладки могут запросить их после deploy. Для SSR дополнительно проверяют startup/readiness и совместимость server/client assets.

**Verification.** Smoke checks подтверждают delivery: HTML имеет ожидаемый release ID, assets возвращают JavaScript/CSS с корректным MIME, API доступен, критичный route открывается. Они не заменяют подробные tests, а ловят wiring/config/cache failures сразу после deploy.

**Observability.** Ошибки, logs и metrics помечают release/commit. Source maps либо публикуют осознанно, либо загружают в error tracker и не раздают публично. Без release metadata массовую ошибку трудно связать с конкретным rollout.

**Rollback.** Возврат frontend artifact помогает, только если предыдущая версия совместима с текущими API, database schema, feature flags и runtime config. Для несовместимых изменений применяют backward-compatible rollout, feature flag или forward fix. Canary/blue-green уменьшают blast radius, но требуют routing и наблюдаемости.

#### Пример

```yaml
stages: [quality, build, deploy]

quality:
  stage: quality
  script:
    - npm ci
    - npm run lint
    - npm run typecheck
    - npm test -- --ci

build_release:
  stage: build
  needs: [quality]
  script:
    - npm ci
    - npm run build
    - printf '%s' "$CI_COMMIT_SHA" > dist/release.txt
  artifacts:
    paths: [dist/]
    expire_in: 30 days

deploy_staging:
  stage: deploy
  needs:
    - job: build_release
      artifacts: true
  environment: staging
  script:
    - ./deploy-static.sh dist staging
    - ./smoke-test.sh "$STAGING_URL" "$CI_COMMIT_SHA"

deploy_production:
  stage: deploy
  needs:
    - job: build_release
      artifacts: true
  environment: production
  rules:
    - if: $CI_COMMIT_TAG
      when: manual
  script:
    - ./deploy-static.sh dist production
    - ./smoke-test.sh "$PRODUCTION_URL" "$CI_COMMIT_SHA"
```

Пример показывает transfer одного `dist` в оба deploy jobs. Конкретные scripts зависят от инфраструктуры. Если `deploy-static.sh` подменяет JavaScript внутри `dist`, инвариант уже нарушен; допустимо отдельно публиковать environment-specific **public** runtime config.

#### Ключевые уточнения

- Pipeline подтверждает не только качество source code, но и путь конкретного release до окружения.
- Production build является самостоятельным quality gate даже при успешных tests.
- Один commit не гарантирует одинаковый output двух независимых builds.
- Runtime config позволяет promote одну SPA-сборку, но доставленные браузеру значения остаются публичными.
- Smoke checks проверяют wiring и доступность после deploy, а не заменяют unit/integration/E2E tests.
- Rollback требует versioned artifact и совместимости предыдущего frontend с текущими contracts.
- Performance/security checks должны иметь измеримый threshold и понятное действие при failure.

#### Связанные темы

- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]
- [[Конспект для подготовки/Tooling/Воспроизводимые версии в команде]]
- [[Конспект для подготовки/Tooling/Bundle analysis и size budgets]]
- [[Конспект для подготовки/DevOps/GitLab CI CD]]
- [[Конспект для подготовки/DevOps/Artifacts cache variables]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/Architecture/Error handling и observability]]
- [[Конспект для подготовки/Testing/E2E testing]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]

#### Источники

- [GitLab Docs: CI/CD](https://docs.gitlab.com/ci/)
- [GitLab Docs: Job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [GitLab Docs: Deployment safety](https://docs.gitlab.com/ci/environments/deployment_safety/)
- [Docker Docs: Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
