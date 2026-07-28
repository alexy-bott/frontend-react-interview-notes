---
aliases:
  - SCSS
  - Sass
  - Sass SCSS
  - Sassy CSS
---

#### Ответ на 60 секунд

SCSS - это CSS-compatible синтаксис Sass. Sass расширяет CSS возможностями, которые выполняются на этапе сборки: переменные, вложенность, mixins, functions, modules, partials и flow control. На выходе браузер всё равно получает обычный CSS, поэтому SCSS не меняет runtime-модель CSS: cascade, specificity, inheritance и порядок правил остаются такими же важными.

В современном проекте SCSS полезен, когда нужно поддерживать дизайн-токены, переиспользуемые mixins, структуру стилей по модулям и legacy-код. Но SCSS не должен превращаться в язык программирования внутри CSS. Sass-абстракция оправдана, когда нативного CSS, custom properties, cascade layers, `clamp()`, `color-mix()` или CSS Modules уже недостаточно для конкретной задачи.

#### Ключевая схема

| Возможность | Где полезна | Риск |
| --- | --- | --- |
| `$variables` | build-time токены, расчёты | не работают в runtime |
| CSS custom properties | темы, runtime-переопределение | зависят от cascade |
| `@mixin` | повторяемые блоки стилей | дублирование CSS в output |
| `@function` | вычисление значений | сложная логика в стилях |
| `@use` | модульная загрузка Sass | нужен Dart Sass |
| `@forward` | публичный API style-library | можно размыть границы |
| nesting | локальная читаемость | рост специфичности |

#### Развернутый ответ

SCSS - синтаксис Sass, совместимый с привычной CSS-записью. Он добавляет build-time возможности: variables, nesting, mixins, functions, modules, partials и flow control. Но результатом всё равно остаётся обычный CSS, поэтому cascade, specificity, inheritance, layers и порядок правил продолжают определять поведение в браузере.

SCSS и CSS Modules не заменяют друг друга. SCSS отвечает за синтаксис и build-time абстракции. CSS Modules локализуют class names на уровне сборщика. Их часто используют вместе: `Button.module.scss` компилируется Sass-ом, а затем class names получают локальные имена.

Sass variables исчезают после компиляции. CSS custom properties остаются в итоговом CSS, участвуют в cascade и могут меняться по теме, состоянию или DOM-контексту. Для runtime-темизации нужны CSS variables; Sass удобно использовать для генерации базовых токенов, fallback-значений и повторяемых build-time паттернов.

Старый Sass `@import` устарел в Dart Sass. В новом коде используют `@use` для подключения модулей и `@forward` для сборки публичного API style-library. `@use` добавляет namespace и не загрязняет глобальную область.

SCSS оправдан, когда есть заметная система токенов, много общих mixins/functions, legacy styles или команда уже поддерживает SCSS-архитектуру. Если проекту хватает CSS Modules, custom properties, cascade layers и простых component styles, обычный CSS может быть проще.

> [!faq]+ Уточнения
> - SCSS расширяет CSS на build-time, но браузер получает обычный CSS.
> - CSS Modules локализуют class names, SCSS не делает это сам.
> - Sass variables не меняются в runtime; CSS variables могут.
> - `@use` и `@forward` заменяют старый Sass `@import`.
> - Sass-абстракции должны упрощать CSS output, а не скрывать его.

#### Пример

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

Здесь Sass помогает собрать build-time токены, а runtime-значения остаются в CSS variables.

#### Частые ошибки

- Думать, что SCSS-переменные можно менять в браузере.
- Использовать старый `@import` в новом коде.
- Делать вложенность на много уровней и случайно разгонять специфичность.
- Писать mixins для каждого маленького повторения вместо обычного класса или custom property.
- Путать пользу SCSS с пользой CSS Modules.
- Прятать архитектурные проблемы CSS за большим количеством Sass-абстракций.

#### Связанные темы

- [[Конспект для подготовки/CSS/SCSS modules @use и @forward]]
- [[Конспект для подготовки/CSS/SCSS переменные mixins functions]]
- [[Конспект для подготовки/CSS/SCSS архитектура и вложенность]]
- [[Конспект для подготовки/CSS/CSS препроцессоры]]
- [[Конспект для подготовки/CSS/Каскад и наследование]]
- [[Конспект для подготовки/CSS/Специфичность селекторов]]

#### Источники

- [Sass: @use](https://sass-lang.com/documentation/at-rules/use/)
- [Sass: Variables](https://sass-lang.com/documentation/variables/)
- [Sass: @import](https://sass-lang.com/documentation/at-rules/import/)
