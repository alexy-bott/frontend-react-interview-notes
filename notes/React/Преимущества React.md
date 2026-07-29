# Преимущества React

<!-- NOTE-NAV-TOP:START -->
[↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Как работает React →](<./Как работает React.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

React - библиотека для построения интерфейса из компонентов. Она даёт декларативную модель: компонент описывает UI для текущих props и state, а React синхронизирует результат с платформой. Это уменьшает объём ручного DOM-кода и делает связь «состояние → интерфейс» предсказуемее.

В больших приложениях полезны композиция компонентов, однонаправленный поток данных, локализация state, Hooks и зрелые инструменты отладки и тестирования. React можно использовать для SPA, подключать к существующей странице или применять через framework с routing, SSR и Server Components.

Цена решения: React не является полным web-framework, добавляет runtime и build tooling, а производительность и доступность не появляются автоматически. Команде всё равно нужно выбрать routing, data layer, forms и архитектуру, понимать browser APIs и контролировать renders.

## Ключевая схема

| Свойство | Практическая польза |
| --- | --- |
| декларативный UI | экран выводится из state, меньше ручной синхронизации DOM |
| компоненты и composition | явные границы, переиспользование поведения и дизайн-система |
| однонаправленный data flow | проще найти источник изменения |
| локальный state | изменение можно держать рядом с использующим UI |
| reconciliation | React вычисляет необходимые platform updates |
| экосистема | routing, SSR, query cache, forms, testing и DevTools |
| renderer abstraction | одна компонентная модель для DOM и React Native |

## Развернутый ответ

**Декларативная модель**

В imperative-коде разработчик вручную находит DOM-узлы, меняет text/classes, добавляет и удаляет listeners. В React render описывает, как должен выглядеть UI при текущих данных. После изменения state React снова вызывает компоненты, сравнивает результат и применяет необходимые DOM-изменения.

Это не устраняет всю сложность, но переносит её из последовательности ручных операций в модель состояния. Интерфейс легче воспроизвести для конкретных props/state и проверить тестом.

**Компоненты и composition**

Компонент объединяет разметку и поведение одной части интерфейса. Хорошая граница позволяет заменить implementation, протестировать сценарий и использовать единый API дизайн-системы.

Главная ценность не в копировании одного компонента повсюду. Composition позволяет собирать разные экраны из небольших частей и передавать изменяемое содержимое через props, `children`, Context и custom Hooks.

**Однонаправленный поток данных**

Props идут от parent к child. Событие поднимается callback-ом или отправляется в store, state меняется, затем дерево получает новые данные. Такой цикл упрощает поиск причины обновления по сравнению со множеством объектов, которые незаметно меняют друг друга.

React не требует всё состояние хранить глобально. Локальный state остаётся рядом с компонентом, URL хранит navigation state, а server data - query cache. Это уменьшает область renders и связанность.

**Экосистема и способы внедрения**

React отвечает за UI, а не за все части приложения. Для SPA команда выбирает router, query/cache, forms и build tool. Framework, например Next.js, добавляет routing, rendering strategies, server/client boundaries и production conventions.

Такая модульность позволяет постепенно внедрить React на часть страницы и подобрать инструменты под проект. Одновременно она создаёт цену выбора: два React-проекта могут иметь разную архитектуру и требования к обновлению зависимостей.

**Performance**

Virtual DOM - промежуточное JavaScript-представление UI, а не гарантия, что React всегда быстрее ручного DOM. React тратит время на render и reconciliation, после чего применяет DOM operations.

Преимущество находится в управляемой модели обновлений и инструментах: stable keys, colocated state, `memo`, virtualization, code splitting, transitions и Profiler. Неправильно расположенный state, большой список без virtualization и тяжёлая синхронная работа могут замедлить любое React-приложение.

**React 18**

React 18 добавляет automatic batching, transitions, interruptible rendering для concurrent-обновлений и streaming SSR. Эти возможности помогают сохранять отзывчивость и отдавать server HTML частями, но требуют framework или правильного использования соответствующих APIs. Не каждый render React 18 автоматически становится прерываемым.

**Ограничения**

- React добавляет JavaScript runtime и обычно требует build pipeline.
- Библиотека не задаёт единственную архитектуру data fetching, forms и routing.
- Hooks требуют понимания snapshots, closures и Effect dependencies.
- Client-side React может отправить слишком большой bundle и потратить время на hydration.
- Компонентная абстракция не заменяет semantic HTML, CSS, accessibility и безопасность.
- Частые releases экосистемы требуют контроля версий и migration strategy.

## Как обосновать выбор для проекта

Выбор React оправдан, если:

- интерфейс содержит много связанных интерактивных состояний;
- нужна общая компонентная дизайн-система;
- команда уже владеет React/TypeScript и его tooling;
- требуется зрелая экосистема библиотек и разработчиков;
- нужен framework-сценарий с SSR/SSG или React Native.

Для небольшой статической страницы без сложного состояния React может добавить больше JavaScript и инфраструктуры, чем пользы. Решение сравнивают по требованиям продукта, компетенциям команды, performance budget и стоимости поддержки, а не только по популярности.

## Пример декларативной связи state и UI

```tsx
import { useState } from "react";

export function Disclosure() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <section>
      <button
        type="button"
        aria-expanded={isOpen}
        onClick={() => setIsOpen((value) => !value)}
      >
        Подробности
      </button>

      {isOpen && <p>Содержимое открыто</p>}
    </section>
  );
}
```

State является источником истины и одновременно определяет текстовую область и `aria-expanded`. Не нужно отдельно искать DOM-узел, переключать его видимость и синхронизировать accessibility-атрибут.

## Ключевые уточнения

- React даёт декларативную компонентную модель, а не автоматическую скорость любого интерфейса.
- Virtual DOM помогает организовать обновления, но сам по себе не гарантирует преимущество над точечным DOM-кодом.
- Локализация state и однонаправленный data flow уменьшают связанность и область обновления.
- React является UI-библиотекой; полноценную application platform формирует выбранный framework и экосистема.
- Performance проверяют Profiler и browser metrics, а не количеством `useMemo`.
- React не отменяет знание HTML, CSS, browser rendering, accessibility и network layer.
- Выбор технологии обосновывают требованиями проекта и команды, включая стоимость bundle и поддержки.

## Связанные темы

- [Как работает React](<./Как работает React.md>)
- [Reconciliation](<./Reconciliation.md>)
- [Состояние в React](<./Состояние в React.md>)
- [Причины рендера](<./Причины рендера.md>)
- [Мемоизация](<./Мемоизация.md>)
- [React 18 и 19](<./React 18 и 19.md>)
- [SSR и SSG](<./SSR и SSG.md>)

## Источники

- [React 18 docs: Describing the UI](https://18.react.dev/learn/describing-the-ui)
- [React 18 docs: Thinking in React](https://18.react.dev/learn/thinking-in-react)
- [React 18 release](https://react.dev/blog/2022/03/29/react-v18)

---

<!-- NOTE-NAV-BOTTOM:START -->
[↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Как работает React →](<./Как работает React.md>)
<!-- NOTE-NAV-BOTTOM:END -->
