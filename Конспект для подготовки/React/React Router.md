---
aliases:
  - React Router
  - routing
  - SPA routing
  - роутинг
  - data router
---

#### Быстрый ответ

React Router связывает URL с деревом React-интерфейса. При client-side navigation он меняет history и URL без загрузки нового HTML-документа, сопоставляет location с routes и рендерит подходящую ветку. `Link` сохраняет SPA-навигацию, а nested routes строят общие layouts через `Outlet`.

В React Router 6.4+ data router дополнительно связывает route с `loader`, `action`, pending navigation и error boundary. Loader получает данные до render route, action обрабатывает mutation, а после action router revalidates связанные loaders.

Frontend route может скрыть экран и перенаправить на login, но не обеспечивает authorization. Backend обязан проверять доступ к данным и операции независимо от router.

#### Версионная база

Основная модель карточки - React Router 6.4+ с `react-router-dom` и data router API. Более новые major-версии развивают тот же route tree, но могут менять packages и framework APIs. В проекте сначала проверяют установленную версию, затем используют соответствующую документацию.

#### Ключевая схема

```text
click Link / submit Form / navigate()
-> History API changes URL
-> router matches route branch
-> matched loaders run, usually in parallel
-> pending navigation state
-> route elements render into nested Outlets
-> route errorElement handles loader/render errors
```

| Понятие | Роль |
| --- | --- |
| route | связывает path, UI, data и error boundary |
| nested route | сопоставляет сегменты URL с layout hierarchy |
| index route | default child внутри родительского path |
| dynamic segment | параметр вида `:projectId` |
| search params | shareable filters, sort и pagination |
| loader | читает данные до render route |
| action | обрабатывает mutation и запускает revalidation |
| `Outlet` | место render дочернего route |
| `errorElement` | ближайшая route error boundary |

#### Развернутый ответ

**Client-side navigation**

Обычная ссылка запрашивает новый document у сервера. React Router перехватывает внутренний переход через `Link` или `NavLink`, вызывает History API и обновляет React UI в уже загруженном приложении. Back/forward продолжают работать, потому что location остаётся частью browser history.

`useNavigate` используют после события или завершённой операции. Для обычной навигации в JSX предпочтительнее `Link`: он создаёт настоящий `href`, поддерживает открытие в новой вкладке и лучше соответствует семантике браузера.

**Deep links и server fallback**

При прямом открытии `/settings` запрос сначала приходит на web server. Для client-only SPA сервер должен вернуть `index.html` для неизвестного route вместо 404, а статические файлы и API не должны попадать под этот rewrite.

`HashRouter` хранит route после `#`, поэтому server не получает этот фрагмент и fallback не требуется. Цена - менее чистый URL и ограничения server rendering. Для обычного production SPA чаще используют `createBrowserRouter`.

**Nested routes**

Route tree связывает URL hierarchy с UI hierarchy. Родитель рендерит layout и `Outlet`; дочерний element появляется внутри него. Это позволяет один раз описать dashboard shell, navigation и error boundary.

Relative `Link to="settings"` разрешается относительно route hierarchy. Dynamic segments доступны в loader/action через `params`, а в component - через `useParams`.

**URL как state**

Состояние, которое должно пережить reload, back/forward и копирование ссылки, хранят в path или search params: page, filters, sort, search query, выбранная сущность. Краткоживущий dropdown или hover остаётся local state.

Search params являются строками. Их нужно parse, validate и приводить к default values. Нельзя считать `?page=abc` корректным числом только потому, что URL сформировал ваш UI.

**Data router: loaders и actions**

`createBrowserRouter` знает route tree до render и может запускать loaders всех matched routes параллельно. Это уменьшает waterfall, который возникает, когда parent сначала рендерится, затем его child начинает собственный request.

Loader получает Web `Request` с `request.signal`. Сигнал передают в `fetch`, чтобы router мог отменить устаревшую navigation. Loader может вернуть данные, `Response`, бросить `Response` с ошибкой или выполнить `redirect`.

