---
aliases:
  - React 18
  - React 19
  - React 19.2
  - Concurrent React
  - Actions
  - Server Components
  - Activity
  - useEffectEvent
---

#### Быстрый ответ

Базовая версия этого конспекта - React 18. React 19 и 19.2 ниже нужны для понимания различий и собеседований, но не выдаются за практический опыт проекта на React 18.

React 18 и React 19 важны не как набор случайных новых хуков, а как два этапа развития модели React. React 18 заложил фундамент concurrent rendering: React получил возможность готовить UI в фоне, прерывать несрочный render, батчить больше обновлений и глубже интегрировать Suspense со streaming SSR. Для разработчика это проявилось через `createRoot`, automatic batching, transitions, `useDeferredValue`, `useId`, `useSyncExternalStore` и новые server rendering APIs.

React 19 развивает этот фундамент в сторону продуктовых сценариев: формы, async mutations, optimistic UI, Server Components, Server Actions, metadata, стили и более понятные hydration errors. Главные темы React 19 - Actions, `useActionState`, `useOptimistic`, `useFormStatus`, `use`, `ref` как обычный prop, `<Context>` как provider и стабильная поверхность React Server Components для фреймворков.

React 19.2 добавляет уже не новый большой перелом, а точечные инструменты поверх React 19: `<Activity>` для скрытия/восстановления UI с сохранением state, `useEffectEvent` для событий внутри эффектов, `cacheSignal` для RSC-кэша, React Performance Tracks и Partial Pre-rendering. Связная картина такая: React 18 - приоритеты и interruptible render, React 19 - формы/RSC/full-stack API, React 19.2 - доводка производительности, эффектов и SSR.

#### Ключевая схема

| Версия | Главная идея | Что спрашивают |
| --- | --- | --- |
| React 18 | concurrent foundation | batching, transitions, Suspense SSR, `createRoot` |
| React 19 | app-level APIs поверх этого фундамента | Actions, forms, `use`, RSC, ref prop, hydration diagnostics |
| React 19.2 | точечные инструменты и DX | Activity, Effect Events, Performance Tracks, Partial Pre-rendering |
| React Compiler | build-time tooling, не runtime API | основной сценарий - React 19; React 17/18 возможны с настройкой |

```text
React 18
-> interruptible rendering model
-> urgent vs non-urgent updates
-> Suspense and streaming SSR foundation

React 19
-> async actions and forms
-> Server Components feature surface
-> better SSR/hydration/DX APIs

React 19.2
-> Activity for hidden UI state
-> useEffectEvent for event logic inside effects
-> SSR and performance tooling improvements
```

#### Развернутый ответ

Чтобы не смешивать версии, удобно разделять feature-релизы. React 18 - это переход к concurrent-фундаменту. React 19 - прикладные API для форм, async actions, optimistic UI, RSC и SSR/DX. React 19.2 добавляет Activity, Effect Events, `cacheSignal`, Performance Tracks и Partial Pre-rendering. Конкретные patch-релизы проверяют при обновлении зависимостей, но они не меняют теоретическое сравнение feature-версий.

Развернутый ответ строится не списком хуков, а причинно: React 18 изменил модель планирования работы, React 19 использовал этот фундамент для более цельных app-level сценариев, React 19.2 добавил инструменты для скрытого UI, эффектов, RSC-кэша и диагностики. Тогда понятно, почему `useTransition` относится к React 18, `useActionState` и `useOptimistic` - к React 19, а `<Activity>` и `useEffectEvent` - к React 19.2.

#### React 18

React 18 отвечает на проблему отзывчивости и SSR: как позволить React готовить большой UI, не блокируя срочные действия пользователя, и как отдавать серверный HTML частями. Поэтому главная тема версии - concurrent foundation, а не просто несколько новых хуков.

**Concurrent rendering**

Concurrent rendering - это внутренняя модель, в которой React может начать render, поставить его на паузу, продолжить позже или отбросить устаревшую работу. Это нужно, чтобы срочный UI, например ввод текста или клик, не блокировался тяжёлым несрочным render.

Важно: concurrency - не отдельная кнопка и не “React теперь всегда параллельный”. React 18 включает concurrent-поведение через новые root APIs и конкретные concurrent features, например transitions и Suspense.

