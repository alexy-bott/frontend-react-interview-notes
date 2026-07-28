---
aliases:
  - as const
  - satisfies
  - literal types
  - литеральные типы
---

#### Быстрый ответ

`as const` сохраняет литеральные типы выражения: строка остаётся конкретным значением `"admin"`, свойства object literal становятся `readonly`, а массив превращается в readonly tuple. Это нужно, когда константные данные должны стать источником точного union-типа.

`satisfies` проверяет, что выражение совместимо с заданным типом, но сохраняет более точный выведенный тип самого выражения. Он полезен для конфигураций, словарей и таблиц соответствий: контракт проверяется, а конкретные ключи и литералы не теряются.

Обе конструкции работают только в типовой системе. `as const` не вызывает `Object.freeze`, а `satisfies` не валидирует внешние данные в runtime.

#### Почему литералы расширяются

Обычный объект остаётся изменяемым даже при `const`, поэтому TypeScript учитывает возможное присваивание нового значения:

```ts
const user = { role: "admin" };
// { role: string }

user.role = "editor";
```

`as const` сообщает, что выражение нужно рассматривать как набор фиксированных значений:

```ts
const user = { role: "admin" } as const;
// { readonly role: "admin" }

const columns = ["id", "name"] as const;
// readonly ["id", "name"]
```

Это const assertion, а не обычная runtime-операция. Изменения через данный тип запрещены компилятором, но объект не становится глубоко замороженным JavaScript-объектом.

#### Получение union из константных данных

```ts
const STATUS = {
  Idle: "idle",
  Loading: "loading",
  Success: "success",
  Error: "error",
} as const;

type Status = typeof STATUS[keyof typeof STATUS];
// "idle" | "loading" | "success" | "error"
```

`typeof STATUS` получает статический тип объекта, `keyof` — union его ключей, а indexed access извлекает union значений. Runtime-объект и тип остаются синхронизированы: добавление нового значения обновит `Status`.

#### Что делает `satisfies`

```ts
const LABELS = {
  idle: "Ожидание",
  loading: "Загрузка",
  success: "Готово",
  error: "Ошибка",
} satisfies Record<Status, string>;
```

TypeScript проверит, что все статусы присутствуют и значения являются строками. При этом `keyof typeof LABELS` остаётся точным union ключей, а не расширяется до произвольного `string`.

Это особенно полезно, когда объект должен соответствовать общему контракту, но дальнейший код использует его конкретные поля:

```ts
type Palette = Record<"red" | "green", string | readonly [number, number, number]>;

const palette = {
  red: "#ff0000",
  green: [0, 255, 0],
} satisfies Palette;

palette.red.toUpperCase();
// red сохранил тип string
```

#### Аннотация, assertion и `satisfies`

| Запись | Проверяет контракт | Сохраняет точный вывод | Может скрыть ошибку |
| --- | --- | --- | --- |
| `const x: T = value` | да | обычно переменная получает общий `T` | нет |
| `value satisfies T` | да | да | нет |
| `value as T` | ограниченно, как assertion | нет гарантии | да |

Annotation подходит, когда переменная должна иметь публичный тип `T`. `satisfies` подходит, когда нужно проверить значение, но оставить его конкретный тип. `as T` применяют, когда у разработчика есть внешний инвариант, который компилятор не способен вывести; это не замена проверке.

#### Границы применения

`as const` не всегда нужен. Если функция ожидает обычный изменяемый массив, readonly tuple может стать несовместимым. В таком случае лучше аннотировать нужный контракт или принимать `readonly`-коллекцию в функции, если она её не изменяет.

`satisfies Record<string, string>` проверяет значения, но не ограничивает конкретный набор ключей. Если полнота словаря важна, ключи задают точным union: `Record<Status, string>`.

#### Ключевые уточнения

- `const` запрещает переприсвоить переменную; `as const` дополнительно сохраняет литералы и делает свойства выражения `readonly` на уровне типов.
- `as const` не является глубокой runtime-заморозкой.
- `satisfies` проверяет совместимость, но не меняет runtime-значение.
- `satisfies` не заменяет annotation, когда наружу нужно намеренно скрыть детали и оставить только публичный тип.
- Для внешнего JSON обе конструкции бесполезны без runtime validation.

#### Связанные темы

- [[Конспект для подготовки/TypeScript/Type inference widening и contextual typing]]
- [[Конспект для подготовки/TypeScript/Type assertions и non-null assertion]]
- [[Конспект для подготовки/TypeScript/keyof indexed access mapped types]]
- [[Конспект для подготовки/TypeScript/enum]]
- [[Конспект для подготовки/TypeScript/Unions intersections discriminated unions]]

#### Источники

- [TypeScript 3.4: const assertions](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-4.html#const-assertions)
- [TypeScript 4.9: The satisfies Operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
