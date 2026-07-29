# Server state и React Query

<!-- NOTE-NAV-TOP:START -->
[← Состояние в React](<./Состояние в React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Error Boundaries →](<./Error Boundaries.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Server state - данные, источник истины которых находится на backend: users, orders, permissions, products. Приложение получает их асинхронно, а данные могут измениться без текущей вкладки. Поэтому нужны cache, статус свежести, refetch, deduplication, retry и синхронизация после mutations.

TanStack Query, ранее React Query, ведёт кэш (cache) server state вне Redux. Query key адресует данные, `queryFn` загружает их, а mutations обновляют backend и затем инвалидируют или изменяют cache. В этой карточке API и названия статусов относятся к TanStack Query v5.

Client state остаётся в React state, URL, Zustand или Redux Toolkit. Query cache не предназначен для открытой модалки и текста несохранённого input.

## Ключевая схема

| Тип state | Примеры | Подходящий владелец |
| --- | --- | --- |
| local UI | input, dropdown, hover | component state |
| shared client state | wizard, UI settings | Context, Zustand, Redux Toolkit |
| URL state | page, filters, sort | path и search params |
| form state | values, touched, validation errors | form library или local state |
| server state | profile, products, permissions | TanStack Query, RTK Query, framework cache |

```text
queryKey + queryFn
-> cache entry
-> fresh: return cache
-> stale: cache can render while refetch runs

mutation
-> backend changes
-> invalidate or update related cache
-> UI converges to server truth
```

## Развернутый ответ

**Почему server state выделяют отдельно**

Client state принадлежит текущему приложению: оно точно знает, когда открыло panel или изменило draft. Server state является удалённым snapshot. Пока он лежит в браузере, запись могла измениться другим пользователем, истечь по времени или стать недоступной из-за новых permissions.

Query-библиотека не делает данные навсегда актуальными. Она задаёт управляемую модель: когда cache считается stale, когда запрашивать заново, что показать во время обновления и как синхронизироваться после mutation.

**Query key**

В TanStack Query top-level key является массивом. В него включают все параметры, от которых зависит `queryFn`: id, page, filters, sort, tenant и locale. Объекты внутри key хэшируются детерминированно, но порядок элементов массива значим.

```tsx
queryKey: ["orders", { page, status, tenantId }]
```

Если забыть `tenantId`, два tenant могут разделить одну cache entry. Если положить в key нестабильное или несериализуемое значение, cache становится трудно предсказывать.

**Fresh, stale и garbage collection**

`staleTime` определяет, сколько времени данные считаются свежими. В TanStack Query v5 default `staleTime` равен `0`: успешный result сразу считается stale, но не исчезает. Stale cache можно немедленно показать, а refetch выполнить в фоне.

Неиспользуемая query становится inactive. По умолчанию её cache удаляется через пять минут; в v5 эта настройка называется `gcTime`. `staleTime` отвечает за свежесть, `gcTime` - за хранение неактивной записи. Это разные таймеры.

По умолчанию stale queries могут refetch при новом mount, возвращении focus окну и восстановлении сети. Неудачный query на клиенте повторяется до трёх раз с задержкой. Defaults меняют осознанно: например, ошибки авторизации обычно не требуют трёх одинаковых retries.

Для JSON-compatible данных TanStack Query по умолчанию применяет structural sharing: сравнивает старый и новый result и сохраняет ссылки на неизменившиеся части. Это помогает стабилизировать props и результаты memoization. Для class instances и других несериализуемых значений такое сравнение не работает как для обычного JSON-result.

**Статусы**

В TanStack Query v5:

- `isPending` означает, что query ещё не имеет успешных данных;
- `isFetching` означает, что `queryFn` сейчас выполняется;
- `isLoading` означает первый fetch: `isPending && isFetching`;
- `isRefetching` означает fetch при уже существующем результате.

UI может показать skeleton для первого load и оставить старые данные с небольшим индикатором во время background refetch.

**Mutation и согласование cache**

Mutation изменяет server state. После успеха используют один из подходов:

1. `invalidateQueries` помечает связанные queries stale и по умолчанию refetches активные;
2. `setQueryData` сразу кладёт точный response backend в cache;
3. optimistic update временно меняет cache до ответа и откатывается при ошибке.

Optimistic update полезен для мгновенного UX, но требует сохранения предыдущего snapshot, обработки concurrent mutations и окончательной сверки с сервером. Для редкого действия простая invalidation часто надёжнее.

**Cancellation и race conditions**

TanStack Query передаёт `AbortSignal` в `queryFn`. Если использовать его в `fetch`, устаревший запрос можно отменить. Отмена и query key защищают от части race conditions лучше, чем ручной `useEffect` с несколькими `setState`.

**TanStack Query и RTK Query**

Обе библиотеки решают server state. RTK Query хранит cache в Redux store, генерирует endpoint hooks и использует tags. TanStack Query не требует Redux, адресует данные query keys и даёт framework-agnostic query cache. Если проект уже построен на Redux Toolkit и OpenAPI API slice, RTK Query часто естественнее. Выбор не требует держать один и тот же response в обеих библиотеках.

**SSR**

Framework может prefetch queries на сервере, dehydrated cache передать клиенту и hydrate его без повторного пустого состояния. Данные и timestamps должны сериализоваться безопасно, а QueryClient на сервере создают на запрос, чтобы не смешивать cache разных пользователей.

**Подключение в client-приложении**

Один `QueryClient` создают вне render и передают через `QueryClientProvider`. Если создавать client внутри компонента без сохранения, каждый render будет терять cache. Общие `staleTime`, retry и refetch-настройки можно задать в `defaultOptions`, а конкретный query при необходимости их переопределяет.

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createRoot } from "react-dom/client";
import { App } from "./App";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
    },
  },
});

