---
aliases:
  - property descriptors
  - getters setters
  - Object.defineProperty
  - дескриптор свойства
---

#### Быстрый ответ

Дескриптор свойства (`property descriptor`) описывает не только значение собственного свойства, но и правила чтения, записи, перечисления, удаления и переопределения.

Дескриптор данных (`data descriptor`) содержит `value` и `writable`. Дескриптор доступа (`accessor descriptor`) содержит `get` и `set`. Оба вида могут содержать `enumerable` и `configurable`; смешивать `value` с `get` или `set` в одном дескрипторе нельзя.

Getter вызывается при чтении свойства, setter - при присваивании. Они позволяют представить вычисление или проверку значения как доступ к свойству, но не должны скрывать сетевой запрос, тяжёлую работу или неожиданные побочные эффекты.

`Object.preventExtensions`, `Object.seal` и `Object.freeze` меняют возможности собственных свойств только верхнего уровня. Они не делают весь граф вложенных объектов автоматически неизменяемым.

#### Ключевая схема

| Вид свойства | Поля дескриптора |
| --- | --- |
| Свойство данных | `value`, `writable`, `enumerable`, `configurable` |
| Свойство доступа | `get`, `set`, `enumerable`, `configurable` |

| Флаг | Что контролирует |
| --- | --- |
| `writable` | можно ли присвоить свойству данных другое значение |
| `enumerable` | участвует ли собственный строковый ключ в обычном перечислении |
| `configurable` | можно ли удалить свойство и существенно изменить его дескриптор |

#### Дескриптор данных

```js
const user = {};

Object.defineProperty(user, "id", {
  value: "u1",
  writable: false,
  enumerable: true,
  configurable: false,
});

console.log(user.id); // "u1"
console.log(Object.keys(user)); // ["id"]
```

В коде без strict mode присваивание свойству с `writable: false` обычно молча не изменяет значение. В strict mode оно выбрасывает `TypeError`:

```js
"use strict";
user.id = "u2"; // TypeError
```

Собственное свойство данных хранит значение непосредственно в дескрипторе. Если это значение является объектом, флаги свойства не замораживают вложенный объект:

```js
const state = {};

Object.defineProperty(state, "settings", {
  value: { theme: "light" },
  writable: false,
});

state.settings.theme = "dark"; // Вложенный объект изменён.
```

Нельзя заменить `settings`, но можно изменить объект, на который оно указывает.

#### Дескриптор доступа

Свойство доступа не хранит обычное `value`. Чтение вызывает getter, а присваивание вызывает setter:

```js
const user = {
  firstName: "Ada",
  lastName: "Lovelace",

  get fullName() {
    return `${this.firstName} ${this.lastName}`;
  },

  set fullName(value) {
    [this.firstName, this.lastName] = value.split(" ");
  },
};

console.log(user.fullName); // "Ada Lovelace"
user.fullName = "Grace Hopper";
```

`this` внутри getter или setter определяется объектом-получателем чтения или записи. Если getter унаследован через прототип, он может читать собственные свойства дочернего объекта:

```js
const person = {
  get label() {
    return this.name;
  },
};

const user = Object.create(person);
user.name = "Ann";

console.log(user.label); // "Ann"
```

Getter вызывается синтаксисом обычного свойства, поэтому вызывающий код может не ожидать большой стоимости. Для сетевого запроса, асинхронной работы и команды изменения состояния лучше использовать явный метод.

#### Значения флагов по умолчанию

Свойства, созданные обычным присваиванием или литералом объекта, обычно имеют `writable`, `enumerable` и `configurable`, равные `true`:

```js
const object = { value: 1 };
console.log(Object.getOwnPropertyDescriptor(object, "value"));
// { value: 1, writable: true, enumerable: true, configurable: true }
```

У `Object.defineProperty` пропущенные логические флаги получают `false`:

```js
Object.defineProperty(object, "hidden", {
  value: 2,
});

console.log(Object.keys(object)); // ["value"]
```

`hidden` также получает `writable: false` и `configurable: false`. Это частая причина неожиданного поведения при ручном определении свойств.

#### `enumerable`

Собственные перечисляемые свойства со строковыми ключами участвуют в:

- `Object.keys`, `Object.values`, `Object.entries`;
- object spread;
- чтении исходного объекта в `Object.assign`;
- `for...in`, где дополнительно учитываются унаследованные перечисляемые ключи;
- обычной JSON-сериализации собственных свойств со строковыми ключами.

Неперечисляемое свойство всё равно доступно напрямую и видно через `Object.getOwnPropertyNames` или `Reflect.ownKeys`.

Символьные ключи не входят в `Object.keys` и JSON независимо от `enumerable`, но перечисляемые символы копируются через object spread и `Object.assign`.

Оператор `in` и `Object.hasOwn` проверяют существование свойства, а не значение его `enumerable`.

#### `configurable`

