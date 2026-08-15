# Обработка ошибок через Error Boundaries

<!-- NOTE-NAV-TOP:START -->
[← key](<./08 key.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Хуки →](<./10 Хуки.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Граница ошибок (Error Boundary) - React-компонент, который перехватывает ошибку в дочернем React tree, показывает fallback вместо повреждённого поддерева и позволяет отправить технические данные в monitoring. Границы размещают по зонам отказа: вокруг route, независимого widget или рискованной сторонней интеграции, чтобы локальная ошибка не скрывала весь интерфейс.

В React 18 Error Boundary реализуется class component через `static getDerivedStateFromError` для fallback-state и `componentDidCatch` для логирования. Он не обрабатывает ошибки event handlers, произвольных asynchronous callbacks, server rendering, а также ошибку, возникшую внутри самого boundary. Ошибки HTTP и бизнес-ошибки являются состоянием данных и обычно отображаются через обычный error state, retry и сообщения формы.

## Ключевая схема

| Ситуация | Обрабатывает Error Boundary? | Подход |
| --- | --- | --- |
| Потомок бросил ошибку во время render | да | ближайший boundary показывает fallback |
| Ошибка в class lifecycle потомка | да | fallback + `componentDidCatch` |
| Ошибка в `onClick` | нет | `try/catch`, локальный state и reporting в event handler |
| Ошибка внутри `setTimeout` или Promise callback | нет автоматически | обработать в async-flow и обновить UI state |
| Ошибка во время SSR | нет на клиентском boundary | обработка framework/server renderer |
| Ошибка в fallback самого boundary | нет этим же boundary | её может поймать boundary выше |

## Базовая модель

Когда дочернее поддерево бросает поддерживаемую render-ошибку, React ищет ближайший Error Boundary вверх по React tree. `getDerivedStateFromError` возвращает state, из-за которого следующий render boundary показывает fallback. После commit `componentDidCatch` получает ошибку и component stack для мониторинга.

Если подходящего boundary нет, React удаляет повреждённое дерево из UI, потому что оставлять потенциально несогласованный интерфейс опаснее, чем скрыть его. Поэтому один boundary у корня полезен как последний уровень защиты, но локальные границы нужны для независимых частей продукта.

Error Boundary остаётся в fallback-state после ошибки. Для повторной попытки нужно явно сбросить его state, изменить `key` boundary или использовать библиотеку с `resetErrorBoundary`. Автоматический повтор без устранения причины может создать цикл падений.

## Развернутый ответ

### Где ставить границы

Граница должна соответствовать UX-зоне, которую можно заменить независимо. Route-level boundary показывает ошибку экрана, сохраняя shell приложения. Widget-level boundary скрывает только график или редактор. Boundary вокруг стороннего виджета защищает остальной интерфейс от ошибки интеграции.

Слишком высокий boundary превращает локальный сбой в потерю большого участка UI. Boundary вокруг каждого маленького компонента создаёт шум и множество бессмысленных fallbacks. Границу выбирают по сценарию восстановления пользователя, а не по количеству компонентов.

### Что делают два class API

`static getDerivedStateFromError(error)` вызывается во время обработки ошибки и должен чисто вычислить state для fallback. Side effects в нём не выполняются.

`componentDidCatch(error, errorInfo)` вызывается для уже обработанной ошибки и подходит для отправки `error`, обычного JavaScript stack и `errorInfo.componentStack` в monitoring. Component stack показывает цепочку React-компонентов; production sourcemaps помогают восстановить имена и строки minified-кода.

Логи не должны без фильтрации включать props, form values, tokens или другие чувствительные данные. Boundary отвечает за изоляцию UI, а политика observability - за дедупликацию, release/version, user context и privacy.

### Что Error Boundary не заменяет

Event handler выполняется после render в обычном event flow. Его ожидаемую ошибку обрабатывают там, где запускается действие. Ошибка запроса также не обязана бросаться во время render: query layer обычно возвращает `error`, а UI показывает retry, toast или field error.

Ошибка в asynchronous callback не становится render-ошибкой только потому, что callback был создан компонентом. Её нужно перехватить в Promise/`async`-цепочке и отразить через state либо передать механизму framework/library, который осознанно интегрирует её с Error Boundary.

### Error Boundary и Suspense

Suspense Boundary показывает fallback, когда дочерний render приостанавливается на поддерживаемом асинхронном ресурсе; Error Boundary показывает fallback при ошибке. Это разные механизмы. Если Promise, прочитанный Suspense-совместимым API, отклоняется, ошибка может перейти к ближайшему Error Boundary.

## Пример

Boundary принимает fallback и callback мониторинга. Сам callback передаётся снаружи, поэтому компонент не привязан к конкретному сервису.

```tsx
import { Component, type ErrorInfo, type ReactNode } from "react";

type ErrorBoundaryProps = {
  children: ReactNode;
  fallback: ReactNode;
  onError?: (error: Error, info: ErrorInfo) => void;
};

type ErrorBoundaryState = {
  hasError: boolean;
};

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    this.props.onError?.(error, info);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}
```

Пример использования:

```tsx
function logError(error: Error, componentStack: string | null) {
  console.error(error, componentStack);
}

<ErrorBoundary
  fallback={<p role="alert">The chart could not be displayed.</p>}
  onError={(error, info) => logError(error, info.componentStack)}
>
  <AnalyticsChart />
</ErrorBoundary>
```

В production `logError` заменяют адаптером сервиса monitoring. Если нужен retry, родитель может изменить `key` boundary после явного действия пользователя либо использовать `react-error-boundary`, где reset является частью API.

## Где применяется во frontend

| Граница | Что сохраняется при ошибке | Возможный fallback |
| --- | --- | --- |
| Корень приложения | ничего ниже boundary | аварийный экран и перезагрузка |
| Route content | navigation и app shell | ошибка страницы и повторная загрузка route |
| Dashboard widget | остальные widgets | локальное сообщение и retry |
| Rich text editor | остальная форма | восстановление draft или упрощённый input |
| Сторонняя интеграция | собственный UI приложения | сообщение о недоступности внешнего блока |

## Ключевые уточнения

- Error Boundary ловит ошибки потомков, но не собственную ошибку; для неё нужен boundary выше.
- `getDerivedStateFromError` выбирает fallback-state, а `componentDidCatch` выполняет reporting после ошибки.
- Event, async и API errors имеют собственные пути обработки и не становятся автоматически render errors.
- Размер boundary определяется независимым пользовательским сценарием восстановления.
- Suspense fallback означает ожидание ресурса, Error Boundary fallback - ошибку; это не один механизм.

## Связанные темы

- [Жизненный цикл](<./21 Жизненный цикл.md>)
- [Suspense и lazy](<./29 Suspense и lazy.md>)
- [SSR и SSG](<./27 SSR и SSG.md>)
- [Обработка ошибок и наблюдаемость](<../Архитектура/05 Обработка ошибок и наблюдаемость.md>)

## Источники

- [React 18: Catching rendering errors with an Error Boundary](https://18.react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [React 18: componentDidCatch](https://18.react.dev/reference/react/Component#componentdidcatch)
- [React 18: Suspense](https://18.react.dev/reference/react/Suspense)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← key](<./08 key.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Хуки →](<./10 Хуки.md>)
<!-- NOTE-NAV-BOTTOM:END -->
