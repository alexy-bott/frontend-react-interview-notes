---
aliases:
  - Next.js deployment
  - Next.js Docker
  - Next.js env variables
  - Next.js self-hosting
---

#### Ответ на 60 секунд

Next.js deployment зависит от режима приложения. Static export создаёт HTML/CSS/JS assets и может отдаваться Nginx, CDN, S3 или любым static server. Но SSR, dynamic rendering, Server Actions, Route Handlers, Middleware и runtime image optimization требуют server runtime: Node.js server, Docker container с Node process или платформу, которая поддерживает Next.js server execution.

Env variables делятся на server-only и public. По умолчанию env доступны только на сервере. Всё с prefix `NEXT_PUBLIC_` попадает в browser bundle и становится публичным. В Docker важно различать build-time env и runtime env: если значение нужно менять между окружениями без пересборки image, его нельзя вшивать в client bundle на этапе `next build`.

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
| private env | читается только на сервере |

#### Развернутый ответ

Для SPA привычная схема проста: собрать `dist`/`build`, положить в Nginx/CDN и отдавать статику. Next.js может работать так же, если проект использует static export. В Next.js 14 команда `next export` удалена; static export включают через `output: "export"` в `next.config.js`. После `next build` получается папка `out`.

SSR-приложение нельзя свести к набору статических файлов. Если route рендерится на request time, использует Server Actions, Route Handlers, Middleware, cookies/headers, dynamic rendering или runtime env, нужен server process. В self-hosting варианте это обычно `next build` + `next start` или standalone output внутри Docker image. Nginx в такой архитектуре может отдавать static assets и проксировать запросы в Node.js, но не заменяет server runtime.

Env variables - частая ловушка. Server-only env можно читать в server code: Server Components, Route Handlers, Server Actions. Public env с `NEXT_PUBLIC_` встраиваются в client bundle во время build, поэтому пользователь может увидеть их в JS. Такие значения подходят для public API base URL, analytics key, feature flag без секрета, но не для токенов, private URLs и credentials.

Build-time и runtime env особенно важны в Docker. Один и тот же image часто продвигают из staging в production. Если значение вшито в bundle на `next build`, оно уже не изменится при `docker run -e`. Для runtime server env используют server-side чтение во время request/dynamic rendering. Для client-visible значений обычно требуется отдельная стратегия: разные builds, runtime config endpoint, server-injected config или hosting-level mechanism.

Self-hosted cache тоже нужно учитывать. ISR/Data Cache по умолчанию может храниться на filesystem/in-memory конкретного контейнера. Если несколько replicas обслуживают один сайт, без общего cache handler возможна рассинхронизация. Для Kubernetes/нескольких containers нужен общий cache layer или настройка cache handler, если приложение активно использует ISR/revalidation.

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

> [!faq]+ Уточнения
> - Static export можно отдавать через Nginx/CDN, но он не поддерживает server-only features.
> - SSR Next.js требует Node.js runtime или совместимую платформу.
> - `NEXT_PUBLIC_*` не секрет, а публичное значение, зашитое в browser bundle.
> - Runtime env в Docker работают для server code, но не меняют уже собранный client JS.
> - При нескольких replicas нужно думать о shared cache для ISR/Data Cache.
> - `NEXT_PUBLIC_*` и sourcemaps считаются публичной поверхностью; секреты держат на сервере/CI/CD secret storage.

#### Пример

Static export:

```js
// next.config.js
const nextConfig = {
  output: "export",
};

module.exports = nextConfig;
```

Server runtime scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

Server-only env:

```tsx
export default async function Page() {
  const apiToken = process.env.INTERNAL_API_TOKEN;
  const data = await getPrivateData(apiToken);

  return <Dashboard data={data} />;
}
```

#### Частые ошибки

- Деплоить SSR Next.js как набор файлов для Nginx.
- Класть секреты в `NEXT_PUBLIC_*`.
- Ожидать, что `docker run -e NEXT_PUBLIC_API_URL=...` изменит уже собранный JS.
- Не учитывать cache/ISR при нескольких replicas.
- Использовать static export, а потом ожидать работу Server Actions или Route Handlers.

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
