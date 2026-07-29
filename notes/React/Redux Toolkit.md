# Redux Toolkit

<!-- NOTE-NAV-TOP:START -->
[← Redux и Flux](<./Redux и Flux.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [RTK Query →](<./RTK Query.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Redux Toolkit (RTK) - официальный рекомендуемый способ писать Redux. Он сохраняет однонаправленный поток Redux, но убирает ручную настройку и boilerplate: `configureStore` собирает store и middleware, `createSlice` генерирует reducer и actions, а Immer позволяет обновлять draft в «мутационном» стиле с immutable-результатом.

RTK используют для разделяемого client/application state и сложных событийных workflows. Side effects не выполняют в reducers: простые async-сценарии размещают в `createAsyncThunk`, реакцию на события - в listener middleware, а server-state cache - в RTK Query.

## Ключевая схема

| API | Основная задача |
| --- | --- |
| `configureStore` | store, root reducer, thunk, DevTools и development checks |
| `createSlice` | slice reducer и action creators |
| Immer | immutable update через изменения draft |
| `createAsyncThunk` | lifecycle одной promise-операции |
| listener middleware | реакция на actions/state и orchestration |
| `createSelector` | memoized derived data |
| `createEntityAdapter` | normalized `ids/entities` collections |
| RTK Query | server-state requests, cache и invalidation |

## Развернутый ответ

**`configureStore`**

`configureStore` принимает reducers и создаёт Redux store. По умолчанию он подключает thunk middleware, Redux DevTools и development-проверки распространённых ошибок: случайной мутации, несериализуемых значений и неправильного использования action creator.

Middleware добавляют через callback `getDefaultMiddleware => getDefaultMiddleware().concat(customMiddleware)`, чтобы не потерять defaults. Проверки можно точечно настроить, но сначала устраняют причину warning.

**`createSlice` и Immer**

`createSlice` связывает имя feature, initial state и case reducers. На основе имени reducer генерируется action type, а для каждого reducer - type-safe action creator.

Reducer получает Immer draft. Внутри одного case reducer выбирают один способ: либо изменяют draft, либо возвращают полностью новое значение. Мутировать draft и одновременно возвращать другое состояние не следует. Вне reducer state остаётся read-only.

**Выбор async-инструмента**

`createAsyncThunk` создаёт actions `pending`, `fulfilled` и `rejected` для одной promise-операции. Он подходит, если результат участвует именно в application state или workflow. Через `thunkAPI.signal` можно поддержать отмену, через `condition` - не запускать дубликат, а `.unwrap()` позволяет handler получить payload или бросить rejected error.

Listener middleware подходит для длительной orchestration: дождаться action, отменить предыдущую задачу, debounce событие, запустить несколько actions после изменения state. Reducer при этом остаётся чистым.

RTK Query выбирают, если данные принадлежат backend и требуют cache, deduplication, refetch и invalidation. Ручной набор `isLoading/data/error` в slice обычно повторяет уже готовую query-модель.

**Selectors и renders**

Компонент подписывают на минимальный slice через `useSelector`. React-Redux по умолчанию сравнивает результат selector по ссылке. Если selector на каждый вызов возвращает новый массив или объект, компонент будет обновляться после каждого action. `createSelector` кэширует derived result до изменения входных selectors.

`createEntityAdapter` хранит коллекцию как `ids` и `entities`, генерирует CRUD reducers и selectors. Нормализация полезна, когда сущности часто обновляются по id. Она не обязательна для маленького списка и не заменяет query cache.

**Структура и TypeScript**

Slices обычно строят по feature/domain, а не по типу данных вроде одного глобального `loadingSlice`. `RootState` и `AppDispatch` выводят из store, после чего создают typed `useAppSelector` и `useAppDispatch`. Типы не дублируют вручную.

Redux рекомендует сериализуемые actions и state. Это делает DevTools, persistence и воспроизведение предсказуемыми. DOM nodes, class instances, promises и AbortController обычно не хранят в store.

## Пример

```ts
// store.ts
import { configureStore, createSlice, type PayloadAction } from "@reduxjs/toolkit";

type Notification = {
  id: string;
  message: string;
  read: boolean;
};

type NotificationsState = {
  items: Notification[];
};

const initialState: NotificationsState = {
  items: [],
};

const notificationsSlice = createSlice({
  name: "notifications",
  initialState,
  reducers: {
    notificationReceived(
      state,
      action: PayloadAction<{ id: string; message: string }>,
    ) {
      state.items.push({ ...action.payload, read: false });
    },
    notificationRead(state, action: PayloadAction<string>) {
      const notification = state.items.find(
        ({ id }) => id === action.payload,
      );

      if (notification) {
        notification.read = true;
      }
    },
  },
});

export const { notificationReceived, notificationRead } =
  notificationsSlice.actions;

export const store = configureStore({
  reducer: {
    notifications: notificationsSlice.reducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const selectUnreadCount = (state: RootState) =>
  state.notifications.items.filter(({ read }) => !read).length;
```

```tsx
// hooks.ts
import {
  useDispatch,
  useSelector,
  type TypedUseSelectorHook,
} from "react-redux";
import type { AppDispatch, RootState } from "./store";

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

В реальном проекте derived selector с тяжёлой фильтрацией лучше создать через `createSelector`, чтобы сохранять ссылку и результат до изменения входных данных.

## Ключевые уточнения

- Redux Toolkit является Redux с официальными abstractions, а не конкурирующей заменой Redux.
- Immer разрешает менять только draft внутри RTK reducer; store снаружи не мутируют.
- Reducer описывает синхронный переход state и не содержит side effects.
- `createAsyncThunk` моделирует lifecycle операции, но не предоставляет полноценный server cache.
- RTK Query отвечает за backend data, а slices - за client/application state.
- Компонент подписывают на минимальные данные; object/array result selector должен сохранять ссылку или быть memoized.
- Store и actions сохраняют сериализуемыми, если нет обоснованного и настроенного исключения.
- Feature-based slices и typed hooks уменьшают связанность компонентов с внутренней формой store.

## Связанные темы

- [Redux и Flux](<./Redux и Flux.md>)
- [RTK Query](<./RTK Query.md>)
- [Server state и React Query](<./Server state и React Query.md>)
- [Zustand](<./Zustand.md>)
- [Причины рендера](<./Причины рендера.md>)
- [State management](<../Architecture/State management.md>)

## Источники

- [Redux Toolkit docs: Getting Started](https://redux-toolkit.js.org/introduction/getting-started)
- [Redux Toolkit docs: Usage with TypeScript](https://redux-toolkit.js.org/usage/usage-with-typescript)
- [Redux Toolkit docs: `createAsyncThunk`](https://redux-toolkit.js.org/api/createAsyncThunk)
- [Redux Toolkit docs: Listener Middleware](https://redux-toolkit.js.org/api/createListenerMiddleware)
- [Redux docs: Deriving Data with Selectors](https://redux.js.org/usage/deriving-data-selectors)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Redux и Flux](<./Redux и Flux.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [RTK Query →](<./RTK Query.md>)
<!-- NOTE-NAV-BOTTOM:END -->
