---
aliases:
  - API слой
  - API contracts
  - frontend API layer
  - DTO
---

#### Ответ на 60 секунд

API-слой во frontend нужен, чтобы изолировать приложение от деталей backend-контракта. Компоненты не должны в каждом месте знать base URL, headers, refresh flow, формат ошибок, отмену запросов и форму DTO. API-слой централизует transport, авторизацию, обработку ошибок, runtime validation и преобразование внешних данных в доменную модель.

Важно различать DTO и доменную модель. DTO - это то, что пришло по сети. Доменная модель - удобная и проверенная форма для приложения. TypeScript помогает описать ожидания, но не проверяет внешний JSON в runtime, поэтому на границе полезны схемы или type guards. Тогда контракт ломается в одном понятном месте, а не случайно в JSX.

#### Ключевая схема

```text
fetch/http client
-> auth headers / credentials
-> cancellation / timeout
-> status and error mapping
-> runtime validation
-> DTO -> domain model
-> query/cache/UI
```

| Зона | Что решить |
| --- | --- |
| Transport | `fetch`, axios, retries, timeout, abort |
| Auth | cookies, bearer token, refresh, logout |
| Errors | network/status/domain validation errors |
| Contracts | OpenAPI/Swagger, schemas, generated types |
| Validation | Zod/type guards на границе |
| Mapping | DTO не протекает глубоко в UI |
| Collections | pagination/filtering/sorting/search как часть cache key |

#### Развернутый ответ

Прямой `fetch` в компоненте допустим в маленьком примере, но в продукте быстро появляются повторяющиеся правила: base URL, credentials, auth headers, refresh flow, `401/403/404/409/422`, abort, retries, timeout, logging и единый формат ошибок. Если эти правила размазаны по компонентам, разные экраны начинают вести себя по-разному.

Граница API-слоя - место, где внешний JSON превращается во внутреннюю модель приложения. DTO отражает контракт backend, а domain model отражает удобную форму для UI и бизнес-логики. Это позволяет менять backend-поля, нормализовать даты, переименовывать snake_case в camelCase и не протаскивать внешний формат в JSX.

TypeScript описывает ожидания на этапе разработки, но не проверяет runtime JSON. Поэтому `response.json() as User` не защищает от сломанного backend-ответа. На критичных границах используют schemas, type guards или generated clients с runtime validation, чтобы ошибка контракта возникала рядом с API, а не случайно в компоненте.

Ошибки стоит разделять по природе: network error, HTTP status error, validation error, business/domain error. Для UI это разные сценарии: re-auth, forbidden, not found, conflict, form errors, retry или fallback. Для observability это тоже разные уровни важности и разные диагностические поля.

Auth flow - часть API boundary. API-слой должен знать, когда добавить `Authorization`, когда отправить `credentials`, как обработать `401`, как не запустить несколько refresh-запросов одновременно и когда очистить user/cache state. Компонент получает уже понятный результат: user загружен, access denied, unauthenticated или form/server error.

Отмена запросов защищает UI от устаревших обновлений. `AbortController` или механизм query-библиотеки нужен при смене страницы, быстром вводе в search, повторных запросах и race conditions, когда более старый ответ приходит позже нового.

Коллекции требуют отдельной политики. API-слой должен одинаково сериализовать filters/sort/search, сбрасывать page/cursor при изменении параметров, включать эти параметры в cache key и не смешивать данные разных запросов. Для infinite scroll важно хранить страницы и cursor, а для таблиц - page, limit, total и текущую сортировку.

OpenAPI/codegen не отменяет маппинг DTO в domain model. Сгенерированный тип описывает внешний контракт, а UI часто работает с другой формой: подготовленные даты, вычисленные флаги, объединённые поля, нормализованные enum-значения. Чем ближе к компонентам протекает DTO, тем дороже менять backend-контракт.

> [!faq]+ Уточнения
> - API-слой централизует transport, auth, errors, cancellation, validation и mapping.
> - DTO - внешний контракт, domain model - удобная внутренняя форма приложения.
> - `as Type` после `json()` не валидирует данные в runtime.
> - OpenAPI может генерировать типы и клиент, но runtime-ответ всё равно приходит извне.
> - `401`, `403`, `404`, `409`, `422` не должны выглядеть одинаково для UI.
> - Pagination/filtering/sorting/search входят в query key/cache key.
> - Generated DTO и domain model можно связывать маппером, а не протаскивать DTO в JSX.
> - Auth headers, credentials, refresh и logout централизуют в API-слое.

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

function mapUser(dto: ApiUserDto): User {
  return {
    id: dto.id,
    name: dto.full_name,
    avatarUrl: dto.avatar_url,
  };
}

async function request<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, {
    credentials: "include",
    signal,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
```

В production-варианте после `json()` добавляют runtime validation, а не доверяют `as Promise<T>`.

#### Частые ошибки

- Размазывать API-логику по компонентам.
- Использовать `response.json() as Type` как полноценную защиту контракта.
- Не отличать DTO от модели, с которой удобно работать UI.
- Не отменять устаревшие запросы.
- Обрабатывать `401`, `403`, `404`, `409`, `422` одинаково.
- Логировать tokens, cookies или персональные данные.

#### Связанные темы

- [[Конспект для подготовки/TypeScript/Проверка данных с backend]]
- [[Конспект для подготовки/Patterns/Adapter и Facade во frontend]]
- [[Конспект для подготовки/Web Basics/HTTP status codes и ошибки API]]
- [[Конспект для подготовки/Web Basics/OpenAPI и Swagger]]
- [[Конспект для подготовки/Web Basics/API pagination filtering sorting]]
- [[Конспект для подготовки/Web Basics/Auth flow и refresh tokens]]
- [[Конспект для подготовки/JavaScript/Fetch и работа с API]]
- [[Конспект для подготовки/JavaScript/AbortController]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/React/RTK Query]]
- [[Конспект для подготовки/Web Basics/Realtime transports]]
- [[Конспект для подготовки/Web Basics/WebSocket]]
- [[Конспект для подготовки/Web Basics/HTTP запрос]]
- [[Конспект для подготовки/Web Basics/Cookies и авторизация]]

#### Источники

- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html)
- [Zod](https://zod.dev/)