const container = document.getElementById("root");

if (container) {
  createRoot(container).render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  );
}
```

## Пример TanStack Query v5

```tsx
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

type User = {
  id: string;
  name: string;
};

async function getUsers(page: number, signal: AbortSignal): Promise<User[]> {
  const response = await fetch(`/api/users?page=${page}`, { signal });

  if (!response.ok) {
    throw new Error("Users request failed");
  }

  return response.json();
}

async function updateUser(user: User): Promise<User> {
  const response = await fetch(`/api/users/${user.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(user),
  });

  if (!response.ok) {
    throw new Error("User update failed");
  }

  return response.json();
}

export function UsersPage({ page }: { page: number }) {
  const queryClient = useQueryClient();

  const usersQuery = useQuery({
    queryKey: ["users", { page }],
    queryFn: ({ signal }) => getUsers(page, signal),
  });

  const updateMutation = useMutation({
    mutationFn: updateUser,
    onSuccess: (updatedUser) => {
      queryClient.setQueryData<User[]>(
        ["users", { page }],
        (current = []) =>
          current.map((user) => (
            user.id === updatedUser.id ? updatedUser : user
          )),
      );
    },
  });

  if (usersQuery.isPending) return <p>Загрузка...</p>;
  if (usersQuery.isError) {
    return <p role="alert">Не удалось загрузить пользователей</p>;
  }

  return (
    <section aria-busy={usersQuery.isFetching}>
      {usersQuery.isFetching && <span>Обновление...</span>}
      {usersQuery.data.map((user) => (
        <button
          key={user.id}
          type="button"
          onClick={() => {
            updateMutation.mutate({ ...user, name: `${user.name}!` });
          }}
        >
          {user.name}
        </button>
      ))}
    </section>
  );
}
```

## Ключевые уточнения

- Server state является удалённым snapshot, а query cache управляет его свежестью и синхронизацией.
- Query key включает каждый параметр, который изменяет результат `queryFn`.
- В TanStack Query v5 default `staleTime: 0`, но stale data не удаляются немедленно.
- `gcTime` удаляет неактивную cache entry; default на клиенте - пять минут.
- Structural sharing сохраняет ссылки на неизменившиеся части JSON-compatible result.
- `isPending` и `isFetching` описывают разные измерения: наличие данных и текущий сетевой процесс.
- Invalidation помечает queries stale и refetches активные; она не равна немедленному удалению всего cache.
- Query cache не дублируют в Redux/Zustand без отдельной причины.
- `QueryClient` в браузере сохраняют между renders; на сервере изолируют на request.
- SSR cache изолируют между запросами пользователей.

## Связанные темы

- [Состояние в React](<./Состояние в React.md>)
- [Redux Toolkit](<./Redux Toolkit.md>)
- [RTK Query](<./RTK Query.md>)
- [Zustand](<./Zustand.md>)
- [SSR и SSG](<./SSR и SSG.md>)
- [HTTP caching](<../Web Basics/HTTP caching.md>)

## Источники

- [TanStack Query v5: Overview](https://tanstack.com/query/v5/docs/framework/react/overview)
- [TanStack Query v5: Important Defaults](https://tanstack.com/query/v5/docs/framework/react/guides/important-defaults)
- [TanStack Query v5: Query Keys](https://tanstack.com/query/v5/docs/framework/react/guides/query-keys)
- [TanStack Query v5: Query Invalidation](https://tanstack.com/query/v5/docs/framework/react/guides/query-invalidation)
- [TanStack Query v5: Query Cancellation](https://tanstack.com/query/v5/docs/framework/react/guides/query-cancellation)
- [RTK Query docs: Overview](https://redux-toolkit.js.org/rtk-query/overview)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Состояние в React](<./Состояние в React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Error Boundaries →](<./Error Boundaries.md>)
<!-- NOTE-NAV-BOTTOM:END -->
