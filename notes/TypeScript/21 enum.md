# enum

<!-- NOTE-NAV-TOP:START -->
[← tsconfig и строгий режим](<./20 tsconfig и строгий режим.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [import type и isolatedModules →](<./22 import type и isolatedModules.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`enum` объявляет набор именованных констант. В отличие от type alias и string literal union, обычный enum создаёт JavaScript-объект, поэтому его члены можно использовать в runtime.

Numeric enum поддерживает автоинкремент и генерирует reverse mapping от числа к имени. String enum требует явных строковых значений и не создаёт reverse mapping, но его runtime-значения понятнее в логах и внешних контрактах.

Если нужен только статический набор вариантов, часто проще union литералов. Если нужен обычный runtime-объект и вывод union из его значений, подходит object `as const`. Enum выбирают, когда его именованный runtime API действительно полезен или уже является частью контракта.

## Обычный enum существует в runtime

```ts
enum Role {
  Admin = "admin",
  User = "user",
}

function canEdit(role: Role): boolean {
  return role === Role.Admin;
}
```

После компиляции остаётся объект `Role`. Поэтому enum можно передать функции, перечислить через `Object.values` и импортировать как значение. Это отличает его от `type Role = "admin" | "user"`, который полностью стирается.

## Числовой enum

```ts
enum HttpStatus {
  Ok = 200,
  NotFound = 404,
}

HttpStatus.Ok;
// 200

HttpStatus[200];
// "Ok"
```

Numeric enum генерирует прямое и обратное соответствие. У членов без initializer значения автоматически увеличиваются от предыдущего числового члена:

```ts
enum Direction {
  Up,    // 0
  Down,  // 1
  Left,  // 2
  Right, // 3
}
```

Автоинкремент удобен только когда конкретные числа не являются внешним стабильным контрактом. Для network protocol, storage и аналитики значения задают явно, иначе перестановка членов изменит данные.

## Строковый enum

```ts
enum RequestStatus {
  Idle = "idle",
  Loading = "loading",
  Success = "success",
  Error = "error",
}
```

Строки самодокументируемы в логах и сериализованных данных. Reverse mapping не генерируется. При изменении строкового значения нужно учитывать backend, storage и другие потребители контракта.

Как и любой TypeScript-тип, enum не проверяет внешние данные. Полученное число или строку сначала проверяют на допустимость, а не приводят через `as RequestStatus`.

## `const enum`

```ts
const enum Direction {
  Up,
  Down,
}

const direction = Direction.Up;
```

Члены `const enum` обычно инлайнятся в места использования, а runtime-объект не создаётся. Поэтому нельзя рассчитывать на `Object.values(Direction)`.

Внутри закрытого проекта с контролируемой цепочкой сборки это может быть допустимо. Публикация ambient `const enum` в `.d.ts` опаснее:

- downstream-проект с `isolatedModules` может быть несовместим;
- проект-потребитель способен скомпилироваться с одной версией значений, а при выполнении получить другую;
- type-only import нельзя использовать как источник runtime-значений.

Поэтому публичные библиотеки обычно не экспортируют ambient `const enum` либо используют отдельную стратегию с `preserveConstEnums` и обработкой declarations.

## Альтернативы

Только тип:

```ts
type Status = "idle" | "loading" | "success" | "error";
```

Runtime-объект и производный тип:

```ts
const STATUS = {
  Idle: "idle",
  Loading: "loading",
  Success: "success",
  Error: "error",
} as const;

type Status = typeof STATUS[keyof typeof STATUS];
```

Object `as const` — обычный JavaScript-объект. В отличие от enum, он не получает специальный enum emit и легко комбинируется с существующим JavaScript. Но если приложению достаточно union, сам объект не нужен.

## Критерий выбора

| Потребность | Подход |
| --- | --- |
| Только ограничить варианты в типах | literal union |
| Нужны и значения в runtime, и union значений | object `as const` |
| Нужен именованный enum API или существующий контракт | обычный enum |
| Нужны bit flags или числовой протокол | явно заданный numeric enum либо константы |
| Нужен инлайнинг в закрытом контролируемом проекте | `const enum` после проверки цепочки сборки |

## Ключевые уточнения

- Обычный enum создаёт JavaScript; string union не создаёт.
- Numeric enum имеет reverse mapping, string enum — нет.
- Внешнее значение всё равно требует runtime validation, даже если совпадает с типом enum.
- Heterogeneous enum со строками и числами обычно ухудшает модель и сериализацию.
- `const enum` не является просто «более быстрым enum»: отсутствие runtime-объекта и правила публикации меняют его область применения.
- Object `as const` и enum оба могут существовать в runtime, но компилируются и типизируются по-разному.

## Связанные темы

- [as const и satisfies](<./19 as const и satisfies.md>)
- [Объединения, пересечения и дискриминируемые объединения](<./06 Объединения, пересечения и дискриминируемые объединения.md>)
- [import type и isolatedModules](<./22 import type и isolatedModules.md>)
- [Файлы деклараций](<./23 Файлы деклараций.md>)
- [Проверка данных с бэкенда](<./24 Проверка данных с бэкенда.md>)

## Источники

- [TypeScript Handbook: Enums](https://www.typescriptlang.org/docs/handbook/enums.html)
- [TypeScript TSConfig: preserveConstEnums](https://www.typescriptlang.org/tsconfig/preserveConstEnums.html)
- [TypeScript TSConfig: isolatedModules](https://www.typescriptlang.org/tsconfig/isolatedModules.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← tsconfig и строгий режим](<./20 tsconfig и строгий режим.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [import type и isolatedModules →](<./22 import type и isolatedModules.md>)
<!-- NOTE-NAV-BOTTOM:END -->
