#### Темы

- [[Конспект для подготовки/Tooling/Файлы frontend проекта]]
- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]
- [[Конспект для подготовки/Tooling/Версии зависимостей semver]]
- [[Конспект для подготовки/Tooling/npm yarn pnpm и package managers]]
- [[Конспект для подготовки/Tooling/Воспроизводимые версии в команде]]
- [[Конспект для подготовки/Tooling/Env files и frontend переменные]]
- [[Конспект для подготовки/Tooling/ESLint Prettier и code quality configs]]
- [[Конспект для подготовки/Tooling/Gitignore npmrc README и служебные файлы]]
- [[Конспект для подготовки/Tooling/Bundle analysis и size budgets]]
- [[Конспект для подготовки/Tooling/Vite]]
- [[Конспект для подготовки/Tooling/Webpack]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]

#### Связанные разделы

- [[Конспект для подготовки/Performance/Bundle size и loading strategy]]

#### Маршрут

1. Прочитать root files как связанные contracts: manifest, lock, TypeScript, build, tests, env и CI.
2. Разделить SemVer constraints, lock resolution, package-manager layout и install result.
3. Зафиксировать воспроизводимый toolchain: Node/manager/platform, frozen install и один release artifact.
4. Разобрать public/build/runtime config, затем `.gitignore`, registry auth, README и quality configs.
5. Понять Vite development graph, dependency optimization, HMR и версионную границу Vite 8/Rolldown.
6. Понять Webpack compilation: entries, loaders, plugins, chunks, output и dev/prod contracts.
7. Проследить состав bundle: import chain, tree shaking, dynamic splits, execution cost и size budgets.
8. Собрать production build contract: resolution, browser target, assets URLs, maps, hosting и smoke verification.
