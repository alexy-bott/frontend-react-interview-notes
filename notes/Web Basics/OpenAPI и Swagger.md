# OpenAPI и Swagger

<!-- NOTE-NAV-TOP:START -->
[← API pagination filtering sorting](<./API pagination filtering sorting.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Хранение данных в браузере →](<./Хранение данных в браузере.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

OpenAPI Specification (OAS) — стандарт машинно-читаемого описания HTTP API. Документ фиксирует операции, параметры, тело запроса, возможные ответы, схемы данных, способы авторизации и примеры. По нему строят документацию, генерируют типы и клиент, поднимают mock server и проверяют совместимость изменений.

Swagger — прежнее название спецификации до OpenAPI 3 и название семейства инструментов, например Swagger UI и Swagger Editor. Фраза «открой Swagger» обычно означает интерфейс документации, построенный из OpenAPI-документа.

OpenAPI уменьшает расхождения, но не гарантирует, что работающий сервер соблюдает описание. Сгенерированный TypeScript-тип существует только во время разработки и не проверяет входящий JSON во время выполнения. Для критичных данных нужны runtime-валидация, контрактные тесты или другой контроль границы.

## Что описывает OpenAPI

| Раздел | Что фиксирует |
| --- | --- |
| `openapi` | версию самой спецификации OAS |
| `info` | название и версию описываемого API |
| `servers` | base URLs и переменные окружения |
| `paths` | URI, HTTP-методы и operations |
| `parameters` | path, query, header и cookie parameters |
| `requestBody` | media types и schema тела запроса |
| `responses` | статусы, headers и schemas ответов |
| `components.schemas` | переиспользуемые модели |
| `securitySchemes` | описание bearer, cookie, API key, OAuth 2 и OpenID Connect |
| `security` | какие схемы требуются глобально или для операции |

Поле `openapi: 3.1.0` не является версией бизнес-API. Версия API находится в `info.version` и может независимо отражаться в URL, header или release policy.

## OpenAPI и Swagger

OpenAPI — формат и правила документа. Swagger UI отображает интерактивную документацию, Swagger Editor редактирует и проверяет описание, а code generation tools создают клиентский или серверный код.

Интерфейс Swagger UI не обязательно является source of truth. Источником может быть YAML в репозитории, аннотации backend-кода или сгенерированный артефакт. Команда должна явно определить направление синхронизации:

```text
contract-first:
OpenAPI document -> backend/client/mocks/tests

code-first:
backend declarations -> generated OpenAPI -> client/docs
```

В обоих подходах CI проверяет, что опубликованный документ соответствует ожидаемой версии и что несовместимое изменение замечено до релиза клиента.

## Contract-first и code-first

**Contract-first** позволяет frontend, backend и QA договориться о запросах и ответах до реализации. Frontend использует mock server, backend реализует operation, а contract tests проверяют обе стороны. Цена — описание нужно поддерживать как настоящий код и заранее решать неоднозначности.

**Code-first** снижает ручное дублирование backend-моделей, но генератор может не выразить продуктовый смысл автоматически. Примеры, разные error responses, nullable, polymorphism и ограничения полей всё равно требуют внимания. Документ, сгенерированный только после deploy, слишком поздно предупреждает frontend о breaking change.

Подход выбирают по процессу команды. Критерий качества один: существует проверяемая цепочка от контракта до реально развернутого API.

## Версии OpenAPI

Официальный индекс спецификации указывает [OpenAPI 3.2.0](https://spec.openapis.org/oas/v3.2.0.html) как последнюю опубликованную версию. Это не означает, что проект обязан немедленно перейти на неё: generators, linters, gateways и documentation tools могут поддерживать разные minor versions.

Практически важное различие проходит между OAS 3.0 и 3.1+:

- в 3.0 nullable value часто задаётся через `nullable: true`;
- в 3.1+ Schema Object согласован с JSON Schema 2020-12 и null можно включить в `type`;
- конкретные keywords и качество codegen зависят от версии инструмента, а не только от валидности документа.

```yaml
# OpenAPI 3.0
type: string
nullable: true

# OpenAPI 3.1+
type:
  - string
  - "null"
```

Версию фиксируют в репозитории и проверяют на всей toolchain. «Валидный OAS 3.2» и «наш генератор правильно создаёт клиент из OAS 3.2» — разные утверждения.

## Схема и TypeScript-тип

OpenAPI различает состояния, которые легко случайно объединить:

```text
required property    -> ключ обязан присутствовать
optional property    -> ключ может отсутствовать
nullable value       -> значение может быть null
readOnly             -> поле приходит в response, но не отправляется при записи
writeOnly            -> поле принимается при записи, но не возвращается
```

Свойство `required` массива schema перечисляет обязательные ключи объекта. Это не то же поле, что `required: true` у path parameter или request body.

`format: date-time` обычно остаётся строкой на wire. Генератор может создать `string`, `Date` или custom type в зависимости от настроек. Подобное преобразование должно быть единым в API-слое.

`default` в schema документирует значение по умолчанию, но не обязывает frontend, сервер или generator автоматически подставить его. Реальное поведение должно быть частью контракта и теста.

## Минимальный документ

```yaml
openapi: 3.1.0
info:
  title: Users API
  version: 1.4.0
paths:
  /users/{id}:
    get:
      operationId: getUserById
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: User found
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "404":
          description: User not found
          content:
            application/problem+json:
              schema:
                $ref: "#/components/schemas/Problem"
components:
  schemas:
    User:
      type: object
      required: [id, name]
      properties:
        id:
          type: string
        name:
          type: string
        avatarUrl:
          type: [string, "null"]
    Problem:
      type: object
      required: [type, title]
      properties:
        type:
          type: string
          format: uri-reference
        title:
          type: string
```

Документ показывает успешный и ошибочный response, но не описывает всё поведение автоматически. Например, UI всё ещё должен решить, как представить `404`, а API-слой — как валидировать ответ и сопоставить DTO с моделью приложения.

## Code generation

Codegen полезен, когда он является воспроизводимым шагом:

1. Используется зафиксированная версия OpenAPI-документа и генератора.
2. Конфигурация и команда лежат в репозитории.
3. `operationId` стабилен и уникален.
4. Результат проверяется TypeScript compiler и тестами.
5. Contract diff блокирует неожиданные breaking changes.

Генерировать можно только types, низкоуровневый client или готовые hooks. Чем больше поведения создаёт generator, тем сильнее приложение зависит от его naming, error handling, serialization и runtime. Часто удобно генерировать transport types и functions, а cache policy, mapping и продуктовые сценарии держать в собственном API-слое.

DTO не обязательно становится доменной моделью UI. Backend может вернуть `created_at`, nullable fields и transport enums, а frontend преобразует их в `createdAt`, явно обработанные состояния и удобные значения.

## Runtime validation и contract tests

TypeScript доверяет объявленному return type функции. Конструкция `response.json() as User` не проверяет JSON и способна скрыть расхождение до production.

Варианты контроля:

- валидировать критичные ответы runtime-схемой;
- запускать provider/consumer contract tests;
- проверять backend response against schema в тестовой среде;
- генерировать mock data из контракта и тестировать UI-сценарии;
- собирать ошибки декодирования с endpoint и trace ID.

Полная runtime validation каждого большого ответа имеет стоимость. Её применяют на внешних и рискованных границах, а не добавляют механически без оценки.

## Что проверять перед интеграцией

- operation и фактический server URL;
- path/query serialization и обязательность параметров;
- request media type и форма body;
- все ожидаемые success statuses, включая `202` и `204`;
- error statuses и стабильная error schema;
- `required`, optional и nullable поля;
- enum и поведение при новом неизвестном значении;
- pagination, sorting и filters;
- security requirement и CORS/cookie условия;
- deprecation и план миграции.

## Ключевые уточнения

- OpenAPI является спецификацией HTTP API, а Swagger — историческим именем и экосистемой инструментов.
- `openapi` задаёт версию формата документа, а `info.version` — версию описываемого API.
- Сгенерированный TypeScript-код проверяет использование типов, но не доказывает соответствие runtime-ответа.
- Поддержка версии определяется всей toolchain; последняя OAS не становится автоматически лучшей версией для существующего проекта.
- Контракт приносит пользу только при проверяемой синхронизации с сервером, codegen, CI и правилами breaking changes.

## Связанные темы

- [REST](<./REST.md>)
- [HTTP status codes и ошибки API](<./HTTP status codes и ошибки API.md>)
- [API pagination filtering sorting](<./API pagination filtering sorting.md>)
- [API слой и контракты](<../Architecture/API слой и контракты.md>)
- [Проверка данных с backend](<../TypeScript/Проверка данных с backend.md>)
- [RTK Query](<../React/RTK Query.md>)

## Источники

- [OpenAPI Specification](https://spec.openapis.org/oas/)
- [OpenAPI Specification 3.2.0](https://spec.openapis.org/oas/v3.2.0.html)
- [OpenAPI Learn](https://learn.openapis.org/specification/)
- [Swagger Docs: What is OpenAPI?](https://swagger.io/docs/specification/v3_0/about/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← API pagination filtering sorting](<./API pagination filtering sorting.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Хранение данных в браузере →](<./Хранение данных в браузере.md>)
<!-- NOTE-NAV-BOTTOM:END -->
