---
aliases:
  - Vue Proxy
  - Proxy
  - Vue 3 Proxy
---

#### Быстрый ответ

Vue 3 использует JavaScript `Proxy` для реактивных объектов. `reactive(rawObject)` возвращает обёртку, которая перехватывает чтение, запись, удаление, проверку ключа и перебор свойств. Во время чтения Vue связывает текущий effect со свойством, а во время изменения уведомляет только зависимости, которых касается операция.

Proxy решает ограничения Vue 2 вокруг добавления свойств, массивов и коллекций, но не делает реактивной любую переменную. Он наблюдает операции, проходящие через Proxy: деструктурированное примитивное значение и мутация исходного raw object обходят traps. Кроме того, Proxy и raw object имеют разные ссылки, что важно для сравнений и ключей Map/Set.

#### Ключевая схема

```text
raw object
-> reactive(raw)
-> Proxy
   get/has/ownKeys -> track
   set/delete       -> trigger
-> scheduler reactive effects
```

| Операция JavaScript | Что может отслеживать Vue |
| --- | --- |
| `proxy.key` | чтение конкретного property |
| `proxy.key = value` | добавление или изменение property |
| `delete proxy.key` | удаление property |
| `key in proxy` | проверку наличия |
| `Object.keys(proxy)` / iteration | изменение набора keys |
| `map.get()` / `set.add()` | операции поддерживаемых коллекций через instrumentation |

#### Базовая модель

Proxy - отдельный объект-посредник с traps. Vue хранит структуру зависимостей примерно как «target -> key -> effects». Если effect прочитал `state.count`, изменение `state.name` само по себе не требует запускать именно эту зависимость; изменение `count` выполняет trigger для подписанных effects.

Nested object становится reactive при доступе через глубокий reactive Proxy. Vue возвращает для него собственный Proxy и кеширует соответствие, поэтому повторный `reactive(raw)` обычно возвращает тот же Proxy, а вызов `reactive(proxy)` возвращает сам Proxy.

`ref` использует getter/setter свойства `.value`, а не JavaScript Proxy для самого контейнера. Благодаря контейнеру Vue может отслеживать замену примитива или целого объекта, чего нельзя сделать с простой локальной переменной.

#### Развернутый ответ

**Identity.** `reactive(raw) !== raw`, хотя оба представляют одни данные. Если raw object помещён в `Set`, поиск по Proxy не совпадёт. Для сущностей приложения надёжнее использовать `id`; смешивание raw/proxy identity оставляют только для осознанной интеграции.

**Raw mutation.** После `const state = reactive(raw)` запись `raw.count++` не проходит через Proxy и не запускает effects. Данные при следующем чтении через Proxy могут уже иметь новое значение, но автоматического update в момент raw mutation не было.

**Деструктурирование.** `const { count } = state` вызывает `get` один раз и кладёт число в локальную переменную. Дальнейшее чтение `count` не проходит через Proxy. `toRef(state, "count")` сохраняет связь через `.value`.

**Коллекции.** `Map`, `Set`, `WeakMap` и `WeakSet` требуют не только обычных property traps, поэтому Vue применяет специальные instrumentations к их методам. Реактивность коллекций не означает, что каждое произвольное внутреннее состояние экземпляра стороннего класса безопасно proxy-фицировать.

**Выход из глубокой реактивности.** `shallowReactive`, `shallowRef` и `markRaw` применяют для интеграции с внешним state, тяжёлыми immutable structures или class instances. Они создают смешанное дерево с другими правилами вложенности, поэтому относятся к точечным advanced-инструментам, а не к общей оптимизации.

#### Пример

```js
import { reactive, toRef, watchEffect } from "vue";

const raw = { count: 0 };
const state = reactive(raw);
const count = toRef(state, "count");

watchEffect(() => {
  console.log("count:", count.value);
});

state.count += 1; // проходит через Proxy и повторяет effect
raw.count += 1;   // обходит Proxy и само по себе effect не запускает
```

Пример использует публичный `watchEffect`, а не внутренний низкоуровневый effect. После raw mutation следует снова читать данные через `state`; постоянное хранение и изменение обеих ссылок делает поведение неочевидным.

#### Ключевые уточнения

- Proxy отслеживает операции только тогда, когда они проходят через reactive-обёртку.
- `reactive` не изменяет identity исходного объекта: raw и Proxy нельзя бездумно смешивать в reference comparisons.
- Глубокая реактивность создаёт вложенные proxies по мере доступа, но не делает реактивным извлечённый примитив.
- `ref` и `reactive` используют разные interception-механизмы и дополняют друг друга.
- `toRaw`, `markRaw` и shallow APIs нужны интеграционным границам; длительная работа одновременно с raw и Proxy повышает риск identity bugs.

#### Связанные темы

- [[Конспект для подготовки/Vue/Реактивность]]
- [[Конспект для подготовки/Vue/Options API и Composition API]]
- [[Конспект для подготовки/JavaScript/Prototype]]
- [[Конспект для подготовки/JavaScript/Проверка свойств объекта]]

#### Источники

- [Vue: Reactivity in Depth](https://vuejs.org/guide/extras/reactivity-in-depth.html)
- [Vue: Reactivity API - Core](https://vuejs.org/api/reactivity-core.html)
- [Vue: Reactivity API - Advanced](https://vuejs.org/api/reactivity-advanced.html)
- [MDN: Proxy](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy)
