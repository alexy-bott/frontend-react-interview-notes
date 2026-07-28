---
aliases:
  - .gitignore
  - .npmrc
  - README
  - служебные файлы проекта
  - project service files
---

#### Ответ на 60 секунд

Служебные файлы проекта задают правила работы команды и инструментов. `.gitignore` говорит Git, какие неотслеживаемые файлы игнорировать: `node_modules`, `dist`, `.env.local`, coverage, cache, logs. `.npmrc` настраивает npm: registry, scope registry, auth token через env, strict-peer-deps, proxy и другие параметры. `README.md` описывает, как проект запускать, тестировать, собирать и какие env нужны.

Эти файлы важны не меньше исходников: ошибка в `.gitignore` может привести к коммиту секретов или build artifacts, ошибка в `.npmrc` - к проблемам с private packages, плохой README - к долгому onboarding и разным локальным сценариям у команды.

#### Ключевая схема

| Файл | Зачем нужен |
| --- | --- |
| `.gitignore` | не коммитить generated/local/sensitive files |
| `.npmrc` | настроить registry и поведение npm |
| `.yarnrc.yml` | настройки Yarn |
| `.editorconfig` | базовые настройки editor formatting |
| `.nvmrc` / `.node-version` | ожидаемая версия Node |
| `README.md` | команды, env, запуск, тесты, troubleshooting |
| `.dockerignore` | исключить лишнее из Docker build context |
| `.gitattributes` | line endings, linguist, merge strategies |

#### Развернутый ответ

**`.gitignore` работает только для untracked files.**
Если файл уже попал в git, добавление его в `.gitignore` не уберёт файл из истории и не перестанет отслеживать автоматически. Нужно отдельно удалить его из index и, если это секрет, считать его скомпрометированным и ротировать.

**В `.gitignore` хранят командные правила, а не личные привычки.**
Общие generated files вроде `node_modules`, `dist`, `coverage`, `.env.local` должны быть в проектном `.gitignore`. Личные файлы editor/OS лучше держать в глобальном git ignore, чтобы не загрязнять репозиторий команды.

**`.npmrc` часто нужен для private registry.**
В корпоративных проектах пакеты могут лежать в GitLab Package Registry, GitHub Packages, npm org registry или внутреннем registry. `.npmrc` задаёт registry для scope, но токены лучше подставлять через env/CI variables, а не коммитить реальным значением.

**README - часть developer experience.**
Хороший README отвечает на практические вопросы: какая версия Node, какой package manager, как поставить зависимости, какие env нужны, как запустить dev server, tests, lint, build, Storybook, Docker, где troubleshooting.

**`.dockerignore` похож на `.gitignore`, но решает другую задачу.**
Он не влияет на git. Он уменьшает Docker build context и защищает от случайного попадания `node_modules`, `.git`, локальных env, coverage и кэшей в image layers.

#### Где применяется во frontend

| Ситуация | Какой файл смотреть |
| --- | --- |
| В repo попал `.env.local` | `.gitignore`, git history, rotation secrets |
| CI не может скачать private package | `.npmrc`, CI variables, registry auth |
| Новый разработчик не может запустить проект | `README.md`, `.nvmrc`, `packageManager` |
| Docker build медленный | `.dockerignore`, порядок `COPY`, lock-файл |
| Разные line endings | `.editorconfig`, `.gitattributes` |
| Node version отличается | `.nvmrc`, `.node-version`, `engines` |

#### Если уточнили

> - **Почему `.gitignore` не сработал на уже закоммиченный файл?** Git ignore применяется к untracked files. Уже tracked файл нужно отдельно убрать из index.
> - **Можно ли хранить npm token в `.npmrc`?** Не реальным значением. Безопаснее использовать `${NPM_TOKEN}` и передавать token через env/CI variables.
> - **Что обязательно написать в README frontend-проекта?** Node/package manager, install, env, dev, build, test, lint, deploy notes и troubleshooting.
> - **Чем `.dockerignore` отличается от `.gitignore`?** `.dockerignore` влияет только на Docker build context, `.gitignore` - на Git.

#### Пример

```gitignore
node_modules
dist
coverage
.env.local
.env.*.local
.vite
.turbo
npm-debug.log*
```

```ini
# .npmrc
@company:registry=https://registry.example.com/npm/
//registry.example.com/npm/:_authToken=${NPM_TOKEN}
strict-peer-deps=true
```

Первый пример не даёт коммитить generated/local файлы. Второй показывает идею private registry без хардкода реального токена.

#### Частые ошибки

- Коммитить `.env.local` или реальные tokens в `.npmrc`.
- Думать, что `.gitignore` удаляет уже tracked files.
- Игнорировать lock-файл вместе с generated files.
- Не документировать package manager и Node version в README.
- Путать `.dockerignore` и `.gitignore`.
- Хранить личные editor-файлы в проектном `.gitignore`.

#### Связанные темы

- [[Конспект для подготовки/Tooling/Файлы frontend проекта]]
- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]
- [[Конспект для подготовки/Tooling/npm yarn pnpm и package managers]]
- [[Конспект для подготовки/Tooling/Env files и frontend переменные]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/Security/Supply chain secrets и third-party scripts]]
- [[Конспект для подготовки/Git/Git для frontend]]

#### Источники

- [Git Docs: gitignore](https://git-scm.com/docs/gitignore)
- [npm Docs: .npmrc](https://docs.npmjs.com/cli/v10/configuring-npm/npmrc/)
- [npm Docs: package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json/)
- [Docker Docs: .dockerignore](https://docs.docker.com/build/concepts/context/#dockerignore-files)