**Automatic batching**

До React 18 batching в основном работал внутри React event handlers. В React 18 обновления батчатся шире: в promises, timers, native event handlers и других асинхронных источниках. Это уменьшает число лишних render.

**Transitions**

Transitions разделяют срочные и несрочные обновления. Ввод в input должен быть срочным, а пересчёт большого списка результатов можно пометить как transition через `startTransition` или `useTransition`.

**Suspense и streaming SSR**

React 18 расширил Suspense и добавил server APIs для streaming: `renderToPipeableStream` для Node.js и `renderToReadableStream` для Web Streams. Это позволяет серверу отдавать HTML частями и связывать SSR с Suspense boundaries.

**Новые APIs и hooks**

| API | Зачем нужен |
| --- | --- |
| `createRoot` | новый client root, нужен для возможностей React 18 |
| `hydrateRoot` | hydration для SSR-приложений |
| `useId` | стабильные id между сервером и клиентом |
| `useDeferredValue` | отложить несрочное обновление части UI |
| `useSyncExternalStore` | корректные подписки на external stores |
| `useInsertionEffect` | CSS-in-JS библиотеки, вставка стилей до layout effects |

#### React 19

React 19 переносит часть типовых продуктовых сценариев ближе к React API: формы, async mutations, optimistic UI, Server Components, Server Actions и SSR/DX. Это не “замена React 18”, а слой поверх concurrent-фундамента: React 18 дал модель планирования, React 19 добавил более прикладные API для full-stack React-приложений.

**Actions и формы**

Actions - это подход для async mutations с pending state, error handling и optimistic updates. React 19 добавил `useActionState`, `useOptimistic`, `useFormStatus` и поддержку функций в `action` / `formAction` у форм. Это особенно полезно для сценариев “отправить форму, показать pending, обработать ошибку, сбросить форму или обновить UI”.

**`use`**

`use` позволяет читать promise или context во время render в поддерживаемых сценариях. Если promise ещё не готов, компонент suspends и ближайший Suspense boundary показывает fallback. Это не замена произвольному `fetch` в любом компоненте: нужна архитектура, где данные кэшируются и интегрированы с Suspense/framework.

**Server Components и Server Actions**

React 19 включает стабильную поверхность React Server Components для фреймворков. Server Components выполняются в отдельной серверной среде до client bundle и помогают уменьшать количество JavaScript на клиенте. Server Actions позволяют клиентским компонентам вызывать async-функции на сервере через framework-интеграцию.

Ключевая ловушка: `"use server"` - это директива для Server Actions, а не метка Server Component. Server Components обычно определяются правилами framework.

**DOM и DX**

React 19 также добавил или улучшил:

- `ref` как prop для function components, без обязательного `forwardRef` в новых компонентах.
- `<Context>` как provider вместо `<Context.Provider>`.
- Более понятные hydration mismatch errors с diff.
- Нативную поддержку document metadata: `<title>`, `<meta>`, `<link>`.
- Управление stylesheet precedence.
- `react-dom/static` APIs для prerender/static generation.
- Лучшую поддержку Custom Elements.

#### React 19.2

React 19.2 уточняет уже существующую линию React 19: скрытые части UI, корректная логика внутри эффектов, диагностика производительности и новые SSR/prerender сценарии. Это точечный релиз, но он важен для вопросов про effects, сохранение state и profiling.

**`<Activity>`**

`<Activity>` позволяет скрывать часть UI, сохраняя её внутреннее состояние. В hidden mode React прячет children, очищает эффекты и откладывает обновления скрытой части на более низкий приоритет. Когда Activity снова становится visible, состояние возвращается, а эффекты создаются заново.

**`useEffectEvent`**

`useEffectEvent` отделяет event-логику внутри эффекта от реактивной синхронизации самого эффекта. Это помогает, когда обработчик должен видеть свежие props/state, но изменение этих значений не должно пересоздавать подписку или соединение.

**Performance Tracks**

React Performance Tracks добавляют в Chrome DevTools профили информацию о работе React Scheduler и Components. Это помогает видеть приоритеты, transitions, render/effect work и искать реальные узкие места вместо гадания.

