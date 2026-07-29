# Error handling и observability

<!-- NOTE-NAV-TOP:START -->
[← API слой и контракты](<./API слой и контракты.md>) · [↑ Architecture](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Feature flags →](<./Feature flags.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Обработка ошибок определяет, как приложение классифицирует сбой, сохраняет работоспособную границу и помогает пользователю восстановиться. Наблюдаемость (observability) даёт команде production-сигналы для ответа на вопросы: какой release и сценарий сломался, сколько пользователей затронуто и где искать причину.

Ожидаемые API/domain errors обрабатывают рядом со сценарием и показывают конкретное действие. Неожиданные render/runtime errors изолируют Error Boundaries и последними global handlers. В error tracking передают stack trace, component/route context, release, breadcrumbs и correlation id, но очищают tokens и персональные данные, ограничивают объём и проверяют source maps.

## Ключевая схема

```text
error
-> classify expected/unexpected + scope
-> user fallback/recovery
-> diagnostic event with safe context
-> aggregation and alert by impact
-> fix linked to release
-> verify recovery metrics
```

| Класс | Где обрабатывается | Пользовательский результат |
| --- | --- | --- |
| Validation/domain | form/use case | точное сообщение и исправление input |
| HTTP/network | API/query boundary | retry, re-auth, forbidden или offline state |
| Render | ближайший Error Boundary | fallback одной зоны и reset |
| Event/async callback | локальный `try/catch`/Promise handler | сохранение сценария и report |
| Unhandled runtime | global handler как последний рубеж | report и безопасное восстановление/перезагрузка |

## Базовая модель

Expected error является частью контракта: неверный промокод, `409` conflict, отсутствие permission. Его не следует превращать в исключение уровня всего приложения. Unexpected error нарушает предположение кода: обращение к `undefined`, invalid invariant или ошибка SDK. Для него важны isolation и диагностика.

React 18 Error Boundary ловит исключения во время render, constructor и lifecycle descendants. Он не ловит event handlers, произвольный async callback, SSR error и ошибку внутри самого boundary. Поэтому boundary дополняет, а не заменяет API handling и локальные `try/catch`.

Observability обычно объединяет errors, logs, metrics и traces. Breadcrumbs - короткая последовательность безопасных событий перед сбоем; correlation/request id связывает frontend error с backend logs. Сам по себе большой поток events без release и ownership не делает систему наблюдаемой.

## Развернутый ответ

**Boundary placement.** App-level boundary предотвращает полностью белый экран. Route/widget boundaries позволяют остальной оболочке работать и дают перезапустить только сломанную зону. Слишком мелкие boundaries создают множество несогласованных fallbacks, поэтому граница соответствует независимо восстанавливаемому сценарию.

**Recovery.** Fallback объясняет, что не выполнено, сохраняет введённые данные по возможности и предлагает осмысленный retry, navigation или reload. Повтор без сброса сломанного state вызывает ту же ошибку; boundary reset связан со сменой route/key или явной reset policy.

**Global events.** `window.error` и `unhandledrejection` собирают то, что не было обработано ближе к источнику. Они не знают UX-контекста и могут увидеть third-party/browser extension noise, поэтому events фильтруют, deduplicate и rate-limit.

**Source maps.** Production stack содержит minified positions. Source maps связывают их с source files и конкретным release artifact. Неподходящая map от другого build даёт ложный stack; pipeline загружает maps с release id и проверяет реальный test error. Публичная выдача source maps оценивается отдельно от загрузки в закрытый monitoring service.

**Privacy.** URL query, form values, request bodies и breadcrumbs могут содержать PII или secrets. Политика allowlist безопаснее попытки убрать несколько известных полей после сбора. Scrubbing выполняют до отправки и повторяют на ingestion boundary.

**Alerts.** Alert строят по impact и regression: новая ошибка после release, рост affected sessions или падение успешности checkout. Уведомление на каждый event создаёт noise и скрывает реальный incident.

## Пример

```tsx
function ProfileRoute() {
  return (
    <RouteErrorBoundary
      fallback={({ reset }) => (
        <ProfileFallback onRetry={reset} />
      )}
    >
      <Profile />
    </RouteErrorBoundary>
  );
}
```

```ts
window.addEventListener("unhandledrejection", (event) => {
  reportUnexpectedError(event.reason, {
    source: "unhandledrejection",
    route: location.pathname,
    release: APP_RELEASE,
  });
});
```

`RouteErrorBoundary` обозначает project/library abstraction вокруг React 18 class boundary. Global handler только сообщает о необработанной причине; ожидаемые Promise rejections должны быть обработаны раньше и не попадать сюда.

## Ключевые уточнения

- Expected domain error является состоянием сценария, а не обязательно incident; unexpected error требует isolation и диагностики.
- Error Boundary покрывает render/lifecycle descendants, но не все источники JavaScript errors.
- Fallback без reset/recovery policy скрывает экран, но не восстанавливает приложение.
- Source map должна соответствовать точному release artifact; наличие файла само по себе не гарантирует читаемый stack.
- Observability context собирают по allowlist и минимизации данных, а alerts привязывают к impact, не к каждому event.

## Связанные темы

- [Error Boundaries](<../React/Error Boundaries.md>)
- [API слой и контракты](<./API слой и контракты.md>)
- [Feature flags](<./Feature flags.md>)
- [E2E testing](<../Testing/E2E testing.md>)
- [Memory leaks и profiling](<../Browser Internals/Memory leaks и profiling.md>)

## Источники

- [React: Error Boundary](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [MDN: Window error event](https://developer.mozilla.org/en-US/docs/Web/API/Window/error_event)
- [MDN: unhandledrejection event](https://developer.mozilla.org/en-US/docs/Web/API/Window/unhandledrejection_event)
- [Sentry: Source Maps](https://docs.sentry.io/platforms/javascript/sourcemaps/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← API слой и контракты](<./API слой и контракты.md>) · [↑ Architecture](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Feature flags →](<./Feature flags.md>)
<!-- NOTE-NAV-BOTTOM:END -->
