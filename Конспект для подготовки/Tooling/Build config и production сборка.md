---
aliases:
  - build config
  - production build
  - frontend build setup
  - Vite config
  - Webpack config
  - aliases env assets
---

#### Ответ на 60 секунд

Build config описывает путь от исходного кода до deployable artifact: как приложение стартует, как резолвятся импорты, какие env-переменные попадают в клиент, как обрабатываются CSS/assets, как работает dev proxy, какие sourcemaps создаются, куда кладётся production output и как настраиваются chunks.

В Vite базовые зоны настройки - `plugins`, `resolve.alias`, `server.proxy`, `base`, `build`, `import.meta.env`. На 16 июля 2026 актуальная документация Vite показывает ветку v8.1.5, где production build настраивается через `build.rolldownOptions`; dev server работает вокруг native ESM и HMR. В Webpack конфиг читается через `entry`, `output`, `resolve`, `module.rules`, `plugins`, `devServer`, `devtool`, `optimization`.

Главный практический риск - перепутать dev и production. `server.proxy` и `devServer.proxy` работают только локально; production routing настраивается в Nginx/CDN/backend/hosting. `VITE_*`, `DefinePlugin` и похожие compile-time constants попадают в клиентский JavaScript, поэтому туда кладут только публичную конфигурацию. Production build проверяют отдельно: dev server не доказывает корректность `base/publicPath`, hashed assets, routes, sourcemaps и static serving.

#### Ключевая схема

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

#### Развернутый ответ

Build config удобно читать как набор контрактов. Первый контракт - entry и output: откуда начинается приложение и какие файлы получаются после сборки. Для SPA это обычно HTML, JS/CSS chunks, fonts/images и manifest-like связи между ними. В production файлы часто получают content hash, чтобы сервер мог кешировать assets долго, а `index.html` обновлялся быстрее.

Второй контракт - module resolution. Alias вроде `@/shared/ui` должен одинаково работать в bundler, TypeScript, Jest/Vitest, ESLint и IDE. Если alias есть только в Vite/Webpack, код соберётся, но typecheck или tests могут сломаться. Если alias есть только в `tsconfig`, IDE будет довольна, но bundler не найдёт модуль.

Третий контракт - env и public config. В Vite `import.meta.env` даёт built-in constants и env-переменные, а значения с `VITE_*` попадают в клиентский bundle как строки. В Webpack значения обычно подставляют через `DefinePlugin` или похожий механизм. Всё, что встроилось в JS bundle, считается публичным. Для секретов нужен backend, secret manager, CI/CD variables или runtime окружение сервера, а не frontend bundle.

Четвёртый контракт - dev/prod различия. Dev server отвечает за скорость разработки: HMR, proxy, удобные sourcemaps, history fallback. Production build отвечает за deploy: minification, hashed filenames, code splitting, static assets, browser target, sourcemaps policy. Поэтому перед релизом проверяют именно production artifact: build, preview/static serving, smoke route, загрузку assets и работу API base URL.

Пятый контракт - static serving. `base` в Vite и `publicPath` в Webpack должны соответствовать месту, где приложение реально доступно: корень домена, поддиректория или CDN. Ошибка в этом месте проявляется не в TypeScript, а в браузере: HTML загрузился, но JS/CSS/images идут по неверным URL.

> [!faq]+ Уточнения
> - Alias нужно синхронизировать между bundler, TypeScript, тестами и IDE.
> - Dev proxy решает локальную разработку, но не production routing.
> - Build-time env в SPA нельзя изменить после сборки без runtime config или новой сборки.
> - `base/publicPath` влияет на URL итоговых JS/CSS/assets.
> - Sourcemaps выбирают по балансу debug и риска раскрытия исходников.
> - Production artifact проверяют отдельно от dev server.

#### Пример

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  base: "/app/",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
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

#### Частые ошибки

- Настроить alias только в bundler и забыть TypeScript/tests.
- Использовать dev proxy как production routing.
- Класть secrets в `VITE_*` или `DefinePlugin`.
- Не учитывать, что env values в Vite приходят строками.
- Деплоить SPA в поддиректорию без корректного `base/publicPath`.
- Проверять только dev server и не запускать production build.
- Публиковать подробные sourcemaps без осознанной политики доступа.
- Делить код на chunks без проверки waterfall и initial bundle.

#### Связанные темы

- [[Конспект для подготовки/Tooling/Vite]]
- [[Конспект для подготовки/Tooling/Webpack]]
- [[Конспект для подготовки/Tooling/Файлы frontend проекта]]
- [[Конспект для подготовки/Tooling/Env files и frontend переменные]]
- [[Конспект для подготовки/Tooling/Bundle analysis и size budgets]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/Security/Supply chain secrets и third-party scripts]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/Testing/Jest]]
- [[Конспект для подготовки/TypeScript/tsconfig и strict mode]]
- [[Конспект для подготовки/React/Suspense и lazy]]

#### Источники

- [Vite Guide](https://vite.dev/guide/)
- [Vite Env Variables and Modes](https://vite.dev/guide/env-and-mode)
- [Vite Build Options](https://vite.dev/config/build-options.html)
- [Vite Server Options](https://vite.dev/config/server-options.html)
- [Webpack Concepts](https://webpack.js.org/concepts/)
- [Webpack Asset Modules](https://webpack.js.org/guides/asset-modules/)
