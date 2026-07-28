---
aliases:
  - Type Guards
  - type guard
  - type predicate
  - сужение типов
  - control flow analysis TypeScript
---

#### Быстрый ответ

Narrowing, или сужение типа, — это уточнение широкого типа на основании проверок и потока выполнения. Если значение имеет тип `string | number`, после `typeof value === "string"` TypeScript знает, что в этой ветке это строка.

Type guard — условие, которое TypeScript умеет связать с таким уточнением. Встроенные способы: `typeof`, `instanceof`, `in`, `Array.isArray`, сравнение с литералом, проверка `null` и equality narrowing. Для доменного типа можно написать функцию-предикат с результатом `value is User`.

Проверка выполняется JavaScript в runtime, а TypeScript анализирует её результат статически. Пользовательскому предикату компилятор доверяет, поэтому его реализация должна действительно подтверждать все признаки, на которых дальше полагается код.

#### Как работает narrowing

TypeScript отслеживает присваивания, условия, ранние возвраты и достижимость веток. Это называется control flow analysis — анализ потока управления.

```ts
function format(value: string | number): string {
  if (typeof value === "number") {
    return value.toFixed(2);
  }

  return value.trim();
}
```

После раннего `return` ветка с `number` недостижима, поэтому в оставшемся коде `value` сужен до `string`. Сужение относится к конкретной точке программы; после присваивания нового значения или вызова, способного изменить объект, оно может быть пересчитано или потеряно.

#### Встроенные guards

| Проверка | Что подтверждает | Важная граница |
| --- | --- | --- |
| `typeof value === "string"` | JavaScript primitive и `function` | для `null` возвращается `"object"` |
| `value instanceof Date` | связь с constructor prototype | может не сработать между разными realms |
| `"id" in value` | свойство есть в объекте или prototype chain | сначала значение должно быть объектом |
| `Array.isArray(value)` | значение является массивом | тип элементов отдельно не проверен |
| `value === null` | точное значение `null` | не покрывает `undefined` |
| `result.status === "success"` | вариант discriminated union | поле должно иметь литеральные типы |

Equality narrowing также связывает два значения. Если `a: string | number` и `b: string`, то внутри `a === b` переменная `a` может быть только строкой.

#### Сужение по truthy/falsy

Проверка `if (value)` исключает все falsy-значения: `undefined`, `null`, `false`, `0`, `NaN` и `""`. Она подходит, только если каждое из них действительно означает отсутствие значения.

```ts
function printLength(value: string | null) {
  if (value) {
    console.log(value.length);
  }
}
```

Пустая строка здесь тоже пропускается. Если она является допустимым значением, точнее проверить `value !== null`.

#### Пользовательский type predicate

```ts
type User = {
  id: number;
  name: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isUser(value: unknown): value is User {
  return (
    isRecord(value) &&
    typeof value.id === "number" &&
    typeof value.name === "string"
  );
}
```

`value is User` связывает `true` с типом аргумента. В JavaScript функция возвращает обычный boolean; дополнительный смысл существует для компилятора.

TypeScript не доказывает корректность предиката. Функция `isUser`, которая проверяет только `id` или всегда возвращает `true`, создаст ложную гарантию. Поэтому type predicate должен подтверждать тот runtime-контракт, который обещает.

#### Type guards в массивах

Предикат особенно полезен в `filter`:

```ts
const values: Array<User | null> = [
  { id: 1, name: "Ann" },
  null,
];

function isPresent<T>(value: T | null | undefined): value is T {
  return value != null;
}

const users = values.filter(isPresent);
// User[]
```

Обычная функция фильтра с результатом `boolean` не всегда передаёт достаточно информации о новом типе массива. Type predicate формально связывает условие фильтрации с типом элемента.

#### Assertion functions

Assertion function не возвращает boolean вызывающему коду, а либо подтверждает условие, либо бросает ошибку:

```ts
function assertUser(value: unknown): asserts value is User {
  if (!isUser(value)) {
    throw new Error("Invalid user");
  }
}

const payload: unknown = JSON.parse('{"id":1,"name":"Ann"}');
assertUser(payload);

payload.name;
// после assertUser тип payload — User
```

Такой API удобен на границе данных, когда невалидное значение должно сразу прервать выполнение. Если ошибка является ожидаемым результатом, schema validator или тип `Result` может дать более удобную модель.

#### Ключевые уточнения

- Guard является runtime-проверкой; narrowing — статическим выводом TypeScript на её основе.
- `typeof value === "object"` требует отдельной проверки `value !== null`.
- `Array.isArray` доказывает массив, но не тип каждого элемента.
- `instanceof` проверяет prototype chain и может быть ненадёжен для JSON и объектов из другого iframe или контекста выполнения (realm).
- Truthiness-проверка подходит только тогда, когда все falsy-значения действительно нужно исключить.
- Пользовательский predicate и assertion function являются обещанием разработчика компилятору; неверная реализация опасна так же, как необоснованный `as`.

#### Связанные темы

- [[Конспект для подготовки/TypeScript/Unions intersections discriminated unions]]
- [[Конспект для подготовки/TypeScript/never any unknown]]
- [[Конспект для подготовки/TypeScript/Проверка данных с backend]]
- [[Конспект для подготовки/TypeScript/Type assertions и non-null assertion]]
- [[Конспект для подготовки/TypeScript/Array map типизация]]

#### Источники

- [TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript 3.7: Assertion Functions](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-7.html#assertion-functions)
