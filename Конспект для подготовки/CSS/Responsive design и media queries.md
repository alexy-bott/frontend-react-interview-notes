---
aliases:
  - responsive design
  - media queries
  - адаптивная верстка
  - responsive layout
---

#### Ответ на 60 секунд

Responsive design - это подход, при котором интерфейс адаптируется под разные размеры экрана, способы ввода и возможности устройства. Основа - гибкие layout-модели, относительные единицы, корректные breakpoints, responsive images и media queries.

Адаптив не сводится к набору хаотичных `@media`. Сначала строят гибкую базовую верстку, часто mobile-first, а media queries используют точечно, когда layout действительно должен измениться. Breakpoints выбирают по моменту, где ломается интерфейс, а не только по конкретным моделям устройств.

#### Ключевая схема

| Инструмент | Для чего |
| --- | --- |
| `%`, `fr`, `minmax`, `clamp` | гибкие размеры |
| `@media` | условия по viewport или устройству |
| mobile-first | базовые стили для малого экрана |
| `srcset`, `sizes`, `picture` | responsive images |
| `rem`, `em` | масштабируемые размеры |

#### Развернутый ответ

Responsive design начинается с гибкой базовой верстки: fluid widths, Grid/Flexbox, `minmax()`, `clamp()`, responsive images и разумные ограничения. Media queries добавляют в точках, где layout действительно должен изменить структуру, а не для каждой модели устройства.

Mobile-first означает, что базовые стили пишутся для малого экрана, а затем расширяются через `@media (min-width: ...)`. Такой подход уменьшает количество переопределений и хорошо ложится на progressive enhancement. Desktop-first тоже возможен, но часто требует большего числа сбросов для узких экранов.

Breakpoints выбирают по контенту. Названия вроде tablet/desktop удобны для общения, но технически breakpoint должен появляться там, где карточка, навигация, таблица, форма или layout начинает ломаться. Поэтому ширины проверяют не только в популярных presets, а в промежуточных состояниях.

Container queries решают локальную адаптивность компонента. Media query смотрит на viewport, а container query - на размер контейнера. Один и тот же виджет может быть компактным в sidebar и широким в main area на одном и том же viewport.

> [!faq]+ Уточнения
> - Responsive design включает layout, typography, media, input types и performance.
> - Mobile-first обычно строится через `min-width`.
> - Breakpoint выбирают по месту поломки контента, а не только по устройству.
> - Container queries подходят для компонентной адаптивности.
> - Responsive images важны, чтобы мобильный экран не скачивал лишние мегабайты.

#### Пример

```css
.layout {
  display: grid;
  gap: 16px;
}

@media (min-width: 768px) {
  .layout {
    grid-template-columns: 240px 1fr;
  }
}
```

#### Частые ошибки

- Подбирать breakpoints только под устройства.
- Делать фиксированные ширины там, где нужны `max-width` и гибкие треки.
- Забывать про изображения и получать тяжелую загрузку на мобильных.
- Масштабировать шрифт через `vw` без ограничений.
- Проверять адаптив только в одной ширине.

#### Связанные темы

- [[Конспект для подготовки/CSS/Flexbox]]
- [[Конспект для подготовки/CSS/Grid]]
- [[Конспект для подготовки/CSS/Box Model]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]

#### Источники

- [MDN: Responsive design](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design)
- [MDN: Using media queries](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_media_queries/Using_media_queries)
- [MDN: Responsive images](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images)
- [MDN: CSS values and units](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Values_and_units)
