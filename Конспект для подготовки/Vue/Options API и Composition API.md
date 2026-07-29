---
aliases:
  - Options API и Composition API
  - Options API
  - Composition API
  - script setup
---

#### Быстрый ответ

Options API и Composition API - два поддерживаемых способа описывать компоненты Vue 3. Options API группирует код по типам опций: `data`, `computed`, `methods`, `watch` и lifecycle hooks. Composition API использует импортируемые функции внутри `setup()` или `<script setup>` и позволяет располагать рядом состояние, вычисления и эффекты одной feature.

Options API удобен предсказуемой структурой небольших компонентов и часто встречается в существующем коде. Composition API лучше масштабирует сложную связанную логику, переиспользуется через composables и естественнее типизируется TypeScript без компонентного `this`. Для новых Single-File Components официальная документация рекомендует Composition API с `<script setup>`, но Options API не объявлен устаревшим.

#### Ключевая схема

| Критерий | Options API | Composition API |
| --- | --- | --- |
| Организация | по типам опций | по связанным features |
| Переиспользование логики | mixins и функции вне компонента | composables с явным контрактом |
| Доступ к экземпляру | через `this` | переменные и closures внутри `setup` |
| TypeScript inference | сложнее для `this`, mixins и inject | опирается на обычные функции и типы |
| Основной Vue 3 SFC-стиль | поддерживается | `<script setup>` рекомендуется docs |

#### Базовая модель

Оба API используют одну систему компонентов и реактивности. Options API в Vue 3 реализован поверх Composition API, поэтому выбор не меняет саму модель обновления DOM. Отличаются способ объявления зависимостей, организация кода и возможности повторного использования логики.

`setup()` выполняется один раз для каждого экземпляра компонента до mount. Внутри него нет компонентного `this`: props передаются аргументом, context содержит `attrs`, `slots`, `emit` и `expose`, а bindings возвращаются в template. `<script setup>` компилируется в `setup()` и автоматически делает top-level bindings доступными template.

Composable - функция, которая использует Composition API для инкапсуляции stateful-логики, например `useUserSearch()`. Её входы и возвращаемые значения видны в месте вызова. Mixin объединяет options неявно и может создавать конфликты имён или скрытые зависимости от полей компонента.

#### Развернутый ответ

**Выбор API.** Для небольшого компонента Options API может быть проще: разработчик сразу знает, где искать methods и computed. Когда одна feature размазывается между `data`, `computed`, `watch` и hooks, Composition API позволяет собрать её в одном блоке и затем вынести в composable.

**`<script setup>`.** Это compile-time syntax, а не отдельный runtime API. Макросы `defineProps`, `defineEmits`, `defineExpose` и другие обрабатываются compiler и не импортируются из `vue`. Компоненты и функции, импортированные на верхнем уровне, доступны template напрямую.

**TypeScript.** В Composition API значения имеют типы обычных переменных и функций. Options API тоже поддерживает TypeScript, но inference усложняется вокруг `this`, mixins и dependency injection. Это преимущество модели, а не запрет использовать Options API с TS.

**Производительность.** Главная причина выбора Composition API - организация и reuse. При этом Vue docs отмечают, что `<script setup>` может создавать более эффективный и лучше минифицируемый output: template обращается к переменным напрямую, без instance proxy. Это возможное дополнительное преимущество, а не основание переписывать работающий компонент без измерения.

**Смешивание.** Composition API можно вызвать через опцию `setup` внутри Options API-компонента, что полезно при постепенной миграции. Новый код не стоит без причины делить между обоими стилями: связанные данные становятся сложнее искать, а значения из Options API недоступны через `this` внутри `setup`.

#### Пример

Одна feature счётчика собрана рядом и может быть вынесена в composable:

```vue
<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  initialValue?: number;
}>();

const emit = defineEmits<{
  change: [value: number];
}>();

const count = ref(props.initialValue ?? 0);
const doubled = computed(() => count.value * 2);

function increment() {
  count.value += 1;
  emit("change", count.value);
}
</script>

<template>
  <button type="button" @click="increment">
    {{ count }} / {{ doubled }}
  </button>
</template>
```

В JavaScript-коде `ref` читается через `.value`, а в template top-level ref автоматически разворачивается. `defineProps` и `defineEmits` задают входной и выходной контракт компонента.

#### Версии и совместимость

Composition API встроен в Vue 3 и Vue 2.7; для более ранних Vue 2 использовался отдельный plugin. `<script setup>` требует Single-File Component build pipeline. Конкретные возможности compiler macros зависят от minor-версии Vue, поэтому при поддержке старого проекта их сверяют с установленной версией.

#### Ключевые уточнения

- Options API и Composition API являются двумя интерфейсами к одной системе Vue 3; Composition API не заменяет renderer и реактивность другой реализацией.
- Composition API улучшает организацию только при группировке по feature. Механический перенос всех `data`, затем всех computed и methods сохраняет прежнюю проблему.
- `setup()` и `<script setup>` не имеют компонентного `this`; зависимости должны быть явными переменными, аргументами и imports.
- Composable полезен явным входом, выходом и lifecycle; скрытая запись в global state делает его контракт таким же неочевидным, как неудачный mixin.
- Options API остаётся поддерживаемым и может быть разумным выбором для небольшого или существующего компонента.

#### Связанные темы

- [[Конспект для подготовки/Vue/Реактивность]]
- [[Конспект для подготовки/Vue/Lifecycle]]
- [[Конспект для подготовки/Vue/Proxy]]
- [[Конспект для подготовки/TypeScript/Generics]]

#### Источники

- [Vue: Composition API FAQ](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Vue: setup](https://vuejs.org/api/composition-api-setup.html)
- [Vue: TypeScript with Composition API](https://vuejs.org/guide/typescript/composition-api.html)
