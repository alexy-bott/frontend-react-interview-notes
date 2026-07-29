---
aliases:
  - Lifecycle
  - lifecycle hooks
  - жизненный цикл Vue
---

#### Быстрый ответ

Экземпляр Vue-компонента создаёт reactive state и render effect, монтирует DOM, обновляет его при изменении зависимостей и в конце размонтируется. Composition API подключается к этим этапам через `onMounted`, `onUpdated`, `onBeforeUnmount`, `onUnmounted` и другие hooks; Options API предоставляет соответствующие options `mounted`, `updated`, `beforeUnmount`, `unmounted`.

Состояние, computed и watchers создают в `setup`; DOM refs и browser-only integrations используют после mount; внешние listeners, timers, connections и observers очищают при unmount. DOM updates батчатся, поэтому после изменения state актуальный DOM читают через `nextTick` или post-flush watcher. Кешируемый `<KeepAlive>` использует activation/deactivation вместо обычного unmount при переключении.

#### Ключевая схема

```text
create instance
-> setup + регистрация effects/hooks
-> beforeMount
-> render + mount DOM
-> mounted
-> reactive update -> render/patch -> updated
-> beforeUnmount
-> stop effects + remove DOM
-> unmounted
```

| Задача | Подходящий этап |
| --- | --- |
| Создать state/computed/watch | `setup` |
| Прочитать template ref | `onMounted` |
| Подключить DOM/third-party library | `onMounted` + cleanup |
| Прочитать DOM после конкретного state update | `await nextTick()` или `watch(..., { flush: "post" })` |
| Освободить внешний ресурс | `onBeforeUnmount`/`onUnmounted` по контракту ресурса |
| Поставить кешируемый экран на паузу | `onDeactivated` |
| Возобновить кешируемый экран | `onActivated` |

#### Базовая модель

`setup()` выполняется до создания DOM компонента. Здесь Vue знает текущий component instance, поэтому lifecycle hooks и watchers, созданные синхронно, связываются с ним. Callback hook выполняется позже на нужной фазе, но зарегистрировать его нужно во время setup.

`onMounted` вызывается после создания DOM tree компонента, mount всех синхронных child components и вставки дерева в parent container. Async components и descendants внутри `<Suspense>` могут ещё не быть готовы. Template ref становится доступен после mount, но это не означает, что все изображения загрузились или layout стабилизировался.

При изменении реактивной зависимости Vue планирует update, а не patch-ит DOM после каждой записи. `onUpdated` вызывается после DOM update компонента, но не сообщает, какое state вызвало его. Для реакции на конкретное значение используют `watch`; для одного imperative действия после собственной записи - `nextTick`.

#### Развернутый ответ

**Cleanup.** Vue останавливает render effect и watchers, синхронно созданные в setup, при unmount. Browser listeners, `setInterval`, WebSocket, `ResizeObserver` и сторонние instances Vue не может очистить автоматически. Owner, который создаёт ресурс, регистрирует его disposal рядом.

**Async-created watchers.** Watcher, созданный асинхронно после setup, может не быть автоматически привязан к component instance. Обычно watcher создают синхронно и условие помещают внутрь callback; если это невозможно, явно вызывают stop handle.

**`onBeforeUnmount` и `onUnmounted`.** В before-hook instance и DOM ещё полностью функциональны, поэтому можно снять snapshot или уведомить библиотеку до удаления nodes. В unmounted DOM уже удалён, child components размонтированы и reactive effects остановлены; этот этап подходит окончательному освобождению внешних ресурсов.

**KeepAlive.** Кешируемый component instance при переключении удаляется из активного DOM, но не уничтожается. Его interval или realtime subscription продолжит работать, если cleanup находится только в `onUnmounted`. `onDeactivated` ставит работу на паузу, `onActivated` синхронизирует данные и возобновляет её.

**SSR.** Mount/update/unmount hooks не выполняются во время server rendering, потому что сервер не создаёт browser DOM. Для server data dependency существует `onServerPrefetch`; обращения к `window`, DOM и browser APIs размещают в client-only path.

**Update loops.** Безусловная запись reactive state в `onUpdated` запускает следующий update и может создать цикл. Производное значение вычисляют через `computed`, а измерение DOM обновляет state только при реальном изменении и с защитой от повторов.

#### Пример

```vue
<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from "vue";

const buttonRef = ref<HTMLButtonElement | null>(null);
const expanded = ref(false);

function onResize() {
  // Считать viewport и обновить только действительно зависящий state.
}

onMounted(() => {
  window.addEventListener("resize", onResize);
  buttonRef.value?.focus();
});

onUnmounted(() => {
  window.removeEventListener("resize", onResize);
});

async function expand() {
  expanded.value = true;
  await nextTick();
  // DOM ветки v-if уже создан, теперь его можно измерить.
}
</script>

<template>
  <button ref="buttonRef" type="button" @click="expand">Подробнее</button>
  <section v-if="expanded">Дополнительная информация</section>
</template>
```

Listener принадлежит lifecycle компонента и удаляется при unmount. `nextTick` нужен не для изменения state, а только для операции, зависящей от уже применённого DOM patch.

#### Ключевые уточнения

- Lifecycle hook регистрируется синхронно в setup, а его callback выполняется позже на соответствующей фазе.
- `onMounted` означает готовность DOM данного компонента и синхронных children, но не завершение всех async descendants и загрузки ресурсов.
- Для реакции на конкретную dependency используют `watch`, а не общий `onUpdated`.
- Vue автоматически останавливает связанные reactive effects, но не может закрыть произвольный внешний browser resource.
- `<KeepAlive>` меняет lifecycle: деактивация не равна unmount и требует отдельной политики паузы.

#### Связанные темы

- [[Конспект для подготовки/Vue/Реактивность]]
- [[Конспект для подготовки/Vue/Options API и Composition API]]
- [[Конспект для подготовки/Vue/Virtual DOM]]
- [[Конспект для подготовки/JavaScript/AbortController]]
- [[Конспект для подготовки/JavaScript/Event Loop]]

#### Источники

- [Vue: Lifecycle Hooks](https://vuejs.org/guide/essentials/lifecycle.html)
- [Vue: Composition API Lifecycle Hooks](https://vuejs.org/api/composition-api-lifecycle.html)
- [Vue: KeepAlive](https://vuejs.org/guide/built-ins/keep-alive.html)
- [Vue: Server-Side Rendering](https://vuejs.org/guide/scaling-up/ssr.html)
