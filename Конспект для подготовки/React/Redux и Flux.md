---
aliases:
  - Redux и Flux
  - Redux data flow
  - Flux architecture
---

#### Быстрый ответ

Redux - это state container с однонаправленным потоком данных. Store хранит дерево состояния; код отправляет plain object action через `dispatch`; reducers вычисляют следующее immutable-состояние; подписанные компоненты снова читают выбранные данные и при необходимости рендерятся.

Reducer остаётся чистым. Запросы, timers, analytics и сложную orchestration размещают в middleware, thunks, listener middleware или query-слое. В современных проектах Redux пишут через Redux Toolkit, а server-state cache обычно ведёт RTK Query.

Flux - более общий архитектурный подход, из которого вырос Redux. В классическом Flux action проходит через отдельный Dispatcher в несколько stores, после чего View читает изменения. Redux упростил модель: рекомендует один store, не использует отдельный Dispatcher и описывает переходы чистыми reducers.

#### Ключевая схема

```text
event / async result
-> store.dispatch(action)
-> middleware can observe, delay or dispatch more actions
-> reducers(currentState, action)
-> next immutable state
-> store notifies subscribers
-> selectors read slices
-> affected React components render
```

| Понятие | Роль |
| --- | --- |
| store | хранит state tree и предоставляет `dispatch`, `getState`, `subscribe` |
| action | сериализуемое описание произошедшего события |
| reducer | чистая функция перехода к следующему state |
| middleware | слой вокруг `dispatch` для async-логики, logging и orchestration |
| selector | читает или вычисляет данные из state |
| React-Redux | связывает store с React через Provider и subscription hooks |

#### Развернутый ответ

**Однонаправленный поток**

Компонент не изменяет store напрямую. Он отправляет action, например `{ type: "cart/itemAdded", payload: item }`. Store вызывает root reducer с предыдущим state и action. Reducers возвращают новое состояние, store уведомляет подписчиков, а `useSelector` повторно запускает selector.

Этот порядок делает изменение наблюдаемым: в Redux DevTools видно, какое событие произошло, каким был state и каким стал. Action лучше называть как доменное событие, а не как команду присвоить случайное поле.

**Immutable update**

Redux определяет изменение по ссылкам. Reducer сохраняет ссылки на неизменившиеся ветви и создаёт новые для изменившихся. Прямая мутация с возвратом прежнего объекта мешает подписчикам обнаружить обновление.

В Redux Toolkit reducers работают с Immer draft, поэтому запись `state.count += 1` безопасно превращается в immutable update. Это разрешено только внутри Immer-controlled reducer, а не в компонентах или произвольном коде.

**Middleware и async-логика**

Middleware образуют pipeline вокруг `dispatch`. Они могут увидеть action до reducer и state после reducer, отправить дополнительные actions, выполнить async-работу или остановить дальнейшую передачу. Thunk - функция, которой middleware передаёт `dispatch` и `getState`.

Reducers не выполняют side effects, потому что запускаются во время расчёта state и должны оставаться повторяемыми. Server-state запросы чаще описывают в RTK Query; длинные реактивные workflows - через listener middleware или специализированный инструмент.

**Подписка React-компонента**

`useSelector(selector)` подписывает компонент на store. После action selector выполняется снова, а React-Redux по умолчанию сравнивает предыдущий и новый результат по строгому равенству ссылки. Selector, который каждый раз создаёт новый object или array, вызовет render даже при тех же данных. Для derived collections используют memoized selector, например `createSelector`.

**Redux и Flux**

Flux - схема, а не одна обязательная библиотека. Классический поток выглядит как Action → Dispatcher → Store → View. Stores могут содержать собственную логику и сообщать об изменениях.

Redux отличается следующими решениями:

- одно дерево state в рекомендуемом store;
- чистые reducers вместо mutable Flux stores;
- нет отдельного Dispatcher-объекта;
- подписчики получают изменение после вычисления root reducer;
- middleware расширяет `dispatch` и изолирует side effects.

**Когда Redux оправдан**

Redux Toolkit полезен, если state разделяется между многими feature, переходы сложны, нужны middleware, DevTools, replay/debug, audit или единые командные соглашения. Открытие локального dropdown, hover и значение одного input остаются рядом с компонентом. URL хранит shareable navigation state, а query cache - данные сервера.

#### Пример

```ts
import { configureStore, createSlice, type PayloadAction } from "@reduxjs/toolkit";

type CartItem = {
  id: string;
  quantity: number;
};

type CartState = {
  items: CartItem[];
};

const cartSlice = createSlice({
  name: "cart",
  initialState: { items: [] } satisfies CartState,
  reducers: {
    itemAdded(state, action: PayloadAction<{ id: string }>) {
      const item = state.items.find(({ id }) => id === action.payload.id);

      if (item) {
        item.quantity += 1;
      } else {
        state.items.push({ id: action.payload.id, quantity: 1 });
      }
    },
  },
});

export const { itemAdded } = cartSlice.actions;

export const store = configureStore({
  reducer: {
    cart: cartSlice.reducer,
  },
});
```

`itemAdded` описывает событие. `createSlice` генерирует action creator и reducer, а Immer преобразует изменения draft в новое immutable-состояние.

#### Ключевые уточнения

- Redux управляет предсказуемым application state, а не требует выносить в store всё состояние интерфейса.
- Action описывает событие; reducer синхронно и чисто вычисляет следующий state.
- Middleware расширяет путь `dispatch` и содержит side effects, которые не принадлежат reducer.
- React-компонент обновляется по результату своего selector, а не автоматически из-за любой части store.
- Стабильные ссылки и memoized selectors уменьшают лишние renders.
- Redux Toolkit является официальным способом писать современный Redux.
- Server state требует cache, deduplication и invalidation; в Redux-экосистеме это задача RTK Query.
- Flux объясняет историческую архитектурную основу, а Redux задаёт конкретные ограничения и API.

#### Связанные темы

- [[Конспект для подготовки/React/Состояние в React]]
- [[Конспект для подготовки/React/Context]]
- [[Конспект для подготовки/React/Redux Toolkit]]
- [[Конспект для подготовки/React/RTK Query]]
- [[Конспект для подготовки/React/Zustand]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/React/Причины рендера]]

#### Источники

- [Redux docs: Redux Fundamentals](https://redux.js.org/tutorials/fundamentals/part-2-concepts-data-flow)
- [Redux docs: Style Guide](https://redux.js.org/style-guide/)
- [Redux docs: Deriving Data with Selectors](https://redux.js.org/usage/deriving-data-selectors)
- [Redux Toolkit docs: Getting Started](https://redux-toolkit.js.org/introduction/getting-started)
