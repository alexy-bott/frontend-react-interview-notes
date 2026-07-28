---
aliases:
  - Options API и Composition API
  - Options API
  - Composition API
  - script setup
---

#### Ответ на 60 секунд

Options API и Composition API - это два способа писать компоненты Vue. В Options API код группируется по опциям: `data`, `methods`, `computed`, `watch`, lifecycle hooks. Это удобно для простых компонентов и для чтения legacy-кода. В Composition API логика собирается внутри `setup()` или `<script setup>` и группируется по фичам: состояние, computed, watchers, lifecycle hooks и функции одной бизнес-задачи лежат рядом.

Главное преимущество Composition API не в производительности, а в архитектуре. Когда компонент растёт, Options API разносит одну фичу по разным секциям, а Composition API позволяет вынести её в composable вроде `useUserSearch()` с явным входом и выходом. Такой код проще масштабировать, тестировать и типизировать в TypeScript, потому что меньше магии вокруг `this`.

На практике в новых Vue 3 проектах чаще выбирают Composition API с `<script setup>`. Options API не является “неправильным”: он остаётся поддерживаемым и нормален для простых или старых компонентов. Миксины в новом коде обычно заменяют composables, потому что у composable явнее зависимости, меньше конфликтов имён и понятнее контракт.

#### Ключевая схема

| Критерий | Options API | Composition API |
| --- | --- | --- |
| Группировка | по типам опций | по фичам |
| Переиспользование | mixins, extends | composables |
| TypeScript | больше ограничений из-за `this` | точнее inference |
| Новые проекты Vue 3 | можно, но реже | чаще основной выбор |
| Legacy-код | часто встречается | постепенно добавляется |

#### Развернутый ответ

**Options API**

```vue
<script>
export default {
  data() {
    return {
      count: 0,
    };
  },

  computed: {
    doubled() {
      return this.count * 2;
    },
  },

  methods: {
    inc() {
      this.count += 1;
    },
  },
};
</script>
```

Здесь структура понятна, пока компонент небольшой. Когда фич становится много, связанный код оказывается разбросан по разным опциям.

**Composition API**

```vue
<script setup>
import { computed, ref } from "vue";

const count = ref(0);
const doubled = computed(() => count.value * 2);

function inc() {
  count.value += 1;
}
</script>
```

Логика одной фичи находится рядом и может быть вынесена в composable.

**Composable вместо mixin**

```ts
import { computed, ref } from "vue";

export function useCounter(start = 0) {
  const count = ref(start);
  const doubled = computed(() => count.value * 2);

  function inc() {
    count.value += 1;
  }

  return {
    count,
    doubled,
    inc,
  };
}
```

У composable явный API: видно, что он принимает и что возвращает. У mixin зависимости часто скрыты внутри компонента.

**`<script setup>`**

`<script setup>` - синтаксический сахар для Composition API в Single File Components. Top-level переменные и функции автоматически доступны в template, а код получается короче, чем ручной `setup() { return ... }`.

**`this`**

В Composition API внутри `setup` нет компонентного `this`. Это осознанная модель: зависимости берутся из closure, импортов и возвращаемых значений. Для TypeScript это обычно проще и предсказуемее.

#### Частые ошибки

- Считать, что Composition API заменяет Options API из-за скорости runtime.
- Механически переносить Options API в `setup`, не группируя код по фичам.
- Искать `this` внутри `setup`.
- Возвращать из обычного `setup()` всё подряд, даже если template это не использует.
- Делать composable со скрытыми глобальными зависимостями и неявными побочными эффектами.
- Забывать `.value` у `ref` в JavaScript-коде.

#### Связанные темы

- [[Конспект для подготовки/Vue/Реактивность]]
- [[Конспект для подготовки/Vue/Lifecycle]]
- [[Конспект для подготовки/Vue/Proxy]]
- [[Конспект для подготовки/TypeScript/Generics]]

#### Источники

- [Vue: Composition API FAQ](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Vue: Reactivity Fundamentals](https://vuejs.org/guide/essentials/reactivity-fundamentals.html)
