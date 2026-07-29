---
aliases:
  - Next.js deployment
  - Next.js Docker
  - Next.js env variables
  - Next.js self-hosting
---

#### Быстрый ответ

Deployment Next.js определяется используемыми runtime features. `output: "export"` создаёт static files для Nginx/CDN/object storage, но dynamic rendering, Server Actions, runtime Route Handlers, Middleware и built-in image optimization требуют Next.js server. Для self-hosting это обычно Node process или Docker image; Nginx может быть reverse proxy и отдавать static assets, но не заменяет Next.js runtime.

`NEXT_PUBLIC_*` statically inlined во время `next build`, попадает в browser bundle и замораживается в image. Обычная env может оставаться server-only, но будет прочитана при runtime только кодом, который действительно выполняется при runtime: statically rendered Server Component способен вычислить значение ещё во время build. Один image для разных environments требует явного разделения build config, runtime server config и публичного runtime config.

#### Ключевая схема

| Сценарий | Runtime |
| --- | --- |
| Static export `output: "export"` | static hosting: Nginx/CDN/S3 |
| App Router static rendering без server features | может быть static export, если нет unsupported features |
| SSR/dynamic rendering | Node.js server или совместимая платформа |
| Server Actions | server runtime |
| Route Handlers/webhooks | server runtime |
| Middleware | server runtime/edge-compatible runtime |
| `NEXT_PUBLIC_*` | встраивается в client bundle |
| private env | server code; время чтения зависит от rendering mode |

#### Базовая модель

Для SPA привычная схема проста: собрать `dist`/`build`, положить в Nginx/CDN и отдавать статику. Next.js может работать так же, если проект использует static export. В Next.js 14 команда `next export` удалена; static export включают через `output: "export"` в `next.config.js`. После `next build` получается папка `out`.

SSR-приложение нельзя свести к набору статических файлов. Если route рендерится на request time, использует Server Actions, Route Handlers, Middleware, cookies/headers, dynamic rendering или runtime env, нужен server process. В self-hosting варианте это обычно `next build` + `next start` или standalone output внутри Docker image. Nginx в такой архитектуре может отдавать static assets и проксировать запросы в Node.js, но не заменяет server runtime.

`output: "standalone"` использует Output File Tracing и копирует минимальный server плюс необходимые dependencies в `.next/standalone`. Папки `public` и `.next/static` автоматически туда не копируются: их либо доставляет CDN/reverse proxy, либо Dockerfile копирует рядом с generated `server.js`.

#### Развернутый ответ

**Environment values.** Public env с `NEXT_PUBLIC_` встраиваются при build и видны пользователю. Server-only env доступны Server Components, Route Handlers и Server Actions, но момент чтения зависит от execution: static render может выполниться при build, dynamic render — при request. Если значение должно меняться после запуска image, route/service обязан читать его в runtime path. Client-visible runtime config передают отдельным public endpoint/file и не считают секретом.

**Immutable release.** Если staging и production собирают отдельно с разными `NEXT_PUBLIC_*`, это два разных artifacts. Вариант допустим, но не соответствует build once/promote. Для продвижения одного image environment-specific server secrets передают при container start, а public values — через runtime config. Release ID помогает проверить, какой image и config обслуживают request.

**Multiple instances.** Локальный filesystem/in-memory cache одной replica не обеспечивает согласованность ISR/Data Cache всего deployment. Нужны shared cache handler и координация tag invalidation. Server Actions между несколькими instances также требуют согласованной encryption configuration. При rolling deploy старый client и новый server могут встретиться одновременно, поэтому учитывают version skew и сохраняют совместимые assets.

**Proxy/runtime.** Reverse proxy должен поддерживать streaming и не буферизовать response без необходимости. Health/readiness checks подтверждают, что Node process готов принимать traffic. Static chunks кешируют как immutable, а HTML/RSC responses — по policy Next.js и CDN, чтобы внешний cache не переиспользовал personalized output.

Для Next.js 14 production также важна patch-line. После RSC security advisories affected Next.js 14.x проекты должны быть обновлены до `next@14.2.35` или актуальной patched версии своей линии. Это особенно важно для приложений с App Router, RSC, Server Actions и Route Handlers, потому что server runtime становится частью attack surface.

#### Где применяется во frontend

| Ситуация | Deployment вывод |
| --- | --- |
| Чистый static export | можно отдавать Nginx/CDN/S3 |
| SSR/dynamic routes | нужен Node/server runtime |
| Server Actions/Route Handlers | static hosting не подходит |
| Один Docker image на staging/prod | не вшивать секреты в client build |
| Несколько replicas + ISR | нужен shared cache/стратегия revalidation |
| Security patching | следить за Next/RSC patched versions |

#### Пример

Static export:

```js
// next.config.js
const nextConfig = {
  output: "export",
};

module.exports = nextConfig;
```

Standalone server output:

```js
// next.config.js
module.exports = {
  output: "standalone",
};
```

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build --chown=node:node /app/public ./public
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

Server-only runtime env внутри dynamic route:

```tsx
export const dynamic = "force-dynamic";

export default async function Page() {
  const apiToken = process.env.INTERNAL_API_TOKEN;
  const data = await getPrivateData(apiToken);

  return <Dashboard data={data} />;
}
```

`force-dynamic` показан для демонстрации runtime reading, а не как универсальная рекомендация. Если route может оставаться static, конфигурацию лучше определить на build или отделить от page rendering.

#### Ключевые уточнения

- Static rendering внутри Next.js server и static export — разные deployment models.
- `NEXT_PUBLIC_*` является публичным build-time constant; `docker run -e` не перепишет готовый client bundle.
- Обычная env не попадает в client bundle автоматически, но static server render может прочитать её при build.
- Standalone output не включает `public` и `.next/static` автоматически; deployment обязан доставить их отдельно.
- Несколько replicas требуют общей cache/invalidation strategy и согласованной Server Actions configuration.
- Reverse proxy/CDN должен сохранять streaming и не кешировать personalized responses как shared public content.
- Rollout проверяет health, release ID, assets и возможность rollback, а не только факт запуска container.

#### Связанные темы

- [[Конспект для подготовки/DevOps/Docker для frontend]]
- [[Конспект для подготовки/DevOps/Dockerfile и multi-stage build]]
- [[Конспект для подготовки/DevOps/Nginx и static serving]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/Next.js/SSR SSG ISR Streaming]]
- [[Конспект для подготовки/Next.js/Data fetching cache revalidation]]
- [[Конспект для подготовки/Security/Supply chain secrets и third-party scripts]]

#### Источники

- [Next.js 14 docs: Deploying](https://nextjs.org/docs/14/app/building-your-application/deploying)
- [Next.js 14 docs: Static Exports](https://nextjs.org/docs/14/app/building-your-application/deploying/static-exports)
- [React RSC critical security advisory](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components)
