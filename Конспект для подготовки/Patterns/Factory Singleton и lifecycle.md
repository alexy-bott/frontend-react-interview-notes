---
aliases:
  - Factory pattern
  - Singleton pattern
  - factory frontend
  - singleton frontend
  - lifecycle services
---

#### Ответ на 60 секунд

Factory - это паттерн создания объектов или сервисов через отдельную функцию/метод, а не вручную в каждом месте. Singleton - это один общий экземпляр на приложение или процесс. Во frontend эти темы часто всплывают вокруг API clients, SDK, analytics, WebSocket connections, stores, feature flag clients, i18n и browser-only services.

Factory полезна, когда создание зависит от env, runtime config, auth token, platform, test mock или SSR/client boundary. Singleton может быть удобен для общего client-а, но опасен в SSR, тестах и multi-user окружении: общий экземпляр может случайно хранить состояние между запросами или тестами.

Главное правило: создание и lifecycle должны быть явными. Нужно понимать, где создаётся client, кто его переиспользует, когда он очищается, можно ли заменить его в тесте и не протекает ли состояние между пользователями.

#### Ключевая схема

| Паттерн | Что решает | Риск |
| --- | --- | --- |
| Factory | централизует создание зависимости | лишняя абстракция для простого объекта |
| Singleton | даёт один общий instance | глобальное состояние, сложные тесты, SSR leaks |
| Provider | отдаёт instance через React/Vue context | нужно следить за lifecycle |
| Composition root | место сборки зависимостей | не размазывать creation по компонентам |

#### Развернутый ответ

Factory появляется, когда объект нельзя просто создать inline. Например, API client должен знать base URL, headers, credentials, refresh policy и logger. Если каждый компонент создаёт его сам, настройки начнут расходиться. Factory собирает зависимость в одном месте: `createApiClient(config)`.

Singleton часто возникает естественно: `analytics`, `queryClient`, `featureFlagClient`, `i18n`, `socket`. Проблема не в самом единственном экземпляре, а в скрытом mutable state. В SPA singleton может быть нормальным, если это действительно app-level dependency. В SSR один module-level singleton может стать багом, если хранит user-specific данные между запросами.

В тестах singleton мешает изоляции. Если один тест поменял глобальный client, следующий тест может получить загрязнённое состояние. Поэтому для тестируемости зависимости часто передают через provider, параметры функции или factory, которая создаёт fresh instance для каждого теста.

Factory и Singleton часто комбинируются: factory создаёт instance, а composition root решает, будет он singleton на всё приложение или отдельным для запроса/теста. Так lifecycle становится управляемым, а не случайным.

#### Где применяется во frontend

| Ситуация в проекте | Что создаётся | Какой подход выбрать |
| --- | --- | --- |
| API client зависит от base URL и auth policy | HTTP client/service | factory `createApiClient(config)` в app setup |
| React Query использует `QueryClient` | cache client | singleton на SPA, fresh instance для SSR/request/tests |
| Analytics SDK должен инициализироваться один раз | analytics client | singleton/facade, но без user-specific state внутри module global |
| WebSocket соединение зависит от пользователя | realtime connection | создавать при login/session и закрывать при logout/unmount |
| Feature flags зависят от env и user | flags client | factory + provider, чтобы обновлять user context |
| Unit-тест должен заменить backend | mock service | factory/provider позволяет подставить fake implementation |

> [!faq]+ Уточнения
> - Factory не обязана быть классом; во frontend это часто обычная функция `createX`.
> - Singleton в SPA допустим для app-level services, если lifecycle понятен.
> - В SSR нельзя бездумно хранить user-specific state в module-level singleton.
> - Provider/context часто используется как способ передать созданную зависимость.
> - Для тестов удобно создавать fresh instance через factory.

#### Пример

```ts
type ApiClientConfig = {
  baseUrl: string;
  getToken(): string | null;
};

function createApiClient(config: ApiClientConfig) {
  return {
    async get<T>(path: string): Promise<T> {
      const token = config.getToken();

      const response = await fetch(`${config.baseUrl}${path}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      return response.json() as Promise<T>;
    },
  };
}
```

В приложении можно создать один client, а в тесте - отдельный mock/fake client.

#### Частые ошибки

- Создавать API client прямо внутри компонента на каждый render.
- Использовать module-level singleton для user-specific state в SSR.
- Не очищать WebSocket/SDK subscriptions при logout или unmount.
- Делать singleton, который невозможно заменить в тестах.
- Прятать слишком много логики в factory вместо явного service/use-case.

#### Связанные темы

- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/Patterns/Adapter и Facade во frontend]]
- [[Конспект для подготовки/Principles/SOLID во frontend]]
- [[Конспект для подготовки/React/Context]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/Web Basics/WebSocket]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]

#### Источники

- Design Patterns: Elements of Reusable Object-Oriented Software
- [Martin Fowler: Inversion of Control Containers and the Dependency Injection pattern](https://martinfowler.com/articles/injection.html)
