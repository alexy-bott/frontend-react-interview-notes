# display и контексты форматирования

<!-- NOTE-NAV-TOP:START -->
[← Блочная модель (Box Model)](<./04 Блочная модель (Box Model).md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Единицы измерения →](<./06 Единицы измерения.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`display` определяет, какой box создаёт элемент, как этот box участвует в раскладке среди соседей и по какому алгоритму располагаются его дети. Например, block-level box участвует в блочном потоке, inline-level box - в строковом, а `flex` и `grid` создают специальные модели раскладки для потомков.

Formatting context, или контекст форматирования, задаёт правила расположения группы box. Block formatting context (BFC) изолирует блочную раскладку, содержит внутренние floats и ограничивает схлопывание margins через свою границу. Явно создать BFC можно через `display: flow-root`; Flexbox и Grid создают собственные formatting contexts.

## Ключевая схема

| Значение | Поведение |
| --- | --- |
| `block` | block-level box в обычном потоке |
| `inline` | inline-level box внутри строки |
| `inline-block` | inline-сосед + можно задавать размеры |
| `none` | элемент не создаёт box и не участвует в layout |
| `flex` | flex formatting context |
| `grid` | grid formatting context |
| `flow-root` | создаёт новый block formatting context |
| `contents` | убирает собственную box-обёртку, оставляя детей |

```text
display
-> outer display type: как элемент ведёт себя среди соседей
-> inner display type: как раскладываются его дети
```

## Базовая модель

Элемент DOM и CSS box - не одно и то же. Один элемент может создать principal box и дополнительные box, например строки или маркеры списка; `display: none` не создаёт box, а `display: contents` убирает principal box элемента, но сохраняет box его потомков.

Outer display type отвечает за участие principal box во внешнем потоке. Inner display type определяет formatting context для содержимого. Например, `display: inline flex` означает inline-level box с flex layout внутри; привычное `display: flex` в обычной записи создаёт block-level flex container.

## Развернутый ответ

Block-level box с `width: auto` в обычном горизонтальном writing mode обычно заполняет доступное пространство по inline axis. Это следствие алгоритма normal flow, а не буквальное определение `block`: ограничения ширины, writing mode и внешний formatting context могут изменить результат.

Inline box участвует в строках, а свойства `width` и `height` к обычному non-replaced inline element не применяются так, как к block box. Горизонтальные padding, border и margin учитываются в строке, а вертикальные не раздвигают line boxes тем же способом. Для управляемого прямоугольного размера используют `inline-block`, `block`, `flex` или `grid` в зависимости от задачи.

`display: none` убирает box вместе с потомками из layout; такое поддерево также не представляется пользователю через accessibility tree. `visibility: hidden` сохраняет занимаемое место, но скрывает элемент и исключает его из фокуса. Если контент нужно скрыть только визуально, но оставить доступным для screen reader, применяют отдельный visually-hidden pattern, а не эти свойства.

Block formatting context изолирует блочную раскладку: содержит floats, предотвращает некоторые случаи margin collapse с внешними элементами и ограничивает влияние внутреннего layout. `display: flow-root` - современный явный способ создать BFC без хаков вроде `overflow: hidden`.

`display: contents` полезен, когда промежуточная DOM-обёртка не должна участвовать в Grid или Flex layout. При этом у элемента исчезает собственный box: на нём нельзя ожидать обычного фона, border или размеров. Для семантических и интерактивных элементов нужно проверять поведение в целевых браузерах и assistive technologies.

## Пример

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

## Ключевые уточнения

- `block` описывает тип участия в потоке, а заполнение доступной ширины зависит от алгоритма layout и `width: auto`.
- `display: none` не оставляет box для интерполяции обычного transition между скрытым и видимым состояниями.
- BFC и stacking context решают разные задачи: первый относится к layout, второй - к порядку отрисовки.
- `flow-root` явно создаёт BFC без побочного обрезания содержимого через `overflow`.
- `display: contents` сохраняет DOM-узел, но убирает его principal box; это влияет на оформление и требует проверки доступности.

## Связанные темы

- [Блочная модель (Box Model)](<./04 Блочная модель (Box Model).md>)
- [Flexbox](<./07 Flexbox.md>)
- [CSS Grid](<./08 CSS Grid.md>)
- [Позиционирование](<./18 Позиционирование.md>)
- [Каскад и наследование](<./01 Каскад и наследование.md>)

## Источники

- [MDN: display](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/display)
- [MDN: Block formatting context](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Display/Block_formatting_context)
- [CSS Display Module Level 3](https://www.w3.org/TR/css-display-3/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Блочная модель (Box Model)](<./04 Блочная модель (Box Model).md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Единицы измерения →](<./06 Единицы измерения.md>)
<!-- NOTE-NAV-BOTTOM:END -->
