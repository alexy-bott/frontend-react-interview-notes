---
aliases:
  - box model
  - CSS box model
  - блочная модель
---

#### Ответ на 60 секунд

Box Model - это модель, по которой браузер считает размер элемента. Любой элемент можно представить как прямоугольник из четырех слоев: content, padding, border и margin. От того, как считается ширина и высота, зависит предсказуемость layout.

По умолчанию `box-sizing: content-box`: `width` задает только ширину контента, а padding и border добавляются сверху. В современной верстке часто ставят `box-sizing: border-box`, чтобы `width` уже включал content, padding и border. Отдельно важно помнить margin collapse: вертикальные margins блочных элементов могут схлопываться, поэтому расстояние между блоками иногда получается не суммой двух margins, а максимальным из них.

#### Ключевая схема

| Слой | Что означает |
| --- | --- |
| `content` | содержимое элемента |
| `padding` | внутренний отступ |
| `border` | рамка |
| `margin` | внешний отступ |

| `box-sizing` | Как считается размер |
| --- | --- |
| `content-box` | `width` только для content |
| `border-box` | `width` включает content, padding и border |

#### Развернутый ответ

Box Model определяет, какую площадь занимает элемент и как эта площадь влияет на соседей. `content` содержит текст/детей, `padding` добавляет внутренний отступ, `border` рисует рамку, `margin` создаёт внешнее расстояние. Ошибки в этой модели быстро превращаются в неожиданные переполнения и сломанный layout.

`box-sizing` меняет смысл `width` и `height`. При `content-box` ширина относится только к content, а padding/border добавляются сверху. При `border-box` заданная ширина включает content, padding и border, поэтому компонент проще вписывать в сетку. Поэтому base reset часто задаёт `box-sizing: border-box` для всех элементов.

Margin collapse - схлопывание вертикальных margins у блочных элементов в нормальном потоке. Если у одного блока `margin-bottom: 20px`, а у следующего `margin-top: 30px`, расстояние между ними может стать `30px`, а не `50px`. Это не баг, а правило блочной модели.

Margins не схлопываются во flex/grid-контейнерах, у absolutely positioned элементов, при наличии border/padding между родителем и потомком, а также внутри нового block formatting context. Поэтому переход на flex/grid часто меняет поведение расстояний.

`display` влияет на размеры. `block` занимает доступную ширину и начинается с новой строки. `inline` течёт внутри строки, и ширина/высота для него работают ограниченно. `inline-block` остаётся inline-соседом, но позволяет задавать размеры, padding и margins предсказуемее.

> [!faq]+ Уточнения
> - `content-box`: `width` задаёт только content.
> - `border-box`: `width` включает content, padding и border.
> - Margin collapse касается вертикальных margins блочных элементов в normal flow.
> - Flex/grid и BFC меняют поведение margin collapse.
> - Padding - внутреннее расстояние, margin - внешнее.

#### Пример

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}

.card {
  width: 320px;
  padding: 24px;
  border: 1px solid #ddd;
}
```

С `border-box` итоговая ширина `.card` останется `320px`, а не превратится в `370px`.

#### Частые ошибки

- Считать, что `width` всегда означает итоговую ширину элемента.
- Не учитывать padding и border при `content-box`.
- Удивляться схлопыванию вертикальных margins.
- Использовать margins для внутреннего расстояния вместо padding.
- Не понимать разницу между `inline`, `block` и `inline-block`.

#### Связанные темы

- [[Конспект для подготовки/CSS/Flexbox]]
- [[Конспект для подготовки/CSS/Grid]]
- [[Конспект для подготовки/CSS/CSS reset и normalize]]
- [[Конспект для подготовки/CSS/Позиционирование]]

#### Источники

- [MDN: Introduction to the CSS basic box model](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_box_model/Introduction_to_the_CSS_box_model)
- [MDN: box-sizing](https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing)
- [MDN: Mastering margin collapsing](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_box_model/Mastering_margin_collapsing)
