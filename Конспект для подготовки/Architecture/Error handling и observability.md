---
aliases:
  - error handling
  - frontend observability
  - мониторинг frontend
  - обработка ошибок
---

#### Ответ на 60 секунд

Error handling во frontend - это не один `try/catch`, а система: где ошибка возникла, как её показать пользователю, как восстановиться, что залогировать и как потом найти причину в production. Ошибки бывают разными: render error, network error, validation error, business error, unhandled promise rejection, runtime exception в third-party коде.

Observability отвечает на вопрос “что происходит у пользователей после релиза?”. Для этого нужны error tracking, logs, performance metrics, breadcrumbs, release version, source maps, user/session context без лишних персональных данных. Надёжный frontend не просто падает тише, а даёт команде достаточно сигналов, чтобы понять impact и исправить причину.

#### Ключевая схема

| Уровень | Что делать |
| --- | --- |
| UI fallback | показать понятное состояние, не ломать весь экран |
| Error Boundary | ловить render errors в React-дереве |
| API layer | нормализовать network/status/business errors |
| Global handlers | `unhandledrejection`, `error` для последнего рубежа |
| Monitoring | error tracking, release, source maps, breadcrumbs |
| Privacy | не отправлять tokens, cookies, PII без необходимости |

#### Развернутый ответ

Error handling начинается с классификации ошибки. Render error, network error, status error, validation error, business error, unhandled promise rejection и runtime exception требуют разных реакций. Один общий fallback “что-то пошло не так” скрывает полезный смысл и для пользователя, и для команды.

React Error Boundary ловит ошибки рендера, lifecycle и constructors ниже по дереву. Он не ловит event handlers, async callbacks, SSR-ошибки и ошибки внутри самого boundary. Поэтому boundary - только один уровень защиты: рядом с ним нужны API error handling, fallback states, global handlers и мониторинг.

Ошибки запросов должны маппиться в понятные сценарии. `401` может вести к re-auth, `403` - к экрану запрета, `404` - к not found, `409` - к конфликту версии, `422` - к ошибкам формы. API-слой помогает UI различать эти случаи и не превращать все ответы в один generic error.

Observability собирает диагностический контекст: route, release version, feature flag state, breadcrumbs, request id/correlation id, performance metrics и source maps. Breadcrumbs показывают короткую историю действий перед ошибкой: route change, click, request, state change. Source maps помогают сопоставить минифицированный production stack trace с исходным кодом.

Privacy - часть observability. В monitoring не отправляют tokens, cookies, full request body, лишние персональные данные и чувствительные бизнес-поля. Диагностика должна помогать искать причину, но не создавать новую утечку.

> [!faq]+ Уточнения
> - Error Boundary ловит render/lifecycle errors ниже себя, но не ловит event handlers и async callbacks.
> - API errors маппят по статусам и доменным причинам, а не в один generic fallback.
> - Breadcrumbs показывают события перед ошибкой: route, click, request, flags.
> - Source maps нужны для чтения production stack traces.
> - Monitoring должен содержать release/context, но не tokens, cookies и лишний PII.

#### Пример

```tsx
function ProfileRoute() {
  return (
    <ErrorBoundary fallback={<ProfileFallback />}>
      <Profile />
    </ErrorBoundary>
  );
}
```

```ts
window.addEventListener("unhandledrejection", (event) => {
  reportError(event.reason, {
    source: "unhandledrejection",
  });
});
```

Error Boundary защищает UI-зону, а глобальный handler является последним рубежом для ошибок, которые не были обработаны ближе к месту возникновения.

#### Частые ошибки

- Показывать один и тот же fallback для всех типов ошибок.
- Ставить Error Boundary только на уровень всего приложения.
- Логировать ошибку без release version и route.
- Отправлять в monitoring tokens, cookies, full request body или PII.
- Не проверять, что source maps реально сопоставляют production stack trace.
- Скрывать ошибку от пользователя и не оставлять команде диагностического сигнала.

#### Связанные темы

- [[Конспект для подготовки/React/Error Boundaries]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]
- [[Конспект для подготовки/Testing/E2E testing]]
- [[Конспект для подготовки/Testing/Flaky tests]]

#### Источники

- [React: Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [MDN: Window error event](https://developer.mozilla.org/en-US/docs/Web/API/Window/error_event)
- [MDN: unhandledrejection event](https://developer.mozilla.org/en-US/docs/Web/API/Window/unhandledrejection_event)
- [web.dev: Metrics](https://web.dev/articles/metrics)
- [Sentry Docs: Source Maps](https://docs.sentry.io/platforms/javascript/sourcemaps/)
