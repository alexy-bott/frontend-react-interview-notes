---
aliases:
  - package.json
  - package-lock.json
  - lock-файлы
  - npm ci
  - npm install
---

#### Ответ на 60 секунд

`package.json` - это manifest frontend-проекта. В нём описывают имя проекта, scripts, зависимости, ограничения по Node/package manager, настройки публикации и иногда конфиги инструментов. Для приложения самые важные поля: `scripts`, `dependencies`, `devDependencies`, `peerDependencies`, `engines`, `type`, `private`, `packageManager`, иногда `exports` и `workspaces`.

Lock-файл (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) фиксирует конкретное дерево установленных зависимостей: точные версии, resolved URLs, integrity hashes и транзитивные зависимости. Его коммитят, чтобы локальная установка, CI и production build получали одинаковое дерево пакетов.

`npm install` может обновить lock-файл, если `package.json` и lock расходятся. `npm ci` предназначен для чистой воспроизводимой установки в CI: он ставит зависимости строго по lock-файлу и падает, если lock не соответствует `package.json`.

#### Ключевая схема

| Файл/поле | Зачем нужно |
| --- | --- |
| `package.json` | manifest проекта и точка входа для npm scripts |
| `scripts` | команды `dev`, `build`, `test`, `lint`, `typecheck` |
| `dependencies` | пакеты, нужные приложению в runtime/bundle |
| `devDependencies` | инструменты разработки: TS, linters, test runners, bundlers |
| `peerDependencies` | требование к пакету, который должен предоставить consumer |
| `engines` | ожидаемые версии Node/npm |
| `packageManager` | фиксирует npm/yarn/pnpm и версию package manager |
| `type` | режим `.js` файлов: ESM или CommonJS |
| `exports` | публичные entrypoints пакета |
| `private` | защита от случайной публикации |
| lock-файл | точное dependency tree для команды и CI |
| `node_modules` | установленный результат, обычно не коммитится |

#### Развернутый ответ

**`package.json` отвечает на вопрос “что это за проект и как с ним работать”.**
Frontend-разработчик обычно смотрит туда первым: какие есть scripts, какой package manager используется, какие версии React/Next/Vite/Jest стоят, какие зависимости runtime, а какие нужны только для разработки.

**`dependencies` и `devDependencies` различаются по смыслу, а не по месту в bundle.**
`dependencies` - это библиотеки, которые нужны приложению или пакету как часть работы: React, state manager, date library, UI kit. `devDependencies` - инструменты для разработки и сборки: TypeScript, ESLint, Prettier, Jest/Vitest, Vite/Webpack plugins. Но bundler может включить пакет в клиентский bundle, если код импортирует его из runtime-кода, даже если пакет случайно лежит в `devDependencies`.

**`peerDependencies` важны для библиотек и UI-kit пакетов.**
Если библиотека работает с React, она часто объявляет React как peer dependency. Это означает: “я совместима с React такой версии, но React должен быть установлен в проекте-потребителе”. Так избегают ситуации, когда в приложении случайно появляются две копии React.

**Lock-файл фиксирует не только прямые зависимости.**
В `package.json` может быть `"react": "^19.0.0"`, но реальная установка включает много транзитивных пакетов. Lock-файл записывает конкретное дерево, чтобы завтра npm не собрал чуть другое окружение из-за обновившейся транзитивной зависимости.

**`npm install` и `npm ci` используют разные сценарии.**
`npm install` удобен в разработке: он может добавить пакет и обновить lock. `npm ci` удобен в CI и Docker build: он ожидает готовый lock, удаляет существующий `node_modules` и ставит зависимости воспроизводимо. Если `package.json` и lock не совпадают, `npm ci` завершится ошибкой.

**Удалять lock-файл без причины опасно.**
После удаления lock npm пересоберёт dependency tree заново. Даже если версии в `package.json` выглядят теми же, транзитивные зависимости могут измениться, и проект получит другой результат. Lock обновляют осознанно: при добавлении/удалении пакета, обновлении зависимостей, смене package manager или исправлении конфликтов.

#### Где применяется во frontend

| Ситуация | Что проверять |
| --- | --- |
| Новый проект | `scripts`, `packageManager`, версия Node, lock-файл |
| CI падает на install | совпадают ли `package.json`, lock и package manager |
| “У меня работает” | одинаковые ли Node, package manager и lock |
| Bundle неожиданно вырос | не импортируется ли heavy dependency в runtime-код |
| UI-kit или shared package | корректны ли `peerDependencies` |
| Docker build | используется ли `npm ci`/аналог и копируется ли lock |
| Обновление зависимостей | понятен ли diff lock-файла |

#### Если уточнили

> - **Нужно ли коммитить lock-файл?** Для приложений - да. Он нужен для воспроизводимых установок у команды, в CI и при сборке Docker image.
> - **Почему не коммитят `node_modules`?** Это тяжёлый сгенерированный результат установки, зависящий от платформы, package manager и lock-файла. В репозитории хранят manifest и lock, а зависимости устанавливают заново.
> - **Можно ли иметь сразу `package-lock.json` и `yarn.lock`?** Обычно нет. Один проект должен использовать один package manager и один lock-файл, иначе команда и CI могут ставить разные деревья зависимостей.
> - **Что делает `"private": true`?** Защищает проект от случайной публикации в npm registry.
> - **Зачем `"type": "module"`?** Поле влияет на то, как Node интерпретирует `.js` файлы: как ES modules или CommonJS.

#### Пример

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
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
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

#### Частые ошибки

- Удалять lock-файл, чтобы “починить установку”, не понимая последствия.
- Смешивать npm/yarn/pnpm lock-файлы в одном проекте.
- Использовать `npm install` в CI вместо `npm ci`, когда нужен строгий reproducible install.
- Класть runtime dependency в `devDependencies` и считать, что bundler её не включит.
- Забывать про `peerDependencies` в shared packages и UI-kit.
- Не фиксировать package manager в `packageManager`.
- Игнорировать diff lock-файла в merge request.

#### Связанные темы

- [[Конспект для подготовки/Tooling/Версии зависимостей semver]]
- [[Конспект для подготовки/Tooling/npm yarn pnpm и package managers]]
- [[Конспект для подготовки/Tooling/Воспроизводимые версии в команде]]
- [[Конспект для подготовки/Tooling/Файлы frontend проекта]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/Security/Supply chain secrets и third-party scripts]]

#### Источники

- [npm Docs: package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json/)
- [npm Docs: package-lock.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json/)
- [npm Docs: npm ci](https://docs.npmjs.com/cli/v10/commands/npm-ci/)
- [Node.js Docs: Packages](https://nodejs.org/api/packages.html)
