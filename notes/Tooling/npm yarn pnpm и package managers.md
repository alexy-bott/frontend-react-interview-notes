# npm yarn pnpm и package managers

<!-- NOTE-NAV-TOP:START -->
[← Версии зависимостей semver](<./Версии зависимостей semver.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Воспроизводимые версии в команде →](<./Воспроизводимые версии в команде.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Package manager разрешает semver constraints, создаёт/проверяет lock, материализует dependency graph, запускает lifecycle/scripts и управляет workspaces. npm, Yarn и pnpm могут получить различное layout/peer behavior из одного manifest, поэтому проект фиксирует один manager/version и один lock format.

npm - стандартный package manager, который идёт вместе с Node.js. Yarn часто используют из-за развитой workspace-модели, Plug'n'Play и настроек монорепозиториев. pnpm отличается content-addressable store и строгой моделью зависимостей: пакеты физически переиспользуются через общий store, а проект получает ссылки на них.

Для команды важны не “личные предпочтения”, а воспроизводимость: `packageManager` в `package.json`, lock-файл, одинаковые команды в README/CI/Docker и отсутствие смешивания `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`.

## Ключевая схема

| Инструмент | Lock-файл | Что важно понимать |
| --- | --- | --- |
| npm | `package-lock.json` | стандартный выбор, `npm ci` для CI |
| Yarn | `yarn.lock` | workspaces, `.yarnrc.yml`, возможен Plug'n'Play |
| pnpm | `pnpm-lock.yaml` | общий store, symlinks, строгие зависимости |
| Corepack | нет своего lock | при установке/включении запускает manager из `packageManager` |
| `packageManager` | поле в `package.json` | фиксирует ожидаемый manager и его версию |

## Базовая модель

**Package manager отвечает за dependency resolution.**
Он читает `package.json`, выбирает версии по semver-диапазонам, строит dependency tree, записывает lock-файл и создаёт окружение, из которого Node/bundler сможет импортировать пакеты.

Resolution отвечает «какая version выбрана», layout — «откуда module доступен». Hoisting npm/Yarn может случайно сделать undeclared transitive dependency доступной; строгая linked layout pnpm чаще обнаруживает такой import. Код обязан объявлять прямые dependencies независимо от manager.

## Развернутый ответ

**Смешивание package managers ломает воспроизводимость.**
Если один разработчик запускает `npm install`, второй `yarn install`, а CI использует `pnpm install`, lock-файлы и дерево зависимостей могут расходиться. В результате баги становятся плавающими: локально всё работает, а pipeline падает или собирает другой bundle.

**npm обычно объясняют через простоту и `npm ci`.**
Для большинства приложений npm достаточно: он понятен, установлен вместе с Node.js и поддерживает lock-файл. В CI обычно используют `npm ci`, потому что команда ставит зависимости строго по `package-lock.json`.

**Yarn и pnpm часто всплывают в монорепозиториях.**
Yarn активно используется с workspaces и своими настройками в `.yarnrc.yml`. pnpm популярен за счёт быстрого переиспользования пакетов через общий store и более строгой модели: пакет не должен случайно импортировать зависимость, которую он сам не объявил.

**`packageManager` делает выбор явным.**
Поле `"packageManager": "pnpm@9.0.0"` или `"npm@10.9.8"` помогает инструментам и людям понять, чем ставить зависимости. Это особенно важно для onboarding, CI, Docker и больших команд.

Install выполняет package lifecycle scripts, то есть сторонний code может запускаться на машине/CI. `--ignore-scripts` снижает attack surface, но ломает packages, которым scripts нужны; решение принимают как supply-chain policy, а не универсальный флаг.

## Практическое применение

| Ситуация | Что проверять |
| --- | --- |
| Onboarding в проект | какой package manager указан в `packageManager` |
| CI install | команда должна соответствовать lock-файлу |
| Docker build | копировать нужный lock и использовать правильный install command |
| Монорепозиторий | workspaces и shared packages |
| Peer dependency warnings | версии React, UI-kit, testing libs |
| Ошибка “module not found” | зависимость реально объявлена или случайно подтягивалась hoisting-ом |
| Merge conflict lock-файла | не был ли lock создан другим manager |

## Пример команд

| Задача | npm | Yarn | pnpm |
| --- | --- | --- | --- |
| Установить зависимости | `npm install` | `yarn install` | `pnpm install` |
| CI install | `npm ci` | `yarn install --immutable` | `pnpm install --frozen-lockfile` |
| Добавить пакет | `npm install react` | `yarn add react` | `pnpm add react` |
| Добавить dev dependency | `npm install -D vite` | `yarn add -D vite` | `pnpm add -D vite` |
| Запустить script | `npm run build` | `yarn build` | `pnpm build` |

## Ключевые уточнения

- Manager выбирает graph по manifest и lock; npm/Yarn/pnpm layout и peer resolution не обязаны совпадать.
- Workspaces связывают несколько packages, но каждый package сохраняет собственные dependency boundaries.
- `packageManager` фиксирует intent; фактический manager обеспечивает Corepack/version manager/CI image.
- Frozen install запрещает незаявленное изменение lock, но не обновляет dependencies и не устраняет platform differences.
- Peer warning анализируют как compatibility problem; suppress flag может оставить runtime с двумя несовместимыми copies.
- Смена manager является migration с новым lock, CI/Docker/cache policy и полным verification.
- Install scripts выполняют dependency code и входят в supply-chain threat model.

## Связанные темы

- [package.json и lock-файлы](<./package.json и lock-файлы.md>)
- [Версии зависимостей semver](<./Версии зависимостей semver.md>)
- [Файлы frontend проекта](<./Файлы frontend проекта.md>)
- [Frontend pipeline](<../DevOps/Frontend pipeline.md>)
- [Dockerfile и multi-stage build](<../DevOps/Dockerfile и multi-stage build.md>)
- [FSD](<../Architecture/FSD.md>)

## Источники

- [npm Docs: package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json/)
- [npm Docs: Workspaces](https://docs.npmjs.com/cli/v10/using-npm/workspaces/)
- [Yarn Docs: Manifest package.json](https://yarnpkg.com/configuration/manifest)
- [pnpm Docs: Motivation](https://pnpm.io/motivation)
- [pnpm Docs: package.json](https://pnpm.io/package_json)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Версии зависимостей semver](<./Версии зависимостей semver.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Воспроизводимые версии в команде →](<./Воспроизводимые версии в команде.md>)
<!-- NOTE-NAV-BOTTOM:END -->
