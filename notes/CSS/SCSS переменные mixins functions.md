# SCSS переменные mixins functions

<!-- NOTE-NAV-TOP:START -->
[← SCSS modules @use и @forward](<./SCSS modules @use и @forward.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [SCSS архитектура и вложенность →](<./SCSS архитектура и вложенность.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Variables, mixins и functions в SCSS решают разные build-time задачи. `$variable` хранит значение во время компиляции. Mixin через `@include` генерирует declarations или rules. Function возвращает одно Sass-значение для использования внутри выражения.

Выбор определяется результатом: для меняющегося в браузере значения нужна CSS custom property; для параметризованного блока CSS - mixin; для чистого вычисления значения - function. Sass выполняется при сборке, поэтому не может прочитать состояние DOM или изменить тему без заранее сгенерированного CSS.

## Ключевая схема

| Инструмент | Возвращает | Использовать для |
| --- | --- | --- |
| `$variable` | значение на этапе сборки | токены, настройки, промежуточные значения |
| `!default` | configurable default | настройки библиотеки или темы |
| `@mixin` | CSS-блок | media helpers, focus-ring, typography, reusable patterns |
| `@content` | место для переданного блока | hover/focus/media wrappers |
| `@function` | значение | расчёты, map lookup, unit conversion |
| `sass:map`, `sass:math`, `sass:color` | built-in modules | безопасные встроенные операции |

## Базовая модель

```text
Нужно повторить значение?
-> build time: $variable
-> runtime/cascade: --custom-property

Нужно вставить CSS rules/declarations?
-> @mixin + @include

Нужно вычислить и вернуть значение?
-> @function
```

Sass variable хранит текущее значение в точке использования. Позднее присваивание не переписывает уже вычисленные declarations. Mixin, напротив, вставляет новый CSS output в каждую точку `@include`; сокращение SCSS не обязательно означает сокращение итогового файла.

## Развернутый ответ

`!default` позволяет библиотеке задать значение, которое потребитель может сконфигурировать при первом `@use ... with (...)`. Это подходит для ограниченного compile-time API. Для нескольких тем, существующих на одной странице, обычно генерируют CSS custom properties в разных selectors и переключают их каскадом.

Mixin нужен, когда повторяется параметризованный CSS-паттерн: focus ring, visually hidden, media wrapper или набор declarations. `@content` принимает вложенный блок от вызывающего кода. Если паттерн статичен и должен переиспользоваться многими элементами в runtime, общий class или composition может дать меньший output.

Function нужна для вычисления значения: чтения token из map, проверки входа, преобразования единиц или расчёта scale. Хорошая function имеет понятные единицы входа/выхода и выдаёт ошибку для недопустимого token вместо молчаливого `null`, если такой результат сломает CSS.

Слишком умный mixin с множеством boolean-параметров и вложенными selectors превращается в непрозрачный генератор. Разработчику трудно предсказать специфичность, порядок и размер output. В этом случае лучше разделить API на несколько узких patterns или выразить варианты через class/data attributes и custom properties.

В современном Sass числовое деление выполняют через `math.div()` из `sass:math`: символ `/` должен сохранять обычный CSS-смысл в значениях вроде shorthand `font` или grid line syntax. Для maps, colors и списков также предпочитают встроенные modules с namespace.

## Пример

```scss
@use "sass:map";
@use "sass:math";

$spaces: (
  2: 0.5rem,
  4: 1rem,
  6: 1.5rem,
);

@function space($step) {
  @return map.get($spaces, $step);
}

@function rem($px, $base: 16px) {
  @return math.div($px, $base) * 1rem;
}

@mixin focus-ring($color: currentColor) {
  outline: 2px solid $color;
  outline-offset: 2px;
}

.button {
  padding: space(2) space(4);
  font-size: rem(14px);

  &:focus-visible {
    @include focus-ring;
  }
}
```

## Практичный паттерн с CSS variables

```scss
$theme-colors: (
  primary: #2563eb,
  danger: #dc2626,
);

:root {
  @each $name, $value in $theme-colors {
    --color-#{$name}: #{$value};
  }
}

.button {
  background: var(--color-primary);
}
```

Sass генерирует набор CSS custom properties, а компоненты используют runtime-переменные.

## Ключевые уточнения

- Sass variable фиксируется при сборке, CSS custom property вычисляется браузером и участвует в каскаде.
- Mixin создаёт CSS в каждой точке `@include`; общий class переиспользует один уже сгенерированный rule.
- Function возвращает значение и должна иметь предсказуемые типы и единицы.
- `!default` открывает compile-time конфигурацию module, но не создаёт runtime theme API.
- Built-in modules `sass:math`, `sass:map` и `sass:color` делают происхождение операций явным.
- Cycles и token maps проверяют по размеру и содержанию итогового CSS.

## Связанные темы

- [SCSS](<./SCSS.md>)
- [SCSS modules @use и @forward](<./SCSS modules @use и @forward.md>)
- [SCSS архитектура и вложенность](<./SCSS архитектура и вложенность.md>)
- [Единицы измерения](<./Единицы измерения.md>)
- [Каскад и наследование](<./Каскад и наследование.md>)

## Источники

- [Sass: Variables](https://sass-lang.com/documentation/variables/)
- [Sass: @mixin and @include](https://sass-lang.com/documentation/at-rules/mixin/)
- [Sass: @function](https://sass-lang.com/documentation/at-rules/function/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← SCSS modules @use и @forward](<./SCSS modules @use и @forward.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [SCSS архитектура и вложенность →](<./SCSS архитектура и вложенность.md>)
<!-- NOTE-NAV-BOTTOM:END -->
