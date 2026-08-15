# Vue

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./01 Options API и Composition API.md>)

Заметок в разделе: **6**
<!-- SECTION-NAV:END -->

## Темы

- [Options API и Composition API](<./01 Options API и Composition API.md>)
- [Реактивность](<./02 Реактивность.md>)
- [Виртуальный DOM](<./03 Виртуальный DOM.md>)
- [Слоты](<./04 Слоты.md>)
- [Жизненный цикл](<./05 Жизненный цикл.md>)
- [Proxy](<./06 Proxy.md>)

## Маршрут

1. Начать с двух способов описания компонента и понять, почему Composition API упрощает feature-based organization и composables.
2. Разобрать публичную модель реактивности: `ref`, `reactive`, `computed`, `watch`, scheduler и `nextTick`.
3. Углубиться в Proxy как механизм reactive objects: traps, identity, raw mutations и границы деструктурирования.
4. Проследить rendering pipeline от template compiler и render effect до VNode patch и DOM.
5. Разобрать slots как контракт композиции между parent и child, включая lexical scope и scoped slot props.
6. Завершить lifecycle: момент регистрации hooks, DOM timing, cleanup, `<KeepAlive>` и SSR.

Версионная база раздела - Vue 3. Options API остаётся поддерживаемым, а для новых Single-File Components основной путь в документации - Composition API с `<script setup>`.
