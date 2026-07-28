---
aliases:
  - Utility Types
  - утилитарные типы
  - Partial Pick Omit Record
  - ReturnType Parameters Awaited
---

#### Быстрый ответ

Utility types — встроенные generic-типы TypeScript, которые получают один тип из другого. Они позволяют выбрать или исключить поля, изменить модификаторы, преобразовать union либо извлечь параметры и результат функции без ручного дублирования.

Часто используются `Partial`, `Required`, `Readonly`, `Pick`, `Omit`, `Record`, `Exclude`, `Extract`, `NonNullable`, `Parameters`, `ReturnType` и `Awaited`.

Utility type не меняет данные во время выполнения и обычно выполняет неглубокое преобразование. Например, `Readonly<T>` запрещает переприсваивать только верхнеуровневые поля, а `Partial<T>` не делает поля вложенного объекта необязательными.

#### Основные группы

| Задача | Utility type | Результат |
| --- | --- | --- |
| Сделать поля необязательными | `Partial<T>` | все верхние поля получают `?` |
| Сделать поля обязательными | `Required<T>` | удаляется `?` |
| Запретить запись в поля | `Readonly<T>` | верхние поля получают `readonly` |
| Выбрать поля | `Pick<T, K>` | объект только с ключами `K` |
| Исключить поля | `Omit<T, K>` | объект без ключей `K` |
| Построить словарь | `Record<K, V>` | каждый ключ `K` имеет значение `V` |
| Удалить варианты union | `Exclude<T, U>` | варианты `T`, не совместимые с `U` |
| Оставить варианты union | `Extract<T, U>` | варианты `T`, совместимые с `U` |
| Убрать отсутствие | `NonNullable<T>` | без `null` и `undefined` |
| Получить параметры функции | `Parameters<F>` | tuple параметров |
| Получить результат функции | `ReturnType<F>` | return type |
| Развернуть promise-like тип | `Awaited<T>` | значение после `await` |

#### Производные объектные контракты

```ts
type User = {
  id: string;
  name: string;
  email: string;
  passwordHash: string;
  role: "user" | "admin";
};

type PublicUser = Omit<User, "passwordHash">;

type UpdateUserInput = Partial<
  Pick<User, "name" | "email">
>;
```

`PublicUser` следует исходной модели, а `UpdateUserInput` разрешает изменить только `name` и `email`. Запись `Partial<User>` была бы шире и сделала бы необязательными также `id`, `role` и служебные поля.

Для публичного API не всегда нужно производить тип прямо из доменной модели. Если контракт backend или формы развивается независимо, отдельная транспортная модель данных (DTO) может быть безопаснее тесной связи через `Omit`.

#### `Record` и полнота словаря

```ts
type Status = "idle" | "loading" | "success" | "error";

const labels: Record<Status, string> = {
  idle: "Ожидание",
  loading: "Загрузка",
  success: "Готово",
  error: "Ошибка",
};
```

При добавлении нового `Status` компилятор потребует добавить подпись. `Record<string, string>` такой полноты не даёт: он разрешает произвольные строковые ключи.

Если доступ по ключу может не найти значение, это должно отражаться в модели. `Partial<Record<string, V>>`, index signature с `V | undefined` или `noUncheckedIndexedAccess` честнее, чем обещание, что любая строка существует.

#### Преобразование unions

```ts
type State = "idle" | "loading" | "success" | "error";

type FinishedState = Exclude<State, "idle" | "loading">;
// "success" | "error"

type ErrorState = Extract<State, "error" | "cancelled">;
// "error"

type Present = NonNullable<string | null | undefined>;
// string
```

`Exclude` и `Extract` являются distributive conditional types: они проверяют каждый вариант union отдельно.

#### Типы функций и async-кода

```ts
async function loadUser(id: string): Promise<User> {
  throw new Error(`Not implemented: ${id}`);
}

type LoadUserArgs = Parameters<typeof loadUser>;
// [id: string]

type LoadUserPromise = ReturnType<typeof loadUser>;
// Promise<User>

type LoadedUser = Awaited<LoadUserPromise>;
// User
```

Такие типы полезны, когда функция является источником контракта и производный тип действительно должен меняться вместе с её сигнатурой. Если публичная модель должна оставаться стабильной независимо от реализации функции, её лучше объявить отдельно.

#### Неглубокая работа

```ts
type Settings = {
  profile: {
    theme: string;
  };
};

type PartialSettings = Partial<Settings>;
// profile может отсутствовать,
// но если он есть, theme остаётся обязательным
```

Deep-версии utility types пишут рекурсивно или берут из библиотеки. Они усложняют сообщения об ошибках и могут неверно обработать arrays, functions, maps или special objects, поэтому универсальный `DeepPartial` не применяют без понимания его семантики.

#### Ключевые уточнения

- Utility types создают статические типы и не преобразуют runtime-объекты.
- `Partial`, `Required` и `Readonly` неглубокие.
- `Pick<T, K>` ограничивает `K` ключами `T`; стандартный `Omit<T, K>` принимает любой `PropertyKey`, поэтому опечатка в исключаемом ключе может оставить тип без изменений.
- `Readonly<T>` не равен `Object.freeze` и не гарантирует глубокую неизменяемость.
- Длинная цепочка utility types не всегда лучше отдельного именованного контракта.
- Производный тип полезен только когда его изменение действительно должно следовать исходной модели.

#### Связанные темы

- [[Конспект для подготовки/TypeScript/keyof indexed access mapped types]]
- [[Конспект для подготовки/TypeScript/infer и conditional types]]
- [[Конспект для подготовки/TypeScript/Generics]]
- [[Конспект для подготовки/TypeScript/as const и satisfies]]

#### Источники

- [TypeScript Handbook: Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)
- [TypeScript source: Utility type definitions](https://github.com/microsoft/TypeScript/blob/main/src/lib/es5.d.ts)
