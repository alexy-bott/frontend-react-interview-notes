---
aliases:
  - Sass modules
  - SCSS modules
  - "@use"
  - "@forward"
  - Sass module system
---

#### Ответ на 60 секунд

Модульная система Sass нужна, чтобы стили не жили в одной глобальной области. В старом `@import` переменные, mixins и functions становились глобальными, один и тот же файл мог выполняться несколько раз, а происхождение значения было трудно понять. `@use` решает это через modules и namespace: файл подключается один раз, а его members доступны через имя модуля.

`@forward` нужен для сборки публичного API. Например, внутри дизайн-системы можно держать токены, mixins и functions в разных файлах, а наружу отдавать один entrypoint. В новом SCSS-коде основной выбор такой: `@use` - чтобы пользоваться модулем в текущем файле, `@forward` - чтобы переэкспортировать модуль из общего входа.

#### Ключевая схема

| Правило | Роль |
| --- | --- |
| `@use "tokens"` | загрузить module и обращаться через namespace |
| `@use "tokens" as t` | задать короткий namespace |
| `@use "tokens" as *` | загрузить без namespace, применять осторожно |
| `@forward "tokens"` | переэкспортировать public members |
| `@forward "tokens" hide $private` | скрыть часть API |
| `@forward "tokens" as theme-*` | добавить prefix к members |

#### Развернутый ответ

Старый Sass `@import` делает members глобальными, усложняет поиск источника переменной, создаёт риск конфликтов имён, может повторно добавлять CSS в output и делает `@extend` менее предсказуемым. Module system решает это через одноразовую загрузку и namespace.

`@use` подключает module в начале файла, до style rules. Перед ним допускают только `@forward` и переменные, которыми module конфигурируют через `with`. Namespace делает происхождение значения явным: `tokens.$space-4` показывает источник, а глобальный `$space-4` теряет контекст.

`@forward` используют для entrypoint-ов. Например, `styles/index.scss` может forward-ить `tokens`, `mixins`, `functions`, чтобы компоненты подключали один публичный интерфейс. Важно: `@forward` переэкспортирует members наружу, но не делает их автоматически доступными внутри текущего файла; для внутреннего использования нужен `@use`.

Private members начинаются с `_` или `-`. Их нельзя использовать снаружи module через `@use`, поэтому так отделяют внутренние детали от public API style-library.

> [!faq]+ Уточнения
> - `@import` создаёт глобальность и риск повторного CSS output.
> - `@use` подключает module с namespace.
> - `@forward` собирает public API entrypoint.
> - `@use ... as *` убирает namespace и требует осторожности.
> - Private members начинаются с `_` или `-`.

#### Пример

```scss
// styles/_tokens.scss
$space-2: 0.5rem;
$space-4: 1rem;
$radius-md: 8px;
```

```scss
// styles/_mixins.scss
@mixin focus-ring {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
```

```scss
// styles/index.scss
@forward "tokens";
@forward "mixins";
```

```scss
// Button.module.scss
@use "../styles" as s;

.button {
  padding: s.$space-2 s.$space-4;
  border-radius: s.$radius-md;

  &:focus-visible {
    @include s.focus-ring;
  }
}
```

Так компонент подключает один entrypoint и явно показывает, какие значения пришли из style-library.

#### Частые ошибки

- Продолжать писать новый код на Sass `@import`.
- Использовать `@use ... as *` для чужих библиотек и получать конфликты имён.
- Делать один огромный `index.scss`, который forward-ит всё без границ.
- Переэкспортировать private/internal mixins как часть публичного API.
- Думать, что `@forward` автоматически делает members доступными внутри текущего файла: для внутреннего использования всё равно нужен `@use`.
- Подключать module после style rules.

#### Связанные темы

- [[Конспект для подготовки/CSS/SCSS]]
- [[Конспект для подготовки/CSS/SCSS переменные mixins functions]]
- [[Конспект для подготовки/CSS/SCSS архитектура и вложенность]]
- [[Конспект для подготовки/CSS/CSS препроцессоры]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]

#### Источники

- [Sass: @use](https://sass-lang.com/documentation/at-rules/use/)
- [Sass: @forward](https://sass-lang.com/documentation/at-rules/forward/)
- [Sass: @import](https://sass-lang.com/documentation/at-rules/import/)
