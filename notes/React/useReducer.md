# useReducer

<!-- NOTE-NAV-TOP:START -->
[← Хуки](<./Хуки.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [useEffect vs useLayoutEffect →](<./useEffect vs useLayoutEffect.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`useReducer` управляет локальным state через reducer - чистую функцию перехода. Reducer получает текущее состояние и action, который описывает произошедшее событие, а возвращает следующее состояние. `dispatch(action)` ставит это обновление в очередь и вызывает новый render с результатом reducer.

Hook полезен, когда у состояния несколько связанных полей, одно событие меняет их вместе или возможные переходы удобнее описать централизованно. Для одного независимого значения `useState` обычно проще.

`useReducer` сам по себе не является глобальным store и не выполняет side effects. Запросы, timers, navigation и запись в storage остаются в event handlers или Effects; reducer только вычисляет state.

## Ключевая схема

```text
user action or async result
-> dispatch({ type, payload })
-> reducer(currentState, action)
-> nextState
-> React render
```

| Часть | Роль |
| --- | --- |
| state | snapshot состояния текущего render |
| action | описание события и необходимые данные |
| reducer | чистая функция `(state, action) => nextState` |
| dispatch | ставит action в очередь обновлений |
| initializer | лениво создаёт начальный state |

## Развернутый ответ

**Когда reducer делает код понятнее**

Несколько вызовов `setState` могут разнести правила перехода по разным handlers. Reducer собирает их в одном месте. Например, форма переходит из `idle` в `submitting`, затем в `success` или `error`; action называет событие, а reducer показывает все поля, которые должны измениться вместе.

Action лучше описывает намерение: `{ type: "submitted" }` или `{ type: "requestFailed", message }`. Универсальный action `{ type: "setState", payload }` возвращает прямые мутации из компонентов и убирает преимущество reducer-модели.

**Чистота reducer**

Reducer участвует в вычислении следующего state во время render. React может повторить или не использовать это вычисление, поэтому reducer должен быть чистым:

- не изменять существующий state;
- не выполнять fetch, navigation, analytics и работу с DOM;
- возвращать одинаковый результат для одинаковых аргументов;
- создавать новый объект только для действительно изменившегося state.

Мутация меняет предыдущий state, хотя он должен оставаться неизменяемым снимком (snapshot), а побочный эффект (side effect) может выполниться несколько раз даже для работы, которая не дошла до commit. В Strict Mode React 18 в development специально вызывает reducer и initializer дважды, чтобы такие нарушения стали заметнее. Результат одного вызова игнорируется; в production этого дополнительного вызова нет.

**Как работает dispatch**

`dispatch` не меняет переменную state в уже выполняющемся handler. State является snapshot текущего render; новое значение появится в следующем render. Identity `dispatch` стабилен, поэтому его можно передавать в props и обычно не добавлять в dependencies.

Если reducer вернул значение, равное предыдущему через `Object.is`, React пропустит обновление descendants. Сам вызов компонента при проверке обновления всё ещё возможен, поэтому на это не опираются как на side effect.

**Начальное состояние**

Третий аргумент `useReducer` лениво вычисляет initial state:

```tsx
const [state, dispatch] = useReducer(reducer, userId, createInitialState);
```

React вызывает `createInitialState(userId)` при инициализации, а не на каждом render. Вызов `createInitialState(userId)` прямо во втором аргументе потерял бы это преимущество.

**Связь с Context и Redux**

`useReducer + Context` подходит для state ограниченного feature-поддерева. Но каждый новый context value может обновлять всех потребителей, поэтому state и dispatch иногда разделяют на разные contexts или используют selector-based store.

Redux Toolkit решает другую задачу: общий store, DevTools, middleware, разделение slices и интеграция с server-state инструментами. Похожее слово reducer не делает `useReducer` заменой Redux.

## Пример

```tsx
import { useReducer, type FormEvent } from "react";

async function subscribe(email: string) {
  const response = await fetch("/api/subscriptions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (!response.ok) {
    throw new Error("Subscription request failed");
  }
}

type State = {
  email: string;
  status: "idle" | "submitting" | "success" | "error";
  error: string | null;
};

type Action =
  | { type: "emailChanged"; email: string }
  | { type: "submitted" }
  | { type: "succeeded" }
  | { type: "failed"; message: string };

const initialState: State = {
  email: "",
  status: "idle",
  error: null,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "emailChanged":
      return { ...state, email: action.email };
    case "submitted":
      return { ...state, status: "submitting", error: null };
    case "succeeded":
      return { ...state, status: "success", error: null };
    case "failed":
      return { ...state, status: "error", error: action.message };
  }
}

export function SubscribeForm() {
  const [state, dispatch] = useReducer(reducer, initialState);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    dispatch({ type: "submitted" });

    try {
      await subscribe(state.email);
      dispatch({ type: "succeeded" });
    } catch {
      dispatch({ type: "failed", message: "Не удалось оформить подписку" });
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={state.email}
        onChange={(event) => {
          dispatch({ type: "emailChanged", email: event.target.value });
        }}
      />
      <button disabled={state.status === "submitting"}>
        Подписаться
      </button>
      {state.error && <p role="alert">{state.error}</p>}
    </form>
  );
}
```

Async-операция находится в handler, а reducer описывает только синхронные переходы. Для production-кода запрос также должен учитывать повторную отправку, отмену и unmount; это отдельная ответственность, а не логика reducer.

## Ключевые уточнения

- `useReducer` удобен для связанных переходов, а `useState` - для простых независимых значений.
- Reducer выполняется во время render и остаётся чистой синхронной функцией.
- Action описывает событие, а не произвольную замену всей внутренней структуры state.
- `dispatch` планирует следующий render; текущий handler продолжает видеть старый state snapshot.
- Возврат того же значения state через `Object.is` позволяет React пропустить обновление descendants.
- Lazy initializer используют для дорогого или параметризованного initial state.
- Server state с cache, deduplication, retries и invalidation хранится в query-библиотеке, а не только в reducer.

## Связанные темы

- [Состояние в React](<./Состояние в React.md>)
- [Context](<./Context.md>)
- [Server state и React Query](<./Server state и React Query.md>)
- [Причины рендера](<./Причины рендера.md>)
- [Redux Toolkit](<./Redux Toolkit.md>)
- [Чистая функция](<../JavaScript/Чистая функция.md>)

## Источники

- [React 18 docs: `useReducer`](https://18.react.dev/reference/react/useReducer)
- [React 18 docs: Extracting State Logic into a Reducer](https://18.react.dev/learn/extracting-state-logic-into-a-reducer)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Хуки](<./Хуки.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [useEffect vs useLayoutEffect →](<./useEffect vs useLayoutEffect.md>)
<!-- NOTE-NAV-BOTTOM:END -->
