# Adapter и Facade во frontend

<!-- NOTE-NAV-TOP:START -->
[← Strategy во frontend](<./Strategy во frontend.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Observer PubSub и события →](<./Observer PubSub и события.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Adapter («Адаптер») преобразует интерфейс одной сущности в контракт, который ожидает приложение. Например, он превращает DTO с `snake_case` в внутреннюю модель или callback API стороннего SDK в `Promise`.

Facade («Фасад») предоставляет небольшой согласованный API к более сложной подсистеме. Например, `authService.login()` может скрывать HTTP-запрос, нормализацию ошибок и обновление сессии. Adapter меняет форму взаимодействия, Facade уменьшает число деталей, с которыми работает вызывающий код; внутри одного Facade могут использоваться несколько adapters.

## Ключевая схема

| Паттерн | Исходная проблема | Результат |
| --- | --- | --- |
| Adapter | внешний интерфейс несовместим с внутренним | совместимый контракт |
| Facade | подсистема требует знать много участников и шагов | единая точка входа для типового сценария |

```text
component/use case
-> facade приложения
-> adapter или mapper
-> проверенный внешний API, SDK или browser API
```

## Базовая модель

Adapter располагается на границе двух контрактов. Его задача - перевести названия, структуру, типы или способ вызова, сохранив смысл операции. Для DTO это может быть преобразование `created_at: string` в `createdAt: Date`; для callback API - обёртка, которая завершает `Promise` при вызове callback.

Facade располагается перед подсистемой. Он координирует несколько участников и даёт вызывающему коду операции на языке приложения: `loadCurrentUser`, `trackPurchase`, `openCheckout`. Компонент знает назначение операции, но не знает порядок вызовов внутренних клиентов.

Оба паттерна уменьшают связанность с внешней реализацией. Если меняется DTO, исправляется adapter; если меняется последовательность auth flow, исправляется Facade. Это работает только тогда, когда наружу не протекают типы, исключения и детали заменяемой системы.

## Развернутый ответ

**Adapter и проверка данных.** TypeScript-тип не проверяет JSON во время выполнения. Сначала внешний ответ разбирают и убеждаются, что он имеет допустимую структуру, затем adapter преобразует проверенный DTO во внутреннюю модель. Иногда эти шаги объединены одной parser-функцией, но у них разные задачи: validation отвергает некорректные данные, adaptation меняет корректный контракт.

**Adapter и бизнес-логика.** Переименование полей, нормализация nullable-значений и преобразование формата даты относятся к границе данных. Решение «может ли пользователь отменить заказ» зависит от правил предметной области и не должно случайно прятаться в DTO mapper.

**Граница Facade.** Facade закрывает одну связную подсистему или сценарий. `analytics`, `auth` и `payments` обычно требуют разных facade. Один `appService` со всеми методами создаёт центральную зависимость, которую трудно изменять и тестировать.

**Компромисс.** Дополнительный слой требует кода и именования. Для стабильного локального API прямой вызов может быть понятнее. Adapter или Facade оправдан, когда внешняя деталь уже повторяется, меняется независимо, затрудняет тестирование или не должна определять внутреннюю модель приложения.

## Где применяется во frontend

| Ситуация | Решение | Практический результат |
| --- | --- | --- |
| Backend отдаёт `full_name` и `avatar_url` | DTO adapter | компоненты работают со стабильными `name` и `avatarUrl` |
| SDK использует callbacks | adapter в `Promise` API | use case использует обычный `async/await` |
| Analytics provider имеет собственные event types | Facade `analytics.track` | замена SDK не затрагивает компоненты |
| Авторизация состоит из нескольких запросов и обновлений cache | Auth Facade | UI запускает один понятный сценарий |
| `localStorage` используется в разных модулях | storage Facade | ключи, JSON parsing и fallback определены один раз |
| OpenAPI-клиент отражает транспортный контракт | adapter в domain/view model | сгенерированные типы не распространяются по JSX |

## Пример

Adapter преобразует уже проверенный DTO во внутреннюю модель:

```ts
type ApiUserDto = {
  id: number;
  full_name: string;
  avatar_url: string | null;
};

type User = {
  id: number;
  name: string;
  avatarUrl: string | null;
};

type UserApi = {
  getCurrentUser(): Promise<unknown>;
};

function parseApiUserDto(value: unknown): ApiUserDto {
  if (typeof value !== "object" || value === null) {
    throw new Error("Invalid user response");
  }

  const dto = value as Record<string, unknown>;
  if (
    typeof dto.id !== "number" ||
    typeof dto.full_name !== "string" ||
    (typeof dto.avatar_url !== "string" && dto.avatar_url !== null)
  ) {
    throw new Error("Invalid user response");
  }

  return {
    id: dto.id,
    full_name: dto.full_name,
    avatar_url: dto.avatar_url,
  };
}

function mapUserDto(dto: ApiUserDto): User {
  return {
    id: dto.id,
    name: dto.full_name,
    avatarUrl: dto.avatar_url,
  };
}

function createUserFacade(api: UserApi) {
  return {
    async getCurrentUser(): Promise<User> {
      const json: unknown = await api.getCurrentUser();
      const dto = parseApiUserDto(json);
      return mapUserDto(dto);
    },
  };
}
```

`parseApiUserDto` проверяет внешние данные, `mapUserDto` меняет их форму, а Facade задаёт единый сценарий получения пользователя. Компонент получает `User` и не зависит от структуры ответа API.

## Ключевые уточнения

- Adapter отвечает за совместимость контрактов, а Facade - за упрощённый доступ к подсистеме. Они могут использоваться вместе, но не являются синонимами.
- Приведение `response as ApiUserDto` не проверяет backend-ответ. Runtime-проверка выполняется до безопасной адаптации данных.
- Хороший wrapper не возвращает наружу специфичные типы и ошибки SDK, от которого должен изолировать приложение.
- Facade не обязан скрывать каждую возможность подсистемы. Он предоставляет только устойчивые операции, нужные приложению.
- Дополнительная прослойка оправдана реальной границей изменений; локальный helper не становится полезнее только из-за названия `Adapter`.

## Связанные темы

- [API слой и контракты](<../Architecture/API слой и контракты.md>)
- [Проверка данных с backend](<../TypeScript/Проверка данных с backend.md>)
- [Strategy во frontend](<./Strategy во frontend.md>)
- [Factory Singleton и lifecycle](<./Factory Singleton и lifecycle.md>)
- [SOLID во frontend](<../Principles/SOLID во frontend.md>)
- [OpenAPI и Swagger](<../Web Basics/OpenAPI и Swagger.md>)
- [Fetch и работа с API](<../JavaScript/Fetch и работа с API.md>)
- [RTK Query](<../React/RTK Query.md>)

## Источники

- Erich Gamma et al. Design Patterns: Elements of Reusable Object-Oriented Software
- [Martin Fowler: Data Transfer Object](https://martinfowler.com/eaaCatalog/dataTransferObject.html)
- [Martin Fowler: Gateway](https://martinfowler.com/eaaCatalog/gateway.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Strategy во frontend](<./Strategy во frontend.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Observer PubSub и события →](<./Observer PubSub и события.md>)
<!-- NOTE-NAV-BOTTOM:END -->
