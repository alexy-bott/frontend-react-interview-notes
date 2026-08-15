# Инструменты разработки

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./01 Файлы фронтенд-проекта.md>)

Заметок в разделе: **12**
<!-- SECTION-NAV:END -->

## Темы

- [Файлы фронтенд-проекта](<./01 Файлы фронтенд-проекта.md>)
- [package.json и lock-файлы](<./02 package.json и lock-файлы.md>)
- [Версии зависимостей и semver](<./03 Версии зависимостей и semver.md>)
- [npm, Yarn, pnpm и менеджеры пакетов](<./04 npm, Yarn, pnpm и менеджеры пакетов.md>)
- [Воспроизводимые версии в команде](<./05 Воспроизводимые версии в команде.md>)
- [Файлы окружения и переменные фронтенда](<./06 Файлы окружения и переменные фронтенда.md>)
- [ESLint, Prettier и конфигурация качества кода](<./07 ESLint, Prettier и конфигурация качества кода.md>)
- [.gitignore, .npmrc, README и служебные файлы](<./08 .gitignore, .npmrc, README и служебные файлы.md>)
- [Анализ бандла и бюджет размера](<./09 Анализ бандла и бюджет размера.md>)
- [Vite](<./10 Vite.md>)
- [Webpack](<./11 Webpack.md>)
- [Конфигурация production-сборки](<./12 Конфигурация production-сборки.md>)

## Связанные разделы

- [Размер бандла и стратегия загрузки](<../Производительность/03 Размер бандла и стратегия загрузки.md>)

## Маршрут

1. Прочитать root files как связанные contracts: manifest, lock, TypeScript, build, tests, env и CI.
2. Разделить SemVer constraints, lock resolution, package-manager layout и install result.
3. Зафиксировать воспроизводимый toolchain: Node/manager/platform, frozen install и один release artifact.
4. Разобрать public/build/runtime config, затем `.gitignore`, registry auth, README и quality configs.
5. Понять Vite development graph, dependency optimization, HMR и версионную границу Vite 8/Rolldown.
6. Понять Webpack compilation: entries, loaders, plugins, chunks, output и dev/prod contracts.
7. Проследить состав bundle: import chain, tree shaking, dynamic splits, execution cost и size budgets.
8. Собрать production build contract: resolution, browser target, assets URLs, maps, hosting и smoke verification.
