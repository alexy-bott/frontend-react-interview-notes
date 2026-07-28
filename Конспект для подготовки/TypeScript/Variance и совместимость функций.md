---
aliases:
  - variance TypeScript
  - covariance
  - contravariance
  - bivariance
  - strictFunctionTypes
  - вариантность TypeScript
---

#### Быстрый ответ

Variance, или вариантность, объясняет совместимость generic-типов и функций при замене вложенного типа на более общий или более конкретный. На практике вопрос обычно возникает у callbacks, обработчиков событий, коллекций и контейнеров.

Результат функции обычно ковариантен: функцию, возвращающую более конкретный тип, можно использовать там, где ожидается общий. Параметр function type при `strictFunctionTypes` проверяется контравариантно: безопасен обработчик, который умеет принять не меньше вариантов, чем может передать вызывающий код.

TypeScript не является полностью sound и сохраняет отдельные послабления для совместимости с JavaScript. В частности, параметры методов имеют bivariant-поведение в ряде проверок, тогда как свойства-функции проверяются строже.

#### Базовая модель

Пусть `ClickEventData` содержит все поля `EventData` и дополнительную координату:

```ts
type EventData = {
  timestamp: number;
};

type ClickEventData = EventData & {
  x: number;
  y: number;
};
```

`ClickEventData` является более конкретным типом: его можно использовать как `EventData`, но не каждый `EventData` является кликом.

#### Ковариантность результата

```ts
const createClick = (): ClickEventData => ({
  timestamp: Date.now(),
  x: 10,
  y: 20,
});

const createEvent: () => EventData = createClick;
```

Код ожидает получить `EventData`. Фактическая функция возвращает `ClickEventData`, в котором гарантированно есть все нужные поля. Поэтому более конкретный результат безопасен.

Обратная замена небезопасна: функция, возвращающая только `EventData`, не обещает координаты, которые требуются `ClickEventData`.

#### Контравариантность параметра callback

```ts
type Handler<T> = (event: T) => void;

const handleAnyEvent: Handler<EventData> = event => {
  console.log(event.timestamp);
};

const handleClick: Handler<ClickEventData> = event => {
  console.log(event.x, event.y);
};

const clickHandler: Handler<ClickEventData> = handleAnyEvent;
// допустимо: handleAnyEvent умеет обработать и ClickEventData

const eventHandler: Handler<EventData> = handleClick;
// ошибка при strictFunctionTypes
```

Последнее присваивание небезопасно. Код, владеющий `eventHandler`, имеет право вызвать его с любым `EventData`, в том числе без `x` и `y`. `handleClick` к такому вызову не готов.

Полезный способ рассуждать: не «какой тип уже», а «что имеет право передать вызывающая сторона». Callback должен принимать весь обещанный набор значений.

#### Основные виды вариантности

| Вложенный тип используется | Ожидаемое направление | Пример |
| --- | --- | --- |
| только как результат | ковариантность | фабрика, readonly-источник |
| только как вход | контравариантность | обработчик, получатель данных |
| и как вход, и как результат | обычно инвариантность | изменяемая ячейка |

```ts
type Cell<T> = {
  get: () => T;
  set: (value: T) => void;
};
```

`Cell<T>` и отдаёт, и принимает `T`. Свободная замена `Cell<EventData>` на `Cell<ClickEventData>` в любом направлении может нарушить либо чтение, либо запись, поэтому концептуально контейнер должен быть invariant.

Readonly-контейнеры проще: если значение можно только читать, более конкретный элемент обычно безопасно использовать как общий.

#### `strictFunctionTypes` и методы

При включённом `strictFunctionTypes` параметры function types и свойств-функций проверяются строже:

```ts
type Listener<T> = {
  onEvent: (event: T) => void;
};
```

Синтаксис метода исторически имеет послабление:

```ts
type ListenerMethod<T> = {
  onEvent(event: T): void;
};
```

Для методов TypeScript допускает bivariant-проверку параметров в большем числе случаев, чтобы не ломать распространённые иерархии и DOM-типы. Bivariance означает совместимость в обоих направлениях; она удобнее, но может пропустить небезопасную замену.

Поэтому для callback props и API, где важна строгая совместимость, свойство-функция часто предсказуемее синтаксиса метода.

#### Где это встречается во frontend

- callback props: компонент обещает, какие данные передаст обработчику;
- event bus и подписки: subscriber должен принять каждое событие заявленного типа;
- middleware: входной action не должен быть уже, чем набор возможных actions;
- generic-компоненты: callbacks для элементов таблицы или списка связываются с типом item;
- `map`, `filter`, `reduce`: тип элемента передаётся в callback, а результат формирует новый generic-тип;
- readonly и mutable collections: возможность записи меняет направление безопасной совместимости.

#### Ключевые уточнения

- Для результата безопаснее более конкретный тип; для параметра callback — достаточно общий обработчик.
- Проверять нужно контракт вызывающей стороны: какие значения она имеет право передать.
- `strictFunctionTypes` входит в `strict`, но методы имеют историческое bivariant-послабление.
- Mutable-контейнер сложнее readonly-контейнера, потому что тип одновременно читается и записывается.
- Ошибка компилятора обычно не содержит слова variance; тема проявляется как несовместимость callbacks или generic-типов.
- TypeScript поддерживает `in`/`out` variance annotations для отдельных generic declarations, но в прикладном коде вариантность обычно выводится из использования `T`; аннотации нужны редко.

#### Связанные темы

- [[Конспект для подготовки/TypeScript/Generics]]
- [[Конспект для подготовки/TypeScript/Типизация функций]]
- [[Конспект для подготовки/TypeScript/Structural typing]]
- [[Конспект для подготовки/TypeScript/tsconfig и strict mode]]
- [[Конспект для подготовки/TypeScript/Array map типизация]]

#### Источники

- [TypeScript Handbook: Type Compatibility](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)
- [TypeScript TSConfig: strictFunctionTypes](https://www.typescriptlang.org/tsconfig/strictFunctionTypes.html)
- [TypeScript 4.7: Optional Variance Annotations](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-7.html#optional-variance-annotations-for-type-parameters)
