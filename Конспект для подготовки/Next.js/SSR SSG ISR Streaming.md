---
aliases:
  - Next.js SSR
  - Next.js SSG
  - Next.js ISR
  - Next.js streaming
  - static dynamic rendering Next.js
---

#### Ответ на 60 секунд

В Next.js 14 rendering точнее описывать не только через SSR/SSG, а через static rendering, dynamic rendering, ISR и streaming. Static rendering создаёт результат заранее или в фоне после revalidation и хорошо кешируется/CDN. Dynamic rendering выполняется на request time, когда route зависит от cookies, headers, search params, `no-store` данных или другой request-time информации. ISR позволяет отдавать статический результат и обновлять его по времени или событию. Streaming разбивает server render на chunks и отправляет готовые части UI раньше, чем завершится весь route.

SSR в разговорной формулировке обычно означает “HTML создаётся на сервере”, но в Next.js 14 важно уточнять модель: страница может быть полностью static, dynamic per request, static с revalidation или streamed через Suspense. После server render клиентские части всё равно проходят hydration.

#### Ключевая схема

| Модель | Когда рендерится | Когда подходит |
| --- | --- | --- |
| Static rendering | build time или после revalidation | публичные страницы, каталоги, блог, документация |
| Dynamic rendering | на каждый request | auth, cookies, user-specific данные, request-time logic |
| ISR | static + обновление по TTL/tag/path | данные меняются, но не требуют fresh response на каждый request |
| Streaming | chunks по мере готовности | медленные части UI, большие страницы, Suspense |
| CSR внутри Next | в Client Components после hydration | highly interactive widgets, browser-only state |

#### Развернутый ответ

Static rendering в App Router включается, когда route не зависит от request-time данных и может быть безопасно закеширован. Результат можно переиспользовать между пользователями и отдавать быстро. В Next.js 14 static route может обновляться через `revalidate`, `revalidatePath` или `revalidateTag`, поэтому static не обязательно означает “навсегда неизменяемый”.

Dynamic rendering включается, когда Next.js видит зависимость от конкретного запроса: `cookies()`, `headers()`, `searchParams`, uncached data request, `cache: "no-store"`, `revalidate: 0` или route segment config вроде `dynamic = "force-dynamic"`. Такой route рендерится на request time, потому что результат может отличаться для разных пользователей или запросов.

ISR - компромисс между SSG и SSR. Пользователь получает закешированную страницу, а обновление происходит по времени или по событию. Time-based revalidation задаётся через `next: { revalidate: seconds }` у `fetch` или `export const revalidate = seconds` для segment. On-demand revalidation делается через `revalidatePath` или `revalidateTag`, обычно после мутации в Server Action или Route Handler.

Streaming решает проблему “всё или ничего”. Без streaming сервер ждёт все данные и только потом отдаёт HTML. С `loading.tsx` и Suspense можно отправить shell и готовые участки сразу, а медленные части догрузить позже. Это улучшает perceived performance, но требует аккуратных boundaries: fallback должен быть meaningful, а не ломать layout.

SSR/SSG/ISR не отменяют hydration. Server Components могут не отправлять свой JS в клиент, но Client Components должны загрузиться и гидратироваться. Поэтому performance зависит от cache strategy, streaming boundaries, размера client bundle и количества интерактивных islands.

#### Где применяется во frontend

| Страница/фича | Rendering choice |
| --- | --- |
| Публичный лендинг | static rendering |
| Блог/CMS | ISR/time-based или on-demand revalidation |
| Account page | dynamic rendering |
| Dashboard с медленными виджетами | streaming + Suspense boundaries |
| Product catalog | static/ISR + dynamic filters при необходимости |
| Browser-only editor | Client Component внутри server-rendered shell |

> [!faq]+ Уточнения
> - `cookies()` и `headers()` в Server Component переводят route в dynamic rendering.
> - `fetch(..., { cache: "no-store" })` делает данные request-time и влияет на rendering route.
> - `revalidate` задаёт TTL для кеша, но не делает данные персональными.
> - Streaming работает через route segments, `loading.tsx` и React Suspense.
> - Static export отличается от static rendering: export создаёт набор файлов для static hosting и не поддерживает server-only features.

#### Пример

Static/ISR:

```tsx
export const revalidate = 3600;

export default async function ProductsPage() {
  const res = await fetch("https://api.example.com/products", {
    next: { revalidate: 3600 },
  });
  const products = await res.json();

  return <ProductList products={products} />;
}
```

Dynamic:

```tsx
import { cookies } from "next/headers";

export default async function AccountPage() {
  const token = cookies().get("token")?.value;
  const user = await getUser(token);

  return <Account user={user} />;
}
```

Streaming:

```tsx
import { Suspense } from "react";

export default function Page() {
  return (
    <>
      <Hero />
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews />
      </Suspense>
    </>
  );
}
```

#### Частые ошибки

- Называть весь Next.js server render просто SSR и терять различия static/dynamic/ISR.
- Использовать cookies/headers в route, который должен оставаться static.
- Ожидать, что ISR мгновенно обновит все копии без продуманной invalidation.
- Ставить Suspense boundary слишком высоко и скрывать весь экран fallback-ом.
- Забывать, что Client Components после server render требуют hydration.

#### Связанные темы

- [[Конспект для подготовки/React/SSR и SSG]]
- [[Конспект для подготовки/React/Hydration]]
- [[Конспект для подготовки/React/Suspense и lazy]]
- [[Конспект для подготовки/Next.js/Data fetching cache revalidation]]
- [[Конспект для подготовки/Next.js/Deployment env Docker]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]

#### Источники

- [Next.js 14 docs: Server Components and rendering strategies](https://nextjs.org/docs/14/app/building-your-application/rendering/server-components)
- [Next.js 14 docs: Data Fetching, Caching, and Revalidating](https://nextjs.org/docs/14/app/building-your-application/data-fetching/fetching-caching-and-revalidating)
