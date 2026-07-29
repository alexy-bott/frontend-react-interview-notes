# CSS препроцессоры

<!-- NOTE-NAV-TOP:START -->
[← CSS reset и normalize](<./CSS reset и normalize.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [SCSS →](<./SCSS.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

CSS-препроцессор принимает исходные стили с дополнительным синтаксисом и во время сборки преобразует их в обычный CSS, который понимает браузер. Sass/SCSS, Less и Stylus дают build-time variables, вложенность, mixins, functions и средства разбиения кода на модули.

Препроцессор не меняет модель выполнения CSS: после компиляции остаются каскад, специфичность, наследование и browser compatibility итоговых свойств. Его выбирают, когда build-time абстракции действительно уменьшают сложность проекта. Custom properties, CSS nesting, `color-mix()` и cascade layers уже закрывают часть прежних причин использовать препроцессор.

## Ключевая схема

| Возможность | Зачем нужна |
| --- | --- |
| Переменные | единые цвета, отступы, размеры |
| Вложенность | локальная структура селекторов |
| Mixins | переиспользование блоков CSS |
| Functions | вычисления и генерация значений |
| Modules | `@use` и `@forward` вместо глобального `@import` |
| Partials | разбиение стилей на файлы |

## Базовая модель

```text
.scss/.less source
-> compiler или bundler plugin
-> обычный .css
-> оптимизация и source map
-> загрузка и выполнение CSS браузером
```

Ошибки бывают на двух уровнях. Compiler проверяет синтаксис и вычисляет build-time конструкции. Браузер затем применяет итоговый CSS и может отбросить неизвестное или невалидное свойство. Успешная SCSS-сборка не гарантирует правильный cascade, layout или поддержку CSS-функции в целевых браузерах.

## Развернутый ответ

Sass - препроцессор, у которого есть два синтаксиса. SCSS использует фигурные скобки и точки с запятой и принимает обычный CSS как валидный исходник. Indented syntax в файлах `.sass` использует отступы. В frontend-проектах чаще встречается `.scss`.

Sass-переменные и CSS custom properties решают разные задачи. Sass-переменные вычисляются на этапе сборки и исчезают из итогового CSS. CSS custom properties остаются в браузере, участвуют в cascade, могут меняться по теме, состоянию, media/container context и DOM-структуре.

PostCSS занимает соседнее место в toolchain, но не является одним конкретным языком препроцессора: это платформа, где plugins анализируют и преобразуют CSS. Например, один plugin добавляет vendor prefixes, другой обрабатывает будущий синтаксис. CSS Modules, в свою очередь, локализуют class names и могут использоваться как с обычным CSS, так и с SCSS.

Препроцессор в новом проекте нужен не всегда. SCSS оправдан, когда проект использует общие build-time tokens, параметризованные mixins/functions, библиотеку стилей или уже имеет поддерживаемую Sass-архитектуру. Если задача решается нативным CSS короче и прозрачнее, дополнительная стадия сборки не даёт преимущества.

Для отладки важны source maps и проверка скомпилированного output. Цикл или mixin может незаметно сгенерировать тысячи селекторов, а глубокая вложенность - повысить специфичность. Размер, порядок и форма итогового CSS важнее компактности исходного SCSS.

## Пример

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

Mixin уменьшает повторение исходника, но каждое `@include card` вставит declarations в итоговый CSS. Если одинаковый визуальный паттерн можно выразить общим классом, он может дать меньший output и более явный runtime contract.

## Ключевые уточнения

- Sass - препроцессор, SCSS - один из его синтаксисов; CSS Modules - другой механизм сборки.
- Sass variables вычисляются при сборке, CSS custom properties остаются в браузере и участвуют в каскаде.
- Препроцессор не добавляет браузеру поддержку сгенерированных CSS-свойств.
- Mixins и loops могут уменьшить исходник, но увеличить итоговый CSS.
- `@use` и `@forward` формируют модульные границы современного Sass; `@import` устарел.
- Source maps связывают итоговый CSS с исходником, но output всё равно нужно проверять напрямую.

## Связанные темы

- [Специфичность селекторов](<./Специфичность селекторов.md>)
- [SCSS](<./SCSS.md>)
- [SCSS modules @use и @forward](<./SCSS modules @use и @forward.md>)
- [SCSS переменные mixins functions](<./SCSS переменные mixins functions.md>)
- [SCSS архитектура и вложенность](<./SCSS архитектура и вложенность.md>)
- [CSS reset и normalize](<./CSS reset и normalize.md>)
- [Responsive design и media queries](<./Responsive design и media queries.md>)
- [Bundlers и code splitting](<../Web Basics/Bundlers и code splitting.md>)

## Источники

- [Sass documentation](https://sass-lang.com/documentation/)
- [Sass: @use](https://sass-lang.com/documentation/at-rules/use/)
- [Sass: @forward](https://sass-lang.com/documentation/at-rules/forward/)
- [MDN: CSS custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← CSS reset и normalize](<./CSS reset и normalize.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [SCSS →](<./SCSS.md>)
<!-- NOTE-NAV-BOTTOM:END -->
