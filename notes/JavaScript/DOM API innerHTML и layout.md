# DOM API innerHTML и layout

<!-- NOTE-NAV-TOP:START -->
[← Debounce и throttle](<./Debounce и throttle.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [DOM events →](<./DOM events.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

DOM API представляет HTML-документ как дерево объектов `Node`. JavaScript находит узлы, создаёт и перемещает элементы, меняет текст и атрибуты, читает геометрию; затем браузер отражает изменения через стили, layout, paint и compositing.

Для обычного текста используют `textContent`, который не интерпретирует строку как HTML. `innerHTML` запускает HTML-парсер и создаёт поддерево. Недоверенная строка в таком месте может привести к DOM XSS, поэтому разрешённый HTML очищают с учётом контекста и дополняют защитой CSP или Trusted Types.

Записи в DOM не обязаны немедленно вызвать paint: браузер может объединить их. Но чтение геометрии после записи способно потребовать актуальный layout и синхронно запустить пересчёт стилей и расположения. Частое чередование чтений и записей называют layout thrashing.

Производительность улучшают не правилом «всегда использовать `DocumentFragment`», а уменьшением числа необходимых DOM-операций, группировкой чтений и записей, понятным владением узлами и измерением реального узкого места.

## Ключевая схема

```text
HTML parse / DOM API
→ DOM tree changes
→ style calculation
→ layout
→ paint
→ composite
```

```text
обычный недоверенный текст → textContent
доверенная или статическая разметка → создание DOM/template
разрешённый внешний rich HTML → проверенный sanitizer + политика Trusted Types/CSP
```

## Node, Element и выборка

`Node` - базовый тип для `Document`, `Element`, `Text`, `Comment` и других узлов дерева. `Element` добавляет API тегов, атрибутов, классов и поиска.

```js
const form = document.querySelector("form[data-profile]");

if (!form) {
  throw new Error("Profile form not found");
}
```

`querySelector` возвращает первый `Element` или `null`. `querySelectorAll` возвращает статический снимок `NodeList`:

```js
const items = document.querySelectorAll(".item");
```

`getElementsByClassName` и `getElementsByTagName` возвращают живую `HTMLCollection`, которая автоматически отражает изменения DOM. Изменение DOM во время обхода такой коллекции может пропустить элемент или посетить его повторно; снимок через `Array.from` делает набор стабильным.

Динамическую часть CSS-селектора экранируют через `CSS.escape`. Прямое добавление пользовательской строки может создать некорректный селектор или изменить его смысл.

## Создание и перемещение узлов

```js
const item = document.createElement("li");
item.className = "user";
item.textContent = user.name;

list.append(item);
```

Добавление уже существующего узла перемещает его, а не копирует:

```js
secondContainer.append(item);
// item удалён из list и теперь находится во secondContainer
```

Для копии используют `cloneNode(deep)`, но обработчики `addEventListener` и пользовательское JavaScript-состояние не копируются. Глубокое клонирование также способно продублировать `id`, что нарушит уникальность и связь подписей с полями формы.

`replaceChildren` позволяет одной операцией заменить дочерние узлы владельца. `DocumentFragment` собирает узлы вне основного дерева и при `append` переносит своих потомков:

```js
const fragment = document.createDocumentFragment();

for (const user of users) {
  const item = document.createElement("li");
  item.textContent = user.name;
  fragment.append(item);
}

list.replaceChildren(fragment);
```

Фрагмент удобен для пакетного создания узлов, но современные браузеры и так объединяют рендеринг. Реальный выигрыш зависит от числа DOM-операций и чтений, требующих layout, поэтому его проверяют измерением.

## `textContent`, `innerText` и `innerHTML`

`textContent` читает и записывает текстовое содержимое без разбора HTML:

```js
message.textContent = userInput;
```

Теги из введённой строки отображаются как текст. Это основной выбор для недоверенного обычного текста.

`innerText` отражает отображаемый текст и учитывает стили, видимость и переносы строк. Его чтение может потребовать layout, поэтому для обычной работы с данными и текстом используют `textContent`.

`innerHTML` сериализует или разбирает HTML-разметку:

```js
container.innerHTML = "<strong>Saved</strong>";
```

Присваивание заменяет поддерево: старые узлы-потомки и привязанные к ним обработчики или состояние больше не находятся в документе. Делегирование событий на стабильном контейнере переживает такую замену, но внешние ссылки на удалённые узлы всё равно нужно очищать.

## XSS и HTML sinks

```js
container.innerHTML = userComment; // DOM XSS risk
```

Даже если тег `<script>`, вставленный конкретным API, обычно не выполняется, опасными остаются атрибуты-обработчики, контексты SVG и MathML, небезопасные URL и особенности HTML-парсера. Поэтому одного удаления `<script>` недостаточно для очистки.

Для обычного текста используют `textContent`. Если продукт действительно разрешает rich HTML, применяют проверенную библиотеку очистки с явным списком разрешённых элементов и атрибутов. Content Security Policy ограничивает последствия, а Trusted Types централизует создание значений для опасных HTML-точек вставки в поддерживающих браузерах.

`insertAdjacentHTML`, `outerHTML`, `Range.createContextualFragment` и низкоуровневые точки вставки фреймворка также разбирают HTML и требуют той же модели доверия.

Frontend-валидация не превращает сохранённый HTML в безопасный навсегда: очистка должна соответствовать месту вставки и текущей политике.

## Attributes и properties

HTML-атрибут задаёт исходное или сериализованное состояние, а DOM-свойство - текущее состояние объекта. Они не всегда синхронизируются симметрично.

```js
input.setAttribute("value", "initial");
input.value = "current";
```

После ввода `input.value` отражает текущее значение, а атрибут может сохранить исходное значение по умолчанию.

Логический атрибут определяется присутствием, а не строковым значением:

```html
<button disabled="false">Disabled всё равно включён</button>
```

Правильно:

```js
button.disabled = false;
button.toggleAttribute("disabled", shouldDisable);
```

Для `data-*` используется `element.dataset`, а значения остаются строками.

## Запись в DOM и рендеринг

```js
element.style.width = "200px";
element.classList.add("active");
```

Изменение DOM или стилей обновляет внутреннее состояние, но браузер обычно откладывает рендеринг до подготовки кадра. Несколько записей могут быть обработаны вместе.

Некоторые чтения требуют актуальной геометрии:

- `getBoundingClientRect()`;
- `offsetWidth`/`offsetHeight`;
- `clientWidth`/`clientHeight`;
- `scrollTop` и связанные метрики в определённых условиях;
- `getComputedStyle()` для свойств, зависящих от layout.

Если отложенная запись сделала layout устаревшим, браузер может синхронно пересчитать его перед возвратом значения.

## Layout thrashing

```js
for (const item of items) {
  item.style.width = `${containerWidth}px`; // write
  console.log(item.offsetWidth);            // read, возможный layout
}
```

Чередование создаёт повторные принудительные пересчёты layout. Чтения группируют перед записями:

```js
const widths = items.map((item) => item.offsetWidth);

items.forEach((item, index) => {
  item.style.transform = `translateX(${widths[index]}px)`;
});
```

Для следующего визуального обновления записи можно объединить в `requestAnimationFrame`, но rAF сам не исправляет чтение после записи внутри callback.

Профиль в DevTools Performance показывает события Layout и места принудительного reflow. Оптимизацию подтверждают измерением, а не только перестановкой строк по догадке.

## Большие списки

Создание тысяч узлов увеличивает стоимость расчёта стилей, layout, paint и расход памяти. Возможные решения:

- пагинация или постепенный рендеринг;
- virtualization видимой области;
- `content-visibility` для содержимого вне области просмотра;
- event delegation;
- упрощение поддерева одной строки;
- точечные стабильные обновления вместо полной замены списка.

Виртуализация усложняет переменную высоту строк, focus, навигацию скринридера и восстановление прокрутки. Её применяют после измерения размера DOM и с учётом пользовательского сценария.

## DOM lifecycle и память

`element.remove()` удаляет узел из документа, но объект остаётся живым, если JavaScript хранит на него ссылку. Отсоединённое поддерево может удерживать обработчики и данные через замыкания.

```js
let cachedPanel = document.querySelector(".panel");
cachedPanel.remove();
// cachedPanel всё ещё удерживает node
```

После завершения жизненного цикла очищают внешние ссылки, обработчики, observers, таймеры и кэши. Цикл «узел - обработчик» сам по себе может быть собран, если вся группа недостижима; важен путь удержания от живого корня.

## DOM API или framework render

React и Vue управляют своим DOM-поддеревом. Ручное изменение узлов внутри него может быть перезаписано следующим render и нарушить модель владения.

DOM API используют через предусмотренные точки интеграции: ref для focus или измерения, effect для стороннего виджета, portal для отдельного контейнера. Состояние фреймворка остаётся источником истины для декларативной части.

Для независимого виджета без фреймворка прямое управление DOM нормально, если функция монтирования возвращает полную очистку.

## Где применяется во frontend

- Обычный пользовательский текст вставляется через `textContent`.
- Rich HTML проходит очистку и централизованную политику Trusted Types.
- Динамический список строится с понятным владением узлами и делегированием событий.
- Геометрия читается до записей, чтобы избежать повторных пересчётов layout.
- Большой список получает виртуализацию только после измерения стоимости DOM и рендеринга.
- Ref фреймворка используется для focus или измерения, а не для параллельного ручного рендеринга.

## Ключевые уточнения

- Объект DOM-узла и отображаемый пиксель относятся к разным этапам рендеринга.
- `querySelectorAll` возвращает статический снимок, а некоторые старые коллекции являются живыми.
- Добавление существующего узла перемещает его; клонирование не копирует обработчики `addEventListener`.
- `textContent` вставляет текст, а `innerHTML` запускает парсер и создаёт риск XSS.
- Атрибут и свойство могут по-разному описывать исходное и текущее состояние.
- Браузер объединяет записи в DOM, но чтение геометрии может принудительно обновить layout.
- Layout thrashing возникает из-за повторного чтения после записи, а не просто из-за количества строк DOM-кода.
- Удалённый узел освобождается только после исчезновения всех сильных путей удержания.

## Связанные темы

- [DOM events](<./DOM events.md>)
- [Observer APIs](<./Observer APIs.md>)
- [requestAnimationFrame и requestIdleCallback](<./requestAnimationFrame и requestIdleCallback.md>)
- [Rendering pipeline reflow repaint composite](<../../Конспект для подготовки/Browser Internals/Rendering pipeline reflow repaint composite.md>)
- [XSS](<../../Конспект для подготовки/Web Basics/XSS.md>)
- [CSP и security headers](<../../Конспект для подготовки/Web Basics/CSP и security headers.md>)

## Источники

- [WHATWG DOM Standard](https://dom.spec.whatwg.org/)
- [WHATWG HTML Standard: Dynamic markup insertion](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html)
- [MDN: Document Object Model](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)
- [web.dev: Avoid large, complex layouts and layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Debounce и throttle](<./Debounce и throttle.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [DOM events →](<./DOM events.md>)
<!-- NOTE-NAV-BOTTOM:END -->
