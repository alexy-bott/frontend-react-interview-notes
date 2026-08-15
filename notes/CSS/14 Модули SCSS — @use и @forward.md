# Модули SCSS — @use и @forward

<!-- NOTE-NAV-TOP:START -->
[← SCSS](<./13 SCSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Переменные, миксины и функции SCSS →](<./15 Переменные, миксины и функции SCSS.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Модульная система Sass ограничивает область видимости variables, mixins и functions. `@use` загружает module один раз и по умолчанию открывает его public members через namespace. Это показывает происхождение имени и предотвращает случайные глобальные конфликты старого `@import`.

`@forward` переэкспортирует public members через общий entrypoint, например API дизайн-системы. Критерий простой: `@use` нужен текущему файлу для использования member, `@forward` - потребителям текущего файла. Это Sass modules; они не имеют отношения к локализации class names в CSS Modules.

## Ключевая схема

| Правило | Роль |
| --- | --- |
| `@use "tokens"` | загрузить module и обращаться через namespace |
| `@use "tokens" as t` | задать короткий namespace |
| `@use "tokens" as *` | загрузить без namespace, применять осторожно |
| `@forward "tokens"` | переэкспортировать public members |
| `@forward "tokens" hide $private` | скрыть часть API |
| `@forward "tokens" as theme-*` | добавить prefix к members |

## Базовая модель

```text
_tokens.scss --@forward--> _index.scss --@use as ui--> Button.module.scss
                                              -> ui.$space-4
                                              -> ui.focus-ring()
```

Имя файла с ведущим `_` обозначает partial и не меняет модульную семантику. При разрешении пути Sass обычно позволяет не писать `_` и расширение. Module определяется canonical URL и загружается один раз в рамках компиляции, поэтому его CSS также не дублируется при повторных `@use` одного module.

## Развернутый ответ

Старый Sass `@import` вставляет файл в глобальный контекст, затрудняет поиск источника имени и может повторять CSS. Module system даёт локальную область, одноразовую загрузку и явный public API.

`@use` располагают до style rules; перед ним могут идти `@forward` и declarations переменных для конфигурации. Namespace делает происхождение явным: `tokens.$space-4` показывает module. `as *` убирает namespace и уместен только в небольшой контролируемой области без риска конфликтов.

`@forward` может скрывать members через `hide`, разрешать только выбранные через `show` и добавлять prefix через `as prefix-*`. Переэкспорт не делает members доступными внутри текущего файла: если entrypoint сам их использует, ему также нужен `@use`.

Module можно конфигурировать при первом `@use ... with (...)`, но только variables, объявленные в нём с `!default`. После загрузки тот же module нельзя заново сконфигурировать в этой компиляции. Для библиотеки это формирует явный набор поддерживаемых настроек вместо изменения её внутренних variables.

Private members начинаются с `_` или `-` и недоступны потребителю. Публичный entrypoint должен экспортировать только стабильные tokens и helpers, иначе внутренние детали становятся контрактом, который трудно изменить.

## Пример

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

Компонент подключает один entrypoint и явно показывает источник names через `s.`. `@forward` собрал API, а `@use` сделал его доступным в `Button.module.scss`.

## Ключевые уточнения

- `@use` импортирует API для текущего файла, `@forward` переэкспортирует его потребителям.
- Sass modules управляют members Sass, а CSS Modules - локальными class names.
- Один module загружается один раз; конфигурацию через `with` задают при первой загрузке и только для `!default` variables.
- `@forward` не добавляет members в локальную область текущего файла.
- Namespace сохраняют по умолчанию; `as *` повышает риск конфликтов и скрывает происхождение имени.
- Entry point должен быть ограниченным публичным контрактом, а не выгрузкой всех внутренних helpers.

## Связанные темы

- [SCSS](<./13 SCSS.md>)
- [Переменные, миксины и функции SCSS](<./15 Переменные, миксины и функции SCSS.md>)
- [Архитектура SCSS и вложенность](<./16 Архитектура SCSS и вложенность.md>)
- [CSS-препроцессоры](<./12 CSS-препроцессоры.md>)
- [Бандлеры и разделение кода](<../Основы веб-платформы/19 Бандлеры и разделение кода.md>)

## Источники

- [Sass: @use](https://sass-lang.com/documentation/at-rules/use/)
- [Sass: @forward](https://sass-lang.com/documentation/at-rules/forward/)
- [Sass: @import](https://sass-lang.com/documentation/at-rules/import/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← SCSS](<./13 SCSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Переменные, миксины и функции SCSS →](<./15 Переменные, миксины и функции SCSS.md>)
<!-- NOTE-NAV-BOTTOM:END -->
