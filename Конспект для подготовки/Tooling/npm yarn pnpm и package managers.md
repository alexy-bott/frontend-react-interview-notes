---
aliases:
  - npm yarn pnpm
  - package managers
  - npm
  - yarn
  - pnpm
  - Corepack
---

#### Ответ на 60 секунд

Package manager устанавливает зависимости, строит `node_modules` или альтернативную модель доступа к пакетам, запускает scripts и поддерживает lock-файл. Во frontend чаще встречаются npm, Yarn и pnpm. Главное правило: в одном проекте используют один package manager и один lock-файл.

npm - стандартный package manager, который идёт вместе с Node.js. Yarn часто используют из-за развитой workspace-модели, Plug'n'Play и настроек монорепозиториев. pnpm отличается content-addressable store и строгой моделью зависимостей: пакеты физически переиспользуются через общий store, а проект получает ссылки на них.

Для команды важны не “личные предпочтения”, а воспроизводимость: `packageManager` в `package.json`, lock-файл, одинаковые команды в README/CI/Docker и отсутствие смешивания `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`.

#### Ключевая схема

| Инструмент | Lock-файл | Что важно понимать |
| --- | --- | --- |
| npm | `package-lock.json` | стандартный выбор, `npm ci` для CI |
| Yarn | `yarn.lock` | workspaces, `.yarnrc.yml`, возможен Plug'n'Play |
| pnpm | `pnpm-lock.yaml` | общий store, symlinks, строгие зависимости |
| Corepack | нет своего lock | помогает использовать указанную версию package manager |
| `packageManager` | поле в `package.json` | фиксирует ожидаемый manager и его версию |

#### Развернутый ответ

**Package manager отвечает за dependency resolution.**
Он читает `package.json`, выбирает версии по semver-диапазонам, строит dependency tree, записывает lock-файл и создаёт окружение, из которого Node/bundler сможет импортировать пакеты.

**Смешивание package managers ломает воспроизводимость.**
Если один разработчик запускает `npm install`, второй `yarn install`, а CI использует `pnpm install`, lock-файлы и дерево зависимостей могут расходиться. В результате баги становятся плавающими: локально всё работает, а pipeline падает или собирает другой bundle.

**npm обычно объясняют через простоту и `npm ci`.**
Для большинства приложений npm достаточно: он понятен, установлен вместе с Node.js и поддерживает lock-файл. В CI обычно используют `npm ci`, потому что команда ставит зависимости строго по `package-lock.json`.

**Yarn и pnpm часто всплывают в монорепозиториях.**
Yarn активно используется с workspaces и своими настройками в `.yarnrc.yml`. pnpm популярен за счёт быстрого переиспользования пакетов через общий store и более строгой модели: пакет не должен случайно импортировать зависимость, которую он сам не объявил.

**`packageManager` делает выбор явным.**
Поле `"packageManager": "pnpm@9.0.0"` или `"npm@10.9.8"` помогает инструментам и людям понять, чем ставить зависимости. Это особенно важно для onboarding, CI, Docker и больших команд.

#### Где применяется во frontend

| Ситуация | Что проверять |
| --- | --- |
| Onboarding в проект | какой package manager указан в `packageManager` |
| CI install | команда должна соответствовать lock-файлу |
| Docker build | копировать нужный lock и использовать правильный install command |
| Монорепозиторий | workspaces и shared packages |
| Peer dependency warnings | версии React, UI-kit, testing libs |
| Ошибка “module not found” | зависимость реально объявлена или случайно подтягивалась hoisting-ом |
| Merge conflict lock-файла | не был ли lock создан другим manager |

#### Если уточнили

> - **Почему pnpm иногда ловит ошибки, которых не было в npm?** Из-за более строгой модели доступа к зависимостям. Если пакет импортирует зависимость, которую не объявил, pnpm чаще проявит проблему.
> - **Что такое workspaces?** Это способ управлять несколькими пакетами внутри одного репозитория: например, `app`, `shared/ui`, `shared/config`.
> - **Зачем Corepack?** Он помогает запускать нужный package manager/version, указанный проектом, вместо случайной глобальной версии.
> - **Можно ли просто удалить lock и поставить другим manager?** Только как осознанная миграция. Нужно обновить docs, CI, Docker, lock-файл и проверить сборку.

#### Пример команд

| Задача | npm | Yarn | pnpm |
| --- | --- | --- | --- |
| Установить зависимости | `npm install` | `yarn install` | `pnpm install` |
| CI install | `npm ci` | `yarn install --immutable` | `pnpm install --frozen-lockfile` |
| Добавить пакет | `npm install react` | `yarn add react` | `pnpm add react` |
| Добавить dev dependency | `npm install -D vite` | `yarn add -D vite` | `pnpm add -D vite` |
| Запустить script | `npm run build` | `yarn build` | `pnpm build` |

#### Частые ошибки

- Хранить несколько lock-файлов без явной причины.
- Не указывать package manager в README/CI.
- Путать глобальную версию manager и версию, ожидаемую проектом.
- Игнорировать peer dependency warnings.
- Мигрировать с npm на pnpm/yarn без обновления Docker и pipeline.
- Считать, что `node_modules` у разных package managers устроен одинаково.

#### Связанные темы

- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]
- [[Конспект для подготовки/Tooling/Версии зависимостей semver]]
- [[Конспект для подготовки/Tooling/Файлы frontend проекта]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/Architecture/FSD]]

#### Источники

- [npm Docs: package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json/)
- [npm Docs: Workspaces](https://docs.npmjs.com/cli/v10/using-npm/workspaces/)
- [Yarn Docs: Manifest package.json](https://yarnpkg.com/configuration/manifest)
- [pnpm Docs: Motivation](https://pnpm.io/motivation)
- [pnpm Docs: package.json](https://pnpm.io/package_json)
