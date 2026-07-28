---
aliases:
  - bundle analysis
  - bundle analyzer
  - size budgets
  - что входит в bundle
  - контроль размера bundle
---

#### Ответ на 60 секунд

В bundle попадает не всё из `package.json`, а только то, до чего дошёл dependency graph от entrypoints: статические imports, CSS/assets imports, код зависимостей, который реально импортируется из runtime-кода, и chunks от dynamic import. `dependencies` или `devDependencies` сами по себе не решают, попадёт пакет в клиентский bundle или нет: решает импорт и настройка bundler.

Чтобы понять состав bundle, используют production build, bundle analyzer, sourcemap/visualizer, Webpack stats, Vite/Rollup output и browser Coverage. Важно смотреть не только общий размер, а initial JS, route chunks, vendor chunks, parse/execute cost и waterfall.

Ограничивают bundle через size budgets в CI, Webpack performance hints, custom scripts, bundle analyzer checks, dependency review, lazy loading, tree shaking, точечные imports, замену тяжёлых библиотек, `manualChunks`/`splitChunks`, правильный `sideEffects` и запрет случайных imports через lint/review.

#### Ключевая схема

```text
entrypoint
  -> static imports
  -> dependency graph
  -> tree shaking / minification
  -> initial chunks + async chunks + assets
  -> analyzer / budgets / CI gate
```

| Вопрос | Что смотреть |
| --- | --- |
| Что попало в bundle? | analyzer, stats, output chunks |
| Почему пакет попал в bundle? | import chain / module reasons |
| Почему bundle большой? | vendor chunk, heavy deps, duplicated deps, locales, icons |
| Что грузится сразу? | initial chunks / entrypoint size |
| Что грузится позже? | dynamic import chunks |
| Почему tree shaking не сработал? | CommonJS, side effects, namespace imports, wrong package metadata |
| Как ограничить размер? | budgets в CI, Webpack performance, custom size check |
| Как не сломать UX splitting-ом? | Network waterfall, preload/prefetch, Suspense fallback |

#### Развернутый ответ

**Bundle начинается с entrypoint.**
Bundler берёт входные точки приложения и строит dependency graph. Если файл импортируется из entrypoint напрямую или через цепочку imports, он становится кандидатом на попадание в build output. Dynamic import обычно создаёт отдельный async chunk: код всё ещё входит в build output, но не загружается на первом экране.

**`dependencies` и `devDependencies` не являются границей bundle.**
Если runtime-код импортирует пакет, bundler может включить его в клиентский JS даже если пакет лежит в `devDependencies`. И наоборот: пакет из `dependencies` не попадёт в bundle, если он нигде не импортируется в клиентском графе. Разделы зависимостей важны для install/deploy semantics, но состав bundle определяется графом импортов.

**Tree shaking удаляет неиспользуемый код не всегда.**
Лучше всего он работает с ES modules, где bundler статически видит imports/exports. Ограничения: CommonJS, top-level side effects, неправильное поле `sideEffects`, namespace imports, barrel files, библиотеки с неочевидными runtime effects. Иногда точечный импорт или замена пакета дают больше, чем настройка bundler.

**Analyzer нужен до оптимизации, а не после догадок.**
Типичный порядок: собрать production build, открыть analyzer, найти самые дорогие chunks/modules, понять import chain, проверить Coverage/Network, затем решить: lazy load, заменить dependency, импортировать точечно, вынести в async chunk, настроить splitting или удалить лишний код.

**Size budget должен быть автоматическим.**
Ручная проверка analyzer полезна, но легко забывается. В CI можно падать при превышении threshold: initial JS, общий JS, конкретный chunk, gzip/brotli размер, bundle diff относительно main branch. В Webpack есть `performance.maxAssetSize`, `performance.maxEntrypointSize` и `hints`; в Vite/Rollup часто используют visualizer/custom script или отдельный budget check.

**Budget не должен быть слепым числом.**
Один общий лимит “bundle меньше 500 KB” часто бесполезен. Лучше разделять: initial route JS, async route chunks, vendor, CSS, images/fonts. Для UX важнее то, что нужно до первого экрана и первого взаимодействия.

#### Где применяется во frontend

| Ситуация | Что делать |
| --- | --- |
| После MR вырос bundle | открыть analyzer diff и найти import chain |
| В initial попал chart/editor/map | вынести через dynamic import |
| В bundle попала вся icon library | заменить import pattern или настроить tree shaking |
| Много locale data | импортировать нужные locales |
| Дублируется dependency | проверить версии, lock и package manager |
| Route грузится медленно | проверить async chunks и waterfall |
| CI должен ловить регрессии | добавить size budget check |
| Нужно CDN external | осознанно настроить external и fallback/SRI, если уместно |

#### Если уточнили

> - **Как понять, почему библиотека попала в bundle?** Смотреть analyzer/stats и цепочку imports: какой файл впервые импортировал пакет.
> - **Попадает ли `devDependency` в bundle?** Может попасть, если её импортирует клиентский runtime-код.
> - **Code splitting уменьшает bundle?** Он не обязательно уменьшает общий build output, но уменьшает initial JS и переносит часть загрузки на момент, когда код реально нужен.
> - **Что такое size budget?** Автоматическое ограничение размера assets/chunks, которое предупреждает или ломает CI при превышении лимита.
> - **Почему gzip-size мало?** Gzip показывает сетевой размер, но JavaScript ещё нужно распарсить, скомпилировать и выполнить на main thread.

#### Пример Webpack budget

```js
// webpack.config.js
module.exports = {
  performance: {
    hints: "error",
    maxEntrypointSize: 250_000,
    maxAssetSize: 250_000,
    assetFilter: filename => filename.endsWith(".js"),
  },
};
```

Такой config не заменяет анализ производительности, но превращает сильный рост initial JS в заметный сигнал на build step.

#### Пример Vite/Rollup splitting

```ts
// vite.config.ts
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          charts: ["recharts"],
        },
      },
    },
  },
});
```

Идея `manualChunks` - управлять разбиением, когда автоматический splitting даёт плохой результат. Настройку проверяют analyzer-ом и Network waterfall, потому что ручное дробление может как помочь, так и создать лишние запросы.

#### Частые ошибки

- Смотреть только размер `dist`, а не initial JS.
- Думать, что `devDependencies` не могут попасть в bundle.
- Добавлять heavy dependency без analyzer diff.
- Настраивать splitting без проверки waterfall.
- Надеяться на tree shaking для CommonJS/side-effect-heavy пакетов.
- Считать gzip-size полной стоимостью JavaScript.
- Не проверять bundle в CI.
- Публиковать sourcemaps без политики доступа и потом путать их с runtime bundle.

#### Связанные темы

- [[Конспект для подготовки/Performance/Bundle size и loading strategy]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]
- [[Конспект для подготовки/Tooling/Vite]]
- [[Конспект для подготовки/Tooling/Webpack]]
- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]
- [[Конспект для подготовки/Tooling/Версии зависимостей semver]]
- [[Конспект для подготовки/Performance/Performance диагностика и профилирование]]
- [[Конспект для подготовки/React/Suspense и lazy]]

#### Источники

- [Webpack Docs: Performance](https://webpack.js.org/configuration/performance/)
- [Webpack Docs: Tree Shaking](https://webpack.js.org/guides/tree-shaking/)
- [Webpack Docs: Code Splitting](https://webpack.js.org/guides/code-splitting/)
- [Vite Docs: Build Options](https://vite.dev/config/build-options.html)
- [Rollup Docs: output.manualChunks](https://rollupjs.org/configuration-options/#output-manualchunks)
