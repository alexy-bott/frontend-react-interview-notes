# RTK Query

<!-- NOTE-NAV-TOP:START -->
[← Redux Toolkit](<./Redux Toolkit.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Zustand →](<./Zustand.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

RTK Query - модуль Redux Toolkit для server state: запросов, кэша (cache), дедупликации одинаковых запросов, loading/error states, refetch, polling, mutations и invalidation. API описывают через `createApi`: `baseQuery`, query/mutation endpoints и tags. React-интеграция генерирует hooks, например `useGetPostsQuery`.

Cache entry определяется именем endpoint и сериализованными аргументами. Компоненты с одинаковыми аргументами используют один запрос и одну запись cache. После исчезновения последней подписки данные по умолчанию остаются в cache 60 секунд, затем удаляются; время можно изменить через `keepUnusedDataFor`.

RTK Query хранит данные backend. Открытая модалка, выбранный tab и черновик UI остаются в React state или client store.

## Ключевая схема

```text
component calls generated query hook(arg)
-> endpoint name + serialized arg = cache key
-> cached data exists: return it
-> request needed: baseQuery sends request
-> result enters Redux cache
-> subscribed components update

mutation succeeds
-> invalidates tags
-> active affected queries refetch
```

| Концепт | Роль |
| --- | --- |
| `createApi` | создаёт API slice, reducer, middleware и endpoints |
| `baseQuery` | общая логика запроса; часто `fetchBaseQuery` |
| query | читает server state |
| mutation | создаёт, изменяет или удаляет данные |
| `providesTags` | отмечает данные, которые предоставил query |
| `invalidatesTags` | отмечает устаревшие данные после mutation |
| `transformResponse` | преобразует wire response перед записью в cache |
| `onQueryStarted` | lifecycle запроса, optimistic update |
| `onCacheEntryAdded` | lifecycle cache entry, streaming/WebSocket updates |
| `selectFromResult` | подписывает компонент на часть query result |

## Развернутый ответ

**Подключение к store**

`createApi` возвращает reducer и middleware с разными ролями. Reducer хранит записи cache, данные и статусы запросов в Redux state по ключу `reducerPath`. Сгенерированные thunks endpoints запускают `baseQuery`, а API middleware отслеживает подписки на cache и управляет invalidation, polling и временем жизни записей. Поэтому к store подключают и reducer, и middleware: без reducer результатам негде храниться, а без middleware не работают предусмотренные механизмы подписок и жизненного цикла cache.

`setupListeners(store.dispatch)` отдельно связывает RTK Query с событиями браузера: возвращением фокуса и восстановлением соединения. Он нужен, если используются `refetchOnFocus` или `refetchOnReconnect`; базовые запросы без этих настроек работают и без него.

**API slice и cache key**

Обычно создают один API slice на один base URL и добавляют endpoints через `injectEndpoints` по feature-модулям. Несколько API slices увеличивают число middleware-проверок на каждый dispatch, а tag invalidation не пересекает границы разных slices.

Для query RTK Query сериализует аргумент и вместе с именем endpoint получает cache key. Поэтому два вызова `getPost("42")` делят cache, а `getPost("43")` создаёт другую запись. Все параметры, влияющие на ответ, должны входить в arg.

RTK Query считает подписки на cache entry. Пока данные использует хотя бы один компонент, запись активна. После последней отписки запускается `keepUnusedDataFor`; default - 60 секунд. Повторный mount в этот период получает cache без нового пустого состояния, а политика refetch определяет, нужно ли обновить данные.

**Query result и UX**

`isLoading` означает первый запрос без доступных данных. `isFetching` означает любой выполняющийся запрос, в том числе background refetch при уже показанном cache. Поэтому skeleton обычно связан с `isLoading`, а небольшой индикатор обновления - с `isFetching`.

`data` может хранить последний успешный result, а `currentData` относится к текущему аргументу hook. Это различие полезно при смене фильтра или страницы, если старые данные не должны временно показываться для нового arg.

Условный запрос задают через `skip` или `skipToken`, запрос по действию пользователя - через lazy query. `refetchOnFocus` и `refetchOnReconnect` работают после вызова `setupListeners(store.dispatch)`.

**Tags и invalidation**

Query объявляет предоставленные tags, mutation - invalidated tags. Если активная cache entry предоставляет invalidated tag, RTK Query запрашивает её заново. Если подписчиков нет, устаревшая запись может быть удалена вместо немедленного запроса.

Для коллекции обычно нужны два уровня:

- `{ type: "Posts", id: "LIST" }` для состава списка;
- `{ type: "Posts", id: post.id }` для конкретной сущности.

Создание post инвалидирует `LIST`. Изменение title может инвалидировать entity и нужные списки. Стратегия зависит от того, какие ответы реально содержат сущность.

**RTK Query не является нормализованной базой**

Cache хранится по endpoint + arg. Одна сущность, полученная в `getPosts()` и `getPost(id)`, может существовать в двух cache entries. RTK Query не дедуплицирует entity между разными ответами автоматически. Tags помогают согласованно refetch, а `transformResponse` или `createEntityAdapter` могут нормализовать конкретный response.

**Mutation и optimistic update**

Простой и надёжный вариант - invalidation после успешной mutation. Если мгновенный UI важен, `onQueryStarted` может вызвать `api.util.updateQueryData`, получить patch result и выполнить `.undo()` при ошибке. При нескольких пересекающихся mutations rollback становится сложнее; иногда безопаснее инвалидировать tags и запросить server truth заново.

**Auth и ошибки**

`prepareHeaders` подходит для добавления access token. Refresh-token flow обычно реализуют обёрткой над `fetchBaseQuery`: при 401 один запрос обновляет token, остальные ожидают mutex, затем исходный запрос повторяется. Бесконечный retry на 401 не используют.

UI должен различать transport error, HTTP error и доменную ошибку API. `fetchBaseQuery` возвращает structured error, который удобно привести к единому application shape.

**Streaming и OpenAPI**

`onCacheEntryAdded` подходит для WebSocket/SSE: дождаться первого cache result, подписаться на stream, обновлять cache и закрыть соединение после `cacheEntryRemoved`.

Из OpenAPI можно генерировать endpoints и типы, но генерация не выбирает за команду tag strategy, auth refresh, DTO mapping, error model и границы API slices.

## Пример

```ts
// postsApi.ts
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

type Post = {
  id: string;
  title: string;
};

type UpdatePost = {
  id: string;
  title: string;
};

export const postsApi = createApi({
  reducerPath: "postsApi",
  baseQuery: fetchBaseQuery({
    baseUrl: "/api",
    prepareHeaders(headers) {
      headers.set("accept", "application/json");
      return headers;
    },
  }),
  tagTypes: ["Post"],
  endpoints: (build) => ({
    getPosts: build.query<Post[], void>({
      query: () => "posts",
      providesTags: (result) =>
        result
          ? [
              { type: "Post", id: "LIST" },
              ...result.map(({ id }) => ({ type: "Post" as const, id })),
            ]
          : [{ type: "Post", id: "LIST" }],
    }),
    updatePost: build.mutation<Post, UpdatePost>({
      query: ({ id, ...body }) => ({
        url: `posts/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (_result, _error, { id }) => [
        { type: "Post", id },
        { type: "Post", id: "LIST" },
      ],
    }),
  }),
});

