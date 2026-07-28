---
aliases:
  - tsconfig
  - strict mode TypeScript
  - strictNullChecks
  - noUncheckedIndexedAccess
  - exactOptionalPropertyTypes
---

#### Быстрый ответ

`tsconfig.json` определяет границы TypeScript-проекта и правила его проверки: какие файлы входят в программу, какая среда выполнения предполагается, как разрешаются модули, насколько строгой является система типов и должен ли `tsc` генерировать файлы.

`strict: true` включает семейство взаимосвязанных строгих проверок, включая `strictNullChecks`, `noImplicitAny` и `strictFunctionTypes`. Для нового проекта это разумная базовая настройка. `noUncheckedIndexedAccess` и `exactOptionalPropertyTypes` усиливают модель отдельно и не включаются одним `strict`.

Во frontend JavaScript часто создаёт Vite, SWC или Babel, поэтому `tsc` запускают с `--noEmit` для отдельного typecheck. Сборка bundle и проверка типов решают разные задачи; обе должны выполняться в CI на зафиксированной версии TypeScript.

#### Что задаёт `tsconfig`

Конфигурация состоит из двух смысловых частей:

- **границы проекта:** `files`, `include`, `exclude`, project references;
- **поведение компилятора:** `compilerOptions`.

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,
    "skipLibCheck": true
  },
  "include": ["src", "vite.config.ts"]
}
```

Это пример для приложения, которое отдаёт emit сборщику. Конкретные `target`, `module`, `moduleResolution` и `lib` выбирают под runtime и bundler проекта, а не копируют без проверки.

#### `strict` как базовая гарантия

`strict: true` включает набор flags. В частности:

| Проверка | Что меняет |
| --- | --- |
| `noImplicitAny` | требует явно обработать места, где тип иначе стал бы `any` |
| `strictNullChecks` | отделяет `null` и `undefined` от остальных типов |
| `strictFunctionTypes` | строже проверяет параметры function types |
| `strictPropertyInitialization` | проверяет инициализацию полей класса |
| `noImplicitThis` | запрещает неявный `any` у `this` |
| `useUnknownInCatchVariables` | рассматривает ошибку `catch` как `unknown` до проверки |

Набор `strict` может расширяться в новых версиях TypeScript. Отдельный flag можно переопределить после `strict`, но каждое отключение уменьшает гарантии и должно иметь понятную причину.

#### Строгость, которую включают отдельно

**`noUncheckedIndexedAccess`.** Доступ по индексу получает `| undefined`, если наличие ключа не доказано:

```ts
const labels: Record<string, string> = {};
const label = labels["missing"];
// string | undefined
```

Это соответствует runtime: произвольного ключа может не быть.

**`exactOptionalPropertyTypes`.** `theme?: "dark" | "light"` означает, что поле может отсутствовать. Запись `theme: undefined` не считается автоматически тем же контрактом, если `undefined` явно не добавлен в тип. Различие важно для `"theme" in settings`, сериализации и PATCH-запросов.

**`noImplicitOverride`.** Наследник обязан пометить переопределение через `override`. Это помогает обнаружить ситуацию, когда базовый метод переименовали, а прежний метод наследника случайно стал независимым.

#### Typecheck и emit

Транспилятор может удалить TypeScript-синтаксис по одному файлу, не строя полную type model проекта. Поэтому успешно созданный bundle ещё может содержать ошибки типов.

Типичная проверка:

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit",
    "build": "vite build"
  }
}
```

В CI запускают обе команды. Версию `typescript` фиксирует lockfile, иначе обновление компилятора может изменить диагностику у разных разработчиков.

#### Границы проекта

`include` задаёт шаблоны входных файлов, `exclude` исключает часть найденных путей. При этом импортированный файл всё равно может попасть в программу: `exclude` не запрещает модулю существовать, а только влияет на начальный поиск.

`extends` позволяет вынести общие правила:

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "types": ["vitest/globals"]
  },
  "include": ["src"]
}
```

В monorepo общий config фиксирует единый уровень строгости, а package configs задают только среду: DOM для приложения, Node для tooling, test globals для тестов.

#### Важные настройки окружения

- `target` задаёт версию JavaScript для emit и влияет на доступный синтаксис.
- `lib` задаёт декларации стандартных API, например ECMAScript и DOM; он не устанавливает polyfills.
- `module` определяет форму модулей в output, если emit делает TypeScript.
- `moduleResolution` определяет, как TypeScript находит файл и package types; режим должен соответствовать bundler или Node runtime.
- `types` ограничивает автоматически подключаемые пакеты `@types`; импортируемые типы при этом продолжают разрешаться обычным способом.
- `skipLibCheck` пропускает проверку содержимого `.d.ts`, ускоряя typecheck, но может скрыть конфликт деклараций зависимостей. Код приложения он не делает менее строгим напрямую.

#### Миграция старого проекта

Строгость внедряют контролируемыми шагами:

1. Зафиксировать TypeScript и добавить стабильный `tsc --noEmit` в CI.
2. Остановить появление новых `any` и assertions без причины.
3. Разобрать границы API, storage и событий как `unknown`.
4. Включать flags по одному и устранять причины ошибок, а не скрывать их через `as any`.
5. В monorepo вынести общую базу и не позволять пакетам незаметно ослаблять её.

Временные исключения должны быть локальными. Массовое отключение `strictNullChecks` или `noImplicitAny` возвращает значительную часть runtime-рисков.

#### Ключевые уточнения

- Расширение `.ts` само по себе не даёт строгих гарантий: результат зависит от config и количества `any`.
- `strict` не включает абсолютно все дополнительные проверки; `noUncheckedIndexedAccess` и `exactOptionalPropertyTypes` выбирают отдельно.
- `noEmit` означает, что `tsc` только проверяет программу; JavaScript создаёт другой инструмент.
- `lib` описывает доступные API для typechecker, но не добавляет их в браузер.
- `exclude` не блокирует файл, импортированный из включённого модуля.
- Обновление TypeScript может изменить диагностику, поэтому версия и lockfile являются частью воспроизводимой сборки.

#### Связанные темы

- [[Конспект для подготовки/TypeScript/Плюсы и минусы TypeScript]]
- [[Конспект для подготовки/TypeScript/import type и isolatedModules]]
- [[Конспект для подготовки/TypeScript/Variance и совместимость функций]]
- [[Конспект для подготовки/TypeScript/never any unknown]]
- [[Конспект для подготовки/Tooling/npm yarn pnpm и package managers]]

#### Источники

- [TypeScript TSConfig Reference](https://www.typescriptlang.org/tsconfig/)
- [TypeScript TSConfig: strict](https://www.typescriptlang.org/tsconfig/strict.html)
- [TypeScript TSConfig: noUncheckedIndexedAccess](https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html)
- [TypeScript TSConfig: exactOptionalPropertyTypes](https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html)
- [TypeScript Handbook: What is a tsconfig.json](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html)
