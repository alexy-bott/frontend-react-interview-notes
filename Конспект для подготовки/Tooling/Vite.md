---
aliases:
  - Vite
  - Vite dev server
  - Vite build
  - HMR
---

#### Ответ на 60 секунд

Vite - современный frontend build tool и dev server. В dev-режиме он не пересобирает всё приложение как единый bundle при каждом изменении, а использует native ES modules в браузере и отдаёт модули по запросу. Поэтому старт проекта и Hot Module Replacement обычно быстрее, особенно на больших приложениях. Для production Vite выполняет полноценную сборку статических assets, применяет оптимизации, hashing, code splitting и обработку CSS/assets.

На 16 июля 2026 актуальная документация Vite показывает ветку v8.1.5, где production build настраивается через `build.rolldownOptions`. В старых версиях Vite production build обычно объясняли через Rollup. Корректная формулировка: Vite - это dev server и build tool с ESM-first dev experience, plugin API и production build pipeline; конкретный bundler зависит от версии Vite.

#### Ключевая схема

| Область | Что делает Vite |
| --- | --- |
| Dev server | отдаёт ESM-модули, быстро стартует |
| HMR | обновляет изменённые модули без полной перезагрузки |
| TS/JSX | трансформирует TypeScript/JSX для dev/build |
| CSS | поддерживает CSS imports, CSS Modules, PostCSS, SCSS/Less при установленном preprocessor |
| Assets | умеет импортировать картинки, raw/url assets, workers |
| Env | даёт `import.meta.env`, expose только для `VITE_*` |
| Build | собирает production assets с оптимизациями |
| Preview | локально проверяет production build |

#### Практическая настройка

Практическая настройка Vite делится на три зоны: dev experience, production build и окружения. В dev это proxy, aliases и порт; в build - `base`, sourcemaps и chunks; в окружениях - `import.meta.env`, modes и контроль переменных, которые попадают в клиент.

| Что настраивают | Зачем |
| --- | --- |
| `plugins` | React, legacy, analyzer, SVG, tsconfig paths |
| `resolve.alias` | короткие импорты вроде `@/shared/ui` |
| `server.proxy` | проксировать API в dev и обходить CORS локально |
| `server.port` / `strictPort` | стабильный порт для команды/докера |
| `base` | корректные пути assets при деплое не в `/` |
| `build.sourcemap` | sourcemaps для debug/error tracking |
| `build.rolldownOptions` | тонкая настройка production bundling в Vite 8 |
| `define` | compile-time constants, не secrets |
| `import.meta.env` | режимы и публичные env-переменные |

```ts
// vite.config.ts
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react()],
    base: env.APP_BASE_PATH || "/",
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    server: {
      port: 5173,
      strictPort: true,
      proxy: {
        "/api": {
          target: env.API_PROXY_TARGET || "http://localhost:3000",
          changeOrigin: true,
          rewrite: path => path.replace(/^\/api/, ""),
        },
      },
    },
    build: {
      sourcemap: "hidden",
    },
  };
});
```

Этот пример читается блоками: `plugins` подключает React, `resolve.alias` задаёт короткие импорты, `server.proxy` помогает локально ходить в backend, `base` влияет на пути assets после deploy, `build.sourcemap` нужен для debug/error tracking.

| Нюанс | Риск |
| --- | --- |
| `server.proxy` работает только в dev | production API routing настраивается в Nginx/CDN/backend/hosting |
| `VITE_*` попадает в клиентский bundle | secrets нельзя класть в такие переменные |
| env values приходят строками | boolean/number нужно преобразовывать явно |
| `base` влияет на пути assets | при деплое в поддиректорию без `base` ломаются JS/CSS/img |
| `vite build` проверяет production | dev server не доказывает готовность к deploy |
| `loadEnv(..., "")` загружает все env | приватные значения легко случайно передать в `define` |

#### Развернутый ответ

В dev-режиме Vite разделяет исходный код приложения и зависимости. Исходные модули отдаются браузеру как native ESM и загружаются по запросу, а зависимости предварительно обрабатываются отдельно. Поэтому старт dev server не требует сборки всего приложения в один большой bundle, а HMR обычно обновляет конкретный участок module graph.

Production build - отдельный режим. Он создаёт оптимизированные assets, применяет minification, hashing, code splitting и обработку CSS/assets. На 16 июля 2026 в документации Vite v8.1.5 production build описан через Rolldown; в старых объяснениях Vite часто встречается Rollup, потому что предыдущие версии production-сборки опирались на него. Поэтому Vite корректнее описывать как build tool/dev server, а не как “просто Rollup wrapper”.

Конфигурация Vite чувствительна к окружению. `server.proxy` работает только в dev и не заменяет production routing. `base` влияет на пути JS/CSS/img после deploy, особенно если приложение лежит не в корне домена. `import.meta.env` отдаёт в клиент только переменные с prefix `VITE_*`, и эти значения видны пользователю в bundle. `mode` выбирает `.env` файлы, а `NODE_ENV` отвечает за development/production поведение экосистемы.

Перед deploy проверяют именно собранные assets: `vite build`, затем `vite preview`, smoke tests или CI checks. Dev server нужен для разработки, но не доказывает, что production-сборка корректно работает с нужным `base`, env, sourcemaps, routes и static serving.

> [!faq]+ Уточнения
> - Vite быстрее в dev за счёт ESM-first модели, pre-bundling зависимостей и точечного HMR.
> - Webpack остаётся актуален в legacy/enterprise проектах, Module Federation и сложных plugin/loader конфигурациях.
> - `VITE_*` переменные попадают в клиентский bundle, поэтому secrets туда не кладут.
> - `vite build --mode staging` остаётся production-сборкой, но берёт staging env.
> - `server.proxy` решает локальную разработку, а production routing настраивается в Nginx/CDN/backend/hosting.

#### Пример использования env

```ts
const apiUrl = import.meta.env.VITE_API_URL;

if (import.meta.env.DEV) {
  console.log("Development mode");
}
```

#### Частые ошибки

- Считать dev server production-сервером.
- Класть secrets в `VITE_*` переменные.
- Забывать, что env values приходят строками.
- Не запускать production build в CI.
- Переносить Webpack-mental-model один в один на Vite.
- Не учитывать `base`, если приложение деплоится не в корень домена.
- Подключать тяжёлые зависимости в общий entrypoint и удивляться размеру bundle.

#### Связанные темы

- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]
- [[Конспект для подготовки/Tooling/Env files и frontend переменные]]
- [[Конспект для подготовки/Tooling/Файлы frontend проекта]]
- [[Конспект для подготовки/JavaScript/ES modules]]
- [[Конспект для подготовки/React/Suspense и lazy]]
- [[Конспект для подготовки/Testing/Jest]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]
- [[Конспект для подготовки/CSS/SCSS]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]

#### Источники

- [Vite Guide](https://vite.dev/guide/)
- [Vite Features](https://vite.dev/guide/features)
- [Vite Config](https://vite.dev/config/)
- [Vite Server Options](https://vite.dev/config/server-options.html)
- [Vite Build Options](https://vite.dev/config/build-options.html)
- [Vite Env Variables and Modes](https://vite.dev/guide/env-and-mode)
