# Проверка данных с backend

<!-- NOTE-NAV-TOP:START -->
[← Declaration files](<./Declaration files.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [React TypeScript типизация →](<./React TypeScript типизация.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Ответ backend является внешним недоверенным значением. TypeScript проверяет код до запуска, но не знает, какой JSON фактически пришёл по сети. Annotation, generic `request<User>()` и assertion `as User` не проверяют поля объекта.

Надёжная модель: принять данные ответа (payload) как `unknown`, выполнить runtime validation — проверку во время работы приложения, затем при необходимости нормализовать данные и только после этого вернуть доменный тип. Простую структуру можно проверить через type guard, сложную — через валидатор по схеме (schema validator), например Zod или другую используемую в проекте библиотеку.

Проверку размещают на границе API до cache, store и UI. Тогда остальная часть приложения работает с уже проверенным контрактом, а не повторяет защитные проверки в каждом компоненте.

## Почему статического типа недостаточно

```ts
type User = {
  id: number;
  name: string;
};

const response = await fetch("/api/user/1");
const user = (await response.json()) as User;
```

`as User` меняет только мнение компилятора. Сервер всё ещё может вернуть `{ id: "1" }`, HTML вместо JSON, `null` или объект другой версии. Assertion исчезнет при компиляции и не создаст `if` или проверку полей.

То же относится к generated types из OpenAPI. Они синхронизируют статический контракт клиента со схемой, но не гарантируют, что конкретный gateway, mock, старая версия сервиса или повреждённый ответ соблюдает эту схему.

## Последовательность на границе данных

```text
HTTP / WebSocket / storage
          ↓
       unknown
          ↓
runtime validation
          ↓
 normalization / mapping
          ↓
    domain model
          ↓
 cache, store и UI
```

**Валидация** отвечает, соответствует ли значение ожидаемой форме и ограничениям.

**Нормализация** преобразует уже допустимые данные в удобную модель приложения: переименовывает поля, превращает ISO-строку в выбранное представление даты, подставляет разрешённое значение по умолчанию, разделяет транспортную модель ответа (DTO) и доменную модель.

Эти шаги полезно различать. Нормализация не должна молча «исправлять» отсутствие обязательного поля и выдавать повреждённые данные за корректные.

## Ручной type guard

```ts
type UserDto = {
  id: number;
  name: string;
  roles: string[];
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isUserDto(value: unknown): value is UserDto {
  return (
    isRecord(value) &&
    typeof value.id === "number" &&
    Number.isFinite(value.id) &&
    typeof value.name === "string" &&
    Array.isArray(value.roles) &&
    value.roles.every(role => typeof role === "string")
  );
}

async function getUser(id: number): Promise<UserDto> {
  const response = await fetch(`/api/users/${id}`);

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  const payload: unknown = await response.json();

  if (!isUserDto(payload)) {
    throw new Error("Invalid user response");
  }

  return payload;
}
```

Guard проверяет реальные JavaScript-признаки. `Array.isArray` доказывает только массив, поэтому тип каждого элемента проверяется отдельно. `typeof value === "object"` дополняется `value !== null`.

Ручной guard удобен для небольшой стабильной структуры. Для глубоко вложенного DTO ручные проверки быстро становятся длинными, а результат `false` не объясняет, какое поле нарушено.

## Schema validation

Schema validator хранит исполняемую схему и выводит из неё TypeScript-тип:

```ts
import { z } from "zod";

const UserDtoSchema = z.object({
  id: z.number().finite(),
  name: z.string().min(1),
  roles: z.array(z.string()),
});

type UserDto = z.infer<typeof UserDtoSchema>;

async function getUser(id: number): Promise<UserDto> {
  const response = await fetch(`/api/users/${id}`);

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return UserDtoSchema.parse(await response.json());
}
```

`parse` возвращает проверенное значение или бросает ошибку. `safeParse` возвращает результат с ветками success/error и подходит, когда ошибка контракта должна обрабатываться без exception.

Выбор библиотеки не является обязательной частью модели. Важны единый источник правил, место проверки и понятная политика ошибки.

## Транспортная (DTO) и доменная модели

Форма ответа сервера не обязана распространяться по всему приложению:

```ts
type UserDto = {
  id: number;
  full_name: string;
  created_at: string;
};

type User = {
  id: number;
  fullName: string;
  createdAt: Date;
};

function toUser(dto: UserDto): User {
  return {
    id: dto.id,
    fullName: dto.full_name,
    createdAt: new Date(dto.created_at),
  };
}
```

Перед созданием `Date` schema должна подтвердить допустимый формат, а mapper — определить политику временной зоны. Отдельная доменная модель изолирует UI от naming и versioning backend-контракта.

## Где размещать проверку

- после `response.json()` в API-клиенте;
- в `transformResponse` RTK Query либо общей обёртке вокруг `baseQuery`;
- в обработчике WebSocket/SSE до dispatch в store;
- при чтении из `localStorage`, IndexedDB, query string и `postMessage`;
- при загрузке сохранённого состояния приложения после обновления версии.

Валидация после записи в cache слишком поздняя: непроверенное значение уже может быть прочитано другими consumers.

## Политика ошибки

Невалидный ответ является отдельным классом ошибки контракта. Возможные реакции зависят от продукта:

- отклонить запрос и показать резервный интерфейс (fallback UI);
- вернуть типизированный `Result`;
- отправить событие в мониторинг с endpoint, версией схемы и безопасными диагностическими данными;
- не повторять автоматически запрос, если повтор не способен исправить несовместимый контракт;
- сохранить приложение в работоспособном состоянии, не записывая повреждённые данные в cache.

Payload может содержать персональные или секретные данные, поэтому его нельзя целиком отправлять в логи без фильтрации.

## Ключевые уточнения

- TypeScript проверяет соответствие кода типам, а не соответствие сетевого ответа документации.
- `as User`, generic API-клиента и OpenAPI-generated type не заменяют runtime validation.
- Guard обязан проверять каждый признак, на котором дальше основан доменный код.
- Валидация определяет допустимость, нормализация преобразует уже допустимые данные.
- Проверка выполняется до cache/store, чтобы внутри приложения существовала одна граница доверия.
- Ошибка контракта должна иметь явную обработку и безопасную диагностику, а не маскироваться default-значениями.

## Связанные темы

- [Type Guards](<./Type Guards.md>)
- [never any unknown](<./never any unknown.md>)
- [Type assertions и non-null assertion](<./Type assertions и non-null assertion.md>)
- [API слой и контракты](<../Architecture/API слой и контракты.md>)
- [RTK Query](<../React/RTK Query.md>)
- [OpenAPI и Swagger](<../Web Basics/OpenAPI и Swagger.md>)

## Источники

- [TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript Handbook: The unknown Type](https://www.typescriptlang.org/docs/handbook/2/functions.html#unknown)
- [Zod documentation](https://zod.dev/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Declaration files](<./Declaration files.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [React TypeScript типизация →](<./React TypeScript типизация.md>)
<!-- NOTE-NAV-BOTTOM:END -->
