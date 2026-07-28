---
aliases:
  - Virtual DOM
  - Vue VDOM
  - VNode
  - patch flags
---

#### Ответ на 60 секунд

Во Vue шаблон компилируется в render function, которая возвращает дерево VNode - обычных JavaScript-объектов с типом узла, props, children и key. При первом render Vue монтирует VNode в настоящий DOM. Когда реактивные зависимости меняются, render function запускается снова, создаёт новое VNode-дерево, а renderer сравнивает новое дерево со старым и применяет минимальные нужные DOM-операции. Этот процесс называется patch или diffing.

Vue 3 важен тем, что его Virtual DOM не полностью “слепой” runtime. Компилятор шаблонов заранее помечает динамические части через patch flags, кеширует статические узлы и строит block tree. Поэтому runtime может не обходить всё дерево одинаково на каждом обновлении, а фокусироваться на местах, где действительно есть динамика.

Для списков ключевую роль играет `key`. Он связывает старые и новые VNode между собой. Без стабильного `key` Vue может переиспользовать DOM по позиции, из-за чего ломаются состояния input-ов, анимации и порядок элементов. Индекс массива как `key` подходит только для статичных списков без вставок, удаления и сортировки.

#### Ключевая схема

```text
template
-> render function
-> VNode tree
-> mount to DOM
-> reactive update
-> new VNode tree
-> patch old vs new
-> targeted DOM operations
```

| Понятие | Роль |
| --- | --- |
| VNode | описание будущего DOM-узла |
| render function | создаёт VNode-дерево |
| patch | сравнивает старое и новое дерево |
| `key` | связывает элементы списка между render-ами |
| patch flags | подсказки компилятора о динамических частях |
| block tree | группировка динамических узлов для более быстрого update |

#### Развернутый ответ

**Render pipeline**

При mount Vue компилирует template в render function, вызывает её, получает VNode и создаёт DOM. Render компонента выполняется как reactive effect, поэтому Vue знает, какие reactive values были прочитаны. При изменении этих values эффект планируется заново, создаётся новое VNode-дерево, и renderer делает patch.

**Templates и render functions**

Templates обычно предпочтительны в приложениях: они ближе к HTML, легче читаются, хорошо сочетаются с доступностью и позволяют компилятору Vue применить оптимизации. Render functions нужны для очень динамических компонентов, библиотек и низкоуровневой композиции.

**Patch flags**

Patch flags - это подсказки, которые compiler добавляет к VNode. Например, если у элемента динамический только `class`, runtime может обновлять именно class, а не заново проверять всё подряд.

**Static hoisting**

Если часть template статична, compiler может вынести её так, чтобы VNode не пересоздавался на каждом render и не участвовал в обычном diff.

**`key`**

`key` должен быть стабильным идентификатором сущности: id из данных, slug, уникальный ключ. Индекс массива ломает сопоставление при сортировке, вставках и удалениях, потому что индекс описывает позицию, а не саму сущность.

#### Пример

```vue
<script setup>
import { ref } from "vue";

const items = ref([
  { id: 1, title: "One" },
  { id: 2, title: "Two" },
]);

function reverse() {
  items.value = [...items.value].reverse();
}
</script>

<template>
  <button @click="reverse">Reverse</button>

  <ul>
    <li v-for="item in items" :key="item.id">
      {{ item.title }}
    </li>
  </ul>
</template>
```

`key` помогает Vue понять, что элементы поменялись местами, а не стали другими сущностями.

#### Частые ошибки

- Не ставить `key` в динамических списках.
- Использовать индекс массива как `key` для сортируемого или изменяемого списка.
- Думать, что Virtual DOM всегда означает полный diff всего дерева.
- Мутировать DOM вручную там, где Vue должен управлять им через render.
- Путать Vue patching с React reconciliation один к одному: идея похожа, но оптимизации и compiler hints отличаются.

#### Связанные темы

- [[Конспект для подготовки/Vue/Реактивность]]
- [[Конспект для подготовки/Vue/Slots]]
- [[Конспект для подготовки/Vue/Lifecycle]]
- [[Конспект для подготовки/React/Reconciliation]]

#### Источники

- [Vue: Rendering Mechanism](https://vuejs.org/guide/extras/rendering-mechanism.html)
- [Vue: key special attribute](https://vuejs.org/api/built-in-special-attributes.html#key)
