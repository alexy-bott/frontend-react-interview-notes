---
aliases:
  - Next.js data fetching
  - Next.js cache
  - Next.js revalidation
  - revalidatePath
  - revalidateTag
---

#### Быстрый ответ

В Next.js 14 data fetching в App Router обычно выполняют внутри async Server Components. Расширенный server `fetch` управляет persistent Data Cache через `cache` и `next.revalidate`, а React Request Memoization устраняет одинаковые GET requests в рамках одного render. Результат static route отдельно хранится в Full Route Cache, а browser сохраняет посещённые RSC segments в Router Cache.

Freshness нужно задавать осознанно: `force-cache` — переиспользовать данные, `no-store` — получать при каждом server render, `revalidate` — обновлять не чаще заданного interval, tags/path — очищать после события. Мутация считается завершённой не тогда, когда запись сохранена, а когда выбрана корректная invalidation strategy и пользователь больше не получает логически устаревший UI.

#### Ключевая схема

| Механизм Next.js 14 | Что хранит | Срок |
| --- | --- | --- |
| Request Memoization | одинаковый GET `fetch` result | один React render/request |
| Data Cache | server `fetch` response | между requests и deployments, до revalidation/eviction |
| Full Route Cache | HTML + RSC Payload static route | между requests, очищается при redeploy/revalidation |
| Router Cache | RSC Payload route segments в browser | client session/time-based |

```text
Server Component render
-> Request Memoization
-> Data Cache or data source
-> HTML + RSC Payload
-> Full Route Cache (только static route)
-> browser Router Cache
```

#### Базовая модель

В Next.js 14 `fetch` без явной policy по умолчанию использует `force-cache`, пока route не вошёл в dynamic context. Например, после `cookies()` или `headers()` default для последующих requests меняется. Поэтому надёжнее выбирать policy по freshness requirement, а не рассчитывать на порядок строк и framework heuristic.

`cache: "no-store"` не кладёт response в Data Cache и получает его при каждом server render. Такой request выводит route из Full Route Cache, но другие явно кешируемые requests в том же dynamic route могут остаться в Data Cache. `next: { revalidate: 3600 }` хранит response и разрешает обновить его после interval.

`revalidateTag("products")` очищает все Data Cache entries с tag `products`, даже если они используются в разных routes. `revalidatePath("/products")` связывает invalidation с path/layout. Выбор определяется ownership данных: tag выражает data dependency, path — конкретную UI-ветку.

#### Развернутый ответ

**Request Memoization.** React memoizes одинаковые GET `fetch` calls во время render component tree. Это позволяет layout, metadata и page запросить один resource без ручного prop drilling и без нескольких network calls. После render memoization исчезает; это не shared cache и её не нужно revalidate. Route Handlers находятся вне React tree, поэтому этот механизм на них не распространяется.

**Data Cache.** Next.js persistent cache хранит server responses между requests. В browser `fetch` option `cache` описывает HTTP cache, а на Next.js server тот же option управляет framework Data Cache. Это разные execution environments и не следует переносить browser-интуицию напрямую.

**Full Route Cache.** Для static route Next.js сохраняет отрендеренные HTML и RSC Payload. Revalidation данных заставляет route заново отрендериться и обновить output. Обратное неверно: dynamic rendering route не обязано очищать отдельно cached data. Новый deploy очищает Full Route Cache, но Data Cache может жить дольше в зависимости от platform/storage.

**Router Cache.** Client navigation переиспользует prefetched/visited RSC segments. `router.refresh()` запрашивает текущий route заново, не очищая server Data Cache. Revalidation из Route Handler не всегда немедленно удаляет уже сохранённый client payload; Server Action лучше связан с текущим route и может обновить UI в том же flow.

**Не-`fetch` источники.** ORM/SDK не получают Next.js Data Cache автоматически. React `cache()` memoizes функцию в render/request scope; для persistent framework cache в Next.js 14 существовал experimental `unstable_cache`. Если явный cache не нужен, dynamic route может обращаться к DB при каждом render.

**Client fetching.** Live search, polling, infinite scroll, browser-triggered refetch и optimistic UI остаются client concerns. SWR, TanStack Query или RTK Query управляют своим cache, который не является Next.js Data Cache. Initial server data можно передать как props/initial state, но нужно определить, кто затем отвечает за freshness.

#### Пример

```tsx
// app/products/page.tsx
export default async function ProductsPage() {
  const response = await fetch("https://api.example.com/products", {
    next: {
      revalidate: 3600,
      tags: ["products"],
    },
  });

  if (!response.ok) {
    throw new Error("Products request failed");
  }

  const products = await response.json();
  return <ProductList products={products} />;
}
```

```ts
// app/products/actions.ts
"use server";

import { revalidateTag } from "next/cache";

export async function updateProduct(input: UpdateProductInput) {
  await requireCatalogEditor();
  const parsed = updateProductSchema.parse(input);

  await saveProduct(parsed);
  revalidateTag("products");
}
```

Tag выбран потому, что products могут отображаться на catalog, search и recommendation routes. Invalidation одного `/products` path не выразила бы все места использования данных.

#### Ключевые уточнения

- Cache policy описывает допустимую свежесть данных и должна следовать business requirement.
- Request Memoization живёт один render; Data Cache переиспользуется между requests.
- Dynamic route не хранится в Full Route Cache, но может читать shared data из Data Cache.
- `revalidateTag` выражает зависимость от набора данных, `revalidatePath` — от route subtree.
- Revalidation очищает cache entry; новый результат обычно появится при следующем обращении, а не заранее по timer.
- Client Router Cache и server Data Cache очищаются разными APIs; `router.refresh()` не делает upstream data fresh сам по себе.
- Cache не является authorization boundary: personalized response нельзя переиспользовать между users по общему key.

#### Связанные темы

- [[Конспект для подготовки/Next.js/SSR SSG ISR Streaming]]
- [[Конспект для подготовки/Next.js/Server Actions и Route Handlers]]
- [[Конспект для подготовки/Next.js/Server и Client Components]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/Web Basics/HTTP caching]]
- [[Конспект для подготовки/Web Basics/REST]]

#### Источники

- [Next.js 14 docs: Caching](https://nextjs.org/docs/14/app/building-your-application/caching)
- [Next.js 14 docs: Fetching, Caching, and Revalidating](https://nextjs.org/docs/14/app/building-your-application/data-fetching/fetching-caching-and-revalidating)
- [Next.js 14 API: fetch](https://nextjs.org/docs/14/app/api-reference/functions/fetch)