export const { useGetPostsQuery, useUpdatePostMutation } = postsApi;
```

```ts
// store.ts
import { configureStore } from "@reduxjs/toolkit";
import { setupListeners } from "@reduxjs/toolkit/query";
import { postsApi } from "./postsApi";

export const store = configureStore({
  reducer: {
    [postsApi.reducerPath]: postsApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(postsApi.middleware),
});

setupListeners(store.dispatch);
```

```tsx
export function Posts() {
  const { data: posts = [], isLoading, isFetching, error } =
    useGetPostsQuery();

  if (isLoading) return <p>Загрузка...</p>;
  if (error) return <p role="alert">Не удалось загрузить записи</p>;

  return (
    <section aria-busy={isFetching}>
      {isFetching && <span>Обновление...</span>}
      {posts.map((post) => (
        <article key={post.id}>{post.title}</article>
      ))}
    </section>
  );
}
```

## Ключевые уточнения

- Query cache key состоит из endpoint и сериализованного аргумента.
- Одинаковые активные queries дедуплицируются и используют общую cache entry.
- Неиспользуемые данные по умолчанию сохраняются 60 секунд; это не то же самое, что время свежести HTTP cache.
- `isLoading` описывает первый запрос без данных, `isFetching` - любой текущий fetch.
- Tags выражают связи для invalidation, но не нормализуют сущности между разными endpoints.
- Active query после invalidation refetches; точная tag strategy должна учитывать списки и entity.
- Optimistic update требует rollback или последующего refetch server truth.
- API reducer хранит query cache в Redux state, а middleware управляет подписками, invalidation, polling и жизненным циклом cache; к store подключаются обе части.
- Client UI state не дублируют в RTK Query cache.

## Связанные темы

- [Redux Toolkit](<./Redux Toolkit.md>)
- [Redux и Flux](<./Redux и Flux.md>)
- [Server state и React Query](<./Server state и React Query.md>)
- [OpenAPI и Swagger](<../Web Basics/OpenAPI и Swagger.md>)
- [REST](<../Web Basics/REST.md>)
- [HTTP status codes и ошибки API](<../Web Basics/HTTP status codes и ошибки API.md>)
- [API слой и контракты](<../Architecture/API слой и контракты.md>)
- [Fetch и работа с API](<../JavaScript/Fetch и работа с API.md>)

## Источники

- [RTK Query docs: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)
- [RTK Query docs: Queries](https://redux-toolkit.js.org/rtk-query/usage/queries)
- [RTK Query docs: Automated Re-fetching](https://redux-toolkit.js.org/rtk-query/usage/automated-refetching)
- [RTK Query docs: Manual Cache Updates](https://redux-toolkit.js.org/rtk-query/usage/manual-cache-updates)
- [RTK Query docs: Streaming Updates](https://redux-toolkit.js.org/rtk-query/usage/streaming-updates)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Redux Toolkit](<./Redux Toolkit.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Zustand →](<./Zustand.md>)
<!-- NOTE-NAV-BOTTOM:END -->
