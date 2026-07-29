# Box Model

<!-- NOTE-NAV-TOP:START -->
[← Псевдоклассы и псевдоэлементы](<./Псевдоклассы и псевдоэлементы.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [display и formatting contexts →](<./display и formatting contexts.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Box Model, или блочная модель, описывает прямоугольные области CSS-элемента: content, padding, border и margin. Она позволяет рассчитать внутренний размер элемента, занимаемое им место и расстояние до соседей.

При `box-sizing: content-box` заданные `width` и `height` относятся к content box, а padding и border увеличивают итоговый border box. При `border-box` они уже входят в заданный размер. Margin не входит в `width` ни в одном режиме. У блочных элементов в обычном потоке вертикальные margins иногда схлопываются, поэтому расстояние не всегда равно их сумме.

## Ключевая схема

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

## Базовая модель

Для элемента с `width: 300px`, горизонтальным `padding: 20px` и `border: 2px`:

```text
content-box: border box = 300 + 20 * 2 + 2 * 2 = 344px
border-box:  border box = 300px, content = 300 - 40 - 4 = 256px
```

Внешняя занимаемая область дополнительно учитывает margin. Однако фактическое положение элемента зависит также от formatting context, доступного пространства, `min-width`, `max-width`, переполнения и правил конкретного layout.

## Развернутый ответ

`content` содержит текст или дочерние элементы. `padding` создаёт пространство между content и border; фон элемента распространяется под padding и, по умолчанию, под border. `border` окружает padding box. Прозрачный margin находится снаружи и разделяет элемент с соседями.

`box-sizing` меняет смысл `width` и `height`. При `content-box` ширина относится только к content, а padding/border добавляются сверху. При `border-box` заданная ширина включает content, padding и border, поэтому компонент проще вписывать в сетку. Поэтому base reset часто задаёт `box-sizing: border-box` для всех элементов.

Margin collapse - схлопывание вертикальных margins блочных элементов в обычном потоке. Если у одного соседнего блока `margin-bottom: 20px`, а у следующего `margin-top: 30px`, общий margin станет `30px`, а не `50px`. Схлопываться также могут margin родителя и первого или последнего дочернего блока, если между ними нет разделяющего border, padding, inline content или других препятствий.

Margins flex- и grid-элементов не схлопываются. Новый block formatting context также предотвращает схлопывание margin своих дочерних элементов с внешним margin контейнера. Поэтому одно и то же значение margin может вести себя по-разному после смены layout-контекста.

Тип outer display определяет участие box во внешнем layout, а inner display - раскладку его потомков. Поэтому размеры нельзя анализировать отдельно от `display`, formatting context и алгоритма Flexbox или Grid.

## Пример

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

С `border-box` border box карточки останется шириной `320px`: content уменьшится, чтобы внутри поместились padding и border. Margin, если его добавить, будет находиться за пределами этих `320px`.

## Диагностика

Если элемент шире ожидаемого, в DevTools нужно сравнить content, padding, border и margin, затем проверить `box-sizing`, `min-width`/`max-width`, intrinsic size содержимого и правила родительского layout. Если расстояние по вертикали не равно сумме margins, следует проверить схлопывание и наличие нового formatting context.

## Ключевые уточнения

- `border-box` включает padding и border в заданные `width` и `height`, но не включает margin.
- `width: auto` и процентные размеры рассчитываются по правилам layout; формула с фиксированным `width` описывает только базовый случай.
- Схлопываются вертикальные margins блочных элементов в обычном потоке, но не margin flex- и grid-элементов.
- Padding создаёт внутреннее пространство и участвует в фоне/области клика; margin создаёт внешнее пространство и прозрачен.
- Переполнение может быть вызвано не только Box Model, но и минимальным размером содержимого, длинным словом или правилами Flexbox/Grid.

## Связанные темы

- [Flexbox](<./Flexbox.md>)
- [Grid](<./Grid.md>)
- [CSS reset и normalize](<./CSS reset и normalize.md>)
- [Позиционирование](<./Позиционирование.md>)

## Источники

- [MDN: Introduction to the CSS basic box model](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_box_model/Introduction_to_the_CSS_box_model)
- [MDN: box-sizing](https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing)
- [MDN: Mastering margin collapsing](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_box_model/Mastering_margin_collapsing)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Псевдоклассы и псевдоэлементы](<./Псевдоклассы и псевдоэлементы.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [display и formatting contexts →](<./display и formatting contexts.md>)
<!-- NOTE-NAV-BOTTOM:END -->
