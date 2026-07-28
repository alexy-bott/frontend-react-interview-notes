---
aliases:
  - Next.js 14
  - Next 14
  - Next.js version 14
---

#### Ответ на 60 секунд

Next.js 14 - версия фреймворка поверх React 18, где основной современный подход строится вокруг App Router, React Server Components, Server Actions, streaming, cache/revalidation и гибридного rendering. В этой версии Server Actions стали стабильными, Turbopack получил заметные улучшения в dev, а Partial Prerendering существовал как preview/experimental-фича.

Важно не смешивать Next.js 14 с более новыми версиями. В официальной документации на 16 июля 2026 актуальная ветка Next.js показывает latest `16.2.10`, а стек в этом конспекте привязан к Next.js 14. Для ответа по Next.js 14 корректно говорить про React 18, App Router, Server Components, Server Actions, `fetch` cache/revalidate-модель версии 14, static/dynamic rendering и SSR/ISR/streaming. React Compiler, современные Cache Components и директива `use cache` относятся к более новым объяснениям экосистемы и не должны звучать как базовая фича Next.js 14.

#### Ключевая схема

| Область | В Next.js 14 |
| --- | --- |
| React | React 18 |
| Router | App Router уже основной современный подход, Pages Router ещё используется в проектах |
| Components | Server Components по умолчанию в `app` |
| Client UI | через `"use client"` boundary |
| Mutations | Server Actions стабильны |
| Rendering | static, dynamic, streaming, ISR |
| Cache | Data Cache, Full Route Cache, `revalidate`, `revalidatePath`, `revalidateTag` |
| PPR | preview/experimental, не базовая production-опора |
| Node.js | минимум `18.17` |
| Static export | `output: "export"`, команда `next export` удалена |
| Security patch line | для Next 14 после RSC advisories ориентир - `14.2.35` |

#### Развернутый ответ

Next.js - это не просто bundler для React, а framework-level слой: routing, rendering, data fetching, cache, image/font optimization, API layer, server-side execution и production conventions. В Next.js 14 главная архитектурная линия - App Router. Внутри `app` route строится файловой структурой: `page.tsx` делает сегмент публичным, `layout.tsx` задаёт общую оболочку, `loading.tsx` и Suspense помогают streaming, `error.tsx` локализует ошибки.

App Router опирается на React Server Components. Компоненты в `app` по умолчанию серверные: они могут читать данные на сервере, обращаться к секретам, не попадать в клиентский JavaScript bundle и отдавать результат в RSC Payload/HTML. Интерактивность выносится в Client Components через директиву `"use client"`. Такая граница важна для размера bundle: если большой layout пометить как client, в клиент уедет больше кода.

Rendering в Next.js 14 гибридный. Если route не использует request-time данные и все данные кешируемы, он может быть static. Если используются `cookies()`, `headers()`, `searchParams`, `cache: "no-store"` или dynamic config, route становится dynamic и рендерится на запросе. ISR позволяет оставить страницу статической, но обновлять её по времени или событию. Streaming через Suspense даёт возможность отправлять готовые части UI раньше, чем завершится медленная часть.

Data fetching в версии 14 часто объясняется через расширенный server-side `fetch`. По умолчанию `fetch` в Server Components может кешироваться в Data Cache, а поведение меняется через `cache: "no-store"`, `next: { revalidate }`, tags и route segment config. Мутации и invalidation связываются с Server Actions или Route Handlers через `revalidatePath` и `revalidateTag`.

Production-вопросы в Next.js отличаются от SPA. Static export можно отдать через Nginx/CDN как статические файлы, но SSR, Server Actions, Middleware, Route Handlers и runtime image optimization требуют server runtime. В Docker для SSR обычно нужен Node process или standalone output; Nginx может быть reverse proxy, но не заменяет Node runtime.

Для production на Next.js 14 важно учитывать RSC security advisories. Официальная React-инструкция для affected Next.js 14.x указывает обновление до `next@14.2.35`. Это не добавляет новую фичу, но важно для проектов с App Router/RSC/Server Actions, потому что часть уязвимостей находилась в серверной RSC-инфраструктуре.

#### Где применяется во frontend

| Ситуация | Что говорить про Next.js 14 |
| --- | --- |
| Собес спрашивает “что нового в Next 14” | App Router, Server Actions stable, cache/revalidation, streaming |
| Просят сравнить с SPA | Next добавляет server runtime, routing, rendering и cache model |
| Проект на Next 14, docs показывают Next 16 | проверять версию docs и не переносить новые API назад |
| Production/self-hosting | SSR/Actions/Route Handlers требуют Node/server runtime |
| Security review | держать `next@14.2.35` для 14.x после RSC advisories |

> [!faq]+ Уточнения
> - Next.js 14 работает с React 18; React 19 не является базой этой версии.
> - Server Actions в Next.js 14 стабильны, но всё равно требуют server-side validation и authorization.
> - Partial Prerendering в Next.js 14 - preview/experimental, поэтому его нельзя описывать как обязательную production-модель.
> - `next export` удалён; для static export используют `output: "export"`.
> - Актуальная документация Next.js уже ушла дальше версии 14, поэтому формулировки про cache/React Compiler нужно проверять по версии проекта.
> - Для Next.js 14.x после RSC security advisories важно обновиться до patched line, указанной официальными React/Next инструкциями.

#### Частые ошибки

- Смешивать App Router и Pages Router в одном объяснении без указания контекста.
- Называть любой server render “SSR”, хотя route может быть static, dynamic, ISR или streamed.
- Считать `"use client"` локальной пометкой только одного компонента, забывая про client module graph.
- Относить React Compiler к Next.js 14.
- Деплоить SSR-приложение как обычную SPA без Node runtime.

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
