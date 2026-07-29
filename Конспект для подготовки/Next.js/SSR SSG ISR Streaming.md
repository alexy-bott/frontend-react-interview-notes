---
aliases:
  - Next.js SSR
  - Next.js SSG
  - Next.js ISR
  - Next.js streaming
  - static dynamic rendering Next.js
---

#### Быстрый ответ

В Next.js 14 route может быть statically rendered и сохранён в Full Route Cache либо dynamically rendered для каждого request. ISR — это обновление static result по времени или событию без полной пересборки приложения. Streaming — способ отправлять HTML/RSC chunks по мере готовности Suspense boundaries; он не является отдельным источником данных или режимом cache.

SSR в разговорной формулировке обычно означает “HTML создаётся на сервере”, но в Next.js 14 важно уточнять модель: страница может быть полностью static, dynamic per request, static с revalidation или streamed через Suspense. После server render клиентские части всё равно проходят hydration.

#### Ключевая схема

| Модель | Когда рендерится | Когда подходит |
| --- | --- | --- |
| Static rendering | build time или при заполнении/обновлении Full Route Cache | публичные страницы, каталоги, блог, документация |
| Dynamic rendering | на каждый request | auth, cookies, user-specific данные, request-time logic |
| ISR | static + обновление по TTL/tag/path | данные меняются, но не требуют fresh response на каждый request |
| Streaming | chunks по мере готовности | медленные части UI, большие страницы, Suspense |
| CSR внутри Next | в Client Components после hydration | highly interactive widgets, browser-only state |

#### Базовая модель

Static rendering в App Router возможен, когда результат не зависит от конкретного incoming request. Next.js сохраняет HTML и RSC Payload в Full Route Cache и переиспользует их между пользователями. Static здесь означает cacheable route output, а не «данные никогда не изменяются»: result может обновляться через revalidation или новый deploy.

Dynamic rendering выполняет route на каждый request, потому что результат зависит от cookies, headers, search params, uncached data либо явного `dynamic = "force-dynamic"`. Dynamic route не хранится в Full Route Cache, но отдельные `fetch(..., { cache: "force-cache" })` всё ещё могут использовать Data Cache. Это позволяет сочетать personalized shell с общими cached data.

#### Развернутый ответ

ISR — lifecycle statically rendered route. При time-based revalidation истечение interval само по себе не запускает timer-job: следующий request может получить stale result и инициировать regeneration; после успешного render cache заменяется. Если regeneration завершилась ошибкой, Next.js продолжает отдавать последнюю успешную версию и повторяет попытку позже. On-demand revalidation очищает entries по path/tag после мутации или webhook.

Streaming решает ожидание «всё или ничего» внутри одного server render. `loading.tsx` создаёт Suspense boundary для route segment, а явный `<Suspense>` отделяет конкретную медленную часть. Server отправляет shell/fallback раньше и продолжает stream готовых chunks. Польза зависит от boundary: если вся page скрыта одним fallback или медленная операция выполняется до boundary, раннего meaningful content не получится.

Термины SSG и SSR пришли из Pages Router и остаются полезными: SSG близок к static rendering, SSR — к dynamic request rendering. Но App Router точнее разделяет время server render, caching route output и streaming. Все модели могут содержать Client Components: Server Components не требуют своего client JS, а Client Components должны загрузиться и гидратироваться.

#### Где применяется во frontend

| Страница/фича | Rendering choice |
| --- | --- |
| Публичный лендинг | static rendering |
| Блог/CMS | ISR/time-based или on-demand revalidation |
| Account page | dynamic rendering |
| Dashboard с медленными виджетами | streaming + Suspense boundaries |
| Product catalog | static/ISR + dynamic filters при необходимости |
| Browser-only editor | Client Component внутри server-rendered shell |

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

#### Ключевые уточнения

- Static/dynamic описывает переиспользование route output; cached/uncached отдельно описывает каждый data request.
- Dynamic route способен читать cached shared data, хотя его HTML/RSC Payload создаются для каждого request.
- `revalidate` задаёт допустимую stale duration и обновление по обращению, а не cron с гарантированным моментом запуска.
- ISR не подходит для строго свежих персональных данных: cached output может временно быть stale и переиспользуется между users.
- Streaming определяет порядок доставки частей render, но не делает медленный backend быстрее.
- Suspense boundary ставят вокруг независимой медленной части, сохраняя стабильный layout и meaningful fallback.
- Static export — отдельный deployment mode без server runtime; он не равен обычному static rendering внутри работающего Next.js server.

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
