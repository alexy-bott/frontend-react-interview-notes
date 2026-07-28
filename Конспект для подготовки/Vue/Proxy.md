---
aliases:
  - Vue Proxy
  - Proxy
  - Vue 3 Proxy
---

#### Ответ на 60 секунд

В Vue 3 реактивность построена вокруг JavaScript `Proxy`. Proxy оборачивает объект и перехватывает операции чтения и записи через traps вроде `get` и `set`. Когда компонент читает реактивное свойство, Vue запоминает зависимость. Когда свойство изменяется, Vue уведомляет связанные эффекты и планирует обновление компонента.

В Vue 2 реактивность строилась через `Object.defineProperty`, из-за чего были ограничения с добавлением новых свойств и массивами. Proxy в Vue 3 позволяет отслеживать больше операций естественнее: добавление, удаление, проверку наличия ключей, работу с коллекциями. При этом Proxy не равен исходному объекту по ссылке, поэтому важно не смешивать raw object и reactive proxy без необходимости.

#### Ключевая схема

| Операция | Что делает Vue |
| --- | --- |
| `get` | отслеживает зависимость |
| `set` | триггерит обновления |
| `deleteProperty` | реагирует на удаление |
| `has` / `ownKeys` | отслеживает `in`, keys, iteration |
| `reactive()` | создает proxy-объект |
| `ref()` | контейнер с `.value` |

#### Развернутый ответ

**Чем Proxy отличается от `Object.defineProperty`?**

Proxy может перехватывать больше операций на объекте целиком, включая добавление и удаление свойств. `Object.defineProperty` работает на уровне уже известных свойств и требует более сложных обходных решений.

**Почему `reactive(obj) !== obj`?**

`reactive` возвращает proxy-обертку, а не мутирует исходный объект в тот же самый reference. Поэтому сравнение по ссылке с raw object может дать неожиданный результат.

**Чем `reactive` отличается от `ref`?**

`reactive` обычно используют для объектов. `ref` используют для примитивов и случаев, когда нужна реактивная ссылка на значение. В JavaScript коде значение `ref` читается через `.value`, а в шаблоне Vue автоматически разворачивает ref.

#### Пример

```js
import { reactive, effect } from "vue";

const state = reactive({
  count: 0,
});

effect(() => {
  console.log(state.count);
});

state.count += 1;
```

При чтении `state.count` Vue запоминает зависимость, а при записи запускает связанный effect.

#### Частые ошибки

- Сравнивать proxy и исходный объект по ссылке.
- Деструктурировать reactive object и терять реактивность без `toRefs`.
- Забывать `.value` у `ref` в JavaScript-коде.
- Считать, что Proxy делает глубокую магию без ограничений.
- Мутировать raw object вместо reactive proxy.

#### Связанные темы

- [[Конспект для подготовки/Vue/Реактивность]]
- [[Конспект для подготовки/Vue/Options API и Composition API]]
- [[Конспект для подготовки/JavaScript/Prototype]]
- [[Конспект для подготовки/JavaScript/Проверка свойств объекта]]

#### Источники

- [Vue Docs: Reactivity in Depth](https://vuejs.org/guide/extras/reactivity-in-depth.html)
- [Vue Docs: Reactivity API Core](https://vuejs.org/api/reactivity-core.html)
- [MDN: Proxy](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy)
