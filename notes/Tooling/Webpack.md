# Webpack

<!-- NOTE-NAV-TOP:START -->
[← Vite](<./Vite.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Build config и production сборка →](<./Build config и production сборка.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Webpack — module bundler: от entry points он строит dependency graph, применяет loaders к отдельным modules, запускает plugins над compilation и создаёт output assets/chunks. Его выбирают не только для legacy: зрелая plugin ecosystem, Module Federation и глубокий контроль compilation остаются самостоятельными причинами.

Ключевые узлы настройки: `entry` задаёт начало графа; `output` определяет, куда и с какими именами класть файлы; `module.rules` через loaders трансформирует TS/JSX/CSS/SCSS/assets; `plugins` делают более широкие операции: HTML generation, env replacement, CSS extraction, analysis. `mode` включает development/production defaults. `optimization` отвечает за splitting, runtime chunk, tree shaking и minimization.

## Ключевая схема

```text
entry -> dependency graph -> loaders -> plugins -> optimization -> output assets
```

| Часть | Что настраивает |
| --- | --- |
| `entry` | входные точки приложения |
| `output` | `path`, `filename`, `publicPath`, chunk names |
| `resolve` | aliases, extensions, module resolution |
| `module.rules` | loaders для TS/JSX/CSS/SCSS/assets |
| `plugins` | HTML, env, CSS extraction, analysis |
| `devServer` | локальный сервер, HMR, history fallback, proxy |
| `devtool` | source maps |
| `optimization` | splitChunks, runtimeChunk, minimizer, tree shaking |
| `mode` | development/production defaults |

## Практическая настройка

Практическая настройка Webpack обычно включает aliases, loaders для TypeScript/React и SCSS, devServer proxy, source maps, output hashing, HTML plugin, CSS extraction, splitChunks и env constants. Для frontend-проекта dev и prod config часто различаются: в dev нужны быстрые rebuilds и удобные sourcemaps, в production - hashed filenames, minimization, extracted CSS, long-term caching и анализ bundle size.

```js
// webpack.config.cjs — CommonJS config работает и при package "type": "module".
const path = require("node:path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const webpack = require("webpack");

module.exports = (_, argv) => {
  const isProd = argv.mode === "production";

  return {
    entry: "./src/index.tsx",
    output: {
      path: path.resolve(__dirname, "dist"),
      filename: isProd ? "js/[name].[contenthash].js" : "js/[name].js",
      chunkFilename: isProd ? "js/[name].[contenthash].chunk.js" : "js/[name].chunk.js",
      publicPath: "/",
      clean: true,
    },
    resolve: {
      extensions: [".tsx", ".ts", ".js"],
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    module: {
      rules: [
        {
          test: /\.[jt]sx?$/,
          exclude: /node_modules/,
          use: "babel-loader",
        },
        {
          test: /\.s?css$/,
          use: [
            isProd ? MiniCssExtractPlugin.loader : "style-loader",
            "css-loader",
            "sass-loader",
          ],
        },
        {
          test: /\.(png|jpg|svg|woff2?)$/i,
          type: "asset",
        },
      ],
    },
    plugins: [
      new HtmlWebpackPlugin({ template: "./public/index.html" }),
      new webpack.DefinePlugin({
        __API_URL__: JSON.stringify(process.env.API_URL),
      }),
      ...(isProd ? [new MiniCssExtractPlugin({ filename: "css/[name].[contenthash].css" })] : []),
    ],
    devServer: {
      historyApiFallback: true,
      hot: true,
      proxy: [
        {
          context: ["/api"],
          target: "http://localhost:3000",
          changeOrigin: true,
        },
      ],
    },
    devtool: isProd ? "source-map" : "eval-cheap-module-source-map",
    optimization: {
      runtimeChunk: "single",
      splitChunks: {
        chunks: "all",
      },
    },
  };
};
```

Config читается по блокам:

| Блок config | Что он показывает |
| --- | --- |
| `entry` | приложение стартует из `src/index.tsx` |
| `output` | файлы кладутся в `dist`, в production получают `contenthash` |
| `resolve` | можно импортировать через `@` и не писать расширения |
| JS/TS rule | TypeScript/JSX проходит через loader |
| CSS/SCSS rule | в dev стили вставляются в DOM, в prod выносятся в CSS-файл |
| asset rule | картинки/fonts идут через Webpack 5 Asset Modules |
| `HtmlWebpackPlugin` | создаёт HTML и подключает bundles |
| `DefinePlugin` | подставляет compile-time constants |
| `devServer` | даёт HMR, SPA fallback и локальный proxy |
| `optimization` | выносит runtime и общие chunks |

Ключевые детали: proxy нужен только локально, `contenthash` нужен для кеширования, `DefinePlugin` подставляет значения на этапе сборки и не хранит secrets.

## Базовая модель

Webpack config описывает pipeline сборки. `entry` задаёт начало dependency graph, `resolve` управляет импортами, `module.rules` через loaders объясняет, как обрабатывать конкретные типы файлов, `plugins` вмешиваются в сборку целиком, `optimization` управляет разделением кода и minimization, а `output` определяет итоговые assets.

Module может попасть в initial chunk, async chunk, быть external либо удалиться tree shaking-ом. Loader transformation происходит до включения output, plugin получает compiler/compilation hooks и способен создавать/изменять assets или graph-wide behavior.

## Развернутый ответ

Loaders и plugins решают разные задачи. Loader отвечает на вопрос “как импортировать этот файл”: TypeScript, JSX, CSS, SCSS, SVG, images. Plugin работает шире: создаёт HTML, заменяет compile-time constants, вытаскивает CSS в отдельные файлы, анализирует bundle, управляет env и оптимизирует assets. Эта разница помогает быстро читать чужой webpack config.

Dev-настройки и production-настройки разделяют по целям. В dev важны быстрые rebuilds, HMR, удобные sourcemaps, SPA fallback и proxy к backend. В production важны `contenthash`, extracted CSS, minification, splitChunks, runtimeChunk, корректный `publicPath`, приватные sourcemaps и понятное static serving.

`babel-loader`/`swc-loader` может удалить TypeScript syntax, но не гарантирует typecheck. Для этого отдельно запускают `tsc --noEmit` или checker plugin. `mode: "production"` включает разумные defaults, но не исправляет `publicPath`, cache policy, source-map exposure и application-specific split strategy.

Env values в Webpack попадают в клиент только через явную подстановку: `DefinePlugin`, `EnvironmentPlugin` или dotenv-подход. Всё, что оказалось в bundle, видно пользователю. Поэтому build-time constants подходят для публичных API URL, feature flags и build metadata, но не для secrets.

## Ключевые уточнения

- Loader преобразует matched module, plugin работает через hooks compilation целиком.
- `mode` задаёт defaults, а dev/prod contracts для filenames, CSS, maps, targets и serving остаются явными.
- `devServer.proxy`/`historyApiFallback` существуют только в dev server; production решает hosting/reverse proxy.
- `DefinePlugin` выполняет compile-time token replacement: переданное значение должно быть сериализовано и считается публичным в client output.
- `contenthash` поддерживает long-term cache только вместе с устойчивым chunk graph и правильной HTML/cache policy.
- Tree shaking наиболее надёжен для statically analyzable ESM и корректного `sideEffects`; ошибочное `sideEffects: false` способно удалить нужные CSS/runtime effects.
- Webpack transform TypeScript не является typecheck, если pipeline явно не запускает checker.
- Source map policy определяет публикацию/upload/access; сам suffix `hidden` не делает map секретной, если файл доступен публично.

## Связанные темы

- [Vite](<./Vite.md>)
- [Build config и production сборка](<./Build config и production сборка.md>)
- [Bundlers и code splitting](<../Web Basics/Bundlers и code splitting.md>)
- [ES modules](<../JavaScript/ES modules.md>)
- [SCSS](<../CSS/SCSS.md>)
- [Suspense и lazy](<../React/Suspense и lazy.md>)
- [Frontend pipeline](<../DevOps/Frontend pipeline.md>)
- [Nginx и static serving](<../DevOps/Nginx и static serving.md>)
- [HTTP caching](<../Web Basics/HTTP caching.md>)

## Источники

- [Webpack: Concepts](https://webpack.js.org/concepts/)
- [Webpack: Configuration](https://webpack.js.org/configuration/)
- [Webpack: DevServer proxy](https://webpack.js.org/configuration/dev-server/#devserverproxy)
- [Webpack: DefinePlugin](https://webpack.js.org/plugins/define-plugin/)
- [Webpack: Asset Modules](https://webpack.js.org/guides/asset-modules/)
- [Webpack: Devtool](https://webpack.js.org/configuration/devtool/)
- [Webpack: Optimization](https://webpack.js.org/configuration/optimization/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Vite](<./Vite.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Build config и production сборка →](<./Build config и production сборка.md>)
<!-- NOTE-NAV-BOTTOM:END -->
