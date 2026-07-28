---
aliases:
  - Webpack
  - webpack config
  - webpack loaders
  - webpack plugins
---

#### Ответ на 60 секунд

Webpack - это module bundler, который строит dependency graph от одного или нескольких entry points и собирает JavaScript, CSS, assets и другие модули в bundles/chunks для браузера. В отличие от Vite, Webpack чаще встречается в зрелых и legacy-проектах, где много кастомной конфигурации: loaders, plugins, devServer, aliases, source maps, optimization, Module Federation, сложная работа с CSS и assets.

Ключевые узлы настройки: `entry` задаёт начало графа; `output` определяет, куда и с какими именами класть файлы; `module.rules` через loaders трансформирует TS/JSX/CSS/SCSS/assets; `plugins` делают более широкие операции: HTML generation, env replacement, CSS extraction, analysis. `mode` включает development/production defaults. `optimization` отвечает за splitting, runtime chunk, tree shaking и minimization.

#### Ключевая схема

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

#### Практическая настройка

Практическая настройка Webpack обычно включает aliases, loaders для TypeScript/React и SCSS, devServer proxy, source maps, output hashing, HTML plugin, CSS extraction, splitChunks и env constants. Для frontend-проекта dev и prod config часто различаются: в dev нужны быстрые rebuilds и удобные sourcemaps, в production - hashed filenames, minimization, extracted CSS, long-term caching и анализ bundle size.

```js
// webpack.config.js
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

#### Развернутый ответ

Webpack config описывает pipeline сборки. `entry` задаёт начало dependency graph, `resolve` управляет импортами, `module.rules` через loaders объясняет, как обрабатывать конкретные типы файлов, `plugins` вмешиваются в сборку целиком, `optimization` управляет разделением кода и minimization, а `output` определяет итоговые assets.

Loaders и plugins решают разные задачи. Loader отвечает на вопрос “как импортировать этот файл”: TypeScript, JSX, CSS, SCSS, SVG, images. Plugin работает шире: создаёт HTML, заменяет compile-time constants, вытаскивает CSS в отдельные файлы, анализирует bundle, управляет env и оптимизирует assets. Эта разница помогает быстро читать чужой webpack config.

Dev-настройки и production-настройки разделяют по целям. В dev важны быстрые rebuilds, HMR, удобные sourcemaps, SPA fallback и proxy к backend. В production важны `contenthash`, extracted CSS, minification, splitChunks, runtimeChunk, корректный `publicPath`, приватные sourcemaps и понятное static serving.

Env values в Webpack попадают в клиент только через явную подстановку: `DefinePlugin`, `EnvironmentPlugin` или dotenv-подход. Всё, что оказалось в bundle, видно пользователю. Поэтому build-time constants подходят для публичных API URL, feature flags и build metadata, но не для secrets.

> [!faq]+ Уточнения
> - Loader преобразует импортируемый файл, plugin управляет сборкой в целом.
> - `devServer.proxy` работает только локально; production proxy/rewrites настраиваются вне dev server.
> - Webpack 5 Asset Modules заменяют многие старые случаи `file-loader`, `url-loader`, `raw-loader`.
> - `devtool` влияет на скорость сборки, debug и риск публикации исходников.
> - `splitChunks` помогает вынести общий код, но чрезмерное дробление создаёт сетевой overhead.
> - Tree shaking наиболее предсказуем с ESM и пакетами без side effects.

#### Частые ошибки

- Не различать loaders и plugins.
- Настраивать proxy в Webpack и думать, что это решает production routing.
- Класть secrets в compile-time constants.
- Забывать `historyApiFallback` для SPA routing в dev.
- Не использовать contenthash для долгого кеширования production assets.
- Использовать старые `file-loader`/`url-loader` в Webpack 5 без понимания Asset Modules.
- Делать один config на dev/prod без различий по sourcemaps, CSS и optimization.
- Включать слишком подробные production sourcemaps публично.
- Ломать tree shaking namespace-import-ами и CommonJS-зависимостями.

#### Связанные темы

- [[Конспект для подготовки/Tooling/Vite]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]
- [[Конспект для подготовки/JavaScript/ES modules]]
- [[Конспект для подготовки/CSS/SCSS]]
- [[Конспект для подготовки/React/Suspense и lazy]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/Web Basics/HTTP caching]]

#### Источники

- [Webpack: Concepts](https://webpack.js.org/concepts/)
- [Webpack: Configuration](https://webpack.js.org/configuration/)
- [Webpack: DevServer proxy](https://webpack.js.org/configuration/dev-server/#devserverproxy)
- [Webpack: DefinePlugin](https://webpack.js.org/plugins/define-plugin/)
- [Webpack: Asset Modules](https://webpack.js.org/guides/asset-modules/)
- [Webpack: Devtool](https://webpack.js.org/configuration/devtool/)
- [Webpack: Optimization](https://webpack.js.org/configuration/optimization/)
