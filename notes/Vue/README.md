# Vue

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Options API и Composition API.md>)

Заметок в разделе: **6**
<!-- SECTION-NAV:END -->

## Темы

- [Options API и Composition API](<./Options API и Composition API.md>)
- [Реактивность](<./Реактивность.md>)
- [Virtual DOM](<./Virtual DOM.md>)
- [Slots](<./Slots.md>)
- [Lifecycle](<./Lifecycle.md>)
- [Proxy](<./Proxy.md>)

## Маршрут

1. Начать с двух способов описания компонента и понять, почему Composition API упрощает feature-based organization и composables.
2. Разобрать публичную модель реактивности: `ref`, `reactive`, `computed`, `watch`, scheduler и `nextTick`.
3. Углубиться в Proxy как механизм reactive objects: traps, identity, raw mutations и границы деструктурирования.
4. Проследить rendering pipeline от template compiler и render effect до VNode patch и DOM.
5. Разобрать slots как контракт композиции между parent и child, включая lexical scope и scoped slot props.
6. Завершить lifecycle: момент регистрации hooks, DOM timing, cleanup, `<KeepAlive>` и SSR.

Версионная база раздела - Vue 3. Options API остаётся поддерживаемым, а для новых Single-File Components основной путь в документации - Composition API с `<script setup>`.
