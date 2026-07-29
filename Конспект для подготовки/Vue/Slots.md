---
aliases:
  - Slots
  - Vue slots
  - scoped slots
  - named slots
---

#### Быстрый ответ

Slots позволяют родителю передать template fragment в точки, которые определил дочерний компонент. Дочерний компонент управляет каркасом и выводит `<slot>`, а родитель управляет содержимым. Это композиция UI: props передают данные и настройки, slots - произвольную разметку.

Default slot обслуживает основную область, named slots разделяют области вроде header/footer, а scoped slot передаёт данные ребёнка родительскому template через slot props. Содержимое слота компилируется в scope родителя и не видит локальный state ребёнка, если ребёнок явно не передал его через props слота.

#### Ключевая схема

```text
parent определяет slot content
-> передаёт slot function child component
-> child вызывает её в <slot outlet>
-> slot props идут child -> parent template
-> VNodes вставляются в структуру child
```

| Вид | Child outlet | Parent content |
| --- | --- | --- |
| Default | `<slot />` | обычное содержимое компонента |
| Named | `<slot name="header" />` | `<template #header>` |
| Scoped | `<slot :item="item" />` | `<template #default="{ item }">` |
| Fallback | `<slot>Нет данных</slot>` | используется при отсутствии content |

#### Базовая модель

Slot похож на функцию: child вызывает slot и передаёт объект props, а функция возвращает VNodes из template родителя. Такая модель объясняет scope. Выражение `{{ title }}` внутри slot ищет `title` в parent component; получить `childTitle` можно только через `<slot :title="childTitle">` и destructuring slot props у родителя.

Named slots задают контракт областей компонента. `Card` может предоставить `header`, default body и `actions`. Имя должно описывать роль области, а не текущий визуальный placement: `actions` устойчивее, чем `bottomRight`.

Scoped slot полезен для headless-компонента: child владеет данными, выбором или keyboard behavior, но parent решает, как отобразить строку. Если parent должен только передать строку или флаг, обычный prop проще.

#### Развернутый ответ

**Fallback.** Содержимое внутри `<slot>` отображается, если parent не передал соответствующий slot. Это позволяет дать разумный default без проверки в каждом consumer. Наличие named slot можно проверить через `$slots` или `useSlots`, когда от него зависит дополнительная wrapper-разметка.

**Slot props.** Child выбирает контракт и передаёт только необходимые значения и actions. Передача всего внутреннего state наружу связывает parent с реализацией. Для списка достаточно `item`, `index` и, возможно, действия `select(item)`; внутренний cache или refs оставляют закрытыми.

**Props или slot.** Prop подходит данным, enum-варианту, boolean-настройке и callback. Slot нужен, когда consumer должен создать несколько элементов, добавить собственный компонент или контролировать markup. API из десятков узких slots может стать сложнее обычного специализированного компонента.

**Performance и обновления.** Runtime представляет slots функциями, которые child вызывает при render. Это позволяет Vue отслеживать зависимости slot content в подходящем rendering context. Тяжёлая разметка всё равно создаёт VNodes при соответствующих updates; slots не являются автоматической memoization.

**Доступность.** Slot даёт свободу разметки, но child должен объяснять семантический контракт. Если slot `trigger` обязан быть фокусируемой кнопкой, произвольный `div` может сломать компонент. Для сложного headless API используют ограничения, runtime warnings или библиотечные primitives с documented contract.

#### Пример

Child владеет перебором данных и передаёт каждой строке узкий slot contract:

```vue
<!-- UserList.vue -->
<script setup lang="ts">
import type { User } from "./types";

defineProps<{
  users: User[];
}>();
</script>

<template>
  <ul>
    <li v-for="(user, index) in users" :key="user.id">
      <slot name="user" :user="user" :index="index">
        {{ user.name }}
      </slot>
    </li>
  </ul>
</template>
```

```vue
<UserList :users="users">
  <template #user="{ user, index }">
    <strong>{{ index + 1 }}. {{ user.name }}</strong>
    <RouterLink :to="`/users/${user.id}`">Открыть</RouterLink>
  </template>
</UserList>
```

`users` и `RouterLink` принадлежат scope родителя, а `user/index` переданы дочерним компонентом. Если slot не задан, используется fallback с именем пользователя.

#### Ключевые уточнения

- Parent определяет slot content, child определяет outlet и slot props; это две стороны одного контракта.
- Slot content имеет lexical scope родителя и получает локальные значения ребёнка только через scoped slot props.
- Props передают данные, slots передают структуру UI. Выбор делается по требуемой свободе consumer.
- Fallback является default content, а не отдельным slot mode.
- Свобода slot composition не отменяет семантику и accessibility-контракт сложного компонента.

#### Связанные темы

- [[Конспект для подготовки/Vue/Virtual DOM]]
- [[Конспект для подготовки/Vue/Options API и Composition API]]
- [[Конспект для подготовки/Patterns/Compound Components и Headless UI]]
- [[Конспект для подготовки/React/Преимущества React]]

#### Источники

- [Vue: Slots](https://vuejs.org/guide/components/slots.html)
- [Vue: Render Functions and Slots](https://vuejs.org/guide/extras/render-function.html#passing-slots)
