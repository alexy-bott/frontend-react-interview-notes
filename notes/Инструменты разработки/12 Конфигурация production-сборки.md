# Конфигурация production-сборки

<!-- NOTE-NAV-TOP:START -->
[← Webpack](<./11 Webpack.md>) · [↑ Инструменты разработки](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Build config описывает путь от исходного кода до deployable artifact: как приложение стартует, как резолвятся импорты, какие env-переменные попадают в клиент, как обрабатываются CSS/assets, как работает dev proxy, какие sourcemaps создаются, куда кладётся production output и как настраиваются chunks.

В Vite базовые зоны — `plugins`, `resolve.alias`, `server.proxy`, `base`, `build`, `import.meta.env`; Vite 8 advanced bundling настраивается через Rolldown, старые majors — через versioned Rollup/esbuild options. Webpack config читается через `entry`, `output`, `resolve`, `module.rules`, `plugins`, `devServer`, `devtool`, `optimization`.

Главный практический риск - перепутать dev и production. `server.proxy` и `devServer.proxy` работают только локально; production routing настраивается в Nginx/CDN/backend/hosting. `VITE_*`, `DefinePlugin` и похожие compile-time constants попадают в клиентский JavaScript, поэтому туда кладут только публичную конфигурацию. Production build проверяют отдельно: dev server не доказывает корректность `base/publicPath`, hashed assets, routes, sourcemaps и static serving.

## Ключевая схема

| Вопрос | Vite | Webpack | На что влияет |
| --- | --- | --- | --- |
| Где entry? | `index.html` + module script | `entry` | старт dependency graph |
| Как работают imports? | `resolve.alias` | `resolve.alias` | короткие пути, монорепа, FSD |
| Как синхронизировать aliases? | Vite + TS + tests | Webpack + TS + tests | одинаковый module resolution |
| Где env? | `import.meta.env`, `VITE_*` | `DefinePlugin`, `EnvironmentPlugin`, dotenv | public build-time config |
| Как работает API локально? | `server.proxy` | `devServer.proxy` | только dev routing |
| Где пути assets? | `base`, `assetsDir` | `publicPath`, `assetModuleFilename` | deploy в поддиректорию/CDN |
| Как подключаются assets? | imports, public dir, `?url/?raw` | Asset Modules, loaders | картинки, fonts, raw files |
| Где sourcemaps? | `build.sourcemap` | `devtool` | debug, Sentry, риск публикации source |
| Как делится код? | dynamic import, build options | `splitChunks`, dynamic import | initial bundle и lazy chunks |
| Что проверяет CI? | `vite build` + preview/smoke | production webpack build | deployable artifact |

## Базовая модель

Build config — набор contracts между source, toolchain и hosting: module graph должен разрешиться, browser target — получить поддерживаемый syntax/polyfills policy, public config — встроиться без secrets, output URLs — совпасть с deploy path, а hashed assets/HTML — получить совместимую cache policy.

## Развернутый ответ

Build config удобно читать как набор контрактов. Первый контракт - entry и output: откуда начинается приложение и какие файлы получаются после сборки. Для SPA это обычно HTML, JS/CSS chunks, fonts/images и manifest-like связи между ними. В production файлы часто получают content hash, чтобы сервер мог кешировать assets долго, а `index.html` обновлялся быстрее.

Второй контракт - module resolution. Alias вроде `@/shared/ui` должен одинаково работать в bundler, TypeScript, Jest/Vitest, ESLint и IDE. Если alias есть только в Vite/Webpack, код соберётся, но typecheck или tests могут сломаться. Если alias есть только в `tsconfig`, IDE будет довольна, но bundler не найдёт модуль.

Третий контракт - env и public config. В Vite `import.meta.env` даёт built-in constants и env-переменные, а значения с `VITE_*` попадают в клиентский bundle как строки. В Webpack значения обычно подставляют через `DefinePlugin` или похожий механизм. Всё, что встроилось в JS bundle, считается публичным. Для секретов нужен backend, secret manager, CI/CD variables или runtime окружение сервера, а не frontend bundle.

Четвёртый контракт - dev/prod различия. Dev server отвечает за скорость разработки: HMR, proxy, удобные sourcemaps, history fallback. Production build отвечает за deploy: minification, hashed filenames, code splitting, static assets, browser target, sourcemaps policy. Поэтому перед релизом проверяют именно production artifact: build, preview/static serving, smoke route, загрузку assets и работу API base URL.

TypeScript transform, lint, tests и production build являются отдельными gates. Bundler может успешно emit-нуть code с type error, а typecheck не обнаружит неправильный `base`, missing asset или unsupported browser syntax. Browser target также не гарантирует автоматическую polyfill всех missing runtime APIs.

Пятый контракт - static serving. `base` в Vite и `publicPath` в Webpack должны соответствовать месту, где приложение реально доступно: корень домена, поддиректория или CDN. Ошибка в этом месте проявляется не в TypeScript, а в браузере: HTML загрузился, но JS/CSS/images идут по неверным URL.

## Пример

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

export default defineConfig({
  plugins: [react()],
  base: "/app/",
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:3000",
        changeOrigin: true,
      },
    },
  },
  build: {
    sourcemap: "hidden",
  },
});
```

Для такого config отдельно проверяют: `@` есть в `tsconfig`, `/app/` совпадает с production path, `/api` в production обрабатывает сервер/hosting, `VITE_*` содержит только публичные значения, production artifact открывается через static serving.

## Ключевые уточнения

- Alias синхронизируют по resolution semantics, но не обязаны копировать config вручную, если plugin читает единый source.
- Dev proxy/history fallback не входят в artifact и не определяют production routing.
- Build-time public env заморожена в client output; secret не передают в bundler replacement.
- `base/publicPath` проверяют на direct navigation, dynamic chunks, CSS URLs, fonts и service worker scope.
- Browser target управляет syntax transforms, но missing Web API может потребовать отдельный polyfill/feature strategy.
- `hidden` source map не содержит reference в emitted JS, но сам `.map` остаётся чувствительным, если опубликован.
- Production verification использует actual artifact и hosting-like server; `vite preview` не является production server policy.
- Chunk strategy оценивают по initial route, waterfall, cache churn и interaction latency.

## Связанные темы

- [Vite](<./10 Vite.md>)
- [Webpack](<./11 Webpack.md>)
- [Файлы фронтенд-проекта](<./01 Файлы фронтенд-проекта.md>)
- [Файлы окружения и переменные фронтенда](<./06 Файлы окружения и переменные фронтенда.md>)
- [Анализ бандла и бюджет размера](<./09 Анализ бандла и бюджет размера.md>)
- [Бандлеры и разделение кода](<../Основы веб-платформы/19 Бандлеры и разделение кода.md>)
- [CI-CD-пайплайн фронтенда](<../DevOps/07 CI-CD-пайплайн фронтенда.md>)
- [Переменные окружения и секреты](<../DevOps/04 Переменные окружения и секреты.md>)
- [Цепочка поставок, секреты и сторонние скрипты](<../Безопасность/04 Цепочка поставок, секреты и сторонние скрипты.md>)
- [Nginx и раздача статических файлов](<../DevOps/03 Nginx и раздача статических файлов.md>)
- [Jest](<../Тестирование/03 Jest.md>)
- [tsconfig и строгий режим](<../TypeScript/20 tsconfig и строгий режим.md>)
- [Suspense и lazy](<../React/29 Suspense и lazy.md>)

## Источники

- [Vite Guide](https://vite.dev/guide/)
- [Vite Env Variables and Modes](https://vite.dev/guide/env-and-mode)
- [Vite Build Options](https://vite.dev/config/build-options.html)
- [Vite Server Options](https://vite.dev/config/server-options.html)
- [Webpack Concepts](https://webpack.js.org/concepts/)
- [Webpack Asset Modules](https://webpack.js.org/guides/asset-modules/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Webpack](<./11 Webpack.md>) · [↑ Инструменты разработки](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-BOTTOM:END -->