Action обрабатывает отправку `<Form>` и другие mutations. После завершения action router revalidates loaders и синхронизирует экран с сервером. `useNavigation` показывает global pending navigation, а `useFetcher` выполняет loader/action без перехода на другой URL.

**Protected routes**

Для data router проверку сессии удобно выполнять в loader и бросать `redirect("/login")` до render приватного element. Нужно различать проверяемую сессию, подтверждённого пользователя и anonymous state, чтобы не показывать приватный UI на один кадр.

Эта проверка улучшает UX, но не безопасность. Пользователь может вызвать API напрямую, поэтому backend повторно проверяет authentication и permissions для каждого защищённого ресурса.

**Errors и code splitting**

`errorElement` обрабатывает ошибки loader, action и render в своей ветке; ошибка поднимается к ближайшей route boundary. 404 resource response можно показать иначе, чем неожиданный exception.

Route-level `lazy` загружает implementation route отдельным chunk. Для chunk load error нужна error boundary и возможность повторить или перезагрузить страницу. После deploy старый HTML может ссылаться на удалённый chunk, поэтому стратегия хранения assets и cache headers относится к устойчивости routing.

#### Пример React Router 6.4+

```tsx
import {
  createBrowserRouter,
  redirect,
  RouterProvider,
  type LoaderFunctionArgs,
} from "react-router-dom";

async function dashboardLoader({ request }: LoaderFunctionArgs) {
  const response = await fetch("/api/dashboard", {
    signal: request.signal,
  });

  if (response.status === 401) {
    const url = new URL(request.url);
    throw redirect(`/login?returnTo=${encodeURIComponent(url.pathname)}`);
  }

  if (!response.ok) {
    throw response;
  }

  return response.json();
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    errorElement: <RootRouteError />,
    children: [
      { index: true, element: <HomePage /> },
      {
        path: "dashboard",
        loader: dashboardLoader,
        element: <DashboardPage />,
      },
      { path: "login", element: <LoginPage /> },
    ],
  },
]);

export function App() {
  return <RouterProvider router={router} />;
}
```

`RootLayout` должен вывести `<Outlet />`. Loader отменяет устаревший fetch через `request.signal`, перенаправляет anonymous user до render и передаёт HTTP-ошибку в ближайший `errorElement`.

#### Ключевые уточнения

- React Router синхронизирует URL, history и route tree; он не является только условным render по строке path.
- Внутренние переходы используют `Link`/`NavLink`, а server fallback обеспечивает открытие deep links в SPA.
- Nested routes связывают URL segments, layouts, data и error boundaries.
- Shareable navigation state хранится в URL и проходит parsing/validation.
- Data router запускает matched loaders до render и передаёт AbortSignal для отмены устаревшей navigation.
- Action выполняет mutation, после чего router revalidates route data.
- Frontend redirect защищает пользовательский сценарий, а реальную authorization выполняет backend.
- Route-level lazy loading требует обработки chunk errors и корректной deploy/cache strategy.

#### Связанные темы

- [[Конспект для подготовки/React/Suspense и lazy]]
- [[Конспект для подготовки/React/Error Boundaries]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/Web Basics/URL в адресной строке]]
- [[Конспект для подготовки/Web Basics/Cookies и авторизация]]
- [[Конспект для подготовки/Web Basics/HTTP caching]]

#### Источники

- [React Router 6.30: Feature Overview](https://reactrouter.com/6.30.1/start/overview)
- [React Router 6.30: `createBrowserRouter`](https://reactrouter.com/6.30.1/routers/create-browser-router)
- [React Router 6.30: Loader](https://reactrouter.com/6.30.1/route/loader)
- [React Router 6.30: Action](https://reactrouter.com/6.30.1/route/action)
- [React Router 6.30: Error Element](https://reactrouter.com/6.30.1/route/error-element)
