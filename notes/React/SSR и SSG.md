# SSR и SSG

<!-- NOTE-NAV-TOP:START -->
[← Zustand](<./Zustand.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Hydration →](<./Hydration.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

SSR (server-side rendering, серверный рендеринг) создаёт HTML на сервере во время запроса или при промахе серверного кэша. Он подходит для персонализированных страниц и данных, которые должны быть свежими в момент ответа. Цена - вычисления на сервере, сложное кэширование и риск увеличения TTFB.

SSG (static site generation, статическая генерация) создаёт HTML заранее во время сборки. Результат можно раздавать через CDN, поэтому стабильные страницы открываются быстро и почти не нагружают application server. Ограничение - данные остаются прежними до следующей сборки или revalidation.

ISR (incremental static regeneration, инкрементальная статическая регенерация) обновляет статическую страницу после публикации по времени или событию. Это framework-возможность, например Next.js, а не API React. В реальном приложении SSR, SSG, ISR, client-side fetching и Server Components часто сочетаются на разных маршрутах и даже на одной странице.

## Ключевая схема

| Подход | Когда создаётся HTML | Где полезен | Основный компромисс |
| --- | --- | --- | --- |
| SSR | при запросе или cache miss | персональные и свежие данные | server cost и TTFB |
| SSG | во время build | документация, лендинги, стабильный каталог | устаревание до новой сборки |
| ISR | статически, затем по правилу revalidation | большой каталог, контент с допустимой задержкой | сложность свежести и invalidation |
| CSR | UI достраивается в браузере | приватные интерактивные части | больше client JS и более поздний контент |

```text
request
├─ SSR: server render now -> HTML
├─ SSG: read prebuilt HTML -> CDN response
└─ ISR: read cached HTML -> revalidate by framework policy

HTML in browser
-> load JavaScript for Client Components
-> hydrate interactive parts
```

## Развернутый ответ

**SSR**

При SSR сервер получает запрос, загружает нужные данные и формирует HTML. Сервер может учитывать cookies, authentication, headers и актуальные данные. Поэтому SSR подходит для личного кабинета, страницы заказа или контента, который зависит от прав пользователя.

SSR не означает, что ответ нельзя кэшировать. Публичный HTML можно хранить в CDN или server cache, а персональный ответ обычно требует private cache либо полного отказа от общего кэша. Реальная модель часто звучит точнее: «dynamic render на запрос или render при cache miss».

**SSG**

При SSG список маршрутов и данные известны во время build. Сгенерированные HTML-файлы размещаются на CDN. Время ответа не зависит от выполнения React на application server, но стоимость переносится в build и публикацию.

SSG хуже подходит для огромного числа редко посещаемых страниц и для персональных данных. Долгая полная пересборка тоже становится архитектурным ограничением.

**ISR**

ISR сохраняет преимущества статической страницы, но позволяет framework обновлять её после deploy. Revalidation может быть основана на времени или событии: например, CMS отправляет webhook после публикации.

Нужно определить, сколько времени допустим устаревший ответ, кто инициирует invalidation и что получит пользователь во время регенерации. Без такой политики «ISR каждые 60 секунд» не гарантирует, что каждый посетитель сразу увидит свежие данные.

**Что происходит после получения HTML**

В классическом React SSR HTML ещё не делает приложение интерактивным. Браузер загружает JavaScript, а React выполняет hydration. Поэтому SSR может улучшить время появления контента и индексируемость, но тяжёлый client bundle по-прежнему ухудшает INP и момент готовности интерфейса к действиям.

В приложении с React Server Components код Server Components не гидратируется. JavaScript и hydration нужны только Client Components. RSC и SSR не являются альтернативами: RSC управляет границей выполнения компонентов, а SSR - созданием HTML.

**Как выбирать подход**

Сначала определяют требования к данным:

1. Зависит ли ответ от конкретного пользователя?
2. Насколько свежими должны быть данные?
3. Можно ли безопасно кэшировать HTML?
4. Сколько маршрутов нужно подготовить?
5. Нужен ли контент поисковому роботу в первом HTML?
6. Сколько клиентского JavaScript потребуется для интерактивности?

Затем выбирают стратегию для маршрута или отдельного сегмента. Универсально «лучшего» способа нет.

## Примеры применения

| Сценарий | Возможная стратегия | Почему |
| --- | --- | --- |
| документация | SSG | содержимое меняется вместе с публикацией |
| блог или новости | SSG + on-demand ISR | CDN и обновление после события CMS |
| публичный каталог | ISR | SEO и допустимая задержка обновления |
| карточка товара с остатками | статическая оболочка + свежий server/client запрос | описание кэшируется дольше, остаток меняется часто |
| личный кабинет | dynamic SSR/RSC | данные зависят от пользователя и прав |
| редактор | SSR shell + Client Component | первый HTML полезен, основная работа интерактивна |

## Пример для Next.js 14 App Router

Динамический render: запрос данных не кэшируется.

```tsx
export default async function OrdersPage() {
  const response = await fetch("https://api.example.com/orders", {
    cache: "no-store",
  });
  const orders: Array<{ id: string; total: number }> = await response.json();

  return (
    <ul>
      {orders.map((order) => (
        <li key={order.id}>
          Заказ {order.id}: {order.total} ₽
        </li>
      ))}
    </ul>
  );
}
```

Статическая страница с revalidation не чаще одного раза в час:

```tsx
export const revalidate = 3600;

export default async function PostsPage() {
  const response = await fetch("https://api.example.com/posts");
  const posts: Array<{ slug: string; title: string }> =
    await response.json();

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.slug}>{post.title}</li>
      ))}
    </ul>
  );
}
```

Это примеры Next.js, а не чистого React API. Конкретное поведение зависит от версии Next.js, cache options и route segment configuration.

## Влияние на performance

- SSR/SSG могут улучшить FCP и LCP, потому что браузер раньше получает содержательный HTML.
- SSR может увеличить TTFB, если данные и render медленные.
- SSG и ISR хорошо сочетаются с CDN, но требуют политики обновления.
- Большой client bundle и тяжёлая hydration могут свести на нет выигрыш первого HTML.
- Streaming позволяет начать отправку ответа до готовности всего дерева.
- SEO зависит не только от способа render, но и от метаданных, HTTP-статуса, canonical URL и доступности контента.

## Ключевые уточнения

- SSR создаёт HTML динамически, а SSG создаёт его заранее; различие находится во времени рендеринга и политике свежести.
- ISR является механизмом framework для обновления статического результата после deploy.
- SSR-ответ можно кэшировать, если ключ кэша учитывает персонализацию и права доступа.
- SSG подходит только тогда, когда допустимо показывать один и тот же заранее подготовленный результат.
- Hydration требуется интерактивным Client Components, даже если их HTML пришёл с сервера.
- RSC, SSR и SSG могут работать вместе и отвечают за разные части архитектуры.
- Выбор стратегии проверяют измерениями TTFB, LCP, INP, cache hit rate и стоимостью сервера.

## Связанные темы

- [Hydration](<./Hydration.md>)
- [Server Components](<./Server Components.md>)
- [Suspense и lazy](<./Suspense и lazy.md>)
- [SSR SSG ISR Streaming](<../Next.js/SSR SSG ISR Streaming.md>)
- [Data fetching cache revalidation](<../Next.js/Data fetching cache revalidation.md>)
- [Core Web Vitals](<../Web Basics/Core Web Vitals.md>)
- [HTTP caching](<../Web Basics/HTTP caching.md>)

## Источники

- [React 18 docs: Server APIs](https://18.react.dev/reference/react-dom/server)
- [React 18 docs: `hydrateRoot`](https://18.react.dev/reference/react-dom/client/hydrateRoot)
- [Next.js 14 docs: Static and Dynamic Rendering](https://nextjs.org/docs/14/app/building-your-application/rendering/server-components#static-rendering-default)
- [Next.js 14 docs: Data Fetching, Caching, and Revalidating](https://nextjs.org/docs/14/app/building-your-application/data-fetching/fetching-caching-and-revalidating)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Zustand](<./Zustand.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Hydration →](<./Hydration.md>)
<!-- NOTE-NAV-BOTTOM:END -->
