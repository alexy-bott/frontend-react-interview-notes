# Виртуальный DOM

<!-- NOTE-NAV-TOP:START -->
[← Реактивность](<./02 Реактивность.md>) · [↑ Vue](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Слоты →](<./04 Слоты.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Virtual DOM во Vue - дерево Virtual Nodes (VNode), которое описывает желаемый UI обычными JavaScript-объектами. Template компилируется в render function; при mount renderer создаёт реальные DOM nodes, а при изменении прочитанных реактивных зависимостей снова вызывает render function и выполняет patch старого и нового VNode-деревьев.

Vue 3 использует compiler-informed Virtual DOM. Compiler заранее выделяет статические части, добавляет patch flags для динамических bindings и строит blocks с динамическими descendants. Поэтому runtime не обязан одинаково обходить всё template на каждом update. `key` задаёт identity узла между renders и особенно важен для перестановок, вставок и удаления элементов списка.

## Ключевая схема

```text
template
-> compile
-> render function
-> VNode tree
-> mount DOM

reactive dependency changes
-> scheduled render effect
-> new VNode tree
-> patch old/new
-> необходимые DOM updates
```

| Понятие | Роль |
| --- | --- |
| VNode | описание element, component, text или fragment |
| Render function | создаёт VNode tree из текущего state |
| Mount | создаёт host nodes из первого дерева |
| Patch | сопоставляет старые и новые VNodes и обновляет host environment |
| Patch flag | compile-time подсказка о типе динамического binding |
| Block tree | плоский список динамических descendants внутри стабильной структуры |
| `key` | identity sibling VNode между renders |

## Базовая модель

Render компонента является reactive effect. Во время его выполнения Vue отслеживает прочитанные reactive values. Их изменение планирует повторный render этого компонента, создающий новое описание UI. Renderer сравнивает VNodes того же уровня и применяет необходимые операции к DOM.

Patch не ищет математически минимальный набор операций для произвольных деревьев. Он использует предсказуемые эвристики и identity по `type`/`key`, чтобы достаточно быстро получить правильный DOM. Стабильные keys позволяют распознать перемещённую сущность; позиционные keys сообщают только новое положение.

Template compiler видит, что в `<div :class="active">Text</div>` динамичен только `class`, и добавляет соответствующий patch flag. Полностью статичные узлы hoist-ятся или объединяются, а tree flattening позволяет обходить динамические descendants, пропуская стабильные ветки.

## Развернутый ответ

**Compile.** Single-File Component обычно компилируется во время build. При использовании runtime compiler template может компилироваться в browser. Предварительная компиляция уменьшает client work и позволяет поставлять runtime-only build.

**Mount и update.** При первом render старого дерева нет, поэтому renderer создаёт DOM и устанавливает props/listeners. При update VNode того же типа и key переиспользует host element и получает изменённые props/children. Другой type или key приводит к замене соответствующей ветки.

**Списки.** Без `key` Vue по умолчанию применяет in-place patch по позиции, что эффективно для простого вывода без локального состояния. Если строки содержат inputs, component state, transitions или меняют порядок, нужен стабильный primitive key из данных. Индекс массива не сохраняет identity сущности после insertion или sort.

**Templates и render functions.** Template предпочтителен для обычной разметки: он близок к HTML и даёт compiler больше статической информации. Render functions/JSX нужны библиотекам и действительно динамической структуре, но уменьшают часть compile-time guarantees и требуют явного создания VNodes.

**Hydration.** При SSR browser получает существующий HTML, а Vue сопоставляет его с client VNode tree и подключает интерактивность. Несовпадение server/client output вызывает hydration mismatch и может потребовать исправления DOM. Patch flags и block tree также ускоряют этот проход.

**Прямые DOM mutations.** DOM, которым владеет Vue, должен отражать template/state. Ручная перестановка его children не изменяет VNode tree и может быть перезаписана следующим patch. Imperative library изолируют за component boundary и управляют через lifecycle hooks.

## Пример

```vue
<script setup lang="ts">
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
  <button type="button" @click="reverse">Reverse</button>

  <ul>
    <li v-for="item in items" :key="item.id">
      <label>
        {{ item.title }}
        <input :name="`note-${item.id}`">
      </label>
    </li>
  </ul>
</template>
```

После reverse key связывает DOM/component identity с `item.id`, поэтому введённое значение остаётся у той же сущности, а не у прежней позиции списка.

## Ключевые уточнения

- Реактивность определяет, когда компоненту нужен update; Virtual DOM определяет, как следующее описание применить к host environment.
- Patch выполняет необходимые обновления по правилам renderer, но не гарантирует математически минимальный diff.
- Vue 3 сочетает runtime diff с compile-time информацией, поэтому модель «полный обход всего дерева при каждом update» неточна.
- `key` описывает identity, а не только устраняет warning. Стабильный id нужен там, где элементы переживают reorder или имеют локальное состояние.
- Virtual DOM не делает любой render дешёвым: большой список всё ещё создаёт VNodes и DOM, поэтому может потребоваться virtualization.

## Связанные темы

- [Реактивность](<./02 Реактивность.md>)
- [Слоты](<./04 Слоты.md>)
- [Жизненный цикл](<./05 Жизненный цикл.md>)
- [Согласование (Reconciliation)](<../React/04 Согласование (Reconciliation).md>)

## Источники

- [Vue: Rendering Mechanism](https://vuejs.org/guide/extras/rendering-mechanism.html)
- [Vue: key special attribute](https://vuejs.org/api/built-in-special-attributes.html#key)
- [Vue: List Rendering](https://vuejs.org/guide/essentials/list.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Реактивность](<./02 Реактивность.md>) · [↑ Vue](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Слоты →](<./04 Слоты.md>)
<!-- NOTE-NAV-BOTTOM:END -->
