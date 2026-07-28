---
aliases:
  - container queries
  - container query
  - "@container"
  - container-type
---

#### Ответ на 60 секунд

Container queries позволяют менять стили элемента не по размеру viewport, как media queries, а по размеру его контейнера. Это особенно полезно для компонентной верстки: карточка, виджет или sidebar могут выглядеть по-разному в зависимости от доступного места, даже если viewport не изменился.

Чтобы использовать container query, родителю задают containment, например `container-type: inline-size`, а внутри пишут `@container`. Главное различие такое: media queries подходят для глобальных breakpoint-ов страницы, а container queries - для локальной адаптивности компонента. Это делает дизайн-системы и переиспользуемые компоненты гибче.

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

#### Развернутый ответ

Media query смотрит на viewport или характеристики устройства. Container query смотрит на размер конкретного контейнера. Поэтому один и тот же компонент может быть компактным в sidebar и широким в main content на одном и том же viewport.

Чтобы `@container` заработал, родитель должен стать query container. Обычно задают `container-type: inline-size`: в горизонтальном writing mode inline-size соответствует ширине. `container-type: size` учитывает оба измерения, но сильнее влияет на layout, поэтому его используют осторожнее.

Именованные контейнеры нужны, когда у компонента есть несколько потенциальных контейнеров или нужно явно выбрать, относительно какого контейнера считать условие. Тогда задают `container-name` и пишут `@container name (...)`.

Container queries не заменяют media queries полностью. Media queries остаются для глобальной структуры страницы: shell, навигация, крупные layout-переходы. Container queries отвечают за локальную адаптивность карточек, виджетов, панелей и компонентов дизайн-системы.

Контейнером обычно делают wrapper компонента, а не сам элемент, который меняет стили. Так компонент получает стабильную область измерения и не пытается менять себя по собственному размеру без внешнего контекста.

> [!faq]+ Уточнения
> - Media query смотрит на viewport, container query - на контейнер.
> - `container-type: inline-size` включает запросы по inline-размеру.
> - `container-name` выбирает конкретный контейнер.
> - Container query units (`cqw`, `cqi`, `cqh`) считаются от контейнера.
> - Глобальный shell часто остаётся на media queries.

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

Одна и та же карточка становится горизонтальной только там, где её контейнер достаточно широкий.

#### Частые ошибки

- Писать `@container`, не задав родителю `container-type`.
- Использовать container queries для глобальной навигации, где проще media query.
- Делать контейнером сам элемент и ожидать, что он сможет менять себя по собственному размеру без wrapper.
- Забывать, что inline-size зависит от writing mode.
- Размазывать логику breakpoints между media и container queries без понятного принципа.

#### Связанные темы

- [[Конспект для подготовки/CSS/Responsive design и media queries]]
- [[Конспект для подготовки/CSS/Grid]]
- [[Конспект для подготовки/CSS/Flexbox]]
- [[Конспект для подготовки/CSS/Единицы измерения]]

#### Источники

- [MDN: CSS container queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries)
