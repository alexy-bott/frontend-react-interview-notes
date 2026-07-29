# Structural typing

<!-- NOTE-NAV-TOP:START -->
[← type vs interface](<./type vs interface.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Типизация функций →](<./Типизация функций.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

TypeScript использует преимущественно структурную типизацию: совместимость определяется доступными членами типа, а не его именем. Если объект содержит все обязательные поля ожидаемого типа с совместимыми значениями, его можно использовать, даже если он объявлен через другой `type` или `interface`.

Модель естественна для JavaScript и поддерживает композицию: функция может запросить только `{ id: string }` и принять любой более богатый объект с таким полем. Обратная сторона — разные доменные сущности с одинаковой структурой могут оказаться совместимыми.

Excess property check — дополнительная проверка свежего object literal. Она обнаруживает вероятные опечатки в лишних полях, но не меняет основное правило структурной совместимости.

## Совместимость по форме

```ts
type Named = {
  name: string;
};

type User = {
  id: string;
  name: string;
};

const user: User = { id: "u1", name: "Ann" };
const named: Named = user;
```

Присваивание допустимо: у `user` есть всё, что требуется `Named`. Дополнительное поле `id` не мешает коду, который использует только `name`.

Это позволяет функциям принимать минимальный необходимый контракт:

```ts
function getName(value: { name: string }): string {
  return value.name;
}

getName(user);
```

Функция не зависит от конкретного `User` и подходит для любого значения нужной формы.

## Проверка лишних полей object literal

Свежий object literal проверяется строже:

```ts
getName({ name: "Ann", nmae: "Bob" });
// ошибка: лишнее поле nmae, вероятно опечатка
```

Если сохранить объект в переменную, применяется обычная структурная совместимость:

```ts
const value = { name: "Ann", role: "admin" };
getName(value);
// допустимо: обязательное поле name присутствует
```

Проверка object literal не гарантирует «точный тип без лишних полей». Это эвристика для мест, где лишнее поле часто является ошибкой. В runtime оба объекта сохраняют все свои свойства.

## Когда одинаковая форма нежелательна

```ts
type UserId = string;
type OrderId = string;

declare const userId: UserId;
const orderId: OrderId = userId;
// допустимо: оба типа являются string
```

Если смешивание идентификаторов опасно, можно добавить brand — фиктивный уникальный признак на уровне типов:

```ts
declare const userIdBrand: unique symbol;
declare const orderIdBrand: unique symbol;

type UserId = string & { readonly [userIdBrand]: true };
type OrderId = string & { readonly [orderIdBrand]: true };

function createUserId(value: string): UserId {
  if (!value.startsWith("user_")) {
    throw new Error("Invalid user id");
  }

  return value as UserId;
}
```

Обычная строка больше не совместима с `UserId`. Assertion изолирован внутри конструктора, который проверяет инвариант. Brand обычно не существует в runtime, если отдельно не добавлять свойство объекту.

## Исключения и ограничения модели

TypeScript не является структурным без исключений. Private и protected members классов учитывают происхождение объявления, поэтому два класса с одинаковыми публичными полями могут быть несовместимы. Нативные `#private` поля также создают отдельную идентичность класса.

Совместимость функций зависит не только от формы объекта, но и от параметров, результата и настроек вроде `strictFunctionTypes`. Эта часть подробно разобрана в [Variance и совместимость функций](<./Variance и совместимость функций.md>).

## Структурная и номинальная модели

| Модель | Критерий совместимости | Где полезна |
| --- | --- | --- |
| Structural | нужные поля и сигнатуры совпадают | обычные объекты, callbacks, композиция API |
| Nominal | типы имеют одну декларацию или явную identity | доменные IDs, единицы измерения, сущности, которые нельзя смешивать |

TypeScript по умолчанию выбирает структурную модель. Branded types добавляют nominal-like ограничение точечно, когда цена случайного смешивания выше стоимости дополнительного конструктора.

## Ключевые уточнения

- Разные имена interfaces или type aliases не делают одинаковые структуры несовместимыми.
- Дополнительные поля обычно допустимы, если все обязательные требования ожидаемого типа выполнены.
- Excess property check применяется прежде всего к свежим object literals и помогает находить опечатки.
- Brand добавляют только для реального доменного инварианта; повсеместный branding усложняет код без пользы.
- Assertion при создании branded value должен находиться за проверяющей функцией, а не быть разбросан по приложению.
- Статический brand не валидирует значение после получения из API или storage.

## Связанные темы

- [type vs interface](<./type vs interface.md>)
- [Variance и совместимость функций](<./Variance и совместимость функций.md>)
- [Type assertions и non-null assertion](<./Type assertions и non-null assertion.md>)
- [Классы access modifiers abstract и private](<./Классы access modifiers abstract и private.md>)
- [Проверка данных с backend](<./Проверка данных с backend.md>)

## Источники

- [TypeScript Handbook: Type Compatibility](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)
- [TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- [TypeScript Handbook: Classes](https://www.typescriptlang.org/docs/handbook/2/classes.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← type vs interface](<./type vs interface.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Типизация функций →](<./Типизация функций.md>)
<!-- NOTE-NAV-BOTTOM:END -->
