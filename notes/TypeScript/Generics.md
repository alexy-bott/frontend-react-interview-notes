# Generics

<!-- NOTE-NAV-TOP:START -->
[← Классы access modifiers abstract и private](<./Классы access modifiers abstract и private.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Function overloads →](<./Function overloads.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Generic, или обобщённый тип, позволяет описать алгоритм для разных типов и сохранить связь между ними. В `function identity<T>(value: T): T` параметр `T` запоминает конкретный тип аргумента и переносит его в результат. В отличие от `any`, информация не теряется.

Generics применяют в функциях, коллекциях, API-обёртках, hooks и компонентах, когда один контракт повторяется для разных данных. TypeScript часто выводит параметры типа из аргументов; явно писать `<User>` нужно только когда информации для вывода недостаточно или тип требуется зафиксировать.

Constraint `T extends U` задаёт минимальные требования к `T`. Он нужен, если generic-код обращается к известным свойствам. Generic существует только при проверке типов и не валидирует значение в runtime.

## Какую проблему решает generic

Без generic приходится выбрать между дублированием overloads, потерей точности через `unknown` и отключением проверки через `any`:

```ts
function identityAny(value: any): any {
  return value;
}

const result = identityAny("text");
// any — связь потеряна
```

Generic выражает именно связь:

```ts
function identity<T>(value: T): T {
  return value;
}

const result = identity("text");
// string
```

`T` не означает «любой тип внутри функции». Он означает один конкретный тип, выбранный для данного вызова. Реализация обязана работать для каждого допустимого выбора `T`.

## Вывод параметров типа

```ts
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}

const name = first(["Ann", "Bob"]);
// string | undefined
```

TypeScript выводит `T` из типа массива. Явное `first<string>(...)` здесь дублирует уже известную информацию.

Иногда вывести тип неоткуда:

```ts
type ApiResponse<T> = {
  data: T;
};

type User = {
  id: string;
  name: string;
};

declare function request<T>(url: string): Promise<ApiResponse<T>>;

const response = request<User>("/users/1");
```

`<User>` задаёт статический контракт результата, но не доказывает, что сервер вернул `User`. На внешней границе всё равно нужна runtime validation.

## Ограничения (constraints) через `extends`

Без ограничения `T` может быть числом, строкой или `null`, поэтому читать произвольное поле нельзя:

```ts
function getId<T extends { id: string }>(value: T): string {
  return value.id;
}
```

Constraint читается так: функция принимает любой тип, совместимый с `{ id: string }`. Он не превращает аргумент в этот базовый объект — конкретный `T` сохраняется.

Для связи объекта и ключа используют два параметра:

```ts
function getValue<T, K extends keyof T>(object: T, key: K): T[K] {
  return object[key];
}

const user = { id: 1, name: "Ann" };

const id = getValue(user, "id");
// number
```

`K` ограничен реальными ключами `T`, а `T[K]` связывает конкретный ключ с типом его значения.

## Generic-типы, interfaces и классы

```ts
type Result<TData, TError = Error> =
  | { status: "success"; data: TData }
  | { status: "error"; error: TError };

interface Repository<TEntity> {
  getById(id: string): Promise<TEntity | null>;
}
```

Параметр по умолчанию `TError = Error` позволяет не повторять распространённый вариант, но при необходимости заменить его. Имена `TData`, `TError`, `TKey` понятнее одиночных букв, когда параметров несколько или область большая.

## Когда generic лишний

Generic должен связывать хотя бы две позиции или сохранять информацию для дальнейшего использования:

```ts
function log<T>(value: T): void {
  console.log(value);
}
```

Здесь `T` нигде не используется кроме одного входа. Функция не возвращает значение и не связывает его с callback или другим аргументом, поэтому проще и честнее `log(value: unknown): void`.

Слишком широкий constraint также может скрывать более простой контракт. Если функция всегда работает только с `User`, generic `T extends User` не делает её универсальной автоматически.

## Generics и выполнение программы

После компиляции параметров типа нет:

```ts
function parse<T>(json: string): T {
  return JSON.parse(json) as T;
}
```

Такая функция не проверяет `T`; она только централизует assertion. Без schema или guard вызов `parse<User>(...)` может вернуть объект любой формы. Generic описывает связь статических типов, а не создаёт runtime-информацию о них.

## Ключевые уточнения

- Generic сохраняет связь типов; `any` эту связь уничтожает.
- Type parameter выбирается для конкретного вызова, а реализация должна быть корректна для всех допустимых вариантов.
- `extends` у generic задаёт constraint, а не наследование runtime-класса.
- Явный type argument не является валидацией и может создать ложное доверие к внешним данным.
- Чем меньше параметров типа и чем очевиднее их связь, тем понятнее API.
- Для конечного набора разных сигнатур overload может быть яснее; для взаимоисключающих данных — discriminated union.

## Связанные темы

- [Type inference widening и contextual typing](<./Type inference widening и contextual typing.md>)
- [keyof indexed access mapped types](<./keyof indexed access mapped types.md>)
- [Function overloads](<./Function overloads.md>)
- [Variance и совместимость функций](<./Variance и совместимость функций.md>)
- [Проверка данных с backend](<./Проверка данных с backend.md>)

## Источники

- [TypeScript Handbook: Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [TypeScript Handbook: Guidelines for Writing Good Generic Functions](https://www.typescriptlang.org/docs/handbook/2/functions.html#guidelines-for-writing-good-generic-functions)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Классы access modifiers abstract и private](<./Классы access modifiers abstract и private.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Function overloads →](<./Function overloads.md>)
<!-- NOTE-NAV-BOTTOM:END -->
