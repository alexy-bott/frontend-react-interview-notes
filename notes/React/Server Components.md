# Server Components

<!-- NOTE-NAV-TOP:START -->
[← React 18 и 19](<./React 18 и 19.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [React Compiler →](<./React Compiler.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

React Server Components (RSC, серверные компоненты React) выполняются в серверной среде и не отправляют собственный JavaScript-код в браузер. Они могут читать данные рядом с сервером, использовать серверные зависимости и передавать готовый результат в интерактивные Client Components. За счёт этого часть интерфейса не увеличивает client bundle.

Server Component не может использовать `useState`, `useEffect`, обработчики браузерных событий и DOM API. Интерактивную часть выносят в Client Component, а файл, который образует вход в клиентский module graph, помечают директивой `"use client"`.

RSC и SSR решают разные задачи. RSC определяет, где выполняется компонент и попадёт ли его код в браузер. SSR формирует HTML первого ответа. В Next.js эти механизмы работают вместе: Server Components создают серверное представление дерева, Client Components могут участвовать в первоначальном HTML, а затем гидратируются в браузере.

Версионная граница важна. Стабильная публичная поверхность RSC появилась в React 19. Next.js 14 использовал RSC в App Router и с React 18 благодаря framework-интеграции и совместимым canary-версиям React. Поэтому опыт с Next.js 14 корректно описывать как опыт RSC во framework, а не как самостоятельный React 18 API.

## Ключевая схема

| Понятие | Роль |
| --- | --- |
| Server Component | выполняется на сервере или во время сборки; его код не входит в client bundle |
| Client Component | может использовать state, Effects, event handlers и browser APIs; его код отправляется клиенту |
| `"use client"` | отмечает границу входа в клиентский module graph |
| `"use server"` | отмечает Server Function/Action, а не Server Component |
| RSC payload | сериализованное описание результата Server Components и ссылок на Client Components |
| SSR | превращает React-дерево в HTML для первого ответа |
| hydration | подключает React к HTML клиентских частей и делает их интерактивными |

```text
Server Components
-> получают данные и формируют серверную часть дерева
-> framework создаёт RSC payload
-> SSR может превратить результат в HTML
-> браузер показывает HTML
-> JavaScript Client Components загружается и гидратируется
```

## Развернутый ответ

**Зачем нужны Server Components**

В обычном client-side React импортированный компонент и его зависимости попадают в JavaScript bundle, даже если компонент только читает данные и выводит разметку. Server Component выполняет эту работу вне браузера. Например, он может обратиться к базе данных через серверный слой, отформатировать результат и передать клиенту только представление и необходимые данные.

Это уменьшает объём клиентского JavaScript, но не делает запросы и render бесплатными. Нужно по-прежнему учитывать задержку сервера, кэширование, streaming, повторные запросы и размер данных в RSC payload.

**Граница между Server и Client Components**

В среде с RSC компоненты по умолчанию могут быть серверными по правилам framework. Директива `"use client"` в начале файла создаёт клиентскую границу. Сам файл, его импорты и дальнейшие клиентские зависимости входят в client bundle.

Директиву не требуется повторять в каждом дочернем файле. Её ставят в тех модулях, которые должны быть импортированы из серверного дерева как клиентские точки входа. Чем выше расположена граница, тем больше кода может случайно перейти в клиентский module graph.

Server Component может передать подготовленную серверную разметку в `children` Client Component. Это позволяет оставить содержимое серверным, а клиентский компонент использовать как небольшую интерактивную оболочку.

**Что можно передавать через границу**

Props Client Component должны поддерживаться протоколом сериализации React. Простые строки, числа, массивы и обычные объекты подходят. Нельзя передать произвольное замыкание, подключение к базе данных или экземпляр класса и ожидать, что он продолжит работать в браузере.

Функции являются отдельным случаем: Server Function можно передать через специальный framework-механизм, но это не обычная JavaScript-функция, сериализованная в JSON.

**Чем RSC отличается от SSR**

SSR отвечает на вопрос: «Где и когда был создан первоначальный HTML?». После обычного SSR код клиентских компонентов всё равно загружается в браузер и гидратируется.

RSC отвечает на другой вопрос: «Какая часть компонентного дерева вообще должна выполняться в браузере?». Код Server Component не гидратируется, потому что его нет в client bundle. При этом Client Component в Next.js может быть предварительно отрендерен на сервере в HTML, а затем гидратирован. Название Client Component не означает, что первоначальный HTML обязательно создаётся только в браузере.

**Когда выполняются Server Components**

Конкретный момент определяет framework. Компонент может выполниться во время сборки, при запросе, при промахе кэша или после revalidation. Поэтому фраза «Server Component всегда выполняется на каждый запрос» неверна: это зависит от политики рендеринга и кэширования маршрута.

**Server Functions и `"use server"`**

`"use server"` помечает функцию, которую framework может выполнить на сервере. В Next.js такие функции часто называют Server Actions, когда они используются для mutations и форм.

Server Function следует рассматривать как публичную серверную точку входа. Она обязана заново проверять authentication, authorization и входные данные. То, что кнопку вызова не видно пользователю, не является проверкой доступа.

## Пример для Next.js 14 App Router

```tsx
// app/products/page.tsx
import { db } from "@/server/db";
import { AddToCartButton } from "./AddToCartButton";

export default async function ProductsPage() {
  const products = await db.product.findMany({
    select: { id: true, title: true, price: true },
  });

  return (
    <ul>
      {products.map((product) => (
        <li key={product.id}>
          <h2>{product.title}</h2>
          <p>{product.price} ₽</p>
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

export function AddToCartButton({ productId }: { productId: string }) {
  const [isAdded, setIsAdded] = useState(false);

  return (
    <button type="button" onClick={() => setIsAdded(true)}>
      {isAdded ? "Добавлено" : "Добавить"} {productId}
    </button>
  );
}
```

`ProductsPage` читает данные в серверной среде, а модуль с `db` не попадает в браузер. `AddToCartButton` получает только сериализуемый `productId`, загружается как клиентский код и отвечает за локальное состояние и клик.

## Ключевые уточнения

- RSC определяет место выполнения компонента и состав client bundle; SSR определяет создание первоначального HTML.
- Код Server Component не отправляется в браузер и не гидратируется.
- Client Component может участвовать в SSR, но его JavaScript затем загружается и гидратируется.
- `"use client"` создаёт клиентскую границу для модуля и его клиентского графа импортов.
- `"use server"` относится к Server Functions/Actions, а не объявляет Server Component.
- Через server/client boundary передают значения, поддерживаемые сериализацией React, а не произвольные runtime-объекты.
- Server Components получают доступ к данным только с соблюдением тех же правил безопасности, что и другой backend-код.
- В Next.js 14 RSC были возможностью App Router поверх framework-managed React; стабильный React API RSC относится к React 19.

## Связанные темы

- [React 18 и 19](<./React 18 и 19.md>)
- [SSR и SSG](<./SSR и SSG.md>)
- [Hydration](<./Hydration.md>)
- [Suspense и lazy](<./Suspense и lazy.md>)
- [Server и Client Components](<../Next.js/Server и Client Components.md>)
- [Server Actions и Route Handlers](<../Next.js/Server Actions и Route Handlers.md>)
- [Data fetching cache revalidation](<../Next.js/Data fetching cache revalidation.md>)

## Источники

- [React docs: Server Components](https://react.dev/reference/rsc/server-components)
- [React docs: `use client`](https://react.dev/reference/rsc/use-client)
- [React docs: `use server`](https://react.dev/reference/rsc/use-server)
- [React 19: React Server Components](https://react.dev/blog/2024/12/05/react-19)
- [Next.js 14 docs: Server and Client Components](https://nextjs.org/docs/14/app/building-your-application/rendering/composition-patterns)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← React 18 и 19](<./React 18 и 19.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [React Compiler →](<./React Compiler.md>)
<!-- NOTE-NAV-BOTTOM:END -->
