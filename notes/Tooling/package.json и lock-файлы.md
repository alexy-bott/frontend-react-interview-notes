# package.json и lock-файлы

<!-- NOTE-NAV-TOP:START -->
[← Файлы frontend проекта](<./Файлы frontend проекта.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Версии зависимостей semver →](<./Версии зависимостей semver.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`package.json` - это manifest frontend-проекта. В нём описывают имя проекта, scripts, зависимости, ограничения по Node/package manager, настройки публикации и иногда конфиги инструментов. Для приложения самые важные поля: `scripts`, `dependencies`, `devDependencies`, `peerDependencies`, `engines`, `type`, `private`, `packageManager`, иногда `exports` и `workspaces`.

Lock-файл (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) фиксирует результат dependency resolution: точные versions, transitive graph и данные проверки/получения packages. Его коммитят и устанавливают тем же package manager, чтобы команда и CI не выбирали заново допустимые versions при каждом install.

`npm install` может обновить lock-файл, если `package.json` и lock расходятся. `npm ci` предназначен для чистой воспроизводимой установки в CI: он ставит зависимости строго по lock-файлу и падает, если lock не соответствует `package.json`.

## Ключевая схема

| Файл/поле | Зачем нужно |
| --- | --- |
| `package.json` | manifest проекта и точка входа для npm scripts |
| `scripts` | команды `dev`, `build`, `test`, `lint`, `typecheck` |
| `dependencies` | пакеты, нужные приложению в runtime/bundle |
| `devDependencies` | инструменты разработки: TS, linters, test runners, bundlers |
| `peerDependencies` | требование к пакету, который должен предоставить consumer |
| `engines` | заявленный диапазон совместимости Node/package manager |
| `packageManager` | фиксирует npm/yarn/pnpm и версию package manager |
| `type` | режим `.js` файлов: ESM или CommonJS |
| `exports` | публичные entrypoints пакета |
| `private` | защита от случайной публикации |
| lock-файл | точное dependency tree для команды и CI |
| `node_modules` | установленный результат, обычно не коммитится |

## Базовая модель

`package.json` задаёт **constraints и intent**, lock-файл — выбранный resolution, package manager — алгоритм/materialization, а `node_modules`/PnP map — локальный install result. Один lock не выравнивает Node, OS/CPU, package-manager version и environment-sensitive install scripts, поэтому воспроизводимость требует согласовать весь toolchain.

## Развернутый ответ

**`package.json` отвечает на вопрос “что это за проект и как с ним работать”.**
Frontend-разработчик обычно смотрит туда первым: какие есть scripts, какой package manager используется, какие версии React/Next/Vite/Jest стоят, какие зависимости runtime, а какие нужны только для разработки.

**`dependencies` и `devDependencies` описывают install/deploy intent, а не bundle boundary.**
Для публикуемой library runtime imports относятся в `dependencies`/`peerDependencies`, build/test tools — в `devDependencies`. Static frontend build обычно устанавливает devDependencies на build stage, а runtime image может содержать только готовые assets. Если client source импортирует package, bundler способен включить его независимо от раздела manifest.

**`peerDependencies` важны для библиотек и UI-kit пакетов.**
Если library работает с React, она часто объявляет React как peer dependency: library выражает совместимый range и ожидает единый экземпляр в consumer graph. Современный package manager может автоматически установить peer, но compatibility/duplicate-instance problem от этого не исчезает.

`engines` сообщает supported runtime range и может выдать warning; строгое enforcement зависит от package manager/config. Для команды version дополнительно фиксируют version file, `packageManager`, CI/Docker image.

**Lock-файл фиксирует не только прямые зависимости.**
В `package.json` может быть `"react": "^19.0.0"`, но реальная установка включает много транзитивных пакетов. Lock-файл записывает конкретное дерево, чтобы завтра npm не собрал чуть другое окружение из-за обновившейся транзитивной зависимости.

**`npm install` и `npm ci` используют разные сценарии.**
`npm install` удобен в разработке: он может добавить пакет и обновить lock. `npm ci` удобен в CI и Docker build: он ожидает готовый lock, удаляет существующий `node_modules` и ставит зависимости воспроизводимо. Если `package.json` и lock не совпадают, `npm ci` завершится ошибкой.

**Удалять lock-файл без причины опасно.**
После удаления lock npm пересоберёт dependency tree заново. Даже если версии в `package.json` выглядят теми же, транзитивные зависимости могут измениться, и проект получит другой результат. Lock обновляют осознанно: при добавлении/удалении пакета, обновлении зависимостей, смене package manager или исправлении конфликтов.

## Практическое применение

| Ситуация | Что проверять |
| --- | --- |
| Новый проект | `scripts`, `packageManager`, версия Node, lock-файл |
| CI падает на install | совпадают ли `package.json`, lock и package manager |
| “У меня работает” | одинаковые ли Node, package manager и lock |
| Bundle неожиданно вырос | не импортируется ли heavy dependency в runtime-код |
| UI-kit или shared package | корректны ли `peerDependencies` |
| Docker build | используется ли `npm ci`/аналог и копируется ли lock |
| Обновление зависимостей | понятен ли diff lock-файла |

## Пример

```json
{
  "private": true,
  "type": "module",
  "packageManager": "npm@10.9.8",
  "engines": {
    "node": ">=20"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "test": "vitest run",
    "lint": "eslint ."
  },
  "dependencies": {
    "@reduxjs/toolkit": "^2.0.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^5.0.0",
    "typescript": "^5.0.0",
    "vite": "^8.0.0",
    "vitest": "^4.0.0"
  }
}
```

Этот manifest говорит: проект приватный, использует ESM, ожидает конкретный package manager, имеет стандартные scripts и разделяет runtime-зависимости от инструментов разработки.

## Ключевые уточнения

- Application lock-файл коммитят; library также часто коммитит lock для собственного CI, но published consumers решают graph своим lock.
- `npm ci` проверяет согласованность manifest/lock и делает clean install; это не гарантирует одинаковый native result при разном OS/Node.
- Integrity hash подтверждает соответствие скачанного archive lock-записи, но не доказывает безопасность package.
- `dependencies`/`devDependencies` влияют на install semantics, а imports/tree shaking — на client bundle.
- `peerDependencies` выражает compatibility и shared-instance expectation; warning требует анализа, а не слепого `--legacy-peer-deps`.
- `engines` без enforcement является constraint/documentation, не полноценным version switcher.
- Lock conflict разрешают package manager и проверяют diff, а не удаляют файл по умолчанию.

## Связанные темы

- [Версии зависимостей semver](<./Версии зависимостей semver.md>)
- [npm yarn pnpm и package managers](<./npm yarn pnpm и package managers.md>)
- [Воспроизводимые версии в команде](<./Воспроизводимые версии в команде.md>)
- [Файлы frontend проекта](<./Файлы frontend проекта.md>)
- [Build config и production сборка](<./Build config и production сборка.md>)
- [Frontend pipeline](<../DevOps/Frontend pipeline.md>)
- [Dockerfile и multi-stage build](<../DevOps/Dockerfile и multi-stage build.md>)
- [Supply chain secrets и third-party scripts](<../Security/Supply chain secrets и third-party scripts.md>)

## Источники

- [npm Docs: package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json/)
- [npm Docs: package-lock.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json/)
- [npm Docs: npm ci](https://docs.npmjs.com/cli/v10/commands/npm-ci/)
- [Node.js Docs: Packages](https://nodejs.org/api/packages.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Файлы frontend проекта](<./Файлы frontend проекта.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Версии зависимостей semver →](<./Версии зависимостей semver.md>)
<!-- NOTE-NAV-BOTTOM:END -->
