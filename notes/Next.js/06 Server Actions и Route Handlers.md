# Server Actions и Route Handlers

<!-- NOTE-NAV-TOP:START -->
[← Получение данных, кеш и ревалидация](<./05 Получение данных, кеш и ревалидация.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Деплой, переменные окружения и Docker →](<./07 Деплой, переменные окружения и Docker.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Server Action — server function, интегрированная с React/Next.js mutation flow. Её можно передать в `<form action>` или вызвать из Client Component; framework создаёт network request, выполняет function на server и возвращает обновлённый UI/result. Route Handler — явный HTTP endpoint в `app/**/route.ts` на Web `Request`/`Response` API.

Server Action подходит для мутации, принадлежащей Next.js UI: form submit, validation, authorization, запись и revalidation. Route Handler выбирают, когда нужен самостоятельный HTTP contract: webhook, public API, download/stream, CORS, health check или endpoint для другого клиента. Оба являются server entry points и должны проверять authentication, authorization и runtime input.

## Ключевая схема

| Сценарий | Server Action | Route Handler |
| --- | --- | --- |
| Submit формы в UI | да | можно, но часто избыточно |
| Webhook от внешнего сервиса | нет | да |
| Public REST endpoint | нет | да |
| Mutation + revalidate | да | да |
| Cookies/redirect | да | да |
| CORS/status/HTTP methods | не основной interface | да |
| File download/stream | нет | да |
| Вызов из Server Component | через action/form | прямой server code обычно проще |

## Базовая модель

Server Actions уменьшают расстояние между UI и server mutation. Вместо отдельного API route можно описать server function, передать её в `<form action={...}>` или вызвать из client logic. Action получает `FormData` или serializable аргументы, выполняется на сервере и возвращает serializable результат. Это удобно для CRUD-форм, настроек профиля, лайков, корзины, CMS-actions.

Route Handler экспортирует functions по HTTP method: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`. Он не участвует в layouts и client navigation как `page.tsx`. В Next.js 14 `GET`, возвращающий обычный `Response`, может кешироваться по default; request object, dynamic APIs или route config позволяют выбрать dynamic behavior.

## Развернутый ответ

**Security.** Server Action доступна через generated endpoint, даже если UI временно не показывает кнопку. Внутри каждый вызов заново проверяет session и право на конкретный resource, затем валидирует данные schema-validator. TypeScript types, hidden inputs и client-side validation не являются security checks. Для дорогих/чувствительных operations добавляют rate limiting, idempotency или audit trail по требованиям системы.

**UI flow.** Native form способен вызвать action без собственного `onSubmit`; это поддерживает progressive enhancement. Client Component может показывать pending через `useFormStatus` и отображать validation result через action state. После записи инвалидируют data tag/path, затем при необходимости вызывают `redirect`. `redirect` управляет control flow через исключение Next.js, поэтому его не помещают внутрь `try/catch`, который должен обработать только ожидаемую ошибку записи.

**HTTP flow.** Route Handler явно управляет method, status, headers и body. Webhook обычно требует прочитать raw body и проверить provider signature до parsing/processing. Public endpoint нуждается в versioned contract, CORS policy и rate limits. Ошибка Route Handler возвращается как HTTP response и не попадает автоматически в ближайший `error.tsx` page.

**Shared logic.** Actions и handlers являются adapters. Authentication, schema validation и business operation удобно вынести в server-only service и вызывать из обоих entry points. Server Component не должен делать HTTP request к собственному Route Handler только ради повторного использования: прямой вызов service function короче, быстрее и сохраняет types.

**Version boundary.** Server Actions стали stable в Next.js 14, но детали transport и security patches принадлежат framework implementation. Для линии 14.x используют patched release `14.2.35`; обновление framework не отменяет application-level authorization.

## Где применяется во frontend

| Ситуация | Что выбрать |
| --- | --- |
| Submit формы профиля | Server Action |
| Webhook от Stripe/CMS | Route Handler |
| Public REST endpoint для мобильного клиента | Route Handler |
| UI mutation + обновить кеш страницы | Server Action + `revalidatePath`/`revalidateTag` |
| Download/stream файла | Route Handler |
| Общая бизнес-логика | service function, вызываемая из action/handler |

## Пример

Server Action:

```ts
// app/products/actions.ts
"use server";

import { revalidateTag } from "next/cache";
import { redirect } from "next/navigation";

export async function createProduct(formData: FormData) {
  const user = await requireUser();
  const title = String(formData.get("title") ?? "").trim();

  if (!title) {
    return { error: "Title is required" };
  }

  await saveProduct({ title, authorId: user.id });
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

## Ключевые уточнения

- Server Action — UI-oriented server reference; Route Handler — явный HTTP contract.
- Оба entry points принимают недоверенный input и выполняют authorization для каждого вызова.
- Server Action может работать с progressive form, pending/result state и cache revalidation без отдельного client API layer.
- Route Handler выбирают для external clients, webhooks, streams и точного управления HTTP semantics.
- Server-side code переиспользует service function напрямую, а не обращается к собственному Route Handler по HTTP.
- `revalidateTag` обновляет связанные data entries, `revalidatePath` — route path/layout; выбор следует фактической dependency.
- `redirect` завершается специальным control-flow exception, поэтому его вызывают после ожидаемо обрабатываемого участка.
- `page.tsx` и `route.ts` не могут занимать один и тот же route segment.

## Связанные темы

- [React Hook Form](<../Формы/03 React Hook Form.md>)
- [Получение данных, кеш и ревалидация](<./05 Получение данных, кеш и ревалидация.md>)
- [App Router](<./02 App Router.md>)
- [REST](<../Основы веб-платформы/07 REST.md>)
- [CORS](<../Основы веб-платформы/13 CORS.md>)
- [OpenAPI и Swagger](<../Основы веб-платформы/09 OpenAPI и Swagger.md>)
- [Модель угроз фронтенда](<../Безопасность/01 Модель угроз фронтенда.md>)
- [Цепочка поставок, секреты и сторонние скрипты](<../Безопасность/04 Цепочка поставок, секреты и сторонние скрипты.md>)

## Источники

- [Next.js blog: Server Actions stable in Next.js 14](https://nextjs.org/blog/next-14)
- [Next.js 14 docs: Server Actions and Mutations](https://nextjs.org/docs/14/app/building-your-application/data-fetching/server-actions-and-mutations)
- [Next.js 14 docs: Route Handlers](https://nextjs.org/docs/14/app/building-your-application/routing/route-handlers)
- [React RSC critical security advisory](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Получение данных, кеш и ревалидация](<./05 Получение данных, кеш и ревалидация.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Деплой, переменные окружения и Docker →](<./07 Деплой, переменные окружения и Docker.md>)
<!-- NOTE-NAV-BOTTOM:END -->
