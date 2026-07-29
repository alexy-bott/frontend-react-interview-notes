# never any unknown

<!-- NOTE-NAV-TOP:START -->
[← Type inference widening и contextual typing](<./Type inference widening и contextual typing.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Type assertions и non-null assertion →](<./Type assertions и non-null assertion.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`any`, `unknown` и `never` описывают разные границы системы типов.

`any` практически отключает проверку для значения: с ним можно обращаться как с любым типом, а ошибки переходят из compile time в runtime. `unknown` тоже может хранить любое значение, но запрещает операции до narrowing — проверки, которая уточнит тип. Поэтому для недоверенных входных данных выбирают `unknown`, а `any` оставляют локальным временным компромиссом.

`never` означает, что значение невозможно. Он появляется у функции, которая не завершается нормально, в недостижимой ветке и после исключения всех вариантов union. На этом основана исчерпывающая проверка `switch`.

## Сравнение

| Тип | Что можно присвоить | Что можно сделать без проверки | Основной сценарий |
| --- | --- | --- | --- |
| `any` | почти любое значение | почти любую операцию | изолированная миграция или неточные сторонние типы |
| `unknown` | любое значение | только безопасные общие операции | внешние данные и граница доверия |
| `never` | ни одно обычное значение | значение недостижимо | невозможная ветка и exhaustive check |

Короткая модель:

```text
unknown: значение существует, но его тип ещё не доказан
any: компилятор перестаёт контролировать значение
never: такого значения в этой точке быть не может
```

## `unknown`: сначала доказать тип

```ts
function formatError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === "string") {
    return error;
  }

  return "Неизвестная ошибка";
}
```

До проверки нельзя читать `error.message`, потому что в переменной может находиться строка, `null` или любой другой тип. После `instanceof Error` TypeScript сужает значение до `Error` в этой ветке.

`unknown` полезен для API, `JSON.parse`, `localStorage`, WebSocket, `postMessage`, query parameters и ошибок `catch`. Он не валидирует данные сам, а заставляет код явно провести проверку до использования.

## `any`: локальное отключение гарантий

```ts
function formatPrice(value: any) {
  return value.toFixed(2);
}

formatPrice("free");
// TypeScript не остановит вызов, ошибка возникнет в runtime
```

Опасность `any` в распространении. Если функция возвращает `any`, код-потребитель тоже теряет надёжное автодополнение и проверки. Поэтому вынужденный `any` изолируют внутри небольшого адаптера, а наружу возвращают точный тип или `unknown`.

Разумные временные сценарии: поэтапная миграция JavaScript, интеграция с библиотекой без корректных деклараций, низкоуровневый interoperability-код. В каждом случае важно ограничить область действия.

## `never`: невозможное значение

Функция получает результат `never`, если всегда бросает ошибку или не может завершиться:

```ts
function fail(message: string): never {
  throw new Error(message);
}
```

После проверки всех вариантов discriminated union остаток также становится `never`:

```ts
type State =
  | { status: "loading" }
  | { status: "success"; data: string[] }
  | { status: "error"; error: Error };

function render(state: State): string {
  switch (state.status) {
    case "loading":
      return "Загрузка";
    case "success":
      return state.data.join(", ");
    case "error":
      return state.error.message;
    default: {
      const exhaustive: never = state;
      return exhaustive;
    }
  }
}
```

Если добавить новый статус и не обработать его, `state` в `default` больше не будет `never`, и компилятор покажет ошибку.

## Поведение в unions и intersections

- `T | never` упрощается до `T`: невозможный вариант ничего не добавляет.
- `T & never` становится `never`: значение не может одновременно быть `T` и невозможным.
- `T | unknown` становится `unknown`: один из вариантов может быть каким угодно.
- `T & unknown` обычно становится `T`: неизвестное не добавляет требований к уже известному типу.
- `any` может размыть результат вычислений на уровне типов, поэтому его поведение не используют как надёжную логическую модель.

Эти правила особенно заметны в conditional types и фильтрации union.

## Ключевые уточнения

- `unknown` является безопасным входным типом, но реальную проверку всё равно пишет приложение.
- `any` не означает «любой допустимый тип» в безопасном смысле; он отключает значительную часть анализа.
- Assertion `value as T` не превращает `unknown` в проверенное значение, а только меняет мнение компилятора.
- `never` не является аналогом `null`, `undefined` или пустого объекта.
- Exhaustive check полезен для состояний UI, reducer actions и событий, где каждый новый вариант должен быть обработан явно.

## Связанные темы

- [Type Guards](<./Type Guards.md>)
- [Unions intersections discriminated unions](<./Unions intersections discriminated unions.md>)
- [Type assertions и non-null assertion](<./Type assertions и non-null assertion.md>)
- [Проверка данных с backend](<./Проверка данных с backend.md>)
- [infer и conditional types](<./infer и conditional types.md>)

## Источники

- [TypeScript Handbook: The unknown Type](https://www.typescriptlang.org/docs/handbook/2/functions.html#unknown)
- [TypeScript Handbook: The never Type](https://www.typescriptlang.org/docs/handbook/2/functions.html#never)
- [TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Type inference widening и contextual typing](<./Type inference widening и contextual typing.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Type assertions и non-null assertion →](<./Type assertions и non-null assertion.md>)
<!-- NOTE-NAV-BOTTOM:END -->
