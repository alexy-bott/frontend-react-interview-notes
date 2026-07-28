---
aliases:
  - auth system design frontend
  - protected routes
  - проектирование auth flow
  - frontend auth architecture
---

#### Ответ на 60 секунд

Auth flow во frontend проектируется как набор состояний и переходов: unknown session, unauthenticated, authenticated, refreshing, forbidden, logout. Нужно решить, как приложение узнаёт текущего пользователя, как отправляет authenticated requests, что делает при `401/403`, как обновляет access token, как защищает маршруты и как чистит cache/state при logout.

Protected routes не должны быть только “если нет user, redirect”. На старте приложения session может быть неизвестна, refresh может идти в фоне, пользователь может быть authenticated, но без нужной роли. Поэтому нужны loading gate, redirect policy, access denied UI, role/permission checks и единый API-layer для refresh.

Главная идея: auth - это не только login form. Это API boundary, security model, route access, cache cleanup, UX состояний и тестирование edge cases.

#### Ключевая схема

```text
app start
-> session unknown
-> load/refresh session
-> authenticated | unauthenticated
-> protected route check
-> allowed | forbidden | redirect
```

| Состояние | UI/поведение |
| --- | --- |
| unknown | splash/skeleton, запрос current user/refresh |
| unauthenticated | login page, redirect target |
| authenticated | app shell, user cache, allowed routes |
| refreshing | shared refresh promise, requests wait |
| forbidden | access denied, no refresh |
| logout | clear token, user, query cache, session |

#### Развернутый ответ

Auth начинается с источника истины. Приложение должно понять, есть ли пользователь: через `/me`, session endpoint, refresh endpoint или framework loader. Пока ответ неизвестен, нельзя уверенно показывать ни protected content, ни login redirect, иначе будет flicker или неправильный переход.

`401` и `403` имеют разный смысл. `401` может означать истёкший access token и запуск refresh flow. `403` означает, что пользователь известен, но действие запрещено; refresh здесь не поможет. UI должен показать access denied или скрыть действие заранее по permissions.

Protected route проверяет не только факт login, но и роль/permission. Например, route `/admin` требует `admin:read`. Если пользователь не authenticated - redirect на login. Если authenticated, но без права - forbidden page. Если session unknown - loading gate.

Refresh flow должен быть централизован в API layer. При пачке `401` нельзя запускать несколько refresh-запросов одновременно; нужен shared promise/queue. После успешного refresh исходные запросы повторяются один раз. После неуспеха приложение делает logout flow.

Logout должен очищать не только token. Нужно очистить user state, query cache с приватными данными, selected workspace, realtime connections, feature flags context и закрыть сессию на сервере. Иначе следующий пользователь на том же устройстве может увидеть старые данные из cache.

#### Где применяется во frontend

| Ситуация в проекте | Что проектируется | Конкретное решение |
| --- | --- | --- |
| Пользователь открывает protected URL после reload | session ещё неизвестна | route-level auth gate с состоянием `unknown` |
| Access token истёк у пяти запросов одновременно | возможен refresh storm | один shared refresh promise, остальные запросы ждут |
| Пользователь authenticated, но без роли admin | это не login problem | показать `403/access denied`, не делать refresh |
| Logout из одной вкладки | приватные данные могут остаться в cache | clear query cache/store + cross-tab logout event |
| После login нужно вернуть пользователя назад | redirect target должен сохраниться | хранить intended URL в location state/query |
| WebSocket открыт под старой сессией | соединение пережило logout | закрыть socket/realtime subscriptions при logout |

> [!faq]+ Уточнения
> - `unknown session` - отдельное состояние, не равное logout.
> - `401` и `403` обрабатываются по-разному.
> - Protected route должен учитывать permissions/roles.
> - Refresh централизуют в API client, а не в компонентах.
> - Logout очищает token, user state, query cache и realtime connections.
> - Cookie-based auth требует CSRF/CORS/cookie attributes.

#### Пример

```tsx
function ProtectedRoute({
  permission,
  children,
}: {
  permission?: string;
  children: React.ReactNode;
}) {
  const auth = useAuth();

  if (auth.status === "unknown" || auth.status === "refreshing") {
    return <PageSkeleton />;
  }

  if (auth.status === "unauthenticated") {
    return <Navigate to="/login" replace />;
  }

  if (permission && !auth.permissions.has(permission)) {
    return <AccessDenied />;
  }

  return children;
}
```

#### Частые ошибки

- Считать отсутствие user до загрузки session logout-состоянием.
- Делать refresh на `403`.
- Реализовывать refresh отдельно в каждом запросе/компоненте.
- Не чистить query cache при logout.
- Показывать protected content на мгновение до проверки session.
- Хранить long-lived secret в `localStorage` без оценки XSS-рисков.

#### Связанные темы

- [[Конспект для подготовки/Web Basics/Auth flow и refresh tokens]]
- [[Конспект для подготовки/Web Basics/Cookies и авторизация]]
- [[Конспект для подготовки/Web Basics/CSRF]]
- [[Конспект для подготовки/Web Basics/XSS]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/React/React Router]]
- [[Конспект для подготовки/Testing/Async UI формы и auth]]
- [[Конспект для подготовки/Web Basics/HTTP status codes и ошибки API]]

#### Источники

- [MDN: Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [OWASP: Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP: Cross Site Request Forgery Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
