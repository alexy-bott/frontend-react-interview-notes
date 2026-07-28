---
aliases:
  - type assertion
  - утверждение типа
  - as TypeScript
  - non-null assertion
  - оператор восклицательного знака TypeScript
---

#### Быстрый ответ

Type assertion `value as T` сообщает компилятору, что разработчик знает тип точнее, чем TypeScript. Assertion не проверяет значение и не преобразует его в runtime: объект остаётся прежним, меняется только статическое представление компилятора.

Non-null assertion `value!` удаляет из типа `null` и `undefined`, также без runtime-проверки. Если предположение неверно, код может упасть. Поэтому assertions используют на узких границах, где корректность уже гарантирована внешним условием, а в обычной логике предпочитают narrowing, type guards и явную обработку отсутствующего значения.

#### Зачем нужны assertions

TypeScript анализирует код статически и не знает некоторые факты окружения. Например, разработчик может знать, что DOM-элемент уже создан шаблоном или что библиотека гарантирует конкретный подтип. В таких местах assertion позволяет передать компилятору недостающую информацию.

```ts
const input = document.querySelector("#search") as HTMLInputElement;
```

Но селектор может не найти элемент. Кроме того, элемент с таким `id` может оказаться не `input`. Assertion скрывает обе возможности, поэтому безопаснее проверить результат:

```ts
const element = document.querySelector("#search");

if (!(element instanceof HTMLInputElement)) {
  throw new Error("Search input is missing");
}

element.focus();
```

Теперь проверка существует и для TypeScript, и для runtime.

#### `as`, аннотация и `satisfies`

| Конструкция | Что делает |
| --- | --- |
| `const value: T = expression` | проверяет expression и задаёт переменной тип `T` |
| `expression as T` | утверждает, что expression следует рассматривать как `T` |
| `expression satisfies T` | проверяет совместимость с `T`, сохраняя точный выведенный тип expression |

```ts
type Config = {
  mode: "light" | "dark";
};

const a: Config = { mode: "dark" };
// a.mode: "light" | "dark"

const b = { mode: "dark" } satisfies Config;
// b.mode: "dark"
```

Для конфигураций и словарей `satisfies` обычно лучше assertion: он действительно проверяет объект, а не заставляет компилятор принять предположение.

#### Non-null assertion `!`

```ts
const root = document.getElementById("root")!;
root.textContent = "Ready";
```

`!` убрал `null` только из типа. Если элемента нет, обращение к `textContent` всё равно завершится ошибкой. Такой код оправдан, если наличие `#root` является проверенным инвариантом приложения и ошибка должна считаться нарушением сборки или шаблона. В остальных случаях лучше обработать `null` явно.

Не следует путать `value!` с `!value`: первое является TypeScript assertion после выражения, второе — JavaScript-оператор логического отрицания.

#### Двойной assertion

Запись `value as unknown as T` обходит ограничение совместимости типов. Она означает: сначала забыть исходный тип, затем без проверки назначить новый.

Это может потребоваться в низкоуровневом адаптере или тестовом mock, но в прикладной логике обычно указывает на неверный контракт. Такой переход изолируют в одном месте и поясняют, какой внешний инвариант делает его допустимым.

#### Ключевые уточнения

- Assertions стираются при компиляции и не валидируют внешние данные.
- Сужение через `typeof`, `instanceof`, discriminant или type guard безопаснее, потому что опирается на реальную проверку.
- `as const` является специальным assertion с отдельной семантикой: сохраняет литералы и добавляет `readonly` на уровне типов.
- `!` используют только когда отсутствие значения исключено реальным инвариантом, а не ради устранения ошибки компилятора.
- Assertion допустим на границе с неточно типизированным API; наружу такой адаптер должен возвращать проверенный контракт.

#### Связанные темы

- [[Конспект для подготовки/TypeScript/Type Guards]]
- [[Конспект для подготовки/TypeScript/as const и satisfies]]
- [[Конспект для подготовки/TypeScript/never any unknown]]
- [[Конспект для подготовки/TypeScript/Проверка данных с backend]]
- [[Конспект для подготовки/TypeScript/Type inference widening и contextual typing]]

#### Источники

- [TypeScript Handbook: Type Assertions](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions)
- [TypeScript 4.9: The satisfies Operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
