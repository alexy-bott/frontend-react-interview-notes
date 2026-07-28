---
aliases:
  - optional chaining
  - nullish coalescing
  - optional chaining nullish
  - оператор ??
---

#### Быстрый ответ

Optional chaining `?.` (необязательная цепочка) продолжает чтение свойства, обращение по индексу или вызов, пока значение слева не равно `null` или `undefined`. Если встречается одно из этих значений, вычисление непрерывной цепочки прекращается и результатом становится `undefined`.

Nullish coalescing `??` (оператор нулевого слияния) выбирает правый операнд только для `null` и `undefined`. В отличие от `||`, он сохраняет остальные falsy-значения, то есть значения, приводимые к `false`: `0`, `false`, `""` и `NaN`.

Эти операторы удобны для необязательных данных, но не заменяют валидацию. `user?.profile?.name` не доказывает, что объект имеет правильную структуру, и может скрыть отсутствие обязательного поля.

#### Ключевая схема

```js
value?.property
value?.[expression]
value?.(arguments)

value ?? fallback
value ??= fallback
```

| Значение `value` | `value ?? "default"` | `value || "default"` |
| --- | --- | --- |
| `undefined` | `"default"` | `"default"` |
| `null` | `"default"` | `"default"` |
| `0` | `0` | `"default"` |
| `false` | `false` | `"default"` |
| `""` | `""` | `"default"` |

#### Формы optional chaining

Чтение свойства:

```js
const city = user?.address?.city;
```

Вычисляемый ключ:

```js
const firstItem = items?.[0];
const value = dictionary?.[key];
```

Необязательный вызов:

```js
onComplete?.(result);
service.run?.();
```

`service.run?.()` проверяет только метод. Если сам `service` может быть равен `null` или `undefined`, нужны обе проверки:

```js
service?.run?.();
```

Если свойство существует, но содержит не функцию, необязательный вызов всё равно выбросит `TypeError`. Оператор проверяет отсутствие значения, но не проверяет, можно ли это значение вызвать.

#### Прерывание вычисления

Правая часть необязательной цепочки не вычисляется, если её основание равно `null` или `undefined`:

```js
let index = 0;
const value = items?.[index++];

console.log(index); // 0, если items null или undefined
```

Поэтому аргументы функции, вычисляемые ключи и их побочные эффекты могут не выполниться.

Вычисление прерывается только внутри непрерывной optional chain. Группировка разрывает цепочку:

```js
user?.profile?.name;   // безопасно до name
(user?.profile).name;  // TypeError, если profile отсутствует
```

Первое выражение может прекратить всю цепочку. Во втором результат `user?.profile` вычисляется отдельно, после чего обычный `.name` пытается прочитать свойство у `undefined`.

#### Что `?.` не перехватывает

Optional chaining проверяет только `null` и `undefined` в указанной точке. Он не подавляет:

- ошибку геттера;
- ошибку ловушки (`trap`) объекта `Proxy`;
- `TypeError` при попытке вызвать не функцию;
- `ReferenceError` для необъявленного корневого идентификатора;
- ошибку внутри вызванной функции.

```js
undeclared?.value; // ReferenceError

const object = {
  get value() {
    throw new Error("failed");
  },
};

object?.value; // Error: failed
```

Имя в начале выражения должно существовать в доступной области видимости. В `globalThis.optionalApi?.run()` объект `globalThis` существует, а свойство `optionalApi` уже может отсутствовать.

Optional chain нельзя использовать как левую часть присваивания:

```js
// user?.name = "Ann"; // SyntaxError
```

Если основание цепочки отсутствует, записывать значение некуда. JavaScript не создаёт промежуточный объект автоматически.

#### Nullish coalescing

```js
const pageSize = config.pageSize ?? 20;
const title = response.title ?? "Без названия";
```

Правый операнд вычисляется лениво, только если слева находится `null` или `undefined`:

```js
const settings = cachedSettings ?? loadDefaultSettings();
```

`loadDefaultSettings()` не вызовется, если кэш содержит `false`, `0` или пустую строку.

Значения параметров по умолчанию и значения по умолчанию при деструктуризации тоже срабатывают для `undefined`, но не для `null`:

```js
function render(limit = 10) {}

render(undefined); // limit = 10
render(null);      // limit = null
```

#### `??` и логические операторы

Без скобок JavaScript запрещает смешивать `??` с `&&` или `||`. Скобки должны явно задавать порядок выполнения операторов:

```js
// value ?? fallback || other; // SyntaxError

(value ?? fallback) || other;
value ?? (fallback || other);
```

Эти выражения имеют разный смысл. В первом проверка на falsy-значение выполняется после `??`, во втором она относится только к правой части `??`.

#### Присваивание `??=`

```js
options.timeout ??= 5000;
```

Присваивание происходит, только если текущее значение равно `null` или `undefined`. Левая часть вычисляется один раз, что важно при использовании геттера, вычисляемого индекса или `Proxy`.

`||=` заменил бы также `0`, `false` и `""`, а `&&=` выполнил бы запись только для truthy-значения, то есть значения, приводимого к `true`.

#### Необязательные данные и обязательный контракт

```js
const userName = response?.user?.name ?? "Anonymous";
```

Код корректен, если по контракту `user` и `name` действительно необязательны, а значение `"Anonymous"` является допустимым поведением приложения.

Если backend обязан вернуть `user.name`, такая цепочка может скрыть нарушение контракта и показать «Anonymous» вместо ошибки. Данные из внешнего источника сначала проверяют, а optional chaining оставляют для действительно необязательных ветвей.

#### Где применяется во frontend

- Необязательный callback (функция обратного вызова) вызывается как `onClose?.()` без отдельного `if`.
- Настройка `0` сохраняется через `timeout ?? defaultTimeout`, в отличие от `||`.
- Необязательное поле ответа API читается после проверки обязательной части контракта.
- Наличие браузерного API проверяется через заведомо существующий объект: `navigator.clipboard?.writeText(...)`.
- Результат `Map.get` нельзя бездумно смешивать с отсутствием записи, если `undefined` является допустимым сохранённым значением.

#### Ключевые уточнения

- `?.` проверяет только `null` и `undefined`, а не все falsy-значения.
- Необязательный вызов не проверяет, что существующее значение является функцией.
- Прерывание действует только в непрерывной цепочке и может пропустить вычисление аргументов или индекса.
- Группировка способна закончить optional chain и вернуть обычный доступ с возможным `TypeError`.
- `??` сохраняет `0`, `false` и пустую строку; `||` заменяет их запасным значением.
- Операторы выражают допустимую необязательность, но не валидируют внешний контракт.

#### Связанные темы

- [[Конспект для подготовки/JavaScript/Приведение типов]]
- [[Конспект для подготовки/JavaScript/Проверка свойств объекта]]
- [[Конспект для подготовки/TypeScript/never any unknown]]
- [[Конспект для подготовки/TypeScript/Проверка данных с backend]]

#### Источники

- [ECMAScript: Optional Chains](https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-optional-chains)
- [ECMAScript: Coalesce Expression](https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-coalesce-expression)
- [MDN: Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [MDN: Nullish coalescing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)
