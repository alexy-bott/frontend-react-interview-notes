---
aliases:
  - bundle analysis
  - bundle analyzer
  - size budgets
  - что входит в bundle
  - контроль размера bundle
---

#### Быстрый ответ

Build output определяется client dependency graph, а не разделом package manifest. Static imports формируют initial/shared chunks, dynamic import создаёт async split point, assets/CSS входят по правилам toolchain, а tree shaking может удалить statically unused exports. Package может находиться в `devDependencies` и всё равно попасть в browser, если client source его импортирует.

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

#### Базовая модель

**Bundle начинается с entrypoint.**
Bundler берёт входные точки приложения и строит dependency graph. Если файл импортируется из entrypoint напрямую или через цепочку imports, он становится кандидатом на попадание в build output. Dynamic import обычно создаёт отдельный async chunk: код всё ещё входит в build output, но не загружается на первом экране.

Размер имеет несколько измерений: raw output влияет на storage/cache, gzip/Brotli — на transfer, parse/compile/execute — на main thread и device CPU. Initial request graph и waterfall обычно важнее суммы всех lazy chunks, которые пользователь может никогда не загрузить.

#### Развернутый ответ

**`dependencies` и `devDependencies` не являются границей bundle.**
Если runtime-код импортирует пакет, bundler может включить его в клиентский JS даже если пакет лежит в `devDependencies`. И наоборот: пакет из `dependencies` не попадёт в bundle, если он нигде не импортируется в клиентском графе. Разделы зависимостей важны для install/deploy semantics, но состав bundle определяется графом импортов.

**Tree shaking удаляет неиспользуемый код не всегда.**
Лучше всего он работает с ES modules, где bundler статически видит imports/exports. Ограничения: CommonJS, top-level side effects, неправильное поле `sideEffects`, namespace imports, barrel files, библиотеки с неочевидными runtime effects. Иногда точечный импорт или замена пакета дают больше, чем настройка bundler.

`sideEffects: false` является обещанием package, а не дополнительной minification. Ошибочная metadata способна удалить CSS import, registration или polyfill. Analyzer показывает composition, но не доказывает, что удалённый/оставшийся code семантически корректен.

**Analyzer нужен до оптимизации, а не после догадок.**
Типичный порядок: собрать production build, открыть analyzer, найти самые дорогие chunks/modules, понять import chain, проверить Coverage/Network, затем решить: lazy load, заменить dependency, импортировать точечно, вынести в async chunk, настроить splitting или удалить лишний код.

**Size budget должен быть автоматическим.**
Ручная проверка analyzer полезна, но легко забывается. В CI можно падать при превышении threshold: initial JS, общий JS, конкретный chunk, gzip/brotli размер, bundle diff относительно main branch. В Webpack есть `performance.maxAssetSize`, `performance.maxEntrypointSize` и `hints`; в Vite/Rollup часто используют visualizer/custom script или отдельный budget check.

**Budget не должен быть слепым числом.**
Один общий лимит “bundle меньше 500 KB” часто бесполезен. Лучше разделять: initial route JS, async route chunks, vendor, CSS, images/fonts. Для UX важнее то, что нужно до первого экрана и первого взаимодействия.

#### Практическое применение

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

#### Пример split point

```tsx
import { lazy, Suspense } from "react";

const AnalyticsChart = lazy(() => import("./AnalyticsChart"));

export function AnalyticsSection() {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <AnalyticsChart />
    </Suspense>
  );
}
```

Dynamic import создаёт стабильную version-independent boundary. Он уменьшит initial cost только если chart code не нужен до первого взаимодействия/экрана. Advanced manual chunk config зависит от Vite/Rolldown/Rollup/Webpack version и применяется после analyzer/waterfall, а не вместо application boundary.

#### Ключевые уточнения

- Build output, initial transfer и executed JavaScript — разные metrics.
- Dynamic import переносит cost, но не обязан уменьшать суммарный output; слишком поздний split создаёт interaction latency.
- Analyzer отвечает «что/почему включено», browser Performance/Network — «когда загружено и сколько стоило выполнить».
- Tree shaking зависит от static ESM graph и truthful side-effect metadata, а не только от named import syntax.
- Size budget задают по route/entrypoint и compression mode, фиксируя measurement tool/version в CI.
- Bundle diff оценивают вместе с cache churn: изменение shared vendor chunk может заставить users повторно скачать большой asset.
- Source maps не являются runtime code, но могут раскрывать source и заметно увеличивать published artifacts.

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
