# Gitignore npmrc README и служебные файлы

<!-- NOTE-NAV-TOP:START -->
[← ESLint Prettier и code quality configs](<./ESLint Prettier и code quality configs.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Bundle analysis и size budgets →](<./Bundle analysis и size budgets.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Служебные файлы проекта задают правила работы команды и инструментов. `.gitignore` говорит Git, какие неотслеживаемые файлы игнорировать: `node_modules`, `dist`, `.env.local`, coverage, cache, logs. `.npmrc` настраивает npm: registry, scope registry, auth token через env, strict-peer-deps, proxy и другие параметры. `README.md` описывает, как проект запускать, тестировать, собирать и какие env нужны.

Эти файлы важны не меньше исходников: ошибка в `.gitignore` может привести к коммиту секретов или build artifacts, ошибка в `.npmrc` - к проблемам с private packages, плохой README - к долгому onboarding и разным локальным сценариям у команды.

## Ключевая схема

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

## Базовая модель

Служебный файл является tooling contract. `.gitignore` влияет только на tracking untracked paths, `.npmrc` — на package-manager network/install behavior, `.dockerignore` — на build context, README — на человеческий workflow. Похожие paths не означают одинаковую область действия.

## Развернутый ответ

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

`.env.example` документирует keys и безопасные placeholders, но не содержит production values. `.gitattributes` фиксирует line endings и отдельные merge/diff policies; `.editorconfig` задаёт базовые editor rules, не заменяя formatter.

## Практическое применение

| Ситуация | Какой файл смотреть |
| --- | --- |
| В repo попал `.env.local` | `.gitignore`, git history, rotation secrets |
| CI не может скачать private package | `.npmrc`, CI variables, registry auth |
| Новый разработчик не может запустить проект | `README.md`, `.nvmrc`, `packageManager` |
| Docker build медленный | `.dockerignore`, порядок `COPY`, lock-файл |
| Разные line endings | `.editorconfig`, `.gitattributes` |
| Node version отличается | `.nvmrc`, `.node-version`, `engines` |

## Пример

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

## Ключевые уточнения

- `.gitignore` не прекращает tracking и не очищает history; exposed credential отзывают независимо от удаления файла.
- Project `.npmrc` может ссылаться на `${NPM_TOKEN}`, но secret не передают через Docker `ARG`/layer и не печатают в CI logs.
- Registry auth ограничивают нужным host/scope, чтобы credential не отправлялся постороннему registry.
- Lock-файл и intentional generated contracts не игнорируют вместе с disposable caches.
- `.dockerignore` защищает context/image path, `.gitignore` — repository path; нужны оба независимых списка.
- README фиксирует supported happy path и links на подробные runbooks, а не копирует быстро устаревающую документацию целиком.
- Личные editor/OS patterns лучше хранить в global ignore, если они не являются общим project output.

## Связанные темы

- [Файлы frontend проекта](<./Файлы frontend проекта.md>)
- [package.json и lock-файлы](<./package.json и lock-файлы.md>)
- [npm yarn pnpm и package managers](<./npm yarn pnpm и package managers.md>)
- [Env files и frontend переменные](<./Env files и frontend переменные.md>)
- [Dockerfile и multi-stage build](<../DevOps/Dockerfile и multi-stage build.md>)
- [Env variables и секреты](<../DevOps/Env variables и секреты.md>)
- [Supply chain secrets и third-party scripts](<../Security/Supply chain secrets и third-party scripts.md>)
- [Git для frontend](<../Git/Git для frontend.md>)

## Источники

- [Git Docs: gitignore](https://git-scm.com/docs/gitignore)
- [npm Docs: .npmrc](https://docs.npmjs.com/cli/v10/configuring-npm/npmrc/)
- [npm Docs: package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json/)
- [Docker Docs: .dockerignore](https://docs.docker.com/build/concepts/context/#dockerignore-files)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← ESLint Prettier и code quality configs](<./ESLint Prettier и code quality configs.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Bundle analysis и size budgets →](<./Bundle analysis и size budgets.md>)
<!-- NOTE-NAV-BOTTOM:END -->
