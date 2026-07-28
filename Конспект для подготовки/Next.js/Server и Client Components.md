---
aliases:
  - Next.js Server Components
  - Next.js Client Components
  - use client
  - RSC в Next.js
---

#### Ответ на 60 секунд

В App Router компоненты по умолчанию являются Server Components. Они выполняются на сервере, могут читать данные рядом с источником, обращаться к секретам, не добавлять свой код в клиентский bundle и отдавать результат как часть HTML/RSC Payload. Client Components нужны для интерактивности: state, effects, event handlers, browser APIs, кастомные hooks, работа с `window`, `localStorage`, DOM-событиями.

Граница задаётся директивой `"use client"` в начале файла. Эта директива создаёт client boundary: сам файл, его imports и компоненты, которые он напрямую рендерит, попадают в client module graph. Поэтому `"use client"` ставят как можно ближе к интерактивному UI, а не на весь layout. Props из Server Component в Client Component должны быть serializable.

#### Ключевая схема

| Вопрос | Server Component | Client Component |
| --- | --- | --- |
| Где выполняется | сервер | браузер после hydration |
| `useState` / events | нет | да |
| `useEffect` | нет | да |
| Browser APIs | нет | да |
| DB/API secrets | да | нет |
| Client bundle | не добавляет свой JS | добавляет JS |
| Props | может передать serializable данные | получает serializable props |
| Основная роль | данные, shell, HTML, меньше JS | интерактивность |

#### Развернутый ответ

Server Components решают две задачи: переносят часть работы на сервер и уменьшают клиентский JavaScript. Компонент может быть `async`, получить данные из API/DB/CMS, собрать UI и отправить результат без отправки собственного component code в браузер. Это снижает bundle size и защищает server-only логику: токены, private env, прямые запросы к базе, filesystem.

Client Components нужны там, где UI должен реагировать в браузере: клик, ввод, состояние, эффекты, drag and drop, media query, `localStorage`, focus management, Radix UI components, React Hook Form. Они всё равно могут быть предварительно отрендерены в HTML на сервере для initial preview, но их JavaScript должен загрузиться и пройти hydration, чтобы UI стал интерактивным.

`"use client"` не означает “этот компонент никогда не рендерится на сервере”. Она означает “это entrypoint в client module graph”. Next.js может использовать Client Component для prerendered HTML, но весь код этого client graph должен быть безопасен для браузера и попадёт в bundle. Поэтому случайный import server-only модуля в client graph создаёт ошибку или утечку.

Server Component может рендерить Client Component и передать ему props. Но эти props должны быть serializable: строки, числа, boolean, arrays, objects без функций, class instances и нестандартных runtime-сущностей. Если клиенту нужен callback на сервер, используют Server Action, а не передачу функции как обычного prop.

Composition часто выглядит так: server page получает данные и рисует статическую часть, а внутрь вставляет маленький client island для интерактивности. Providers обычно являются Client Components, но их размещают как можно ниже, чтобы не превращать весь application shell в client subtree.

#### Где применяется во frontend

| Ситуация | Component type |
| --- | --- |
| Page читает товары из DB/API | Server Component |
| Кнопка “Add to cart” с local pending | Client Component |
| Radix Dialog/Select | Client Component |
| Layout с server data и статичным shell | Server Component |
| Theme/Auth provider с hooks | Client Component, размещённый как можно ниже |
| Передача server data в UI island | Server -> Client через serializable props |

> [!faq]+ Уточнения
> - Server Component не может использовать `useState`, `useEffect`, event handlers и browser APIs.
> - Client Component не должен получать секреты и server-only объекты.
> - `"use client"` распространяется на module graph файла, поэтому влияет на размер bundle.
> - Props из server в client должны быть serializable.
> - Server Components и SSR не одно и то же: RSC описывает component model, SSR - генерацию HTML.

#### Пример

```tsx
// app/products/page.tsx
import AddToCartButton from "./AddToCartButton";

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <ul>
      {products.map(product => (
        <li key={product.id}>
          <h2>{product.title}</h2>
          <AddToCartButton productId={product.id} />
        </li>
      ))}
    </ul>
  );
}
```

```tsx
// app/products/AddToCartButton.tsx
"use client";

import { useState } from "react";

export default function AddToCartButton({ productId }: { productId: string }) {
  const [pending, setPending] = useState(false);

  return (
    <button disabled={pending} onClick={() => setPending(true)}>
      Add to cart
    </button>
  );
}
```

#### Частые ошибки

- Ставить `"use client"` на `app/layout.tsx` из-за одного dropdown.
- Импортировать server-only код в Client Component.
- Передавать функции, class instances, `Date`, `Map` или неserializable объекты в props без явного преобразования.
- Думать, что Server Component автоматически делает страницу статической.
- Использовать Client Component для data fetching, который можно выполнить на сервере.

#### Связанные темы

- [[Конспект для подготовки/React/Server Components]]
- [[Конспект для подготовки/React/Hydration]]
- [[Конспект для подготовки/React/Radix UI]]
- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Next.js/App Router]]
- [[Конспект для подготовки/Next.js/Data fetching cache revalidation]]

#### Источники

- [Next.js 14 docs: Server Components](https://nextjs.org/docs/14/app/building-your-application/rendering/server-components)
- [Next.js docs: Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components)
