---
aliases:
  - App Router
  - Next.js App Router
  - app directory
---

#### Ответ на 60 секунд

App Router - современная routing-модель Next.js, основанная на папке `app`. URL собирается из сегментов папок, а специальные файлы задают поведение route: `page.tsx` делает страницу публичной, `layout.tsx` создаёт общую оболочку, `loading.tsx` даёт loading UI и streaming boundary, `error.tsx` локализует ошибки, `not-found.tsx` отвечает за 404, `route.ts` создаёт request handler.

В App Router страницы и layouts по умолчанию являются Server Components. Это меняет привычную модель React-приложения: данные можно получать прямо в server component, layout может сохраняться между навигациями, а интерактивные части выносятся в Client Components через `"use client"`. App Router нужен не только для routing, но и для rendering, data fetching, cache, metadata, streaming и nested UI.

#### Ключевая схема

| Файл | Назначение |
| --- | --- |
| `app/page.tsx` | UI для `/` |
| `app/dashboard/page.tsx` | UI для `/dashboard` |
| `layout.tsx` | общая оболочка сегмента, сохраняется между навигациями |
| `template.tsx` | оболочка, которая пересоздаётся при навигации |
| `loading.tsx` | instant loading state и streaming route segment |
| `error.tsx` | error boundary для сегмента |
| `not-found.tsx` | UI для `notFound()` |
| `route.ts` | HTTP handler без React UI |
| `(group)` | route group без добавления сегмента в URL |
| `[id]` | dynamic segment |

#### Развернутый ответ

В App Router файловая структура становится частью runtime-модели. Папки описывают route segments, а `page.tsx` делает конкретный route доступным по URL. Если в папке нет `page.tsx`, сегмент может использоваться как layout/grouping, но не как самостоятельная страница.

`layout.tsx` нужен для общего UI: навигации, сайдбара, providers, shell. При переходе между дочерними routes layout сохраняет состояние и не пересоздаётся без необходимости. Это важно для UX: можно сохранить раскрытые панели, проигрывание, scroll-состояние в части UI или состояние provider. `template.tsx`, наоборот, пересоздаёт subtree при навигации и подходит, когда нужен fresh lifecycle.

`loading.tsx` связан со streaming. Next.js может отдать часть UI сразу, а медленный server component или Suspense boundary догрузить позже. `error.tsx` работает как React error boundary для сегмента и должен быть Client Component, потому что error boundary в React реализуется на клиентской стороне. `not-found.tsx` используется вместе с `notFound()`.

`route.ts` не рендерит React UI. Это HTTP endpoint на Web Request/Response API: webhooks, BFF endpoints, downloads, CORS, proxy to backend, health checks. На одном уровне route segment нельзя одновременно иметь `page.tsx` и `route.ts`, потому что оба претендуют на один URL endpoint.

Metadata в App Router задаётся через `metadata` object или `generateMetadata`. Это заменяет ручное управление `<head>` для большинства страниц и удобно для SEO, Open Graph и динамических title/description.

#### Где применяется во frontend

| Задача | Файл/механизм App Router |
| --- | --- |
| Общий dashboard shell | `dashboard/layout.tsx` |
| Skeleton для медленной страницы | `loading.tsx` или Suspense boundary |
| Локальная ошибка сегмента | `error.tsx` |
| Страница товара `/products/123` | `products/[id]/page.tsx` |
| Webhook или health check | `route.ts` |
| SEO title/OG | `metadata` или `generateMetadata` |

> [!faq]+ Уточнения
> - `page.tsx` обязателен, чтобы route segment стал публичной страницей.
> - `layout.tsx` сохраняется между навигациями, `template.tsx` пересоздаётся.
> - Route groups `(marketing)` помогают организовать файлы без изменения URL.
> - `loading.tsx` работает на уровне сегмента и связан со streaming.
> - `route.ts` используют для HTTP endpoints, а не для UI-страниц.

#### Пример

```text
app
├─ layout.tsx
├─ page.tsx
├─ dashboard
│  ├─ layout.tsx
│  ├─ loading.tsx
│  ├─ error.tsx
│  └─ page.tsx
├─ products
│  └─ [id]
│     └─ page.tsx
└─ api
   └─ health
      └─ route.ts
```

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <aside>Navigation</aside>
      <main>{children}</main>
    </>
  );
}
```

#### Частые ошибки

- Думать, что папка сама по себе создаёт страницу без `page.tsx`.
- Помечать весь root layout как `"use client"` из-за одного интерактивного элемента.
- Путать `route.ts` с React page.
- Не учитывать, что layout сохраняет состояние между переходами.
- Дублировать providers слишком глубоко или слишком высоко без причины.

#### Связанные темы

- [[Конспект для подготовки/Next.js/Server и Client Components]]
- [[Конспект для подготовки/Next.js/SSR SSG ISR Streaming]]
- [[Конспект для подготовки/Next.js/Data fetching cache revalidation]]
- [[Конспект для подготовки/Next.js/Server Actions и Route Handlers]]
- [[Конспект для подготовки/React/Hydration]]

#### Источники

- [Next.js 14 docs: Pages and Layouts](https://nextjs.org/docs/14/app/building-your-application/routing/pages-and-layouts)
- [Next.js 14 docs: Route Handlers](https://nextjs.org/docs/14/app/building-your-application/routing/route-handlers)
