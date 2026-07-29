# Observer APIs

<!-- NOTE-NAV-TOP:START -->
[← CustomEvent EventTarget dispatchEvent](<./CustomEvent EventTarget dispatchEvent.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [requestAnimationFrame и requestIdleCallback →](<./requestAnimationFrame и requestIdleCallback.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Observer APIs сообщают об изменениях, источник которых не обязательно контролирует текущий код. `MutationObserver` наблюдает изменения DOM-дерева, `ResizeObserver` - размеры элементов, `IntersectionObserver` - пересечение целевого элемента с корневой областью или viewport, `PerformanceObserver` - записи Performance Timeline.

Observer обычно накапливает записи и передаёт их callback пакетно в определённой точке работы браузера. Это эффективнее постоянного опроса, но callback вызывается не мгновенно и не обязательно отдельно для каждого изменения.

Выбор определяется наблюдаемым состоянием. Действие пользователя лучше обрабатывать событием, известное изменение собственного состояния - прямым вызовом, а observer нужен, когда результат может измениться из нескольких внешних источников.

У каждого observer есть жизненный цикл: `observe`, `unobserve`/`disconnect`, иногда `takeRecords`. Наблюдение прекращают вместе с жизненным циклом целевого элемента.

## Ключевая схема

| API | Наблюдает | Типичный сценарий |
| --- | --- | --- |
| `MutationObserver` | дочерние узлы, атрибуты и текст DOM | интеграция со сторонним DOM-кодом |
| `ResizeObserver` | размеры блока элемента | компонент, зависящий от размера контейнера |
| `IntersectionObserver` | пересечение элемента с корневой областью | ленивая загрузка, аналитика видимости |
| `PerformanceObserver` | записи производительности | LCP, долгие задачи, загрузка ресурсов |

```text
браузер обнаруживает изменения
→ добавляет записи наблюдателя
→ группирует их
→ callback получает пакет записей
→ приложение минимально обновляет состояние
```

## `MutationObserver`

```js
const observer = new MutationObserver((records) => {
  for (const record of records) {
    console.log(record.type, record.target);
  }
});

observer.observe(container, {
  childList: true,
  subtree: true,
  attributes: true,
});

observer.disconnect();
```

Настройки выбирают тип наблюдаемых изменений:

- `childList` - добавление или удаление непосредственных дочерних узлов;
- `subtree` - наблюдение за всеми потомками;
- `attributes` и `attributeFilter` - изменения атрибутов;
- `characterData` - изменения текста узла;
- `attributeOldValue`/`characterDataOldValue` - сохранение предыдущих значений.

Callback вызывается после текущего синхронного кода, изменяющего DOM, на этапе микрозадач. Несколько изменений могут прийти одним пакетом.

Если приложение само изменяет свой DOM, прямое обновление состояния обычно понятнее observer. `MutationObserver` полезен на границе Web Component, CMS, стороннего виджета, браузерного расширения или legacy-интеграции, где изменение происходит вне контролируемого API.

`takeRecords()` забирает уже накопленные записи без ожидания callback. `disconnect()` прекращает наблюдение, а оставшиеся записи владелец обрабатывает по правилам своего API.

## MutationObserver и цикл обновлений

Callback может сам изменить наблюдаемый DOM и породить новые записи:

```js
const observer = new MutationObserver(() => {
  container.dataset.processed = "true";
});
```

Если изменение каждый раз создаёт новое наблюдаемое состояние, цикл продолжится на следующих этапах микрозадач. Обработчик проверяет, действительно ли обновление нужно, сужает `attributeFilter` или временно отключает observer.

Observer не заменяет делегирование событий: изменение DOM сообщает, что узел появился, а событие `click` сообщает о действии пользователя.

## `ResizeObserver`

```js
const observer = new ResizeObserver((entries) => {
  for (const entry of entries) {
    const width = entry.contentRect.width;
    entry.target.classList.toggle("compact", width < 480);
  }
});

observer.observe(panel);
```

`ResizeObserver` реагирует на размер элемента, а не только на изменение размера окна. Размер может измениться из-за родительского layout, содержимого, шрифта, CSS или контейнера.

Современные записи также предоставляют размеры разных областей блока (`contentBoxSize`, `borderBoxSize`, `devicePixelContentBoxSize`) в зависимости от поддержки и выбранной модели.

Изменение размера наблюдаемого элемента внутри callback может снова вызвать наблюдатель. Браузер обнаруживает бесконечные циклы и сообщает ошибку, но код должен избегать колебаний: применять изменение только при пересечении устойчивого порога или менять потомка, который не влияет обратно на размер контейнера.

Для чисто стилевой реакции на размер контейнера CSS Container Queries обычно лучше JavaScript: требуется меньше кода жизненного цикла, а браузер сам применяет стили. `ResizeObserver` нужен, когда размер влияет на вычисление, разрешение `canvas` или внешнее состояние.

## `IntersectionObserver`

```js
const observer = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (entry.isIntersecting) {
      loadImage(entry.target);
      observer.unobserve(entry.target);
    }
  }
}, {
  root: null,
  rootMargin: "200px",
  threshold: 0,
});

observer.observe(imagePlaceholder);
```

`root: null` означает viewport (область просмотра). `rootMargin` расширяет или сужает корневую область, а `threshold` задаёт доли пересечения, при которых нужны уведомления.

`IntersectionObserver` работает асинхронно и подходит для решений о видимости, но не сообщает о каждом пикселе прокрутки и не является синхронной проверкой попадания. Для точной текущей геометрии читают layout API, учитывая возможную стоимость пересчёта.

`isIntersecting` говорит о геометрическом пересечении, но не гарантирует, что пользователь действительно увидел элемент: тот может быть перекрыт, прозрачен или находиться в скрытой вкладке. Аналитика должна учитывать Page Visibility и требуемую длительность показа.

## `PerformanceObserver`

```js
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    sendMetric(entry);
  }
});

observer.observe({
  type: "largest-contentful-paint",
  buffered: true,
});
```

`PerformanceObserver` получает записи производительности определённого типа. Поддерживаемые типы проверяют через `PerformanceObserver.supportedEntryTypes`.

`buffered: true` позволяет получить подходящие записи, созданные до вызова `observe`, если конкретный API это поддерживает. Callback не должен синхронно выполнять тяжёлую отправку аналитики для каждой записи; данные объединяют и отправляют подходящим транспортом.

Полевые Core Web Vitals имеют собственные правила жизненного цикла и агрегации. Поэтому измерение в production удобнее строить на проверенной библиотеке `web-vitals`, а `PerformanceObserver` использовать для понимания базового API и собственной телеметрии.

## Lifecycle и память

```js
function observePanel(panel) {
  const observer = new ResizeObserver(handleResize);
  observer.observe(panel);

  return () => observer.disconnect();
}
```

Observer и callbacks могут удерживать целевой элемент и окружающие данные дольше ожидаемого. Отключение обязательно для повторно монтируемого виджета или компонента.

`unobserve(target)` прекращает наблюдение за одним элементом, `disconnect()` - за всеми элементами текущего observer. Один observer часто обслуживает много однотипных элементов, что упрощает жизненный цикл и пакетную обработку.

## Observer или другой механизм

| Требование | Выбор |
| --- | --- |
| Пользователь нажал кнопку | DOM event |
| Собственное состояние изменено | прямое обновление или подписка на store |
| Элемент изменил размер по любой причине | ResizeObserver |
| Стиль зависит от ширины контейнера | CSS Container Query |
| Элемент приблизился к viewport | IntersectionObserver |
| Сторонний код изменил DOM | MutationObserver |
| Нужны записи производительности | PerformanceObserver |
| Нужна точная текущая геометрия | чтение layout с учётом возможного принудительного пересчёта |

## Ключевые уточнения

- Observer доставляет записи пакетами, а не обязательно вызывает callback на каждое отдельное изменение.
- Callbacks `MutationObserver` связаны с этапом микрозадач и могут породить новые изменения.
- `ResizeObserver` отслеживает размеры блока элемента, но их изменение внутри callback способно создать цикл.
- `IntersectionObserver` подходит для проверки порогов видимости, а не для отслеживания каждого пикселя прокрутки.
- Geometric intersection не гарантирует фактический просмотр пользователем.
- CSS Container Queries предпочтительнее ResizeObserver для чистого responsive styling.
- Жизненный цикл observer заканчивается через `unobserve` или `disconnect` вместе с владельцем.

## Связанные темы

- [DOM events](<./DOM events.md>)
- [Event Loop](<./Event Loop.md>)
- [Garbage collection](<./Garbage collection.md>)
- [Оптимизация фронтенда](<./Оптимизация фронтенда.md>)
- [Container queries](<../CSS/Container queries.md>)

## Источники

- [WHATWG DOM Standard: MutationObserver](https://dom.spec.whatwg.org/#mutation-observers)
- [W3C: Resize Observer](https://drafts.csswg.org/resize-observer/)
- [W3C: Intersection Observer](https://w3c.github.io/IntersectionObserver/)
- [W3C: Performance Timeline](https://w3c.github.io/performance-timeline/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← CustomEvent EventTarget dispatchEvent](<./CustomEvent EventTarget dispatchEvent.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [requestAnimationFrame и requestIdleCallback →](<./requestAnimationFrame и requestIdleCallback.md>)
<!-- NOTE-NAV-BOTTOM:END -->
