---
aliases:
  - container queries
  - container query
  - "@container"
  - container-type
---

#### Быстрый ответ

Container queries позволяют менять стили элемента не по размеру viewport, как media queries, а по размеру его контейнера. Это особенно полезно для компонентной верстки: карточка, виджет или sidebar могут выглядеть по-разному в зависимости от доступного места, даже если viewport не изменился.

Для size query подходящему предку задают `container-type`, обычно `inline-size`, а условные стили потомков описывают в `@container`. Media queries подходят для условий уровня viewport и пользовательских настроек; container queries - для компонента, который должен зависеть от места в конкретном layout.

#### Ключевая схема

```text
component parent
-> container-type: inline-size
-> child styles use @container
-> layout adapts to container, not viewport
```

| Механизм | Роль |
| --- | --- |
| `container-type` | включает контейнер для запросов |
| `inline-size` | запросы по inline-размеру |
| `size` | запросы по inline и block размеру |
| `container-name` | имя контейнера |
| `@container` | условные стили по контейнеру |
| `cqw`, `cqh`, `cqi` | container query units |

#### Базовая модель

Элемент внутри `@container` ищет ближайшего предка, который является query container нужного типа и, если указано имя, имеет подходящее `container-name`. Условие сравнивается с размером этого контейнера, после чего стили применяются к потомку.

Size containment разрывает циклическую зависимость: размер query container по запрашиваемой оси не должен определяться изменениями потомка, которые сами зависят от этого размера. Поэтому контейнером обычно служит внешняя layout-обёртка, а `@container` меняет внутреннее представление компонента.

#### Развернутый ответ

Media query смотрит на viewport или характеристики устройства. Container query смотрит на размер конкретного контейнера. Поэтому один и тот же компонент может быть компактным в sidebar и широким в main content на одном и том же viewport.

`container-type: inline-size` позволяет делать size queries по inline axis и устанавливает необходимое containment по этой оси. В привычном горизонтальном writing mode это ширина, но в вертикальном writing mode направление другое. `container-type: size` разрешает запросы по обеим осям и сильнее ограничивает зависимость размера контейнера от содержимого.

Именованные контейнеры нужны, когда у компонента есть несколько потенциальных контейнеров или нужно явно выбрать, относительно какого контейнера считать условие. Тогда задают `container-name` и пишут `@container name (...)`.

Container queries не заменяют media queries. Media queries остаются нужны для viewport, способа ввода и пользовательских предпочтений. Container queries отвечают за локальную геометрию карточек, виджетов и компонентов дизайн-системы.

Container query units связывают размер с query container: `cqi` - 1% inline size, `cqb` - 1% block size, `cqw`/`cqh` - 1% физической ширины/высоты. Логические `cqi` и `cqb` лучше выражают зависимость при разных writing modes.

#### Пример

```css
.card-list {
  container-type: inline-size;
}

.card {
  display: grid;
  gap: 12px;
}

@container (min-width: 520px) {
  .card {
    grid-template-columns: 160px 1fr;
    align-items: start;
  }
}
```

Одна и та же карточка становится горизонтальной только там, где ближайший size query container достаточно широк. Viewport при этом может не меняться.

#### Ключевые уточнения

- Size query ищет подходящий container среди предков, а не измеряет стилизуемый элемент относительно самого себя.
- `inline-size` зависит от writing mode и не всегда означает физическую ширину.
- Containment меняет расчёт intrinsic size, поэтому query container должен получать размер из внешнего layout или явных ограничений.
- Media queries выражают глобальные условия и предпочтения; container queries - доступное место компонента.
- Именованный container делает зависимость явной, когда на пути несколько возможных контейнеров.

#### Связанные темы

- [[Конспект для подготовки/CSS/Responsive design и media queries]]
- [[Конспект для подготовки/CSS/Grid]]
- [[Конспект для подготовки/CSS/Flexbox]]
- [[Конспект для подготовки/CSS/Единицы измерения]]

#### Источники

- [MDN: CSS container queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries)