**Partial Pre-rendering**

Partial Pre-rendering позволяет заранее отрендерить статическую часть приложения, отдать её с CDN, а динамическую часть дорендерить позже через resume APIs. Это тема скорее для framework/SSR-архитектуры; для ответа достаточно понимать идею: статический shell и динамическое продолжение render могут разделяться.

#### React Compiler

React Compiler не привязывают как обычную runtime-фичу React 18/19. Это build-time инструмент, который автоматически мемоизирует компоненты и значения при соблюдении правил React. По официальной документации основной сценарий для него - React 19, при этом React 17 и 18 поддерживаются через дополнительную настройку. Поэтому его относят к современному React tooling, а не к хукам конкретной версии.

#### Пример

React 18: срочное обновление input и несрочное обновление результатов.

```tsx
import { startTransition, useState, type ChangeEvent } from "react";

function HeavyResults({ query }: { query: string }) {
  return <p>Результаты для: {query}</p>;
}

function Search() {
  const [input, setInput] = useState("");
  const [query, setQuery] = useState("");

  function onChange(event: ChangeEvent<HTMLInputElement>) {
    const nextValue = event.target.value;

    setInput(nextValue);

    startTransition(() => {
      setQuery(nextValue);
    });
  }

  return (
    <>
      <input value={input} onChange={onChange} />
      <HeavyResults query={query} />
    </>
  );
}
```

React 19: form Action через `useActionState`.

```tsx
import { useActionState } from "react";

async function updateName(_previousError: string | null, formData: FormData) {
  const name = String(formData.get("name") ?? "");
  const response = await fetch("/api/profile/name", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });

  return response.ok ? null : "Не удалось сохранить имя";
}

function ChangeNameForm() {
  const [error, submitAction, isPending] = useActionState(updateName, null);

  return (
    <form action={submitAction}>
      <input name="name" />
      <button disabled={isPending}>Сохранить</button>
      {error && <p>{error}</p>}
    </form>
  );
}
```

#### Ключевые уточнения

- React 18 прежде всего меняет модель планирования работы: automatic batching, transitions, interruptible rendering для concurrent-обновлений и streaming SSR.
- Concurrent rendering выполняется в том же JavaScript-потоке, но React может разбивать, приостанавливать и отбрасывать несрочную render-работу.
- Состояние управляемого input обновляется срочно; transition используют для зависимой тяжёлой части интерфейса.
- `use` читает поддерживаемый ресурс во время render и работает вместе с Suspense; это не универсальная замена всем способам загрузки данных.
- `"use server"` помечает Server Function/Action. Границу Server Component определяет framework.
- RSC требует framework-интеграции, которая управляет server/client module graph, транспортом и кэшем.
- В hidden-режиме `<Activity>` сохраняет state, но очищает Effects; при возвращении эффекты создаются заново.
- `useEffectEvent` отделяет нереактивную event-логику эффекта, но не скрывает действительно реактивные зависимости.
- React Compiler 1.0 является отдельным build-time инструментом; для React 18 ему нужны `target: "18"` и `react-compiler-runtime`.
- Переход на React 19 начинают с проверки React 18.3, нового JSX transform, warnings и официального upgrade guide.

#### Связанные темы

- [[Конспект для подготовки/React/Fiber]]
- [[Конспект для подготовки/React/Как работает React]]
- [[Конспект для подготовки/React/Server Components]]
- [[Конспект для подготовки/React/React Compiler]]
- [[Конспект для подготовки/React/useEffectEvent]]
- [[Конспект для подготовки/React/Activity]]
- [[Конспект для подготовки/React/Hydration]]
- [[Конспект для подготовки/React/Suspense и lazy]]
- [[Конспект для подготовки/React/useTransition и useDeferredValue]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/React/Controlled и uncontrolled компоненты]]

#### Источники

- [React v18.0](https://react.dev/blog/2022/03/29/react-v18)
- [React v19](https://react.dev/blog/2024/12/05/react-19)
- [React 19.2](https://react.dev/blog/2025/10/01/react-19-2)
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [React 18: Render and Commit](https://18.react.dev/learn/render-and-commit)
- [React docs: React Compiler Installation](https://react.dev/learn/react-compiler/installation)
