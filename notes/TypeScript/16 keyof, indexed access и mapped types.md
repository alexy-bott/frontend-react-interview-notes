# keyof, indexed access и mapped types

<!-- NOTE-NAV-TOP:START -->
[← Типизация Array.map](<./15 Типизация Array.map.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Utility Types →](<./17 Utility Types.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`keyof`, indexed access и mapped types позволяют получать новые типы из уже существующей структуры. `keyof T` создаёт union ключей, `T[K]` получает тип значений по ключу, а mapped type `[K in keyof T]` проходит по ключам и строит новый объектный тип.

Эти конструкции сохраняют связь с исходной моделью. Если поле `User` изменится, тип словаря, формы или getter-функций обновится автоматически. На них основаны `Pick`, `Readonly`, `Partial` и другие utility types.

Главная практическая связка — `K extends keyof T` вместе с `T[K]`: она разрешает только существующий ключ и возвращает тип именно его значения.

## `typeof`: получить тип существующего значения

В позиции типа `typeof` переносит статическую форму переменной или свойства в типовую систему:

```ts
const user = {
  id: 1,
  name: "Ann",
  active: true,
};

type User = typeof user;
// { id: number; name: string; active: boolean }
```

Это не JavaScript-оператор `typeof user`, который во время выполнения вернул бы строку `"object"`. Запрос типа (type query) `typeof` не выполняет код, а получает уже выведенный TypeScript-тип значения. Обычно его применяют к имени переменной или доступу к свойству, а не к произвольному вызову функции.

## `keyof`: получить ключи типа

```ts
type UserKey = keyof User;
// "id" | "name" | "active"
```

`keyof` работает со статическим типом, а не читает объект в runtime. В JavaScript для реального списка собственных строковых ключей используется `Object.keys`, и эти две операции не полностью эквивалентны.

Если тип содержит string index signature, `keyof` может дать `string | number`: в JavaScript числовой ключ объекта преобразуется в строку. Для symbol index signature участвует `symbol`. Общий тип ключа в TypeScript — `PropertyKey`, то есть `string | number | symbol`.

## Indexed access: получить тип значения

```ts
type UserId = User["id"];
// number

type UserSummary = User["id" | "name"];
// number | string
```

Ключ должен быть типом и принадлежать `keyof User`. Если передан union ключей, результатом становится union соответствующих значений.

Связь ключа и значения в generic-функции:

```ts
function getValue<T, K extends keyof T>(object: T, key: K): T[K] {
  return object[key];
}

const user: User = {
  id: 1,
  name: "Ann",
  active: true,
};

const name = getValue(user, "name");
// string
```

Если написать `key: keyof T` без отдельного `K`, результат будет union значений всех ключей. Параметр `K` запоминает конкретный ключ данного вызова.

## Mapped type: преобразовать каждое поле

```ts
type Flags<T> = {
  [K in keyof T]: boolean;
};

type UserFlags = Flags<User>;
// { id: boolean; name: boolean; active: boolean }
```

`K in keyof T` похож на цикл только на уровне типов. Для каждого ключа создаётся свойство, а выражение справа задаёт его значение.

Можно сохранять исходные типы и менять модификаторы:

```ts
type MutableRequired<T> = {
  -readonly [K in keyof T]-?: T[K];
};
```

`-readonly` удаляет `readonly`, `-?` делает поле обязательным. Знаки `+` добавляют модификатор, но обычно подразумеваются по умолчанию.

## Переименование ключей и template literal types

Ключ можно переименовать через `as`:

```ts
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<User>;
// getId(): number
// getName(): string
// getActive(): boolean
```

`string & K` оставляет строковые ключи, потому что `Capitalize` работает со строками. Template literal type строит новое имя из литерального ключа.

Для исключения свойства его новый ключ делают `never`:

```ts
type WithoutKind<T> = {
  [K in keyof T as K extends "kind" ? never : K]: T[K];
};
```

## Граница полезности

Mapped types оправданы, когда производный контракт должен автоматически следовать исходному: form state по полям модели, набор feature flags, getters, handlers или API projection.

Для небольшого публичного объекта явное объявление может быть понятнее. Несколько вложенных conditional types, remapping и `infer` превращают тип в программу, которую нужно отлаживать и поддерживать. Уменьшение дублирования должно окупать сложность.

## Ключевые уточнения

- `keyof T` возвращает union ключей статического типа, а не runtime-массив.
- `typeof` в позиции типа получает тип существующего значения и отличается от одноимённого JavaScript-оператора.
- `T[K]` сохраняет точность только если `K` связан с конкретным ключом; широкий `keyof T` даёт union всех значений.
- Mapped type создаёт новый тип и не преобразует объект во время выполнения.
- Модификаторы `readonly` и `?` можно добавлять и удалять во время преобразования.
- Key remapping через `as` переименовывает ключ, а `never` исключает его.
- Index signatures могут расширить `keyof` до `string | number` или `symbol`; это нужно учитывать в generic API.

## Связанные темы

- [Дженерики](<./12 Дженерики.md>)
- [Utility Types](<./17 Utility Types.md>)
- [infer и условные типы](<./18 infer и условные типы.md>)
- [as const и satisfies](<./19 as const и satisfies.md>)

## Источники

- [TypeScript Handbook: Keyof Type Operator](https://www.typescriptlang.org/docs/handbook/2/keyof-types.html)
- [TypeScript Handbook: Typeof Type Operator](https://www.typescriptlang.org/docs/handbook/2/typeof-types.html)
- [TypeScript Handbook: Indexed Access Types](https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html)
- [TypeScript Handbook: Mapped Types](https://www.typescriptlang.org/docs/handbook/2/mapped-types.html)
- [TypeScript Handbook: Template Literal Types](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Типизация Array.map](<./15 Типизация Array.map.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Utility Types →](<./17 Utility Types.md>)
<!-- NOTE-NAV-BOTTOM:END -->
