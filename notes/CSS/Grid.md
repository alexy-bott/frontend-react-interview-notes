# Grid

<!-- NOTE-NAV-TOP:START -->
[← Flexbox](<./Flexbox.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

CSS Grid - это модель раскладки для двумерных сеток, где одновременно управляют строками и колонками. Grid хорошо подходит для layouts страниц, карточных сеток, таблиц интерфейса и областей, где важны и горизонтальные, и вертикальные связи.

Flexbox обычно отвечает на вопрос “как распределить элементы в одной линии”, а Grid - “как построить сетку”. В Grid мы задаем треки через `grid-template-columns` и `grid-template-rows`, используем единицу `fr` для долей свободного места, `gap` для расстояний, `minmax()` для ограничений и `auto-fit/auto-fill` для адаптивных сеток без ручного количества колонок.

## Ключевая схема

| Задача | Инструмент |
| --- | --- |
| Создать grid-контейнер | `display: grid` |
| Задать колонки | `grid-template-columns` |
| Задать строки | `grid-template-rows` |
| Расстояние между ячейками | `gap` |
| Доля свободного места | `fr` |
| Ограничить размер трека | `minmax()` |
| Повторить шаблон | `repeat()` |
| Адаптивная сетка | `repeat(auto-fit, minmax(...))` |
| Разместить элемент | `grid-column`, `grid-row` |

## Развернутый ответ

Grid управляет строками и колонками одновременно. Flexbox раскладывает элементы по одной оси за раз, поэтому подходит для toolbar, меню и выравнивания в линии. Grid подходит для карточных сеток, layouts страниц, областей с фиксированными зонами и случаев, где важны связи по двум направлениям.

Основные сущности Grid - container, tracks, cells, gaps и placement. `grid-template-columns` и `grid-template-rows` задают треки, `gap` задаёт расстояния, `grid-column`/`grid-row` размещают элементы. Auto-placement сам раскладывает элементы, если не задавать позиции вручную.

`fr` - доля свободного пространства после учёта фиксированных размеров, intrinsic sizes и gap. Например, `1fr 2fr` делит оставшееся место в пропорции 1 к 2. `minmax()` помогает задать нижнюю и верхнюю границу трека, чтобы сетка не ломалась на узких экранах.

`auto-fit` и `auto-fill` оба создают столько колонок, сколько помещается. `auto-fill` сохраняет пустые треки, а `auto-fit` схлопывает их и растягивает существующие колонки. Для адаптивных карточек часто используют `repeat(auto-fit, minmax(240px, 1fr))`.

<details>
<summary><strong>Уточнения</strong></summary>

<dl>
<dd>
<h2></h2>

- Flexbox одномерен, Grid двумерен.
- `fr` делит свободное место после fixed sizes и gaps.
- `minmax()` защищает трек от слишком маленького/большого размера.
- `auto-fit` схлопывает пустые треки, `auto-fill` сохраняет их.
- Ручное placement нужно не всегда; auto-placement часто достаточно.

<h2></h2>
</dd>
</dl>

</details>

## Пример

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.featured {
  grid-column: span 2;
}
```

Такой layout автоматически меняет количество колонок в зависимости от ширины контейнера.

## Частые ошибки

- Использовать Grid для простого выравнивания одной строки, где Flexbox проще.
- Забывать, что `fr` делит свободное пространство после фиксированных размеров и `gap`.
- Делать слишком жесткие колонки без `minmax()`, ломая адаптив.
- Путать `auto-fit` и `auto-fill`.
- Злоупотреблять ручным размещением элементов, когда достаточно auto-placement.

## Связанные темы

- [Flexbox](<./Flexbox.md>)
- [Box Model](<../../Конспект для подготовки/CSS/Box Model.md>)
- [Центрирование](<../../Конспект для подготовки/CSS/Центрирование.md>)
- [Позиционирование](<../../Конспект для подготовки/CSS/Позиционирование.md>)

## Источники

- [MDN: CSS grid layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout)
- [MDN: Basic concepts of grid layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Basic_concepts_of_grid_layout)
- [MDN: repeat()](https://developer.mozilla.org/en-US/docs/Web/CSS/repeat)
- [MDN: minmax()](https://developer.mozilla.org/en-US/docs/Web/CSS/minmax)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Flexbox](<./Flexbox.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-BOTTOM:END -->
