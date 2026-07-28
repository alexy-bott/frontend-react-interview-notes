---
aliases:
  - display
  - block
  - inline
  - inline-block
  - formatting context
  - BFC
---

#### Ответ на 60 секунд

`display` задаёт, как элемент участвует в layout: каким будет его внешний тип поведения для соседей и внутренний формат раскладки для детей. Классические значения: `block` занимает доступную ширину и начинается с новой строки, `inline` течёт внутри строки и не принимает width/height как block, `inline-block` остаётся inline-соседом, но позволяет задавать размеры, `none` убирает элемент из layout и accessibility tree.

Отдельно важно понимать formatting contexts. Block formatting context изолирует часть layout: внутри него по-другому схлопываются margins, он содержит floats и помогает предотвратить вытекание layout-эффектов наружу. Современный способ создать BFC - `display: flow-root`. Flex и Grid тоже создают свои formatting contexts и меняют поведение детей.

#### Ключевая схема

| Значение | Поведение |
| --- | --- |
| `block` | новая строка, доступная ширина |
| `inline` | внутри строки, размеры ограничены текстовым потоком |
| `inline-block` | inline-сосед + можно задавать размеры |
| `none` | нет layout box |
| `flex` | flex formatting context |
| `grid` | grid formatting context |
| `flow-root` | создаёт новый block formatting context |
| `contents` | убирает собственную box-обёртку, оставляя детей |

```text
display
-> outer display type: как элемент ведёт себя среди соседей
-> inner display type: как раскладываются его дети
```

#### Развернутый ответ

`display` задаёт outer и inner layout behavior. Outer display type описывает, как элемент ведёт себя среди соседей: block, inline, inline-block. Inner display type описывает, как раскладываются дети: flow, flex, grid. Поэтому `display` влияет не только на видимость, но и на модель layout.

Inline-элемент участвует в inline formatting context: его размер определяется содержимым и line box. `width` и `height` не работают как у block. Для явного размера используют `block`, `inline-block`, `flex`, `grid` или другой подходящий display.

`display: none` убирает элемент из layout и обычно из accessibility tree. `visibility: hidden` скрывает визуально, но место в layout остаётся. Для интерактивных элементов важно учитывать не только видимость, но и focus, screen readers и возможность взаимодействия.

Block formatting context изолирует блочную раскладку: содержит floats, предотвращает некоторые случаи margin collapse с внешними элементами и ограничивает влияние внутреннего layout. `display: flow-root` - современный явный способ создать BFC без хаков вроде `overflow: hidden`.

`display: contents` убирает box самого элемента, и дети ведут себя так, будто подняты на уровень выше. Это может помочь layout, но опасно для accessibility и стилизации, если элемент несёт семантику, role или является якорем для CSS/JS.

> [!faq]+ Уточнения
> - Outer display type влияет на поведение элемента среди соседей.
> - Inner display type влияет на раскладку детей.
> - `display: none` убирает layout box, `visibility: hidden` сохраняет место.
> - `flow-root` создаёт BFC и помогает с floats/margin collapse.
> - `display: contents` требует проверки accessibility.

#### Пример

```css
.media {
  display: flow-root;
}

.media__image {
  float: left;
  margin-right: 16px;
}
```

`flow-root` заставляет контейнер учитывать float внутри и не отдаёт этот layout-эффект наружу.

#### Частые ошибки

- Использовать `inline` и ждать нормальной работы `width`/`height`.
- Скрывать интерактивный элемент визуально, но оставлять его доступным для фокуса.
- Лечить floats через clearfix-хак, не зная про `flow-root`.
- Использовать `display: none` для анимируемого раскрытия, а потом удивляться, что transition не работает.
- Применять `display: contents` к семантическим элементам без проверки accessibility.

#### Связанные темы

- [[Конспект для подготовки/CSS/Box Model]]
- [[Конспект для подготовки/CSS/Flexbox]]
- [[Конспект для подготовки/CSS/Grid]]
- [[Конспект для подготовки/CSS/Позиционирование]]
- [[Конспект для подготовки/CSS/Каскад и наследование]]

#### Источники

- [MDN: display](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/display)
