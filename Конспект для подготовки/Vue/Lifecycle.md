---
aliases:
  - Lifecycle
  - lifecycle hooks
  - жизненный цикл Vue
---

#### Ответ на 60 секунд

Компонент Vue проходит фазы создания, монтирования, обновления и размонтирования. В Options API для этого есть хуки вроде `created`, `mounted`, `updated`, `beforeUnmount` и `unmounted`. В Composition API их аналоги вызывают из `setup`: `onMounted`, `onUpdated`, `onBeforeUnmount`, `onUnmounted` и другие. В `setup` нет `this`, поэтому состояние и функции берутся из замыканий, `ref`, `reactive` и composables.

Практически правило такое: синхронную подготовку данных можно делать в `setup`, работу с DOM и browser APIs - в `onMounted`, реакции на обновление DOM - в `onUpdated` или через watcher с `flush: "post"`, очистку подписок, таймеров и внешних ресурсов - в `onBeforeUnmount` или `onUnmounted`. Если компонент кэшируется через `<KeepAlive>`, он не всегда размонтируется, поэтому для паузы и возобновления используют `onDeactivated` и `onActivated`.

Если после изменения состояния нужен уже обновлённый DOM, используют `nextTick`. Это важно, потому что Vue батчит reactive updates и применяет DOM patch асинхронно относительно текущего синхронного кода.

#### Ключевая схема

| Фаза | Options API | Composition API | Что делать |
| --- | --- | --- | --- |
| setup/create | `beforeCreate`, `created` | `setup()` | создать state, computed, watchers |
| before mount | `beforeMount` | `onBeforeMount` | редко нужен |
| mounted | `mounted` | `onMounted` | DOM refs, subscriptions, timers |
| before update | `beforeUpdate` | `onBeforeUpdate` | snapshot до DOM patch |
| updated | `updated` | `onUpdated` | работа после DOM patch |
| before unmount | `beforeUnmount` | `onBeforeUnmount` | подготовка очистки |
| unmounted | `unmounted` | `onUnmounted` | очистить внешние ресурсы |

#### Развернутый ответ

**`setup`**

`setup` выполняется до mount и не имеет доступа к DOM. Здесь удобно создавать реактивное состояние, computed, watchers, функции и подключать composables.

**`onMounted`**

`onMounted` вызывается после того, как DOM компонента создан и вставлен. Здесь можно читать template refs, подключать DOM listeners, запускать timers и интегрировать сторонние библиотеки, которым нужен реальный DOM.

**`onUpdated`**

`onUpdated` вызывается после DOM-обновления компонента. Его не используют для изменения того же состояния без условий, иначе можно получить цикл обновлений. Для реакции на конкретное значение обычно применяют `watch`.

**`onUnmounted`**

`onUnmounted` нужен для очистки: `removeEventListener`, `clearInterval`, abort запросов, отписки от store/event bus/websocket. Если ресурс создан в `onMounted`, рядом должна быть понятная очистка.

**`KeepAlive`**

Компонент внутри `<KeepAlive>` может быть деактивирован, но не размонтирован. Например, таймер или websocket иногда нужно ставить на паузу в `onDeactivated` и возобновлять в `onActivated`.

**SSR**

`onMounted` не выполняется на сервере. Для server-side data prefetch во Vue есть `onServerPrefetch`, а browser-only код нужно держать в client-only хуках.

#### Пример

```vue
<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";

const count = ref(0);
const buttonRef = ref(null);

let timerId = null;

onMounted(async () => {
  timerId = window.setInterval(() => {
    count.value += 1;
  }, 1000);

  await nextTick();
  buttonRef.value?.focus();
});

onBeforeUnmount(() => {
  if (timerId !== null) {
    clearInterval(timerId);
  }
});
</script>

<template>
  <button ref="buttonRef" @click="count++">
    Count: {{ count }}
  </button>
</template>
```

#### Частые ошибки

- Искать `this` внутри `setup`.
- Читать DOM refs до `onMounted`.
- Забывать очистку timers, listeners, subscriptions и запросов.
- Менять состояние внутри `onUpdated` без защиты от циклов.
- Ожидать, что `onMounted` выполнится при SSR.
- Забывать про `onActivated`/`onDeactivated` для `<KeepAlive>`.

#### Связанные темы

- [[Конспект для подготовки/Vue/Реактивность]]
- [[Конспект для подготовки/Vue/Options API и Composition API]]
- [[Конспект для подготовки/JavaScript/AbortController]]
- [[Конспект для подготовки/JavaScript/Event Loop]]

#### Источники

- [Vue: Lifecycle Hooks](https://vuejs.org/guide/essentials/lifecycle.html)
- [Vue: Composition API Lifecycle Hooks](https://vuejs.org/api/composition-api-lifecycle.html)
