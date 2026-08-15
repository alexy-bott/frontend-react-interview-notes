# infer и условные типы

<!-- NOTE-NAV-TOP:START -->
[← Utility Types](<./17 Utility Types.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [as const и satisfies →](<./19 as const и satisfies.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Conditional type выбирает тип по условию совместимости: `T extends U ? X : Y`. Здесь `extends` означает «можно ли использовать `T` как `U`», а не наследование runtime-класса.

`infer` объявляет временный параметр типа внутри успешной ветки условия и извлекает часть структуры: элемент массива, результат функции, параметры callback или значение внутри `Promise`.

Если проверяется «голый» type parameter `T` и ему передан union, условие распределяется по каждому варианту. Это distributive conditional type. Обёртка `[T] extends [U]` проверяет union целиком и отключает распределение.

## Условный тип (conditional type)

```ts
type IsString<T> = T extends string ? true : false;

type A = IsString<"text">;
// true

type B = IsString<number>;
// false
```

Условие проверяется компилятором, а не JavaScript в runtime. Результат — новый тип.

В успешной ветке TypeScript также знает, что `T` удовлетворяет constraint `U`. Это позволяет обращаться к членам `U`:

```ts
type MessageOf<T> = T extends { message: unknown }
  ? T["message"]
  : never;

type Email = { message: string };
type EmailMessage = MessageOf<Email>;
// string
```

## Извлечение через `infer`

```ts
type ElementOf<T> = T extends readonly (infer Item)[]
  ? Item
  : never;

type Item = ElementOf<readonly string[]>;
// string
```

`infer Item` говорит: если `T` имеет форму readonly-массива, назови тип элемента `Item` и используй его в ветке `true`.

Результат функции:

```ts
type FunctionResult<T> = T extends (...args: never[]) => infer Result
  ? Result
  : never;

type Result = FunctionResult<(id: string) => Promise<number>>;
// Promise<number>
```

В реальном коде для этого уже существует `ReturnType<T>`. Свои conditional types пишут, когда встроенного преобразования нет или доменная модель требует другого правила.

## Рекурсивное извлечение

```ts
type DeepAwaited<T> = T extends PromiseLike<infer Value>
  ? DeepAwaited<Value>
  : T;

type Data = DeepAwaited<Promise<Promise<{ id: string }>>>;
// { id: string }
```

Современный TypeScript предоставляет встроенный `Awaited<T>` с более полной семантикой promise-like значений. Самописный пример показывает механизм, но в приложении предпочтительнее стандартный utility type.

## Распределение по union

```ts
type ToArray<T> = T extends unknown ? T[] : never;

type Distributed = ToArray<string | number>;
// string[] | number[]
```

Поскольку слева от `extends` находится непосредственно `T`, TypeScript применяет условие отдельно к `string` и `number`, затем объединяет результаты.

Это удобно для фильтрации union:

```ts
type OnlyStrings<T> = T extends string ? T : never;

type TextValues = OnlyStrings<"idle" | 0 | "ready">;
// "idle" | "ready"
```

Варианты, превратившиеся в `never`, исчезают из итогового union.

## Проверка union целиком

```ts
type ToArrayNonDistributed<T> = [T] extends [unknown]
  ? T[]
  : never;

type Together = ToArrayNonDistributed<string | number>;
// (string | number)[]
```

Tuple-обёртка убирает «голый» `T`, поэтому условие применяется ко всему union один раз. Это не особое поведение tuple в runtime — только приём type system.

## Вывод из overloads

При извлечении результата из перегруженной функции inference обычно опирается на последнюю, наиболее общую сигнатуру. Conditional type не выполняет overload resolution для каждого возможного вызова:

```ts
declare function convert(value: string): number;
declare function convert(value: number): string;
declare function convert(value: string | number): string | number;

type Converted = ReturnType<typeof convert>;
// string | number
```

Если нужен точный тип конкретного вызова, его лучше получить из самого выражения вызова, а не пытаться разбирать overloaded type.

## Граница полезности

Conditional types полезны в библиотеках и инфраструктурных типах, где результат действительно зависит от формы входного типа. В прикладной модели состояния часто понятнее discriminated union, а для конечного API — overload или явный результат.

Рекурсивные условия, несколько `infer` и вложенные mapped types могут сделать ошибки компилятора трудночитаемыми и увеличить время typecheck. Type-level программа должна уменьшать сложность для пользователей API, а не переносить её в каждое место использования.

## Ключевые уточнения

- `extends` в conditional type проверяет assignability, а не создаёт наследование.
- `infer` доступен только внутри `extends`-части conditional type и используется в соответствующей ветке.
- Голый type parameter делает conditional type distributive по union.
- Tuple-обёртка `[T] extends [U]` проверяет union целиком.
- `never` исчезает из union, поэтому удобен для фильтрации вариантов.
- Для стандартных задач сначала проверяют `ReturnType`, `Parameters`, `Awaited`, `Exclude` и другие встроенные utility types.

## Связанные темы

- [Дженерики](<./12 Дженерики.md>)
- [Utility Types](<./17 Utility Types.md>)
- [keyof, indexed access и mapped types](<./16 keyof, indexed access и mapped types.md>)
- [never, any и unknown](<./04 never, any и unknown.md>)
- [Перегрузка функций](<./13 Перегрузка функций.md>)

## Источники

- [TypeScript Handbook: Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)
- [TypeScript Handbook: Inferring Within Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#inferring-within-conditional-types)
- [TypeScript Handbook: Distributive Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#distributive-conditional-types)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Utility Types](<./17 Utility Types.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [as const и satisfies →](<./19 as const и satisfies.md>)
<!-- NOTE-NAV-BOTTOM:END -->
