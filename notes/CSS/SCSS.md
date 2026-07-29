# SCSS

<!-- NOTE-NAV-TOP:START -->
[← CSS препроцессоры](<./CSS препроцессоры.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [SCSS modules @use и @forward →](<./SCSS modules @use и @forward.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

SCSS - CSS-совместимый синтаксис препроцессора Sass. Он добавляет build-time variables, вложенность, mixins, functions, modules и управляющие конструкции, а compiler преобразует их в обычный CSS. Браузер не выполняет SCSS и видит только результат компиляции.

SCSS полезен для общих build-time tokens, параметризованных CSS-паттернов, библиотеки style helpers и существующего Sass-кода. Он не локализует class names и не решает каскад автоматически. Абстракция оправдана, если делает итоговый CSS и поддержку проще, а не только сокращает исходный файл.

## Ключевая схема

| Возможность | Где полезна | Риск |
| --- | --- | --- |
| `$variables` | build-time токены, расчёты | не работают в runtime |
| CSS custom properties | темы, runtime-переопределение | зависят от cascade |
| `@mixin` | повторяемые блоки стилей | дублирование CSS в output |
| `@function` | вычисление значений | сложная логика в стилях |
| `@use` | модульная загрузка Sass | нужен Dart Sass |
| `@forward` | публичный API style-library | можно размыть границы |
| nesting | локальная читаемость | рост специфичности |

## Базовая модель

У SCSS две границы ответственности:

```text
Sass compile time: variables, modules, mixins, functions, loops
browser runtime: cascade, custom properties, media/container queries, layout, paint
```

Если значение известно при сборке и одинаково для всех элементов, его можно вычислить Sass. Если оно должно зависеть от темы, DOM-контекста, media query или состояния пользователя без пересборки, оно должно остаться в CSS, обычно как custom property или обычное CSS-правило.

## Развернутый ответ

SCSS - синтаксис Sass, совместимый с привычной CSS-записью. Он добавляет build-time возможности: variables, nesting, mixins, functions, modules, partials и flow control. Но результатом всё равно остаётся обычный CSS, поэтому cascade, specificity, inheritance, layers и порядок правил продолжают определять поведение в браузере.

SCSS и CSS Modules решают разные задачи. Sass компилирует дополнительный синтаксис, CSS Modules преобразует локальные class names и экспортирует mapping для JavaScript. Их можно объединить в `Button.module.scss`; точный порядок loaders/plugins задаёт bundler integration.

Sass variables исчезают после компиляции. CSS custom properties остаются в итоговом CSS, участвуют в cascade и могут меняться по теме, состоянию или DOM-контексту. Для runtime-темизации нужны CSS variables; Sass удобно использовать для генерации базовых токенов, fallback-значений и повторяемых build-time паттернов.

Sass `@import` устарел. В новом коде `@use` загружает module через namespace, а `@forward` собирает его публичный API. Это сокращает глобальные конфликты и показывает источник `$variable`, mixin или function.

Цена SCSS - compiler dependency, конфигурация bundler, дополнительный синтаксис и риск непрозрачной генерации. В небольшом компонентном проекте нативный CSS с CSS Modules и custom properties может быть проще. В зрелой Sass-системе отказ от него без практической причины, наоборот, создаст дорогую миграцию.

## Пример

```scss
// styles/_tokens.scss
$radius-sm: 4px;
$radius-md: 8px;

:root {
  --radius-sm: #{$radius-sm};
  --radius-md: #{$radius-md};
}
```

```scss
// Button.module.scss
@use "../styles/tokens";

.button {
  border-radius: var(--radius-md);
  padding: 0.5rem 1rem;
}
```

Sass один раз подставляет значения в объявления `:root`. Затем custom properties остаются в output и могут переопределяться каскадом. Чтобы компонент действительно менялся в runtime, он использует `var(--radius-md)`, а не `$radius-md` напрямую.

## Ключевые уточнения

- SCSS выполняется на этапе сборки; в runtime его конструкций уже нет.
- CSS Modules локализуют имена классов, а SCSS сам этого не делает.
- Sass variable и CSS custom property выбираются по времени изменения значения.
- Каждый `@include` может дублировать declarations в output; общему статичному паттерну иногда лучше подходит class.
- Вложенность компилируется в обычные селекторы и влияет на их связность и специфичность.
- Качество Sass-кода оценивают по читаемости, размеру и поведению итогового CSS.

## Связанные темы

- [SCSS modules @use и @forward](<./SCSS modules @use и @forward.md>)
- [SCSS переменные mixins functions](<./SCSS переменные mixins functions.md>)
- [SCSS архитектура и вложенность](<./SCSS архитектура и вложенность.md>)
- [CSS препроцессоры](<./CSS препроцессоры.md>)
- [Каскад и наследование](<./Каскад и наследование.md>)
- [Специфичность селекторов](<./Специфичность селекторов.md>)

## Источники

- [Sass: @use](https://sass-lang.com/documentation/at-rules/use/)
- [Sass: Variables](https://sass-lang.com/documentation/variables/)
- [Sass: @import](https://sass-lang.com/documentation/at-rules/import/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← CSS препроцессоры](<./CSS препроцессоры.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [SCSS modules @use и @forward →](<./SCSS modules @use и @forward.md>)
<!-- NOTE-NAV-BOTTOM:END -->
