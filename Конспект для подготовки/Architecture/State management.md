---
aliases:
  - state management
  - управление состоянием
  - frontend state
---

#### Ответ на 60 секунд

State management начинается не с выбора библиотеки, а с классификации состояния. В frontend есть local state, server state, URL state, form state и global client state. Если всё складывать в один глобальный store, приложение быстро получает лишние ререндеры, сложную синхронизацию и неочевидные источники правды.

Local state держат рядом с компонентом. Server state отдают специализированному слою вроде RTK Query, TanStack Query, SWR или loader-слою фреймворка, потому что там нужны кеш, stale data, retry, invalidation и deduplication. URL state подходит для фильтров, сортировки и пагинации, которыми можно поделиться ссылкой. Глобальный store нужен для настоящего client state, который разделяют удалённые части приложения: auth context, настройки интерфейса, feature flags, сложный wizard.

#### Ключевая схема

| Тип состояния | Примеры | Где держать |
| --- | --- | --- |
| Local state | открыта ли dropdown, hover, local input | `useState`, `useReducer` |
| Server state | профиль, список заказов, права | RTK Query, TanStack Query, SWR, loaders |
| URL state | page, sort, filters, tab | query params, route params |
| Form state | values, touched, validation errors | form library или локально |
| Global client state | theme, auth snapshot, wizard | Context, Redux Toolkit, Zustand |

#### Развернутый ответ

Выбор state management начинается с владельца данных. Local UI state живёт рядом с компонентом, потому что не нужен всему приложению. Server state хранится в query/cache слое, потому что он устаревает, зависит от backend, требует invalidation, deduplication, retries и background refetch. URL state хранит то, чем нужно поделиться ссылкой: filters, sort, page, tab.

Redux Toolkit, RTK Query, Zustand и Context решают разные задачи. Redux Toolkit подходит для предсказуемого global client state, сложных событий и требований к debugging. RTK Query закрывает server-state cache внутри Redux Toolkit-экосистемы. Zustand удобен для небольшого client store без большого boilerplate: UI preferences, wizard, selected items, panels. Context подходит для редко меняющихся значений вроде theme, locale, auth snapshot или DI/config, но для частых обновлений может давать лишние renders.

Server state вручную дублируют в global store только при явной архитектурной причине. Если список пользователей уже живёт в query cache, копия в Redux/Zustand создаёт два источника правды: один устарел, другой обновился, optimistic update прошёл в одном месте, invalidation - в другом. Такие баги сложнее, чем сама библиотека.

`useState` удобен для простого состояния, `useReducer` - когда есть несколько связанных переходов и нужно явно описать события. Для формового состояния важны values, touched, dirty, errors и submit lifecycle; его часто держат в form library, а не в общем store.

Главное правило - один владелец данных. Например, список пользователей живёт в query cache, фильтры - в URL, состояние модального окна - локально, auth snapshot - в отдельном client store/context. Тогда изменения не требуют синхронизировать один и тот же смысл в нескольких местах.

> [!faq]+ Уточнения
> - State делят на local, server, URL, form и global client state.
> - Redux/Zustand не должны автоматически становиться складом backend-ответов.
> - Context подходит для редко меняющихся значений; частые updates требуют осторожности.
> - URL хранит состояние страницы, которое должно переживать reload и шариться ссылкой.
> - `useReducer` полезен, когда состояние меняется через набор событий и переходов.

#### Пример

```tsx
const [isOpen, setIsOpen] = useState(false); // local UI state

const [searchParams, setSearchParams] = useSearchParams(); // URL state
const page = Number(searchParams.get("page") ?? 1);

const usersQuery = useQuery({
  queryKey: ["users", page],
  queryFn: () => fetchUsers({ page }),
});
```

Здесь каждый тип состояния лежит в своём естественном месте: dropdown локально, пагинация в URL, серверные данные в query cache.

#### Частые ошибки

- Выбирать библиотеку до понимания типа состояния.
- Дублировать server state в глобальном store.
- Хранить фильтры только локально, из-за чего нельзя поделиться ссылкой.
- Делать один огромный Context для часто меняющихся данных.
- Смешивать form draft, saved server data и optimistic update без явной модели.

#### Связанные темы

- [[Конспект для подготовки/React/Состояние в React]]
- [[Конспект для подготовки/React/Context]]
- [[Конспект для подготовки/React/Redux и Flux]]
- [[Конспект для подготовки/React/Redux Toolkit]]
- [[Конспект для подготовки/React/RTK Query]]
- [[Конспект для подготовки/React/Zustand]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]

#### Источники

- [React: Sharing State Between Components](https://react.dev/learn/sharing-state-between-components)
- [Redux docs: Redux Essentials](https://redux.js.org/tutorials/essentials/part-1-overview-concepts)
- [RTK Query docs: Overview](https://redux-toolkit.js.org/rtk-query/overview)
- [TanStack Query: Overview](https://tanstack.com/query/latest/docs/framework/react/overview)
- [Zustand docs](https://zustand.docs.pmnd.rs/)
