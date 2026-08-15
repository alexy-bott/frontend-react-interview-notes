# type и interface

<!-- NOTE-NAV-TOP:START -->
[← Type Guards](<./07 Type Guards.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Структурная типизация →](<./09 Структурная типизация.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`interface` и `type` могут описывать форму объекта, и в большинстве простых случаев результат одинаков. `interface` предназначен для именованных объектных контрактов: он расширяется через `extends`, участвует в `implements` и поддерживает declaration merging — объединение нескольких объявлений с одним именем.

`type` создаёт alias для любого типа, а не только объекта. Через него описывают unions, tuples, примитивные литералы, типы функций, intersections, mapped и conditional types.

Практический выбор зависит от модели. Для union или вычисляемого типа нужен `type`. Для расширяемого объектного API удобен `interface`. Для обычных props оба варианта корректны; важнее единый стиль проекта и точность контракта.

## Общее и различия

| Возможность | `interface` | `type` |
| --- | --- | --- |
| Описать объект | да | да |
| Описать функцию или callable object | да | да |
| Расширить объектный контракт | `extends` | intersection `&` |
| Реализовать классом | да | да, если результат является объектным типом |
| Declaration merging | да | нет |
| Union | нет | да |
| Tuple или alias примитива | нет | да |
| Mapped и conditional type | не напрямую | да |

## Описание объекта

```ts
interface User {
  id: string;
  name: string;
}

type UserAlias = {
  id: string;
  name: string;
};
```

Эти типы структурно совместимы. Имя и способ объявления не создают отдельную runtime-сущность и сами по себе не делают тип nominal.

## `extends` и intersection

```ts
interface Entity {
  id: string;
}

interface User extends Entity {
  name: string;
}

type Timestamped = {
  createdAt: string;
};

type TimestampedUser = User & Timestamped;
```

Оба способа объединяют требования, но конфликтуют по-разному. `interface extends` сразу запрещает несовместимо переопределить поле базового интерфейса. Intersection пытается удовлетворить оба типа; несовместимое поле может превратиться в `never`:

```ts
type A = { id: string };
type B = { id: number };
type Impossible = A & B;
// id: never
```

Для обычной иерархии объектных контрактов `extends` часто даёт понятнее ошибку. Для композиции вычисляемых типов и utility types нужен `type` с intersection.

## Declaration merging

Несколько interfaces с одним именем объединяются:

```ts
interface Window {
  analytics: { track(name: string): void };
}

interface Window {
  appVersion: string;
}
```

Это полезно для module augmentation и расширения глобальных типов. В прикладном коде та же возможность может неожиданно изменить контракт, поэтому объявление открытого interface должно быть осознанным. Повторно объявить `type` с тем же именем нельзя.

## Где `type` необходим

```ts
type Status = "idle" | "loading" | "success" | "error";

type Point = readonly [x: number, y: number];

type Handler = (event: Event) => void;

type ApiResult<T> =
  | { status: "success"; data: T }
  | { status: "error"; error: Error };
```

Здесь тип является выражением или выбором между вариантами, а не только формой объекта, поэтому interface его не заменяет.

## Критерий выбора

- Выбирай `type`, если нужен union, tuple, тип функции, примитивный alias или преобразование на уровне типов.
- Выбирай `interface`, если контракт намеренно открыт для declaration merging или естественно расширяется как объектная модель.
- Для простой закрытой формы объекта и React props допустимы оба варианта.
- Не заменяй точность модели правилом «везде только interface» или «везде только type».

## Ключевые уточнения

- `type` является alias, а не новым nominal-типом.
- `interface` тоже удаляется при компиляции и не создаёт объект в runtime.
- Класс может `implements` object type, но не union, потому что экземпляр должен иметь статически известный набор членов.
- Declaration merging полезен для библиотек и глобальных расширений, но не обязан быть преимуществом в закрытом коде приложения.
- Для React-компонента форма props важнее способа объявления: взаимоисключающие режимы лучше выражать union через `type`.

## Связанные темы

- [Структурная типизация](<./09 Структурная типизация.md>)
- [Объединения, пересечения и дискриминируемые объединения](<./06 Объединения, пересечения и дискриминируемые объединения.md>)
- [Классы — модификаторы доступа, abstract и private](<./11 Классы — модификаторы доступа, abstract и private.md>)
- [Файлы деклараций](<./23 Файлы деклараций.md>)
- [Utility Types](<./17 Utility Types.md>)

## Источники

- [TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- [TypeScript Handbook: Creating Types from Types](https://www.typescriptlang.org/docs/handbook/2/types-from-types.html)
- [TypeScript Handbook: Declaration Merging](https://www.typescriptlang.org/docs/handbook/declaration-merging.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Type Guards](<./07 Type Guards.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Структурная типизация →](<./09 Структурная типизация.md>)
<!-- NOTE-NAV-BOTTOM:END -->
