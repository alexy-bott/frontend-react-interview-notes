---
aliases:
  - файлы frontend проекта
  - конфиги frontend проекта
  - структура frontend проекта
  - project files frontend
---

#### Быстрый ответ

Frontend-проект состоит из application source и contracts инструментов вокруг него. Root files определяют dependency resolution, Node/package-manager version, TypeScript model, dev/build pipeline, tests, code quality, environment values, container и CI. Поэтому одинаковый `src` способен собраться и работать по-разному при разных manifests/configs.

Самые важные файлы: `package.json`, lock-файл, `tsconfig.json`, `vite.config.ts` или `webpack.config.js`, `.env*`, `.gitignore`, `.npmrc`, `eslint.config.*`, `prettier.config.*`, `jest.config.*`/`vitest.config.*`, `Dockerfile`, `.gitlab-ci.yml`. Не нужно знать каждую опцию наизусть, но нужно понимать назначение файла, когда его трогают и какие ошибки он может вызвать.

#### Ключевая схема

| Файл | За что отвечает |
| --- | --- |
| `package.json` | scripts, зависимости, package metadata |
| `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` | точное dependency tree |
| `tsconfig.json` | TypeScript compiler options, paths, strictness |
| `vite.config.ts` | dev server, aliases, env, proxy, production build |
| `webpack.config.js` | entry/output, loaders, plugins, optimization |
| `.env*` | входные значения tools; build/runtime зависит от потребителя |
| `.gitignore` | что не попадёт в git |
| `.npmrc` | registry, auth/config npm, strict-peer-deps, proxy |
| `eslint.config.*` | правила статического анализа |
| `prettier.config.*` | форматирование кода |
| `jest.config.*` / `vitest.config.*` | test environment, transforms, aliases, setup |
| `Dockerfile` | как собрать image |
| `.gitlab-ci.yml` | pipeline: install, lint, test, build, deploy |
| `README.md` | onboarding и команды проекта |

#### Базовая модель

Конфиги образуют связанный graph, а не независимый набор файлов. Alias должен одинаково пониматься TypeScript, bundler, tests и lint resolver; Node/package-manager version должна совпадать локально, в CI и Docker; public env должна попасть в нужный build, а secret — не попасть в client output.

#### Развернутый ответ

**`package.json` и lock-файл отвечают за зависимости и команды.**
Первое, что смотрят в новом проекте: package manager, scripts, версии основных библиотек и lock-файл. Если CI падает на install, часто причина находится именно здесь.

**`tsconfig.json` задаёт правила TypeScript.**
Там включают `strict`, настраивают `jsx`, `moduleResolution`, `baseUrl`, `paths`, `lib`, `types`, `noEmit`. Ошибка в `tsconfig` может ломать aliases, типы DOM/WebWorker, imports или поведение typecheck в CI.

**Build config отвечает за то, как исходники превращаются в assets.**
В `vite.config.ts` или `webpack.config.js` обычно настраивают aliases, env, proxy, assets, sourcemaps, base/publicPath, code splitting и plugins. Dev server и production build - разные режимы, поэтому работающее dev-окружение ещё не доказывает корректную production-сборку.

**Lint/format/test configs отвечают за качество изменений.**
ESLint ловит проблемы кода и командных правил, Prettier стабилизирует форматирование, Jest/Vitest config задаёт test environment, setup files, transforms, aliases и coverage. Если aliases есть в Vite/TS, их часто нужно синхронизировать и для тестов.

**Env, Docker и CI связывают код с окружением.**
`.env*` управляет значениями окружения, Dockerfile описывает сборку image, `.gitlab-ci.yml` фиксирует pipeline. Ошибки здесь дают типичные проблемы: локально работает, а в CI нет; dev API работает, а production routing сломан; env поменяли, но static bundle остался старым.

#### Диагностика по файлам

| Симптом или вопрос | Где искать contract |
| --- | --- |
| Зачем нужен `package.json`? | понимаешь scripts, dependencies и manifest проекта |
| Зачем lock-файл? | понимаешь воспроизводимость install |
| Зачем `tsconfig.json`? | понимаешь TypeScript как часть build/typecheck |
| Где настраиваются aliases? | умеешь связать TS, bundler и tests |
| Зачем `.npmrc`? | registry, auth, package manager behavior |
| Почему env не секреты? | понимаешь клиентский bundle и server-side границы |
| Чем ESLint отличается от Prettier? | lint rules против форматирования |
| Почему тесты не видят alias `@`? | test config не синхронизирован с TS/bundler |
| Почему Docker build падает на install? | lock/package manager/Node version |
| Почему production build отличается от dev? | разные режимы сборки и env |

#### Пример маршрута чтения нового проекта

1. Открыть `package.json`: scripts, package manager, основные зависимости.
2. Проверить lock-файл: npm/yarn/pnpm, нет ли смешивания.
3. Посмотреть `README.md`: команды запуска и env.
4. Открыть `tsconfig.json`: strictness, paths, JSX, module resolution.
5. Открыть build config: aliases, proxy, base/publicPath, env, sourcemaps.
6. Проверить test/lint config: aliases, setup, environment, coverage.
7. Посмотреть Docker/CI: install command, Node image, cache, build artifacts.

#### Ключевые уточнения

- Роль config определяется инструментом, который его читает; `.env` сам по себе не создаёт runtime configuration.
- Aliases, module format и browser/Node targets согласуют между compiler, bundler, tests и runtime.
- Manifest и lock коммитят, `node_modules`/build cache восстанавливают; generated file не игнорируют автоматически только из-за размера.
- Local env и auth config не являются местом для client secrets; утёкший tracked secret ротируют.
- Dev server проверяет development path, production build и serving проверяются отдельно.
- Опции не запоминают списком: сначала определяют owner contract и читают versioned docs инструмента.

#### Связанные темы

- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]
- [[Конспект для подготовки/Tooling/Версии зависимостей semver]]
- [[Конспект для подготовки/Tooling/npm yarn pnpm и package managers]]
- [[Конспект для подготовки/Tooling/Env files и frontend переменные]]
- [[Конспект для подготовки/Tooling/ESLint Prettier и code quality configs]]
- [[Конспект для подготовки/Tooling/Gitignore npmrc README и служебные файлы]]
- [[Конспект для подготовки/Tooling/Vite]]
- [[Конспект для подготовки/Tooling/Webpack]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]
- [[Конспект для подготовки/TypeScript/tsconfig и strict mode]]
- [[Конспект для подготовки/Testing/Jest]]
- [[Конспект для подготовки/DevOps/GitLab CI CD]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]

#### Источники

- [npm Docs: package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json/)
- [npm Docs: .npmrc](https://docs.npmjs.com/cli/v10/configuring-npm/npmrc/)
- [TypeScript Docs: tsconfig.json](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html)
- [Vite Docs: Config](https://vite.dev/config/)
- [Webpack Docs: Configuration](https://webpack.js.org/configuration/)
- [ESLint Docs: Configuration Files](https://eslint.org/docs/latest/use/configure/configuration-files)
- [Prettier Docs: Configuration File](https://prettier.io/docs/configuration)
- [Jest Docs: Configuration](https://jestjs.io/docs/configuration)
- [Vitest Docs: Configuring Vitest](https://vitest.dev/config/)
