---
aliases:
  - Adapter pattern
  - Facade pattern
  - adapter frontend
  - facade frontend
  - адаптер
  - фасад
---

#### Ответ на 60 секунд

Adapter и Facade помогают отделить приложение от неудобных внешних интерфейсов. Adapter приводит один интерфейс к другому: например, backend DTO со `snake_case` превращается в frontend-модель с `camelCase`, а SDK с нестандартным callback API превращается в Promise-based service. Facade даёт простой вход к сложной подсистеме: например, `authService.login()` скрывает refresh, cookies, headers, error mapping и storage.

Во frontend эти паттерны особенно полезны на границах: API layer, analytics SDK, payment SDK, auth, feature flags, browser APIs, date libraries, form adapters, generated clients. Компоненты не должны знать детали каждого внешнего контракта.

Главная разница: Adapter меняет форму интерфейса, Facade упрощает доступ к сложной системе. На практике они часто работают вместе: facade вызывает adapter внутри.

#### Ключевая схема

| Паттерн | Что делает | Frontend-пример |
| --- | --- | --- |
| Adapter | приводит внешний интерфейс к внутреннему контракту | `ApiUserDto -> User` |
| Facade | скрывает сложность подсистемы за простым API | `authService.login()` |
| DTO mapper | частный случай adapter | `full_name -> name` |
| SDK wrapper | facade/adapter вокруг сторонней библиотеки | `analytics.track(event)` |

```text
Component
-> app service/facade
-> adapter/mapper
-> external API/SDK/browser
```

#### Развернутый ответ

Adapter нужен, когда внешний контракт не совпадает с внутренней моделью приложения. Backend может отдавать `created_at`, `full_name`, вложенные объекты, nullable fields или enum-значения, которые неудобны UI. Adapter превращает это в стабильную frontend-модель: `createdAt`, `name`, подготовленные даты, нормализованные статусы.

Facade нужен, когда за простым действием стоит сложная последовательность. Например, login может включать request, refresh token policy, сохранение user state, обработку `401/422`, очистку query cache и analytics event. Компоненту формы не нужно знать всю эту механику; ему нужен понятный метод `login(credentials)`.

Эти паттерны уменьшают связность. Если поменялся backend DTO, правится mapper. Если поменялся analytics provider, правится wrapper. Если поменялась auth-схема, правится `authService`, а не десятки компонентов.

Важно не делать facade “божественным сервисом”. Если один `appService` знает auth, payments, profile, notifications и routing, он становится новой точкой сильной связности. Facade должен закрывать понятную подсистему.

#### Где применяется во frontend

| Ситуация в проекте | Что не так без паттерна | Как применить |
| --- | --- | --- |
| Компоненты читают `user.full_name` прямо из API response | внешний DTO протекает в UI | Adapter: `mapUserDto(dto): User` |
| В каждом компоненте повторяется обработка `401`, `403`, `422` | error policy размазана по UI | Facade/API client: единый `request` мапит ошибки в понятные app errors |
| Analytics SDK меняется с GA на Amplitude | весь UI зависит от конкретного SDK API | Facade: `analytics.track(name, payload)` скрывает provider |
| Payment SDK работает через callbacks | UI хочет Promise/async-await | Adapter: обернуть callback API в Promise-based interface |
| Browser storage используется напрямую в разных местах | ключи, parsing и fallback повторяются | Facade: `settingsStorage.getTheme()` / `setTheme()` |
| OpenAPI сгенерировал DTO, неудобный для компонента | generated type отражает backend, а не UI-модель | Adapter: generated DTO мапится в domain/view model |

> [!faq]+ Уточнения
> - Adapter меняет форму интерфейса, Facade упрощает работу со сложной подсистемой.
> - DTO mapper - частый frontend-Adapter.
> - API client/service часто является Facade для transport, auth, errors и validation.
> - Wrapper вокруг SDK уменьшает vendor lock-in.
> - Facade не должен становиться огромным глобальным сервисом на всё приложение.

#### Пример

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

function mapUserDto(dto: ApiUserDto): User {
  return {
    id: dto.id,
    name: dto.full_name,
    avatarUrl: dto.avatar_url,
  };
}

class UserService {
  async getCurrentUser() {
    const dto = await request<ApiUserDto>("/api/me");
    return mapUserDto(dto);
  }
}
```

Компонент получает `User` и не знает про `full_name`/`avatar_url`.

#### Частые ошибки

- Протаскивать DTO глубоко в JSX.
- Называть любой helper фасадом.
- Делать один общий facade для всего приложения.
- Прятать в adapter бизнес-логику, которая должна быть в domain/use-case.
- Оборачивать SDK, но всё равно отдавать наружу SDK-specific types.

#### Связанные темы

- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/TypeScript/Проверка данных с backend]]
- [[Конспект для подготовки/Patterns/Strategy во frontend]]
- [[Конспект для подготовки/Principles/SOLID во frontend]]
- [[Конспект для подготовки/Web Basics/OpenAPI и Swagger]]
- [[Конспект для подготовки/JavaScript/Fetch и работа с API]]
- [[Конспект для подготовки/React/RTK Query]]

#### Источники

- Design Patterns: Elements of Reusable Object-Oriented Software
- [Martin Fowler: Patterns of Enterprise Application Architecture](https://martinfowler.com/books/eaa.html)