`configurable: false` запрещает удалить свойство, сменить дескриптор данных на дескриптор доступа и обратно, а также произвольно изменить флаги.

Для неконфигурируемого свойства данных остаётся одно направление ужесточения: `writable: true` можно изменить на `false`, но вернуть обратно нельзя.

```js
const config = {};

Object.defineProperty(config, "version", {
  value: 1,
  writable: true,
  configurable: false,
});

Object.defineProperty(config, "version", {
  writable: false,
});
```

Неконфигурируемый контракт почти необратим. Его применяют для устойчивых платформенных ограничений, а не как повседневный способ управления состоянием UI.

#### Чтение дескрипторов

```js
Object.getOwnPropertyDescriptor(object, "value");
Object.getOwnPropertyDescriptors(object);
```

Первый метод получает дескриптор одного собственного свойства. Второй возвращает дескрипторы всех собственных строковых и символьных ключей.

Это позволяет создать поверхностную копию с тем же прототипом и дескрипторами:

```js
const clone = Object.create(
  Object.getPrototypeOf(source),
  Object.getOwnPropertyDescriptors(source),
);
```

Копия сохраняет getters, setters, флаги и прототип. Вложенные значения всё ещё разделяются с исходным объектом, а внутренние слоты встроенных объектов таким способом не клонируются.

#### Spread и `Object.assign`

При копировании исходного объекта оба механизма читают его собственные перечисляемые свойства. Если исходный объект содержит getter, тот выполняется, а в целевой объект попадает возвращённое значение, а не дескриптор доступа.

```js
const source = {
  get value() {
    console.log("getter called");
    return 42;
  },
};

const copy = { ...source };
console.log(Object.getOwnPropertyDescriptor(copy, "value"));
// обычное свойство данных со значением 42
```

На стороне целевого объекта есть различие. `Object.assign(target, source)` выполняет обычное присваивание и может вызвать setter объекта `target`. Spread внутри нового литерала создаёт собственные свойства данных и не вызывает setter из прототипа как обычное присваивание.

#### `preventExtensions`, `seal`, `freeze`

| Операция | Добавить собственное свойство | Удалить | Изменить значение свойства данных |
| --- | --- | --- | --- |
| `Object.preventExtensions` | нет | да, если configurable | да, если writable |
| `Object.seal` | нет | нет | да, если writable |
| `Object.freeze` | нет | нет | нет для собственных свойств данных |

`seal` запрещает расширять объект и делает все собственные свойства неконфигурируемыми. `freeze` дополнительно устанавливает `writable: false` для собственных свойств данных.

Свойство доступа после `freeze` всё ещё может иметь setter. Его дескриптор нельзя изменить, но вызов setter способен изменить внешнее или закрытое состояние. Поэтому `freeze` ограничивает дескрипторы объекта, но не гарантирует неизменяемость всего связанного поведения.

Все операции shallow. Подробная модель immutable state находится в [[Конспект для подготовки/JavaScript/Неизменяемость объектов]].

#### Практический выбор

| Задача | Подход |
| --- | --- |
| Недорогое вычисляемое свойство | getter |
| Явная команда или асинхронная операция | метод |
| Скрыть свойство от обычного перечисления | `enumerable: false` |
| Сохранить дескрипторы при поверхностном копировании | `getOwnPropertyDescriptors` + `Object.create` |
| Запретить изменение API-объекта в development | `Object.freeze` с пониманием поверхностной границы |
| Реактивное перехватывание многих operations | `Proxy`, если оправдано |

#### Ключевые уточнения

- Дескрипторы данных и доступа взаимоисключающи.
- Присваивание и литерал объекта создают другие флаги по умолчанию, чем `Object.defineProperty` с пропущенными полями.
- Getter выглядит как чтение свойства, но выполняет функцию и может иметь стоимость или побочные эффекты.
- `enumerable` влияет на обычный обход и копирование, но не на прямой доступ и существование свойства.
- `configurable: false` создаёт почти необратимый контракт.
- Spread и `Object.assign` вызывают getter исходного объекта и не сохраняют его дескриптор.
- `freeze` поверхностен и не гарантирует неизменность вложенного графа или поведения getter и setter.

#### Связанные темы

- [[Конспект для подготовки/JavaScript/Проверка свойств объекта]]
- [[Конспект для подготовки/JavaScript/Копирование объектов]]
- [[Конспект для подготовки/JavaScript/Неизменяемость объектов]]
- [[Конспект для подготовки/JavaScript/Prototype]]
- [[Конспект для подготовки/JavaScript/Proxy и Reflect]]

#### Источники

- [ECMAScript: Property Descriptor Specification Type](https://tc39.es/ecma262/multipage/ecmascript-data-types-and-values.html#sec-property-descriptor-specification-type)
- [MDN: Object.defineProperty](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty)
- [MDN: Object.getOwnPropertyDescriptors](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/getOwnPropertyDescriptors)
- [MDN: Object.freeze](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze)
