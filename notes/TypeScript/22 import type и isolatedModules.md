# import type и isolatedModules

<!-- NOTE-NAV-TOP:START -->
[← enum](<./21 enum.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Файлы деклараций →](<./23 Файлы деклараций.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

TypeScript различает пространство типов (type space) и пространство значений (value space). Type alias и interface нужны только компилятору и исчезают из JavaScript; функции, классы, объекты и обычные enums должны существовать при выполнении. `import type` и `export type` явно помечают зависимость, которая нужна только для типов и будет удалена из итогового JavaScript.

`isolatedModules` предупреждает о конструкциях, которые нельзя надёжно преобразовать, анализируя один файл без полной модели типов. Это важно, когда TypeScript-синтаксис удаляет Babel, SWC или esbuild. Настройка не запускает typecheck и сама не меняет сгенерированный код.

`verbatimModuleSyntax` упрощает правила: imports и exports без `type` сохраняются, а помеченные `type` удаляются. Поэтому зависимости времени выполнения и type-only зависимости видны прямо в коде.

## Тип и значение — разные пространства

```ts
export interface User {
  id: string;
}

export class UserModel {
  constructor(public readonly id: string) {}
}
```

`User` существует только как тип. `UserModel` существует и как тип экземпляра, и как значение-конструктор во время выполнения.

```ts
import type { User, UserModel } from "./models";

let user: User;
let model: UserModel;
```

Так можно использовать тип класса. Но создать экземпляр нельзя, потому что значение-конструктор не импортировано:

```ts
new UserModel("1");
// ошибка: UserModel импортирован через import type
```

Для создания объекта нужен обычный import.

## Type-only и runtime-зависимости

```ts
import { createUser, type User } from "./user";
import type { ApiResponse } from "./api-types";
import "./analytics-setup";
```

- `createUser` останется в JavaScript, потому что вызывается во время выполнения;
- `User` и `ApiResponse` исчезнут после компиляции;
- import ради побочного эффекта должен остаться, чтобы модуль выполнил инициализацию.

Обычный `enum` также является значением во время выполнения. Если код обращается к `Role.Admin`, его нельзя импортировать только как тип. Это отличается от union литералов, который полностью стирается.

## Что делает `isolatedModules`

Babel, SWC и esbuild обычно преобразуют файл независимо от остального проекта. Они не знают, является ли импортированное имя типом, как устроен ambient `const enum` или какая декларация скрывается в другом файле.

`isolatedModules: true` просит TypeScript сообщить о коде, который может быть неверно обработан при такой пофайловой транспиляции. Примеры ограничений включают некоторые экспорты type-only имён, ambient `const enum` и namespaces в глобальных script-файлах.

Настройка не выполняет межфайловую проверку типов. Проекту всё равно нужен `tsc --noEmit`; `isolatedModules` лишь проверяет совместимость синтаксиса с пофайловой транспиляцией.

## Что делает `verbatimModuleSyntax`

При включённом `verbatimModuleSyntax` действует простая модель:

```ts
import type { User } from "./types";
// удаляется полностью

import { createUser, type Options } from "./user";
// остаётся import { createUser } from "./user"

import { register } from "./plugin";
// сохраняется как написано
```

TypeScript не пытается угадывать и удалять обычный import только потому, что его имя используется в позиции типа. Если зависимость type-only, разработчик помечает её явно.

Эта предсказуемость также помогает заметить несоответствие системы модулей. TypeScript не перепишет ES import в `require` при несовместимых настройках только ради успешной генерации; `module` и формат пакета нужно согласовать явно.

## Namespaces и ES modules

TypeScript `namespace` группирует имена внутри общего объекта и исторически применялся в global script-файлах. ES modules используют границы файлов, стандартные `import` и `export` и поддерживаются браузерами, Node.js и сборщиками.

В современном приложении основной выбор — ES modules. Namespaces всё ещё встречаются в старом коде и declaration files, но не заменяют модульную систему. Ограничения `isolatedModules` для namespace в global script-файле связаны именно с тем, что пофайловый транспилятор не видит полную общую область.

## Побочные эффекты и удаление imports

Удаление import влияет не только на размер bundle. Модуль мог зарегистрировать web component, polyfill, plugin или глобальный обработчик при загрузке. Если выполнение модуля является частью поведения, это выражают import без импортируемых имён:

```ts
import "./register-custom-elements";
```

Type-only import нельзя использовать ради побочного эффекта: он гарантированно исчезает.

## Практическое правило

| Импортируемая сущность | Как импортировать |
| --- | --- |
| type alias, interface | `import type` или inline `type` modifier |
| тип класса без создания экземпляра | можно `import type` |
| функция, объект, constructor класса | обычный import |
| обычный enum как `Role.Admin` | обычный import |
| модуль ради выполнения | `import "./module"` |

## Ключевые уточнения

- Type-only import удаляется из JavaScript независимо от того, есть ли в модуле выполняемый код.
- Класс имеет типовую сторону и значение-конструктор; способ использования определяет вид import.
- `isolatedModules` не заменяет typecheck, а предупреждает о проблемах пофайловой транспиляции.
- `verbatimModuleSyntax` делает генерацию модулей предсказуемой, но требует явно различать типы и значения.
- Зависимость с побочным эффектом нельзя случайно превращать в type-only import.
- `const enum`, Babel/SWC/esbuild и опубликованные `.d.ts` требуют отдельного внимания из-за отсутствия общего объекта во время выполнения.

## Связанные темы

- [tsconfig и строгий режим](<./20 tsconfig и строгий режим.md>)
- [Файлы деклараций](<./23 Файлы деклараций.md>)
- [enum](<./21 enum.md>)
- [Классы — модификаторы доступа, abstract и private](<./11 Классы — модификаторы доступа, abstract и private.md>)
- [ES-модули](<../JavaScript/32 ES-модули.md>)

## Источники

- [TypeScript TSConfig: isolatedModules](https://www.typescriptlang.org/tsconfig/isolatedModules.html)
- [TypeScript TSConfig: verbatimModuleSyntax](https://www.typescriptlang.org/tsconfig/verbatimModuleSyntax.html)
- [TypeScript 3.8: Type-Only Imports and Exports](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-8.html)
- [TypeScript Handbook: Modules - Theory](https://www.typescriptlang.org/docs/handbook/modules/theory.html)
- [TypeScript Handbook: Namespaces and Modules](https://www.typescriptlang.org/docs/handbook/namespaces-and-modules.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← enum](<./21 enum.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Файлы деклараций →](<./23 Файлы деклараций.md>)
<!-- NOTE-NAV-BOTTOM:END -->
