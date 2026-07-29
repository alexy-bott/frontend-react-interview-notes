# MSW и моки API

<!-- NOTE-NAV-TOP:START -->
[← React Testing Library](<./React Testing Library.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Async UI формы и auth →](<./Async UI формы и auth.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

MSW (Mock Service Worker) перехватывает HTTP requests на network boundary. Application использует настоящий `fetch`/client, serialization и response handling, а test handler возвращает контролируемый status, headers и body. Это проверяет frontend request flow глубже, чем `jest.mock(apiClient)`, но не подтверждает совместимость mock response с настоящим backend.

В unit/integration тестах MSW помогает проверять loading, success, empty state, validation error, server error, timeout и retry logic. В браузере MSW может работать через service worker, а в Node-тестах - через server setup. Главная идея: тест описывает поведение внешней границы, а не детали реализации внутри компонента.

Один глобальный мок на все случаи делает тесты слепыми к разным состояниям API. Для каждого сценария задают отдельный handler: успешный ответ, `500`, задержка, пустой массив, ошибка авторизации. После теста handlers сбрасывают, чтобы сценарии не протекали друг в друга.

## Ключевая схема

```text
component -> real fetch/http client -> MSW handler -> mocked HTTP response
```

| Что мокать | Почему |
| --- | --- |
| API success | happy path UI |
| API error | error state and retry |
| empty response | empty state |
| delayed response | loading and pending UI |
| auth error | redirect/logout behavior |
| validation error | field errors and form alert |

## Базовая модель

MSW полезен там, где нужно проверить поведение приложения вокруг HTTP boundary. Если заменить `apiClient` через `jest.mock`, тест начинает зависеть от конкретной структуры модулей и проверяет вызов функции. MSW оставляет настоящий request flow: компонент вызывает `fetch` или HTTP-клиент, запрос перехватывается на уровне сети, UI получает контролируемый response.

В browser MSW использует Service Worker, а `setupServer` в Node не поднимает настоящий HTTP server: библиотека перехватывает исходящие requests внутри процесса. Один набор handlers можно переиспользовать в development, component tests и Storybook-like environments.

## Развернутый ответ

Для component/integration tests это даёт практичный баланс. Можно проверить loading, success, empty state, `401`, `422`, `500`, timeout, retry и optimistic update, не поднимая реальный backend. Для чистых unit-тестов проще мокать функцию. Для E2E чаще используют тестовый backend, seeded database или routing/mocks самого E2E-инструмента.

Проверяют не факт вызова handler-а, а пользовательский результат: loader появился и исчез, список отрисовался, ошибка показана, submit button стал disabled, retry сработал, form errors привязались к полям. Так тест остаётся про поведение, а не про внутреннюю проводку.

Изоляция handlers обязательна. Сценарий, добавленный через `server.use(...)` в одном тесте, сбрасывают после теста через `resetHandlers()`. Иначе success/error/timeout из одного теста может протечь в следующий и создать flaky.

Unhandled requests в tests настраивают как error, чтобы новый endpoint не ушёл случайно в real network и не прошёл без соответствующего scenario. Handlers строят из contract fixtures/schema; иначе frontend и mock могут одновременно принять несовместимое изменение, пока integration с backend уже сломана.

## Пример

```ts
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

const server = setupServer(
  http.get("/api/users", () => {
    return HttpResponse.json([
      { id: 1, name: "Ann" },
    ]);
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

В конкретном тесте можно переопределить сценарий:

```ts
server.use(
  http.get("/api/users", () => {
    return new HttpResponse(null, { status: 500 });
  }),
);
```

## Ключевые уточнения

- MSW сохраняет frontend HTTP stack, но заменяет backend и network transport beyond interception.
- Handler фиксирует status, headers, delay и body конкретного scenario; один global happy path не покрывает error semantics.
- Unhandled request в test environment должен падать, иначе suite может обратиться во внешнюю сеть.
- Runtime handlers сбрасывают после каждого test, initial handlers остаются baseline.
- Fixture синхронизируют с OpenAPI/contract test или real integration, иначе mock способен достоверно имитировать неправильный API.
- Assertions подтверждают пользовательский result и при необходимости request contract, а не внутреннее устройство API module.

## Связанные темы

- [React Testing Library](<./React Testing Library.md>)
- [Стратегия тестирования frontend](<./Стратегия тестирования frontend.md>)
- [Async UI формы и auth](<./Async UI формы и auth.md>)
- [Fetch и работа с API](<../JavaScript/Fetch и работа с API.md>)
- [HTTP запрос](<../Web Basics/HTTP запрос.md>)

## Источники

- [MSW documentation](https://mswjs.io/docs/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← React Testing Library](<./React Testing Library.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Async UI формы и auth →](<./Async UI формы и auth.md>)
<!-- NOTE-NAV-BOTTOM:END -->
