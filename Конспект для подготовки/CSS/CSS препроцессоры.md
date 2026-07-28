---
aliases:
  - CSS препроцессоры
  - Sass
  - SCSS
  - Less
---

#### Ответ на 60 секунд

CSS-препроцессор - это инструмент, который расширяет CSS дополнительным синтаксисом и компилирует его в обычный CSS. Самые известные примеры: Sass/SCSS, Less и Stylus. Они дают переменные, вложенность, mixins, functions, modules и помогают организовать большие стили.

Сегодня часть возможностей препроцессоров уже появилась в нативном CSS: custom properties, nesting, `color-mix`, cascade layers. Поэтому препроцессор всё ещё полезен в legacy-проектах и дизайн-системах, но его применяют под конкретную задачу. Главный риск - слишком глубокая вложенность, сложные mixins и CSS, который трудно отлаживать после компиляции.

#### Ключевая схема

| Возможность | Зачем нужна |
| --- | --- |
| Переменные | единые цвета, отступы, размеры |
| Вложенность | локальная структура селекторов |
| Mixins | переиспользование блоков CSS |
| Functions | вычисления и генерация значений |
| Modules | `@use` и `@forward` вместо глобального `@import` |
| Partials | разбиение стилей на файлы |

#### Развернутый ответ

Sass - технология и препроцессор, а SCSS - один из синтаксисов Sass. SCSS похож на обычный CSS: фигурные скобки, точки с запятой, CSS-compatible запись. Поэтому в React/Next/Vite/Webpack-проектах под Sass часто имеют в виду именно `.scss`.

Sass-переменные и CSS custom properties решают разные задачи. Sass-переменные вычисляются на этапе сборки и исчезают из итогового CSS. CSS custom properties остаются в браузере, участвуют в cascade, могут меняться по теме, состоянию, media/container context и DOM-структуре.

Препроцессор в новом проекте нужен не всегда. Если хватает CSS Modules, PostCSS, custom properties, cascade layers и нативного nesting, можно писать обычный CSS. SCSS оправдан, когда есть дизайн-токены, общие mixins/functions, legacy styles или уже поддерживаемая SCSS-инфраструктура.

В современном Sass используют `@use` и `@forward` вместо старого `@import`. `@use` подключает файл как module с namespace, поэтому происхождение переменной, mixin или function видно явно. `@forward` собирает публичный entrypoint для design tokens и style helpers.

> [!faq]+ Уточнения
> - Sass - препроцессор, SCSS - CSS-like синтаксис Sass.
> - Sass variables работают build-time, CSS variables живут runtime.
> - SCSS не отменяет cascade, specificity и inheritance.
> - `@use` подключает module, `@forward` переэкспортирует public API.
> - Препроцессор полезен под задачу, а не как автоматическое требование.

#### Пример

```scss
$gap: 16px;

@mixin card {
  border: 1px solid #ddd;
  padding: $gap;
}

.product-card {
  @include card;

  &__title {
    margin: 0 0 $gap;
  }
}
```

#### Частые ошибки

- Делать вложенность на 5-6 уровней и получать слишком специфичные селекторы.
- Использовать миксины для задач, которые решаются обычным классом или custom property.
- Путать build-time переменные Sass и runtime CSS variables.
- Использовать Sass `@import` как основной способ организации нового кода.
- Генерировать огромный CSS через циклы и миксины.
- Прятать сложную cascade-логику в препроцессоре.

#### Связанные темы

- [[Конспект для подготовки/CSS/Специфичность селекторов]]
- [[Конспект для подготовки/CSS/SCSS]]
- [[Конспект для подготовки/CSS/SCSS modules @use и @forward]]
- [[Конспект для подготовки/CSS/SCSS переменные mixins functions]]
- [[Конспект для подготовки/CSS/SCSS архитектура и вложенность]]
- [[Конспект для подготовки/CSS/CSS reset и normalize]]
- [[Конспект для подготовки/CSS/Responsive design и media queries]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]

#### Источники

- [Sass documentation](https://sass-lang.com/documentation/)
- [Sass: @use](https://sass-lang.com/documentation/at-rules/use/)
- [Sass: @forward](https://sass-lang.com/documentation/at-rules/forward/)
- [MDN: CSS custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
