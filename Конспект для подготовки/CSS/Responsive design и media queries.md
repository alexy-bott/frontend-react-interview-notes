---
aliases:
  - responsive design
  - media queries
  - адаптивная верстка
  - responsive layout
---

#### Быстрый ответ

Responsive design, или адаптивный дизайн, - это подход, при котором интерфейс сохраняет читаемость и функциональность при разных размерах области просмотра, масштабе текста, способах ввода и пользовательских настройках. Основа - гибкий layout, ограничения min/max, перенос контента, responsive images и точечные media/container queries.

Media query нужна там, где непрерывного сжатия, переноса или перестроения Grid/Flexbox уже недостаточно. Breakpoint выбирают по поведению контента, а не по названию устройства. Mobile-first означает базовый работоспособный layout для узкой области и добавление улучшений через `min-width`, но не является обязательным правилом для любой кодовой базы.

#### Ключевая схема

| Инструмент | Для чего |
| --- | --- |
| `%`, `fr`, `minmax`, `clamp` | гибкие размеры |
| `@media` | условия по viewport или устройству |
| mobile-first | базовые стили для малого экрана |
| `srcset`, `sizes`, `picture` | responsive images |
| `rem`, `em` | масштабируемые размеры |

#### Базовая модель

Адаптивность строится слоями:

```text
семантичный HTML и viewport meta
-> контент без обязательной фиксированной ширины
-> Grid/Flexbox, wrap и min/max-ограничения
-> изображения подходящего размера
-> media queries для глобальных переходов
-> container queries для локальных компонентов
-> проверка zoom, текста, ввода и пользовательских предпочтений
```

На мобильной странице `<meta name="viewport" content="width=device-width, initial-scale=1">` сообщает браузеру использовать ширину устройства как CSS viewport. Без него responsive breakpoints могут рассчитываться относительно виртуального широкого viewport.

#### Развернутый ответ

Responsive design начинается с гибкой базовой верстки: fluid widths, Grid/Flexbox, `minmax()`, `clamp()`, responsive images и разумные ограничения. Media queries добавляют в точках, где layout действительно должен изменить структуру, а не для каждой модели устройства.

Mobile-first часто сочетается с progressive enhancement: базовый контент и действия доступны в ограниченном пространстве, а широкая область добавляет колонки и дополнительные представления. Desktop-first допустим, если так устроена существующая система; важнее единое направление media queries и отсутствие противоречащих переопределений.

Breakpoints выбирают по контенту. Названия вроде tablet/desktop удобны для общения, но технически breakpoint должен появляться там, где карточка, навигация, таблица, форма или layout начинает ломаться. Поэтому ширины проверяют не только в популярных presets, а в промежуточных состояниях.

Media queries умеют проверять не только размер viewport. `hover` и `pointer` помогают не строить критическое взаимодействие только на hover; `prefers-reduced-motion`, `prefers-contrast` и `prefers-color-scheme` учитывают настройки пользователя. Эти признаки используют для адаптации возможностей, а не для точного определения типа устройства.

Responsive images через `srcset` и `sizes` позволяют браузеру выбрать подходящий файл по ширине и плотности экрана; `<picture>` нужен, когда меняется формат или композиция изображения. CSS не уменьшает объём уже скачанного большого файла, поэтому адаптивность изображения решается также на уровне HTML и asset pipeline.

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

Breakpoint означает не «планшет», а ширину, начиная с которой sidebar и основная область помещаются без потери читаемости. Если контент изменится, значение следует проверить заново.

#### Ключевые уточнения

- Breakpoints принадлежат поведению контента, а не конкретным моделям устройств.
- Mobile-first - стратегия организации стилей, а не гарантия хорошей адаптивности.
- Viewport-based font size ограничивают через `clamp()` и проверяют при zoom и увеличенном тексте.
- Media features `hover`/`pointer` описывают возможности ввода и не являются надёжным device detection.
- Responsive images требуют корректных `srcset`/`sizes` или `<picture>`, а не только `max-width: 100%`.
- Проверка включает промежуточные ширины, browser zoom, длинный перевод, клавиатуру, touch и реальные размеры контента.

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
- [MDN: Viewport meta tag](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Viewport_meta_element)
