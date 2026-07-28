---
aliases:
  - Array map типизация
  - Array.map TypeScript
  - map generic
  - async map
---

#### Быстрый ответ

`Array.map` типизирован как преобразование каждого элемента `T` в новое значение `U`. Функция обратного вызова (callback) получает элемент, индекс и исходный массив, а результатом `map` становится `U[]`. Тип `U` обычно выводится из всех возможных значений, возвращаемых callback.

`map` сохраняет количество позиций и не фильтрует `null` или `undefined`. Если callback возвращает `User | null`, итог имеет тип `(User | null)[]`. Для удаления вариантов нужен `filter` с сужением типа, `flatMap` или отдельный проход.

Асинхронный callback возвращает `Promise<U>`, поэтому `map` создаёт `Promise<U>[]`, а не `Promise<U[]>`. Чтобы дождаться всех операций, массив передают в `Promise.all`.

#### Упрощённая сигнатура

```ts
interface Array<T> {
  map<U>(
    callback: (value: T, index: number, array: T[]) => U,
    thisArg?: unknown
  ): U[];
}
```

`T` принадлежит исходному массиву, `U` выбирается по результату callback. Поэтому `map` может изменить тип элементов:

```ts
const ids = [1, 2, 3];
const labels = ids.map(id => `item-${id}`);
// string[]
```

Для `ReadonlyArray<T>` callback видит readonly-массив, но результатом всё равно является новый изменяемый `U[]`: метод не меняет исходную коллекцию.

#### Как выводится результат

```ts
type User = {
  id: number;
  name: string;
  active: boolean;
};

const users: User[] = [
  { id: 1, name: "Ann", active: true },
  { id: 2, name: "Bob", active: false },
];

const names = users.map(user => user.name);
// string[]

const activeOrNull = users.map(user =>
  user.active ? user : null
);
// (User | null)[]
```

Во втором callback одна ветка возвращает `User`, другая — `null`. TypeScript строит общий результат `User | null`, затем массив этого типа.

Явный type argument `users.map<string>(...)` нужен редко. Он полезен как ожидаемый контракт, но обычно return expression уже даёт точный вывод.

#### `map` и фильтрация

`map` вызывает callback для каждого существующего элемента и помещает результат в соответствующую позицию. Возврат `null` не удаляет элемент.

```ts
function isPresent<T>(value: T | null | undefined): value is T {
  return value != null;
}

const activeUsers = activeOrNull.filter(isPresent);
// User[]
```

Если преобразование и фильтрация являются одной операцией, можно использовать `flatMap`:

```ts
const activeNames = users.flatMap(user =>
  user.active ? [user.name] : []
);
// string[]
```

Выбор зависит от читаемости: отдельные `map` и `filter` понятнее, если шаги имеют самостоятельный смысл.

#### Кортежи (tuples) в результате

```ts
const entries = users.map(user => [user.id, user.name] as const);
// Array<readonly [number, string]>
```

Без `as const` литерал массива обычно выводится как `(string | number)[]`: длина и тип каждой позиции теряются. Const assertion сохраняет tuple фиксированной длины.

#### Асинхронный callback

```ts
declare function loadProfile(id: number): Promise<User>;

const promises = [1, 2, 3].map(loadProfile);
// Promise<User>[]

const loadedUsers = await Promise.all(promises);
// User[]
```

`map` сам не знает об асинхронности и не ожидает promises. `Promise.all` создаёт один promise, который завершается массивом результатов в исходном порядке. Реализация `loadProfile` отдельно отвечает за проверку ответа API.

#### Ключевые уточнения

- Тип результата `U` выводится из каждого возможного `return` callback.
- `map` преобразует, но не удаляет элементы и не выполняет narrowing сам по себе.
- `filter(Boolean)` не является универсальным доказательством типа для сложных unions; явный predicate точнее.
- Const assertion нужен, когда результат должен сохранить tuple, а не стать обычным массивом union-элементов.
- Async `map` возвращает массив promises; ожидание выполняет `Promise.all` или другая выбранная стратегия.
- `map` пропускает пустые позиции sparse array и сохраняет разреженность; в прикладном коде лучше не строить логику на sparse arrays.

#### Связанные темы

- [[Конспект для подготовки/TypeScript/Generics]]
- [[Конспект для подготовки/TypeScript/Type Guards]]
- [[Конспект для подготовки/TypeScript/as const и satisfies]]
- [[Конспект для подготовки/JavaScript/Массивы и методы массивов]]
- [[Конспект для подготовки/JavaScript/Promise combinators]]

#### Источники

- [TypeScript source: Array and ReadonlyArray definitions](https://github.com/microsoft/TypeScript/blob/main/src/lib/es5.d.ts)
- [MDN: Array.prototype.map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map)
- [MDN: Promise.all](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)
