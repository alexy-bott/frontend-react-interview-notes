# SCSS архитектура и вложенность

<!-- NOTE-NAV-TOP:START -->
[← SCSS переменные mixins functions](<./SCSS переменные mixins functions.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Центрирование →](<./Центрирование.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Архитектура SCSS определяет границы глобальных стилей, component styles и публичных build-time helpers. В React-проекте локальные стили часто лежат рядом с компонентом в `Component.module.scss`, а общие tokens, mixins и functions доступны через ограниченный Sass entrypoint.

Nesting полезен, когда показывает состояние или отношение внутри компонента, но каждый combinator связывает selector с DOM-структурой и часто повышает специфичность. Вложенность оставляют только там, где эта зависимость является частью контракта: `&:focus-visible`, `&[data-state="open"]` или короткая связь с дочерним элементом.

## Ключевая схема

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

## Базовая модель

У стилей есть три разных вида границ:

| Граница | Чем задаётся |
| --- | --- |
| Sass API | `@use`, `@forward`, private members |
| Область class names | CSS Modules, naming convention |
| Приоритет итогового CSS | cascade layers, специфичность, порядок |

Один механизм не заменяет остальные. CSS Modules уменьшают случайные конфликты class names, но скомпилированные rules всё равно участвуют в глобальном каскаде, могут зависеть от порядка импорта и наследуемых custom properties.

## Развернутый ответ

Глубокий selector `.page .sidebar .card .button span` кодирует случайную DOM-структуру. Перенос кнопки или добавление wrapper ломает совпадение. Плоские component classes `.root`, `.icon`, `.label` и явные data attributes выражают роль и состояние без привязки к странице.

`&` ссылается на текущий parent selector. Он удобен для pseudo-classes и data states. Конструкция `&--primary` характерна для BEM, но генерирует новое имя класса путём добавления suffix; в нативном CSS nesting такая Sass-возможность не переносится один к одному. Поэтому при миграции нужно проверять итоговые selectors, а не только похожий синтаксис.

SCSS сочетается с BEM, но механическое вложение всего BEM внутрь блока быстро раздувает selectors. Можно использовать `&__item` и `&--active`, сохраняя небольшую глубину. В CSS Modules обычно меньше нужды в длинных class names: пишут `.root`, `.icon`, `.label`, а состояние отражают через data-атрибуты, class composition или props.

Глобальными оставляют осознанные contracts: cascade layer order, reset/base, `@font-face`, root-level tokens и документную типографику. Component styles держат локально. Однако локальное имя само по себе не устраняет зависимость от global layer order, inheritance и условий, в которых подключён CSS chunk.

`@extend` объединяет selectors в output и способен создать длинные комбинации, особенно через границы архитектурных слоёв. Placeholder selector `%name` ограничивает намерение лучше, чем extend конкретного component class, но результат всё равно нужно проверять. Mixin дублирует declarations, utility/class composition переиспользует rule; выбор зависит от ожидаемого output и runtime contract.

## Пример

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

## Ключевые уточнения

- Sass modules ограничивают build-time API, CSS Modules - class names, cascade layers - приоритет output CSS.
- Вложенность должна выражать устойчивое отношение, а не повторять DOM-дерево.
- Состояние компонента лучше задавать явным class или data attribute, чем контекстом конкретной страницы.
- Глобальная область ограничивается правилами, которые действительно являются контрактом всего приложения.
- `@extend`, mixin и utility class создают разный output; решение принимают после его проверки.
- Архитектура должна позволять удалить компонент вместе с его стилями без поиска скрытых зависимостей по всему проекту.

## Связанные темы

- [SCSS](<./SCSS.md>)
- [SCSS modules @use и @forward](<./SCSS modules @use и @forward.md>)
- [SCSS переменные mixins functions](<./SCSS переменные mixins functions.md>)
- [Специфичность селекторов](<./Специфичность селекторов.md>)
- [Каскад и наследование](<./Каскад и наследование.md>)
- [Frontend architecture](<../Architecture/Frontend architecture.md>)

## Источники

- [Sass: Parent Selector](https://sass-lang.com/documentation/style-rules/parent-selector/)
- [Sass: @extend](https://sass-lang.com/documentation/at-rules/extend/)
- [Sass: @use](https://sass-lang.com/documentation/at-rules/use/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← SCSS переменные mixins functions](<./SCSS переменные mixins functions.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Центрирование →](<./Центрирование.md>)
<!-- NOTE-NAV-BOTTOM:END -->
