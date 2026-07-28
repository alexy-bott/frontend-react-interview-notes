---
aliases:
  - React performance
  - React Profiler
  - render performance
  - React optimization
---

#### Ответ на 60 секунд

React performance разбирают через причины и стоимость обновлений. Сам факт render не всегда проблема: проблема возникает, когда часто обновляется большое поддерево, дорогие вычисления выполняются в render, Context заставляет обновляться много consumers, список создаёт тысячи DOM-узлов, или commit вызывает дорогой layout/paint. Поэтому сначала профилируют, а потом выбирают решение.

Основные инструменты: React DevTools Profiler, browser Performance panel и иногда `<Profiler>` API. В Profiler смотрят, какие компоненты обновились, сколько занял render, почему они обновились и помогает ли memoization. В браузерном trace смотрят, не ушло ли время после React commit в layout, paint, scripts или long tasks.

Типовые решения: опустить state ниже, разделить Context, стабилизировать props, применить `React.memo/useMemo/useCallback` точечно, виртуализировать большие списки, вынести тяжёлые вычисления из render, использовать transitions для некритичных UI-обновлений, lazy load тяжёлые части экрана и не забывать про server state cache.

#### Ключевая схема

```text
update source -> render cost -> commit cost -> browser work -> user metric
```

| Причина | Симптом | Решение |
| --- | --- | --- |
| State слишком высоко | обновляется большое дерево | локализовать state |
| Context value новый | много consumers rerender | split context, memoize value |
| Большой список | много DOM/render work | virtualization |
| Дорогой selector/filter | input лагает | memo, debounce, worker, index |
| Нестабильные props | `memo` не помогает | стабилизировать object/function |
| Hydration тяжёлая | слабый INP после загрузки | меньше client JS, split, islands/SSR strategy |

#### Развернутый ответ

React render - это вычисление следующего UI-описания. Commit - применение изменений к host environment, в браузере это DOM. После commit браузер может выполнить style/layout/paint/composite. Поэтому “медленный React” иногда на самом деле является дорогим layout после DOM-изменений.

React DevTools Profiler показывает render-стоимость компонентов. Если один input приводит к render всего page shell, причина может быть в state location. Если каждый consumer Context обновляется при любом изменении, причина может быть в одном большом provider value. Если memoized child всё равно обновляется, причина может быть в новых object/array/function props.

`React.memo`, `useMemo` и `useCallback` работают точечно. Они полезны, когда есть дорогой render/вычисление или ссылка важна для memoized child/effect. Если компонент лёгкий, ручная memoization может добавить шум и не дать выигрыша.

Для больших списков чаще всего первым решением является virtualization, а не memoization каждой строки. Виртуализация уменьшает количество компонентов и DOM-узлов, то есть снижает и React-работу, и browser layout/paint.

#### Где применяется во frontend

| Ситуация | Что профилировать | Возможный фикс |
| --- | --- | --- |
| Search input лагает | render на каждый keypress | debounce, memo, worker, transition |
| Таблица на тысячи строк | DOM size + React commits | virtualization |
| Form rerenders целиком | field state и subscriptions | field-level state, RHF patterns |
| Dashboard обновляется по socket | частота updates + chart cost | batching, throttle, snapshot updates |
| Provider ломает всё дерево | Context consumers | split providers/selectors |

> [!faq]+ Уточнения
> - React Profiler показывает React render, но не всю browser rendering стоимость.
> - `useMemo` не предотвращает render компонента; он кеширует значение внутри render.
> - `useCallback` нужен, когда стабильность ссылки реально используется.
> - React Compiler относится к build-time tooling и не заменяет архитектуру state.
> - Transitions помогают приоритизировать UI-обновления, но тяжёлый CPU-код всё равно нужно уменьшать или выносить.

#### Пример

```tsx
const rows = useMemo(() => {
  return data.filter((row) => row.name.includes(query));
}, [data, query]);

const handleSelect = useCallback((id: string) => {
  setSelectedId(id);
}, []);

return <VirtualizedTable rows={rows} onSelect={handleSelect} />;
```

Здесь memoization помогает только если `data/query` стабильны, а основную нагрузку большого списка снимает virtualization.

#### Частые ошибки

- Мемоизировать всё подряд без Profiler.
- Исправлять React render, хотя bottleneck в layout/paint.
- Хранить состояние input слишком высоко.
- Передавать новый object в Context provider на каждый render.
- Использовать index key в изменяемых списках.
- Заменять virtualization на ручную memoization тысяч строк.

#### Связанные темы

- [[Конспект для подготовки/React/Причины рендера]]
- [[Конспект для подготовки/React/Мемоизация]]
- [[Конспект для подготовки/React/useTransition и useDeferredValue]]
- [[Конспект для подготовки/React/Context]]
- [[Конспект для подготовки/React/Hydration]]
- [[Конспект для подготовки/Browser Internals/Main thread long tasks и responsiveness]]
- [[Конспект для подготовки/Performance/Performance диагностика и профилирование]]

#### Источники

- [React docs: Profiler](https://react.dev/reference/react/Profiler)
- [React docs: memo](https://react.dev/reference/react/memo)
- [React docs: useMemo](https://react.dev/reference/react/useMemo)
- [React docs: useCallback](https://react.dev/reference/react/useCallback)
