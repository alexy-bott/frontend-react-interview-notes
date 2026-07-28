---
aliases:
  - Slots
  - Vue slots
  - scoped slots
  - named slots
---

#### Ответ на 60 секунд

Slots во Vue позволяют родителю передавать разметку внутрь заранее определённых мест дочернего компонента. Дочерний компонент описывает точки вставки через `<slot>`, а родитель решает, какой контент туда передать. Это нужно, когда компонент должен контролировать каркас и поведение, но не должен жёстко знать всё содержимое: layout, modal, table, card, page shell.

Есть default slot, named slots и scoped slots. Default slot используется без имени. Named slots позволяют разделить области вроде `header`, `default`, `footer`. Scoped slot означает, что ребёнок передаёт данные наружу через slot props, а родитель использует эти данные в своём шаблоне. Важно: контент слота вычисляется в scope родителя, а slot props приходят из ребёнка.

В Vue 3 slots внутри runtime - это функции. Поэтому тяжёлый slot content может пересчитываться при обновлениях, а для сложных компонентов важно аккуратно проектировать props, keys и структуру render-а. Для устойчивости можно задавать fallback content внутри `<slot>`, который отрендерится, если родитель ничего не передал.

#### Ключевая схема

| Вид слота | Синтаксис ребёнка | Синтаксис родителя |
| --- | --- | --- |
| Default | `<slot />` | обычный контент внутри компонента |
| Named | `<slot name="header" />` | `<template #header>` |
| Scoped | `<slot :item="item" />` | `<template #default="{ item }">` |
| Fallback | `<slot>Empty</slot>` | используется, если слот не передан |

#### Развернутый ответ

**Default slot**

```vue
<!-- Card.vue -->
<template>
  <article class="card">
    <slot />
  </article>
</template>
```

```vue
<Card>
  <h2>Title</h2>
  <p>Content</p>
</Card>
```

**Named slots**

```vue
<!-- Layout.vue -->
<template>
  <header>
    <slot name="header" />
  </header>

  <main>
    <slot />
  </main>

  <footer>
    <slot name="footer" />
  </footer>
</template>
```

```vue
<Layout>
  <template #header>
    <h1>Dashboard</h1>
  </template>

  <p>Main content</p>

  <template #footer>
    <small>Footer</small>
  </template>
</Layout>
```

**Scoped slots**

Scoped slot используют, когда ребёнок управляет данными или состоянием, но родитель хочет сам определить разметку.

```vue
<!-- UserList.vue -->
<template>
  <ul>
    <li v-for="user in users" :key="user.id">
      <slot :user="user">
        {{ user.name }}
      </slot>
    </li>
  </ul>
</template>
```

```vue
<UserList :users="users">
  <template #default="{ user }">
    <strong>{{ user.name }}</strong>
  </template>
</UserList>
```

**Scope**

Слот-контент пишется в родительском template, поэтому имеет доступ к переменным родителя. Но данные, которые передал ребёнок, доступны через slot props.

**Когда нужны slots вместо props**

Props подходят для данных и простых вариантов поведения. Slots используют, когда нужно передать произвольную разметку, несколько областей компонента или дать родителю контроль над тем, как отображается элемент.

#### Частые ошибки

- Путать имя слота: `name="header"` в ребёнке и `#header` у родителя должны совпадать.
- Ожидать, что слот-контент имеет доступ к локальным переменным ребёнка без slot props.
- Передавать строку вместо выражения из-за пропущенного `:`.
- Делать слишком тяжёлый slot content в часто обновляемом компоненте.
- Использовать slots там, где достаточно простого prop.

#### Связанные темы

- [[Конспект для подготовки/Vue/Virtual DOM]]
- [[Конспект для подготовки/Vue/Options API и Composition API]]
- [[Конспект для подготовки/React/Преимущества React]]

#### Источники

- [Vue: Slots](https://vuejs.org/guide/components/slots.html)
