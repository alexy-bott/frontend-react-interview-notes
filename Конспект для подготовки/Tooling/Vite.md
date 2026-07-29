---
aliases:
  - Vite
  - Vite dev server
  - Vite build
  - HMR
---

#### Быстрый ответ

Vite — dev server и production build tool. В development он отдаёт application source как transformed native ESM, переписывает bare imports и предварительно объединяет dependencies, а HMR обновляет затронутую часть module graph. Production command строит оптимизированные HTML/JS/CSS/assets с hashing и code splitting.

Версионная граница существенна: Vite 8 использует Rolldown/Oxc toolchain и `build.rolldownOptions`; Vite 7 и старее production build обычно опирался на Rollup/esbuild-related options. Стабильная public model остаётся той же, но advanced config переносят только после проверки docs установленной major version.

#### Ключевая схема

| Область | Что делает Vite |
| --- | --- |
| Dev server | отдаёт ESM-модули, быстро стартует |
| HMR | обновляет изменённые модули без полной перезагрузки |
| TS/JSX | трансформирует syntax, но не заменяет полный typecheck |
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
import { fileURLToPath } from "node:url";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react()],
    base: env.APP_BASE_PATH || "/",
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
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

#### Базовая модель

В dev-режиме Vite разделяет source и dependencies. Source modules трансформируются по запросу и отдаются browser как ESM. Bare package imports browser сам не понимает, поэтому Vite resolve-ит их в URLs; CommonJS/UMD и dependencies из сотен ESM files предварительно bundling-уются для compatibility и меньшего числа requests.

#### Развернутый ответ

Production build — отдельный pipeline. Vite 8 создаёт bundle через Rolldown и использует Oxc-based tools; старые projects могут иметь `rollupOptions`/esbuild-specific config. Compatibility aliases не делают старую option вечной: migration guide и plugin compatibility проверяют при major upgrade.

Vite снимает TypeScript annotations и трансформирует syntax, но не обязан проверить все types. Production gate обычно запускает `tsc --noEmit`/project build отдельно. Аналогично successful build не доказывает lint/tests и runtime correctness.

Конфигурация Vite чувствительна к окружению. `server.proxy` работает только в dev и не заменяет production routing. `base` влияет на пути JS/CSS/img после deploy, особенно если приложение лежит не в корне домена. `import.meta.env` отдаёт в клиент только переменные с prefix `VITE_*`, и эти значения видны пользователю в bundle. `mode` выбирает `.env` файлы, а `NODE_ENV` отвечает за development/production поведение экосистемы.

Перед deploy проверяют именно собранные assets: `vite build`, затем `vite preview`, smoke tests или CI checks. Dev server нужен для разработки, но не доказывает, что production-сборка корректно работает с нужным `base`, env, sourcemaps, routes и static serving.

#### Пример использования env

```ts
const apiUrl = import.meta.env.VITE_API_URL;

if (import.meta.env.DEV) {
  console.log("Development mode");
}
```

#### Ключевые уточнения

- Native ESM относится к dev source serving; production всё равно создаёт optimized bundles/chunks.
- Dependency pre-bundling решает CJS/UMD compatibility и request explosion, а не application code splitting.
- HMR сохраняет часть state только при корректной boundary/framework integration и может fallback-нуть к full reload.
- Vite transform TypeScript не заменяет `tsc --noEmit`.
- `server.proxy`/`vite preview` — development verification tools, не production routing/server policy.
- `VITE_*` и `define` являются public compile-time constants; private values не передают в client graph.
- `base`, browser target, sourcemaps и advanced bundler options проверяют на production artifact и по docs major version проекта.

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
