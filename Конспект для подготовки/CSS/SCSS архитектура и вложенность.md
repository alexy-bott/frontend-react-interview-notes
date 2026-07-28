---
aliases:
  - SCSS architecture
  - Sass architecture
  - SCSS nesting
  - архитектура SCSS
---

#### Ответ на 60 секунд

Архитектура SCSS должна помогать контролировать cascade, а не прятать его. Структура разделяет design tokens, mixins/functions, base styles, components и entrypoints. В компонентном React-проекте SCSS часто живёт рядом с компонентом как `Component.module.scss`, а общие токены и helpers лежат в `shared/styles` или похожем слое.

Вложенность в SCSS нужна для читаемости локального контекста, но её легко испортить. Каждый уровень nesting увеличивает связность с DOM-структурой и часто повышает специфичность. Практичное правило: держать вложенность короткой, использовать `&` для состояний и модификаторов, не повторять всю HTML-структуру в SCSS и не вкладывать selectors глубже, чем нужно для понятного контракта компонента.

#### Ключевая схема

```text
styles/
  _tokens.scss
  _functions.scss
  _mixins.scss
  index.scss

components/
  Button/
    Button.tsx
    Button.module.scss
```

| Зона | Что хранить |
| --- | --- |
| Tokens | цвета, spacing, radius, typography scale |
| Functions | расчёты и map lookup |
| Mixins | reusable CSS-паттерны |
| Base | reset, typography, global defaults |
| Components | локальные стили компонента |
| Entry point | `@forward` публичного style API |

#### Развернутый ответ

Глубокое nesting делает selector длинным и хрупким. Если стиль зависит от `.page .sidebar .card .button span`, изменение DOM ломает CSS. Для компонентов class contract держат плоским: `.button`, `.icon`, `.label`, `.button[data-variant="danger"]`.

`&` ссылается на текущий selector. Он удобен для состояний, псевдоклассов и модификаторов: `&:hover`, `&:focus-visible`, `&[data-state="open"]`, `&--primary`. Если через `&` строить сложные цепочки, итоговый CSS становится трудным для чтения и переопределения.

SCSS сочетается с BEM, но механическое вложение всего BEM внутрь блока быстро раздувает selectors. Можно использовать `&__item` и `&--active`, сохраняя небольшую глубину. В CSS Modules обычно меньше нужды в длинных class names: пишут `.root`, `.icon`, `.label`, а состояние отражают через data-атрибуты, class composition или props.

Глобальными оставляют reset, base typography, CSS variables, font-face и действительно общие правила. Компонентные стили держат локально, чтобы не зависеть от порядка импортов и случайной специфичности.

`@extend` в компонентных стилях применяют осторожно: он объединяет selectors и может создать неожиданный output. Для повторяемых паттернов чаще прозрачнее mixin, utility class или composition.

> [!faq]+ Уточнения
> - Nesting держат коротким, чтобы selector не зависел от DOM-дерева.
> - `&` удобен для states/modifiers, но может породить сложные цепочки.
> - CSS Modules позволяют держать class names короче.
> - Глобальные стили ограничивают reset/base/tokens/font-face.
> - `@extend` может создать неожиданные объединённые selectors.

#### Пример

Проблемный вариант:

```scss
.profile-page {
  .content {
    .card {
      .actions {
        button {
          span {
            color: red;
          }
        }
      }
    }
  }
}
```

Вариант без глубокой вложенности:

```scss
.actionsButton {
  color: var(--color-danger);

  &:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 2px;
  }
}
```

Вариант для CSS Modules:

```scss
.root {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.root[data-variant="danger"] {
  color: var(--color-danger);
}

.icon {
  flex: 0 0 auto;
}
```

#### Частые ошибки

- Копировать DOM-дерево в SCSS через вложенность.
- Считать CSS Modules полной заменой архитектуры стилей.
- Хранить все стили в одном глобальном `main.scss`.
- Делать `@extend` для компонентных классов и получать неожиданные объединённые selectors.
- Завязывать component styles на родительскую страницу без явного контракта.
- Генерировать много utility-классов через Sass, не проверяя размер итогового CSS.

#### Связанные темы

- [[Конспект для подготовки/CSS/SCSS]]
- [[Конспект для подготовки/CSS/SCSS modules @use и @forward]]
- [[Конспект для подготовки/CSS/SCSS переменные mixins functions]]
- [[Конспект для подготовки/CSS/Специфичность селекторов]]
- [[Конспект для подготовки/CSS/Каскад и наследование]]
- [[Конспект для подготовки/Architecture/Frontend architecture]]

#### Источники

- [Sass: Parent Selector](https://sass-lang.com/documentation/style-rules/parent-selector/)
- [Sass: @extend](https://sass-lang.com/documentation/at-rules/extend/)
- [Sass: @use](https://sass-lang.com/documentation/at-rules/use/)
