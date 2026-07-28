---
aliases:
  - CSS reset
  - normalize.css
  - reset css
---

#### Ответ на 60 секунд

CSS reset и normalize решают одну проблему: браузеры имеют разные стили по умолчанию, и из-за этого один и тот же HTML может выглядеть немного по-разному. Reset радикально сбрасывает стандартные стили почти до нуля, а normalize сохраняет полезные дефолты и выравнивает различия между браузерами.

На практике reset удобен, когда в проекте есть своя дизайн-система и все базовые стили контролируются вручную. Normalize мягче: он меньше ломает ожидаемое поведение элементов и подходит, когда хочется сохранить разумные дефолты. В современных проектах часто используют не классический reset, а небольшой base layer: `box-sizing: border-box`, сброс margin у body, базовые стили для media, form controls и typography.

#### Ключевая схема

| Подход | Что делает | Когда выбирать |
| --- | --- | --- |
| Reset | агрессивно сбрасывает стили | дизайн-система, полный контроль |
| Normalize | выравнивает различия браузеров | сохранить полезные дефолты |
| Base styles | точечно задает основу проекта | современный прикладной UI |

#### Развернутый ответ

Без reset/base styles часть поведения зависит от user agent stylesheet браузера. Это заметно на headings, lists, buttons, inputs, margins, line-height и form controls. Разные браузеры могут иметь близкие, но не полностью одинаковые дефолты.

Reset агрессивно убирает дефолтные стили, чтобы проект контролировал внешний вид сам. Normalize мягче: сохраняет полезные browser defaults и выравнивает различия. В приложениях с дизайн-системой часто используют не полный reset, а небольшой base layer.

Типичный base layer задаёт `box-sizing: border-box`, убирает margin у `body`, настраивает шрифт, делает media адаптивными через `max-width: 100%`, а form controls наследуют font. Это создаёт предсказуемую основу без уничтожения всей семантики.

Слишком агрессивный reset может навредить: убрать focus outline, стили списков, размеры headings, поведение form controls и доступные состояния. После такого reset приходится вручную восстанавливать базовый UX и accessibility.

> [!faq]+ Уточнения
> - Reset сбрасывает дефолты, normalize выравнивает различия браузеров.
> - Base layer часто достаточно для прикладного UI.
> - `box-sizing: border-box` обычно задают глобально.
> - Focus styles нельзя удалять без замены.
> - Reset проверяют на forms, headings, lists и accessibility.

#### Пример

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: system-ui, sans-serif;
}

img,
picture,
video,
canvas,
svg {
  display: block;
  max-width: 100%;
}

button,
input,
textarea,
select {
  font: inherit;
}
```

#### Частые ошибки

- Убирать `outline` без замены через видимый `:focus-visible`.
- Использовать агрессивный reset и забывать восстановить стили форм.
- Не понимать, что normalize не “обнуляет” всё.
- Сбрасывать списки и headings глобально, ломая контентные страницы.
- Не проверять reset на accessibility.

#### Связанные темы

- [[Конспект для подготовки/CSS/Box Model]]
- [[Конспект для подготовки/CSS/Специфичность селекторов]]
- [[Конспект для подготовки/HTML/Accessibility]]
- [[Конспект для подготовки/CSS/Responsive design и media queries]]

#### Источники

- [MDN: User-agent stylesheet](https://developer.mozilla.org/en-US/docs/Glossary/User_agent_stylesheet)
- [MDN: box-sizing](https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing)
- [MDN: :focus-visible](https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible)
- [Normalize.css](https://necolas.github.io/normalize.css/)
