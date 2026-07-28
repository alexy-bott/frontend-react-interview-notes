---
aliases:
  - GitLab artifacts
  - GitLab cache
  - GitLab variables
  - CI artifacts cache
---

#### Ответ на 60 секунд

В GitLab CI/CD cache и artifacts решают разные задачи. Cache ускоряет jobs: например, переиспользует npm cache между pipeline или jobs. Artifacts передают результат работы job дальше: `dist`, coverage report, junit report, собранный Storybook, bundle analyzer output. Variables хранят конфигурацию pipeline и секреты, но с ними нужно работать аккуратно: protected, masked, environment-scoped, без вывода в logs.

Коротко: cache - оптимизация скорости, artifacts - результат работы, variables - конфигурация и секреты. Если это перепутать, pipeline становится либо медленным, либо нестабильным, либо опасным.

#### Ключевая схема

| Механизм | Для чего | Пример |
| --- | --- | --- |
| `cache` | ускорить повторные jobs | `.npm/`, package manager cache |
| `artifacts` | передать результат между stages | `dist/`, `coverage/`, reports |
| `variables` | конфигурация и secrets | `PUBLIC_API_URL`, registry token |
| `expire_in` | срок жизни artifacts | `1 week`, `30 days` |
| `protected` | доступ только protected refs | production credentials |
| `masked` | скрытие значения в logs | tokens/passwords |

#### Развернутый ответ

Cache ускоряет jobs, но не является частью результата. Он может переживать разные pipelines, ускорять `npm ci --cache`, хранить package manager cache, но не гарантирован: runner может быть другой, cache может быть очищен, ключ может измениться. Job должен уметь выполниться и без cache.

Artifacts - результат работы job. Их используют следующие stages или разработчики: скачать build, посмотреть coverage, открыть JUnit reports, забрать bundle analyzer output. Artifacts делают минимальными, задают `expire_in` и не кладут туда секреты.

Cache key для frontend часто строят на основе lockfile. Если lockfile изменился, зависимости должны обновиться; если нет - cache можно переиспользовать. Это безопаснее, чем один общий cache на все ветки и разные package lockfiles.

Variables делятся по риску. Public config может быть доступен build job. Production secrets должны быть protected, masked и доступны только protected branches/tags или конкретному environment. Merge request из небезопасной ветки не должен получать deploy credentials.

Masked variables скрывают значение в logs, но не являются абсолютной защитой. Секрет можно записать в файл, artifact, Docker image или отправить наружу ошибочной командой. Поэтому pipeline должен не только маскировать секреты, но и не переносить их в результаты сборки.

> [!faq]+ Уточнения
> - Cache ускоряет job, artifacts передают результат работы.
> - Job должен проходить без cache.
> - Build output передают artifacts, а не cache.
> - Cache key часто привязывают к lockfile.
> - Protected/masked variables не должны попадать в logs, artifacts и images.

#### Пример

```yaml
default:
  image: node:22-alpine
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - .npm/
    policy: pull-push

test:
  stage: quality
  script:
    - npm ci --cache .npm --prefer-offline
    - npm test -- --ci --coverage
  artifacts:
    when: always
    paths:
      - coverage/
    reports:
      junit: junit.xml
    expire_in: 1 week

build:
  stage: build
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
```

#### Частые ошибки

- Использовать artifacts вместо cache для зависимостей.
- Использовать cache вместо artifacts для build output, который нужен следующему stage.
- Делать один cache key для разных package lockfiles.
- Сохранять `.env`, tokens или registry auth в artifacts.
- Думать, что masked variable можно безопасно печатать.
- Не задавать `expire_in` для тяжёлых artifacts.
- Ожидать, что cache всегда доступен на любом runner.

#### Связанные темы

- [[Конспект для подготовки/DevOps/GitLab CI CD]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/Testing/Frontend testing]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]

#### Источники

- [GitLab Docs: Caching in GitLab CI/CD](https://docs.gitlab.com/ci/caching/)
- [GitLab Docs: Job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [GitLab Docs: CI/CD variables](https://docs.gitlab.com/ci/variables/)
