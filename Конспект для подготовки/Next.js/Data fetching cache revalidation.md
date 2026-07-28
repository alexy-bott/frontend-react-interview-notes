---
aliases:
  - Next.js data fetching
  - Next.js cache
  - Next.js revalidation
  - revalidatePath
  - revalidateTag
---

#### Ответ на 60 секунд

В Next.js 14 data fetching в App Router чаще всего делают в Server Components через `fetch` или server-side библиотеки. Next.js расширяет server-side `fetch`: запросы могут мемоизироваться внутри React render tree, кешироваться в Data Cache и управляться через `cache`, `next: { revalidate }`, tags и route segment config. Для fresh данных используют `cache: "no-store"` или `revalidate: 0`; для ISR/time-based cache - `next: { revalidate: seconds }`; для on-demand invalidation - `revalidatePath` и `revalidateTag`.

Главная мысль: data fetching, cache и rendering связаны. Кешируемые данные позволяют route быть static/ISR, а request-time данные вроде cookies, headers или `no-store` переводят route в dynamic rendering. Мутации должны не только записать данные, но и инвалидировать нужный path/tag.

#### Ключевая схема

| Задача | Инструмент в Next.js 14 |
| --- | --- |
| Получить данные на сервере | `await fetch(...)` в Server Component |
| Не кешировать запрос | `fetch(url, { cache: "no-store" })` |
| Обновлять по времени | `fetch(url, { next: { revalidate: 3600 } })` |
| Обновлять segment | `export const revalidate = 3600` |
| Пометить cache entry | `next: { tags: ["products"] }` |
| Инвалидировать path | `revalidatePath("/products")` |
| Инвалидировать tag | `revalidateTag("products")` |
| Использовать cookies/headers | `cookies()`, `headers()`; route становится dynamic |
| Client fetching | SWR/React Query/RTK Query или Route Handler |

#### Развернутый ответ

В App Router серверный data fetching можно делать прямо внутри async Server Component. Это убирает лишний client request после загрузки страницы, позволяет держать токены и секреты на сервере и уменьшает клиентский bundle. Если библиотека не использует `fetch`, например ORM или SDK, кеширование уже зависит от route rendering, React `cache` или специальных API Next.js.

В Next.js 14 `fetch` на сервере отличается от browser fetch. React может мемоизировать одинаковые запросы во время render одного component tree, чтобы не выполнять один и тот же запрос несколько раз. Next.js добавляет persistent Data Cache для кешируемых запросов. По умолчанию в документации 14 указано `force-cache`, поэтому для данных, которые должны быть свежими на каждый запрос, нужно явно задать `cache: "no-store"` или `revalidate: 0`.

Revalidation бывает time-based и on-demand. Time-based подходит для данных, где допустима задержка обновления: каталог, блог, CMS-страницы. On-demand используют после события: обновили товар, сохранили пост, получили webhook от CMS. Для path-based invalidation вызывают `revalidatePath("/products")`, для tag-based - помечают запрос `next: { tags: ["products"] }` и затем вызывают `revalidateTag("products")`.

Rendering зависит от cache. Если route использует только кешируемые данные и не читает request-time информацию, Next.js может сделать его static. Если внутри route используются `cookies()`, `headers()`, `searchParams`, uncached request или `force-dynamic`, route станет dynamic. Это не ошибка, но нужно понимать цену: меньше CDN/cache reuse, больше server work, выше чувствительность к latency backend.

На клиенте data fetching остаётся нужен для client-only сценариев: live search, infinite scroll, optimistic UI, polling, user-triggered refetch. Для этого используют SWR, TanStack Query, RTK Query или собственный слой поверх Route Handler/backend API. Server Components не заменяют client state management, они закрывают server render и initial data.

#### Где применяется во frontend

| Ситуация | Cache/data strategy |
| --- | --- |
| Каталог обновляется раз в час | `next: { revalidate: 3600 }` |
| Личный кабинет | `cache: "no-store"` или dynamic rendering |
| CMS webhook после публикации | `revalidateTag` или `revalidatePath` |
| Данные используются на нескольких pages | tag-based invalidation |
| Live search в input | client query library или Route Handler |
| Secret API token | fetch в Server Component/Action/Handler, не в client |

> [!faq]+ Уточнения
> - В Next.js 14 server `fetch` по умолчанию кешируется как `force-cache`; в более новых версиях модель cache описывается иначе, поэтому важно смотреть версию проекта.
> - `cache: "no-store"` означает fresh request и обычно переводит route в dynamic rendering.
> - `revalidatePath` удобно инвалидирует конкретный URL/path, `revalidateTag` - группу данных, используемую разными routes.
> - Route Handlers не являются частью React component tree, поэтому memoization server component render на них не распространяется.
> - Client Components не должны получать server secrets; при необходимости используют Route Handler/BFF или Server Action.

#### Пример

```tsx
export default async function ProductsPage() {
  const res = await fetch("https://api.example.com/products", {
    next: {
      revalidate: 3600,
      tags: ["products"],
    },
  });

  if (!res.ok) {
    throw new Error("Failed to load products");
  }

  const products = await res.json();
  return <ProductList products={products} />;
}
```

```ts
"use server";

import { revalidateTag } from "next/cache";

export async function updateProduct(formData: FormData) {
  await saveProduct(formData);
  revalidateTag("products");
}
```

#### Частые ошибки

- Не указывать cache policy и получать не ту свежесть данных, которую ожидали.
- Использовать `cookies()` в layout и случайно делать большой route subtree dynamic.
- Инвалидировать path, хотя данные переиспользуются на нескольких страницах и нужен tag.
- Дублировать один и тот же server fetch без понимания memoization/cache границ.
- Делать client fetch для initial data, которую можно безопасно получить на сервере.

#### Связанные темы

- [[Конспект для подготовки/Next.js/SSR SSG ISR Streaming]]
- [[Конспект для подготовки/Next.js/Server Actions и Route Handlers]]
- [[Конспект для подготовки/Next.js/Server и Client Components]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/Web Basics/HTTP caching]]
- [[Конспект для подготовки/Web Basics/REST]]

#### Источники

- [Next.js 14 docs: Fetching, Caching, and Revalidating](https://nextjs.org/docs/14/app/building-your-application/data-fetching/fetching-caching-and-revalidating)
- [Next.js docs: Fetching Data](https://nextjs.org/docs/app/getting-started/fetching-data)
