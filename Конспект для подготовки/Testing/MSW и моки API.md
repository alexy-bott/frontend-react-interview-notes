---
aliases:
  - MSW
  - Mock Service Worker
  - API mocks
  - network mocking
  - моки API
---

#### Ответ на 60 секунд

MSW, или Mock Service Worker, позволяет мокать сеть на уровне HTTP-запросов, а не подменять внутренние функции приложения. Это значит, что компонент или сервис продолжает вызывать настоящий `fetch`/HTTP-клиент, но запрос перехватывается тестовой средой и получает контролируемый ответ. Такой подход ближе к реальному приложению, чем мокать каждую функцию API-клиента вручную.

В unit/integration тестах MSW помогает проверять loading, success, empty state, validation error, server error, timeout и retry logic. В браузере MSW может работать через service worker, а в Node-тестах - через server setup. Главная идея: тест описывает поведение внешней границы, а не детали реализации внутри компонента.

Один глобальный мок на все случаи делает тесты слепыми к разным состояниям API. Для каждого сценария задают отдельный handler: успешный ответ, `500`, задержка, пустой массив, ошибка авторизации. После теста handlers сбрасывают, чтобы сценарии не протекали друг в друга.

#### Ключевая схема

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

#### Развернутый ответ

MSW полезен там, где нужно проверить поведение приложения вокруг HTTP boundary. Если заменить `apiClient` через `jest.mock`, тест начинает зависеть от конкретной структуры модулей и проверяет вызов функции. MSW оставляет настоящий request flow: компонент вызывает `fetch` или HTTP-клиент, запрос перехватывается на уровне сети, UI получает контролируемый response.

Для component/integration tests это даёт практичный баланс. Можно проверить loading, success, empty state, `401`, `422`, `500`, timeout, retry и optimistic update, не поднимая реальный backend. Для чистых unit-тестов проще мокать функцию. Для E2E чаще используют тестовый backend, seeded database или routing/mocks самого E2E-инструмента.

Проверяют не факт вызова handler-а, а пользовательский результат: loader появился и исчез, список отрисовался, ошибка показана, submit button стал disabled, retry сработал, form errors привязались к полям. Так тест остаётся про поведение, а не про внутреннюю проводку.

Изоляция handlers обязательна. Сценарий, добавленный через `server.use(...)` в одном тесте, сбрасывают после теста через `resetHandlers()`. Иначе success/error/timeout из одного теста может протечь в следующий и создать flaky.

> [!faq]+ Уточнения
> - MSW мокает HTTP boundary, а не внутреннюю функцию API-клиента.
> - Основная зона MSW - component/integration tests с network behavior.
> - Для E2E часто используют test backend, seeded data или network routing инструмента.
> - Assertions должны смотреть на UI result, а не только на вызов handler-а.
> - Handlers сбрасывают после каждого теста.

#### Пример

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

beforeAll(() => server.listen());
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

#### Частые ошибки

- Мокать внутренний API-клиент и терять проверку реального request flow.
- Делать один общий happy path и не проверять ошибки.
- Не сбрасывать handlers между тестами.
- Проверять implementation details вместо поведения UI.
- Забывать про loading и empty states.
- Мокать API так, что response не похож на реальный контракт backend.

#### Связанные темы

- [[Конспект для подготовки/Testing/React Testing Library]]
- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]
- [[Конспект для подготовки/Testing/Async UI формы и auth]]
- [[Конспект для подготовки/JavaScript/Fetch и работа с API]]
- [[Конспект для подготовки/Web Basics/HTTP запрос]]

#### Источники

- [MSW documentation](https://mswjs.io/docs/)
