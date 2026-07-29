---
aliases:
  - Next.js 14
  - Next 14
  - Next.js version 14
---

#### Быстрый ответ

Next.js 14 — full-stack React framework на базе React 18. Он добавляет file-system routing, server и client rendering, data fetching, cache/revalidation, server endpoints и production build. Основная модель App Router строится вокруг React Server Components: серверная часть UI является default, а интерактивные участки явно образуют client boundaries.

В Next.js 14 Server Actions стали стабильными, server `fetch` по умолчанию получил cache semantics этой версии, а static/dynamic rendering, ISR и streaming управляются на уровне route и данных. Partial Prerendering оставался experimental/preview. React Compiler, Cache Components и директива `use cache` не относятся к базовой модели Next.js 14 и не должны переноситься из документации новых версий без явной оговорки.

#### Ключевая схема

| Область | В Next.js 14 |
| --- | --- |
| React | React 18 |
| Router | App Router уже основной современный подход, Pages Router ещё используется в проектах |
| Components | Server Components по умолчанию в `app` |
| Client UI | через `"use client"` boundary |
| Mutations | Server Actions стабильны |
| Rendering | static, dynamic, streaming, ISR |
| Cache | Request Memoization, Data Cache, Full Route Cache и client Router Cache |
| PPR | preview/experimental, не базовая production-опора |
| Node.js | минимум `18.17` |
| Static export | `output: "export"`, команда `next export` удалена |
| Security patch line | для Next 14 после RSC advisories ориентир - `14.2.35` |

#### Базовая модель

Next.js — не bundler и не замена React, а framework-level слой вокруг него: routing, rendering, data fetching, cache, image/font optimization, server endpoints и production conventions. В Next.js 14 главная архитектурная линия — App Router. Внутри `app` route строится файловой структурой: `page.tsx` делает сегмент публичным, `layout.tsx` задаёт общую оболочку, `loading.tsx` и Suspense помогают streaming, `error.tsx` локализует ошибки.

App Router опирается на React Server Components. Компоненты в `app` по умолчанию серверные: они могут читать данные рядом с server-side источником и не добавляют свой component code в client JavaScript bundle. Интерактивность выносится в Client Components через директиву `"use client"`. Client Component при первоначальной загрузке всё ещё может участвовать в server prerender, но для интерактивности его code загружается в browser и проходит hydration.

#### Развернутый ответ

Rendering в Next.js 14 гибридный. Route без request-time dependencies может быть static и храниться в Full Route Cache. Dynamic functions (`cookies()`, `headers()`), `searchParams`, uncached data или route config могут перевести его в request-time rendering. При этом dynamic route всё ещё способен использовать отдельно кешируемые данные: отказ от Full Route Cache не всегда означает отказ от Data Cache. ISR обновляет static output по времени или событию, а streaming отправляет готовые chunks раньше медленной части.

Data fetching в версии 14 часто объясняется через расширенный server-side `fetch`. До dynamic context default соответствует `force-cache`: response может храниться в persistent Data Cache. `cache: "no-store"`, `next: { revalidate }`, tags и route segment config задают freshness. Request Memoization отдельно устраняет повторные одинаковые GET `fetch` внутри одного React render; это не persistent cache. Мутации инвалидируют нужные entries через `revalidatePath` или `revalidateTag`.

Production-вопросы в Next.js отличаются от SPA. Static export можно отдать через Nginx/CDN как статические файлы, но SSR, Server Actions, Middleware, Route Handlers и runtime image optimization требуют server runtime. В Docker для SSR обычно нужен Node process или standalone output; Nginx может быть reverse proxy, но не заменяет Node runtime.

Для production на Next.js 14 важно учитывать RSC security advisories. Официальная React-инструкция для affected Next.js 14.x указывает обновление до `next@14.2.35`. Это не добавляет новую фичу, но важно для проектов с App Router/RSC/Server Actions, потому что часть уязвимостей находилась в серверной RSC-инфраструктуре.

#### Практическое значение

| Ситуация | Что говорить про Next.js 14 |
| --- | --- |
| Нужно назвать особенности Next 14 | App Router, Server Actions stable, cache/revalidation, streaming |
| Просят сравнить с SPA | Next добавляет server runtime, routing, rendering и cache model |
| Проект на Next 14, docs показывают Next 16 | проверять версию docs и не переносить новые API назад |
| Production/self-hosting | SSR/Actions/Route Handlers требуют Node/server runtime |
| Security review | держать `next@14.2.35` для 14.x после RSC advisories |

#### Ключевые уточнения

- Next.js 14 основан на React 18; возможности React 19 и новых Next.js versions не входят в baseline карточки.
- App Router и Pages Router могут существовать в проектах одновременно, но их data/rendering APIs нельзя смешивать в одном объяснении.
- Server rendering включает разные режимы: static output, dynamic request render, ISR и streaming; не каждый из них является SSR «на каждый запрос».
- `"use client"` создаёт module boundary, а не выключает initial server prerender Client Component.
- Server Actions стабильны как framework feature, но остаются server endpoints и требуют authentication, authorization и runtime validation.
- Static export использует `output: "export"`; server-only features требуют Node или совместимый runtime.
- Для линии Next.js 14 после RSC advisories официально исправленной версией указана `14.2.35`; security patching проверяют отдельно от feature baseline.

#### Связанные темы

- [[Конспект для подготовки/Next.js/App Router]]
- [[Конспект для подготовки/Next.js/Server и Client Components]]
- [[Конспект для подготовки/Next.js/SSR SSG ISR Streaming]]
- [[Конспект для подготовки/Next.js/Data fetching cache revalidation]]
- [[Конспект для подготовки/React/React 18 и 19]]
- [[Конспект для подготовки/React/Server Components]]
- [[Конспект для подготовки/DevOps/Docker для frontend]]

#### Источники

- [Next.js docs: latest version](https://nextjs.org/docs)
- [Next.js 14 docs](https://nextjs.org/docs/14)
- [Next.js docs: upgrading to version 14](https://nextjs.org/docs/app/guides/upgrading/version-14)
- [Next.js blog: Next.js 14](https://nextjs.org/blog/next-14)
- [React RSC critical security advisory](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components)
