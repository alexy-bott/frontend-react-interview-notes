---
aliases:
  - API слой
  - API contracts
  - frontend API layer
  - DTO
---

#### Быстрый ответ

API-слой является границей между frontend-моделью и внешним сервисом. Он централизует transport configuration, credentials, отмену и ограниченную retry policy, нормализует HTTP/network errors, проверяет внешний JSON и преобразует Data Transfer Object (DTO) во внутреннюю модель.

Компонент или use case вызывает операцию на языке приложения, например `getCurrentUser()`, и получает проверенный `User` либо типизированную ошибку. Он не должен повторять base URL, headers, refresh flow и структуру backend response. OpenAPI/codegen помогает поддерживать transport contract, но TypeScript types сами не проверяют фактические данные во время выполнения.

#### Ключевая схема

```text
component/use case
-> query/service operation
-> request policy: URL, credentials, abort
-> HTTP response
-> status/error normalization
-> parse unknown + runtime validation
-> DTO adapter
-> domain/view model
```

| Уровень | Ответственность |
| --- | --- |
| HTTP client | transport, headers, body, credentials, abort |
| Auth integration | single refresh, повтор запроса, logout policy |
| Contract parser | проверка `unknown` response |
| Adapter | DTO -> domain/view model |
| Query/cache | freshness, key, deduplication, invalidation |
| UI | loading/error/success и пользовательское восстановление |

#### Базовая модель

`fetch` возвращает fulfilled Promise даже для `404` или `500`; отклонение происходит при network failure, abort и некоторых request errors. Поэтому API client отдельно проверяет `response.ok`, безопасно разбирает body и сохраняет status/request id для диагностики.

`response.json()` имеет внешнее содержимое. Аннотация generic или `as User` меняет только мнение TypeScript и не создаёт runtime-check. Parser/schema принимает `unknown`, либо возвращает валидный DTO, либо создаёт contract error рядом с границей.

DTO отражает форму передачи: `full_name`, nullable fields, ISO strings. Domain/view model отражает потребности приложения: `name`, проверенный enum, объект даты только если выбранная модель действительно этого требует. Adapter не должен прятать business decision, не связанное с переводом контракта.

#### Развернутый ответ

**Errors.** Network failure, timeout/abort, HTTP status, invalid response и domain rejection имеют разные причины и способы восстановления. `401` может запускать согласованный refresh, `403` - показывать отсутствие права, `409` - конфликт версии, `422` - field errors. Backend может использовать Problem Details (`application/problem+json`) как общий формат, но domain codes всё равно согласуются отдельно.

**Retries.** Автоматический retry безопасен не для каждой операции. Повтор идемпотентного GET после временного network/`5xx` сбоя обычно допустим с limit/backoff. Повтор создания платежа или заказа требует idempotency key и server contract; frontend не может гарантировать отсутствие первого успешного выполнения после потерянного ответа.

**Cancellation.** `AbortController` прекращает ожидание и обработку response на клиенте, но не гарантирует отмену уже начавшейся server operation. Отмена защищает UI от ненужной работы; правильный порядок результатов также обеспечивается query key, request identity или проверкой актуального input.

**Auth.** Refresh централизуют и выполняют single-flight, чтобы несколько `401` не создали refresh storm. Исходный request повторяют ограниченное число раз; refresh endpoint не должен рекурсивно запускать собственный refresh.

**Query parameters.** Serialization filters/sort/page является частью контракта. Все параметры результата входят в query key. API function не обязана владеть cache, но должна принимать нормализованные arguments, чтобы cache layer мог различать requests.

**Generated client.** OpenAPI генерирует request types и client, снижая ручное расхождение. Он не определяет UX errors, cache policy и domain model; runtime validation зависит от generator/configuration и не предполагается автоматически.

#### Пример

Сокращённая операция использует project abstractions `ApiError` и `parseApiUserDto`:

```ts
type ApiUserDto = {
  id: number;
  full_name: string;
};

type User = {
  id: number;
  name: string;
};

async function getCurrentUser(signal?: AbortSignal): Promise<User> {
  const response = await fetch("/api/me", {
    credentials: "include",
    signal,
  });

  if (!response.ok) {
    throw await ApiError.fromResponse(response);
  }

  const json: unknown = await response.json();
  const dto: ApiUserDto = parseApiUserDto(json);

  return {
    id: dto.id,
    name: dto.full_name,
  };
}
```

`ApiError.fromResponse` нормализует status и безопасные details, а `parseApiUserDto` выполняет runtime validation. Эти функции являются отдельными контрактами API-слоя, а не type assertions.

#### Ключевые уточнения

- TypeScript описывает ожидаемый response при разработке, но runtime JSON остаётся `unknown` до проверки.
- HTTP client, contract parser, adapter и query cache решают разные задачи и могут быть отдельными слоями одной boundary.
- Abort прекращает client-side work, но не является гарантированной отменой server transaction.
- Retry зависит от идемпотентности операции и server contract, а не включается одинаково для всех methods.
- Generated DTO не обязан быть удобной domain model; codegen не отменяет mapping и UX error policy.

#### Связанные темы

- [[Конспект для подготовки/TypeScript/Проверка данных с backend]]
- [[Конспект для подготовки/Patterns/Adapter и Facade во frontend]]
- [[Конспект для подготовки/Web Basics/HTTP status codes и ошибки API]]
- [[Конспект для подготовки/Web Basics/OpenAPI и Swagger]]
- [[Конспект для подготовки/Web Basics/Auth flow и refresh tokens]]
- [[Конспект для подготовки/JavaScript/Fetch и работа с API]]
- [[Конспект для подготовки/JavaScript/AbortController]]
- [[Конспект для подготовки/React/RTK Query]]

#### Источники

- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html)
