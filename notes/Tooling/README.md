# Tooling

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Файлы frontend проекта.md>)

Заметок в разделе: **12**
<!-- SECTION-NAV:END -->

## Темы

- [Файлы frontend проекта](<./Файлы frontend проекта.md>)
- [package.json и lock-файлы](<./package.json и lock-файлы.md>)
- [Версии зависимостей semver](<./Версии зависимостей semver.md>)
- [npm yarn pnpm и package managers](<./npm yarn pnpm и package managers.md>)
- [Воспроизводимые версии в команде](<./Воспроизводимые версии в команде.md>)
- [Env files и frontend переменные](<./Env files и frontend переменные.md>)
- [ESLint Prettier и code quality configs](<./ESLint Prettier и code quality configs.md>)
- [Gitignore npmrc README и служебные файлы](<./Gitignore npmrc README и служебные файлы.md>)
- [Bundle analysis и size budgets](<./Bundle analysis и size budgets.md>)
- [Vite](<./Vite.md>)
- [Webpack](<./Webpack.md>)
- [Build config и production сборка](<./Build config и production сборка.md>)

## Связанные разделы

- [Bundle size и loading strategy](<../Performance/Bundle size и loading strategy.md>)

## Маршрут

1. Прочитать root files как связанные contracts: manifest, lock, TypeScript, build, tests, env и CI.
2. Разделить SemVer constraints, lock resolution, package-manager layout и install result.
3. Зафиксировать воспроизводимый toolchain: Node/manager/platform, frozen install и один release artifact.
4. Разобрать public/build/runtime config, затем `.gitignore`, registry auth, README и quality configs.
5. Понять Vite development graph, dependency optimization, HMR и версионную границу Vite 8/Rolldown.
6. Понять Webpack compilation: entries, loaders, plugins, chunks, output и dev/prod contracts.
7. Проследить состав bundle: import chain, tree shaking, dynamic splits, execution cost и size budgets.
8. Собрать production build contract: resolution, browser target, assets URLs, maps, hosting и smoke verification.
