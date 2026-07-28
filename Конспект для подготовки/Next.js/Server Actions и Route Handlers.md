---
aliases:
  - Next.js Server Actions
  - Next.js Route Handlers
  - use server
  - route.ts
---

#### Ответ на 60 секунд

Server Actions и Route Handlers решают разные задачи. Server Action - server function для мутаций, которую можно вызвать из формы или Client Component; она помечается `"use server"`, выполняется на сервере, может валидировать данные, проверять права, писать в базу, делать `revalidatePath`/`revalidateTag`, `redirect`, работать с cookies. В Next.js 14 Server Actions стали стабильной фичей.

Route Handler - HTTP endpoint в `app/**/route.ts`, построенный на Web `Request`/`Response`. Его используют для webhooks, public API, downloads, custom headers, CORS, proxy/BFF, health checks и интеграций, которым нужен настоящий HTTP interface. Если задача - mutation из UI формы, часто подходит Server Action. Если нужен endpoint для внешнего клиента или precise HTTP semantics, подходит Route Handler.

#### Ключевая схема

| Сценарий | Server Action | Route Handler |
| --- | --- | --- |
| Submit формы в UI | да | можно, но часто избыточно |
| Webhook от внешнего сервиса | нет | да |
| Public REST endpoint | нет | да |
| Mutation + revalidate | да | да |
| Cookies/redirect | да | да |
| CORS/custom HTTP methods | ограниченно | да |
| File download/stream | нет | да |
| Вызов из Server Component | через action/form | прямой server code обычно проще |

#### Развернутый ответ

Server Actions уменьшают расстояние между UI и server mutation. Вместо отдельного API route можно описать server function, передать её в `<form action={...}>` или вызвать из client logic. Action получает `FormData` или serializable аргументы, выполняется на сервере и возвращает serializable результат. Это удобно для CRUD-форм, настроек профиля, лайков, корзины, CMS-actions.

Безопасность Server Action не появляется автоматически. Action доступна как server endpoint, поэтому внутри всё равно нужны validation, authorization, rate limiting при необходимости и аккуратная работа с errors. Нельзя доверять client-side disabled-кнопкам, скрытым inputs или типам TypeScript. Типы помогают разработчику, но runtime-вход остаётся внешними данными.

После мутации часто нужно обновить cache. Если изменилась конкретная страница, используют `revalidatePath`. Если данные переиспользуются в разных местах, удобнее tag-based invalidation через `revalidateTag`. Если после записи пользователь должен уйти на другую страницу, можно вызвать `redirect`.

Route Handler нужен, когда важен HTTP layer. Он живёт в `app/api/.../route.ts` или другом route segment и экспортирует функции `GET`, `POST`, `PUT`, `DELETE` и т.д. Handler работает с `Request`, `NextRequest`, `Response`, `NextResponse`, headers, cookies, status codes, body, CORS. Для webhook чаще выбирают Route Handler, потому что внешний сервис не умеет вызывать Server Action как React-интеграцию.

Route Handlers и Server Actions не заменяют backend полностью. В production они могут быть BFF-слоем: проверка auth, нормализация API, сокрытие токенов, агрегация нескольких backend-запросов. Бизнес-критичную server logic выносят в отдельные service-функции и вызывают из action/handler, чтобы не дублировать правила.

После RSC security advisories Server Actions стоит воспринимать как полноценные server endpoints. Для Next.js 14.x важно держать patched framework version, а внутри actions всё равно проверять auth, authorization, schema validation, rate limiting для чувствительных операций и не хранить секреты в исходном коде функции.

#### Где применяется во frontend

| Ситуация | Что выбрать |
| --- | --- |
| Submit формы профиля | Server Action |
| Webhook от Stripe/CMS | Route Handler |
| Public REST endpoint для мобильного клиента | Route Handler |
| UI mutation + обновить кеш страницы | Server Action + `revalidatePath`/`revalidateTag` |
| Download/stream файла | Route Handler |
| Общая бизнес-логика | service function, вызываемая из action/handler |

> [!faq]+ Уточнения
> - Server Action в Next.js 14 стабильна, но входные данные всё равно валидируют на сервере.
> - Route Handler используют, когда нужен HTTP endpoint или интеграция с внешней системой.
> - `revalidatePath` обновляет path, `revalidateTag` обновляет данные по tag.
> - На одном route segment нельзя одновременно иметь `page.tsx` и `route.ts` для одного endpoint.
> - Server Action не подходит как публичный REST API для сторонних клиентов.
> - Server Action - это server boundary, поэтому TypeScript-типы не заменяют runtime validation.

#### Пример

Server Action:

```ts
// app/products/actions.ts
"use server";

import { revalidateTag } from "next/cache";
import { redirect } from "next/navigation";

export async function createProduct(formData: FormData) {
  const title = String(formData.get("title") ?? "").trim();

  if (!title) {
    return { error: "Title is required" };
  }

  await saveProduct({ title });
  revalidateTag("products");
  redirect("/products");
}
```

```tsx
// app/products/new/page.tsx
import { createProduct } from "../actions";

export default function NewProductPage() {
  return (
    <form action={createProduct}>
      <input name="title" required />
      <button type="submit">Create</button>
    </form>
  );
}
```

Route Handler:

```ts
// app/api/health/route.ts
import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({ ok: true });
}
```

#### Частые ошибки

- Выносить любую мутацию в Route Handler, хотя она вызывается только из формы.
- Делать Server Action без server-side validation и authorization.
- Возвращать из action неserializable значения.
- Забывать revalidation после записи и видеть старые данные.
- Использовать Server Action как public API contract для внешних клиентов.

#### Связанные темы

- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Next.js/Data fetching cache revalidation]]
- [[Конспект для подготовки/Next.js/App Router]]
- [[Конспект для подготовки/Web Basics/REST]]
- [[Конспект для подготовки/Web Basics/CORS]]
- [[Конспект для подготовки/Web Basics/OpenAPI и Swagger]]
- [[Конспект для подготовки/Security/Frontend threat model]]
- [[Конспект для подготовки/Security/Supply chain secrets и third-party scripts]]

#### Источники

- [Next.js blog: Server Actions stable in Next.js 14](https://nextjs.org/blog/next-14)
- [Next.js 14 docs: Server Actions and Mutations](https://nextjs.org/docs/14/app/building-your-application/data-fetching/server-actions-and-mutations)
- [Next.js 14 docs: Route Handlers](https://nextjs.org/docs/14/app/building-your-application/routing/route-handlers)
- [React RSC critical security advisory](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components)
