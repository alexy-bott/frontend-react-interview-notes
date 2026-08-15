# App Router

<!-- NOTE-NAV-TOP:START -->
[← Next.js 14](<./01 Next.js 14.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Серверные и клиентские компоненты →](<./03 Серверные и клиентские компоненты.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

App Router — routing и rendering-модель Next.js на основе папки `app`. Папки образуют URL segments, а специальные файлы задают UI и поведение route: `page.tsx` публикует страницу, `layout.tsx` сохраняет общую оболочку, `loading.tsx` создаёт loading boundary, `error.tsx` обрабатывает ошибку сегмента, `not-found.tsx` — отсутствие ресурса, `route.ts` — HTTP endpoint.

В App Router страницы и layouts по умолчанию являются Server Components. Это меняет привычную модель React-приложения: данные можно получать прямо в server component, layout может сохраняться между навигациями, а интерактивные части выносятся в Client Components через `"use client"`. App Router нужен не только для routing, но и для rendering, data fetching, cache, metadata, streaming и nested UI.

## Ключевая схема

| Файл | Назначение |
| --- | --- |
| `app/page.tsx` | UI для `/` |
| `app/dashboard/page.tsx` | UI для `/dashboard` |
| `layout.tsx` | общая оболочка сегмента, сохраняется между навигациями |
| `template.tsx` | оболочка, которая пересоздаётся при навигации |
| `loading.tsx` | instant loading state и streaming route segment |
| `error.tsx` | fallback и повторная попытка для ошибки сегмента |
| `not-found.tsx` | UI для `notFound()` |
| `route.ts` | HTTP handler без React UI |
| `(group)` | route group без добавления сегмента в URL |
| `[id]` | dynamic segment |
| `@slot` | parallel route, передаваемый layout как prop |
| `(.)photo` | intercepted route для modal/detail navigation |

## Базовая модель

В App Router файловая структура становится частью runtime-модели. Папки описывают route segments, а `page.tsx` делает конкретный route доступным по URL. Если в папке нет `page.tsx`, сегмент может использоваться как layout/grouping, но не как самостоятельная страница.

При client navigation Next.js запрашивает RSC payload изменившихся segments и сохраняет общие layouts. Поэтому вложенный route обновляется без полной перезагрузки документа, а client state внутри сохранённой layout subtree может пережить переход. `template.tsx`, напротив, получает новый key и remount-ит subtree при навигации, когда нужен новый lifecycle.

## Развернутый ответ

`layout.tsx` нужен для общего UI: navigation, sidebar, providers и shell. Layout не должен полагаться на повторный server render при каждой navigation; для текущего pathname или search params интерактивная часть использует client hooks. Providers размещают настолько глубоко, насколько позволяет область их состояния, чтобы не расширять client bundle без необходимости.

`loading.tsx` автоматически оборачивает page и вложенные segments в Suspense boundary. Next.js может показать prefetched fallback и сохранить общий layout, пока новый segment рендерится/stream-ится. Для более точного разделения одной страницы используют явные `<Suspense>` boundaries.

`error.tsx` должен быть Client Component: он получает `error` и функцию `reset`, показывает fallback и может повторить render segment. Next.js способен поймать ошибку, возникшую при server rendering, но чувствительные details в production не передаёт клиенту; для диагностики используют server logs и error digest. Ошибка самого layout обрабатывается boundary родительского segment, а не его собственным `error.tsx`.

`route.ts` не рендерит React UI. Это HTTP endpoint на Web Request/Response API: webhooks, BFF endpoints, downloads, CORS, proxy to backend, health checks. На одном уровне route segment нельзя одновременно иметь `page.tsx` и `route.ts`, потому что оба претендуют на один URL endpoint.

Metadata в App Router задаётся через `metadata` object или `generateMetadata`. Это заменяет ручное управление `<head>` для большинства страниц и удобно для SEO, Open Graph и динамических title/description.

Parallel Routes (`@slot`) позволяют layout одновременно рендерить независимые route branches, например dashboard panels. Intercepting Routes показывают другой route внутри текущего navigation context, например photo modal поверх gallery; при direct load тот же URL может открыть полноценную страницу. Эти возможности нужны для конкретной UI-модели, а не для обычной вложенной маршрутизации.

## Где применяется во frontend

| Задача | Файл/механизм App Router |
| --- | --- |
| Общий dashboard shell | `dashboard/layout.tsx` |
| Skeleton для медленной страницы | `loading.tsx` или Suspense boundary |
| Локальная ошибка сегмента | `error.tsx` |
| Страница товара `/products/123` | `products/[id]/page.tsx` |
| Webhook или health check | `route.ts` |
| SEO title/OG | `metadata` или `generateMetadata` |

## Пример

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

## Ключевые уточнения

- Папка задаёт segment, но публичный UI-route появляется только при наличии `page.tsx`.
- `layout.tsx` сохраняется при переходах между дочерними routes; `template.tsx` намеренно remount-ится.
- `loading.tsx` создаёт segment-level Suspense boundary, а локальные медленные части можно оборачивать в собственный `<Suspense>`.
- Ошибка layout попадает в ближайший `error.tsx` выше него, потому что boundary не может поймать ошибку компонента, внутри которого он объявлен.
- Route groups организуют дерево без изменения URL; одинаковый результирующий URL из разных groups создаёт конфликт.
- `route.ts` реализует HTTP endpoint и конфликтует с `page.tsx` на том же route level.
- Client providers и interactive widgets лучше размещать внутри server layout узкими boundaries.

## Связанные темы

- [Серверные и клиентские компоненты](<./03 Серверные и клиентские компоненты.md>)
- [Next.js 14](<./01 Next.js 14.md>)
- [SSR, SSG, ISR и Streaming](<./04 SSR, SSG, ISR и Streaming.md>)
- [Получение данных, кеш и ревалидация](<./05 Получение данных, кеш и ревалидация.md>)
- [Server Actions и Route Handlers](<./06 Server Actions и Route Handlers.md>)
- [Гидратация (Hydration)](<../React/28 Гидратация (Hydration).md>)

## Источники

- [Next.js 14 docs: Pages and Layouts](https://nextjs.org/docs/14/app/building-your-application/routing/pages-and-layouts)
- [Next.js 14 docs: Route Handlers](https://nextjs.org/docs/14/app/building-your-application/routing/route-handlers)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Next.js 14](<./01 Next.js 14.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Серверные и клиентские компоненты →](<./03 Серверные и клиентские компоненты.md>)
<!-- NOTE-NAV-BOTTOM:END -->
