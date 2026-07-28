---
aliases:
  - SCSS variables
  - Sass variables
  - Sass mixins
  - Sass functions
  - SCSS mixins functions
---

#### Ответ на 60 секунд

Переменные, mixins и functions в SCSS решают разные задачи. `$variables` хранят build-time значения: цвета, размеры, map-структуры токенов, настройки модулей. `@mixin` вставляет блок CSS в место вызова и подходит для повторяемых паттернов, которым нужны аргументы или вложенный `@content`. `@function` возвращает значение и подходит для расчётов: например, получить цвет из map, перевести px в rem или вычислить spacing.

Sass работает во время сборки. Если значение должно меняться в браузере от темы, состояния или пользователя, нужны CSS custom properties. Если нужно сгенерировать CSS на основе дизайн-токенов и не тащить логику в runtime, SCSS подходит хорошо.

#### Ключевая схема

| Инструмент | Возвращает | Использовать для |
| --- | --- | --- |
| `$variable` | значение на этапе сборки | токены, настройки, промежуточные значения |
| `!default` | configurable default | настройки библиотеки или темы |
| `@mixin` | CSS-блок | media helpers, focus-ring, typography, reusable patterns |
| `@content` | место для переданного блока | hover/focus/media wrappers |
| `@function` | значение | расчёты, map lookup, unit conversion |
| `sass:map`, `sass:math`, `sass:color` | built-in modules | безопасные встроенные операции |

#### Развернутый ответ

Sass variable выбирают для build-time вычислений и генерации CSS. CSS variable выбирают для runtime-темизации, переопределения в cascade и значений, которые могут отличаться между элементами. Если тема должна переключаться без пересборки, нужны custom properties.

Mixin нужен, когда повторяется не одно значение, а паттерн CSS: media query helper, focus state, visually hidden, typography preset, responsive container, scrollbar styling. Если повторяется только цвет или размер, часто достаточно variable/custom property.

Function нужна, когда нужно вернуть значение, а не вставить CSS-блок. Например, `rem(16px)` возвращает `1rem`, `color("primary")` возвращает значение из map, `space(4)` возвращает spacing token.

Слишком умные mixins скрывают output CSS. Если mixin принимает много boolean-флагов и генерирует разные selectors, разработчику трудно предсказать итоговую специфичность, размер CSS и поведение cascade. Такой mixin превращает стили в непрозрачный генератор.

В современном Sass для математического деления используют `math.div()` из `sass:math`, потому что `/` в CSS часто является частью обычного синтаксиса, например в `font` или `grid`.

> [!faq]+ Уточнения
> - Sass variables работают build-time, CSS variables - runtime.
> - Mixin вставляет CSS-блок в место вызова.
> - Function возвращает значение.
> - `@include` может увеличивать output CSS.
> - Для деления используют `sass:math` и `math.div()`.

#### Пример

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

#### Практичный паттерн с CSS variables

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

#### Частые ошибки

- Использовать Sass variables для темы, которая должна переключаться без пересборки.
- Делать mixin вместо обычного utility-класса или custom property.
- Создавать function с побочным эффектом вместо простого расчёта значения.
- Генерировать огромные наборы классов через циклы без контроля output CSS.
- Использовать глобальные переменные без namespace.
- Забывать, что `@include` буквально добавляет CSS в место вызова.

#### Связанные темы

- [[Конспект для подготовки/CSS/SCSS]]
- [[Конспект для подготовки/CSS/SCSS modules @use и @forward]]
- [[Конспект для подготовки/CSS/SCSS архитектура и вложенность]]
- [[Конспект для подготовки/CSS/Единицы измерения]]
- [[Конспект для подготовки/CSS/Каскад и наследование]]

#### Источники

- [Sass: Variables](https://sass-lang.com/documentation/variables/)
- [Sass: @mixin and @include](https://sass-lang.com/documentation/at-rules/mixin/)
- [Sass: @function](https://sass-lang.com/documentation/at-rules/function/)
