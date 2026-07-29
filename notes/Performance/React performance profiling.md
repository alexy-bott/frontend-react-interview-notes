# React performance profiling

<!-- NOTE-NAV-TOP:START -->
[← Bundle size и loading strategy](<./Bundle size и loading strategy.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Images fonts и resource priority →](<./Images fonts и resource priority.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Производительность React проверяют по частоте и стоимости конкретных updates. Render сам по себе является нормальной частью работы; проблема возникает, когда пользовательское действие запускает слишком много render, дорогое поддерево пересчитывается без нужды или commit приводит к тяжёлому layout и paint в браузере.

Сначала сценарий записывают в React DevTools Profiler и browser Performance panel. Затем связывают update с его источником - state, props, context или external store - и выбирают решение: локализовать state, убрать цепочку Effects, сузить подписку, мемоизировать измеримо дорогую работу, виртуализировать список или разделить срочные и несрочные updates. После изменения повторяют тот же production-сценарий.

## Ключевая схема

```text
state/props/context/external store update
-> React render и reconciliation
-> commit
-> browser style/layout/paint
-> следующий видимый кадр
```

| Наблюдение | Вероятная причина | Направление проверки |
| --- | --- | --- |
| Обновляется большое поддерево | state находится выше реального владельца | опустить state или разделить дерево |
| Все consumers Context обновляются вместе | меняется общее `value` | разделить contexts или состояние |
| `memo` не пропускает render | prop получил новую ссылку | найти конкретный нестабильный prop |
| Один render очень дорогой | вычисление или большой список | измерить calculation, применить memo/virtualization |
| Commit короткий, кадр поздний | дорогой layout/paint | browser Performance panel |
| Updates повторяются цепочкой | Effect синхронно устанавливает производный state | вычислить значение во время render или изменить модель |

## Базовая модель

React 18 запускает render при обновлении state компонента, при render родителя, при изменении используемого context или внешней подписки. Во время render вычисляется следующее описание UI; commit применяет необходимые изменения к DOM. Затем браузер рассчитывает стили, layout и paint. React Profiler измеряет React-часть, но не всю цепочку до кадра.

Количество renders без их длительности мало что говорит. Быстрый render небольшого компонента обычно дешевле сложной мемоизации. И наоборот, один update таблицы с тысячами строк может быть заметен, даже если происходит редко.

Оптимизация должна уменьшать конкретную работу: число затронутых компонентов, стоимость вычисления, количество DOM-узлов или срочность update. Стабильная ссылка сама по себе не ускоряет UI, если ни один consumer не сравнивает её и она не является dependency Hook.

## Развернутый ответ

**Профилирование.** В React DevTools выбирают медленное взаимодействие, записывают commits и находят самые дорогие компоненты. Проверяют, почему они обновились и насколько `actual duration` отличается после изменения. Dev-сборка и Strict Mode добавляют служебную работу, поэтому окончательный замер проводят на production build с сопоставимым устройством и данными.

**State ownership.** Временный state поля, hover или открытой панели держат у ближайшего общего владельца, которому он нужен. Подъём state к корню удобен, но расширяет область потенциального update. Перенос state вниз часто полезнее `memo`, потому что устраняет саму причину обновления внешнего дерева.

**Context.** Consumer обновляется, когда значение используемого provider изменилось по `Object.is`. Разделение часто изменяемых и стабильных данных по разным contexts уменьшает область update. Мемоизация объекта `value` помогает только от новых ссылок при тех же данных; она не мешает consumers обновиться при реальном изменении значения.

**Мемоизация.** `React.memo` сравнивает props компонента, `useMemo` кеширует результат вычисления между renders, `useCallback` кеширует ссылку на функцию. Они полезны, когда измерена стоимость или стабильность ссылки позволяет memoized consumer пропустить работу. Кеш `useMemo` является оптимизацией, а не местом хранения состояния и не семантической гарантией.

**Большие списки.** Virtualization уменьшает число одновременно смонтированных элементов и DOM-узлов. Это обычно сильнее, чем `memo` для каждой из тысяч строк. Для production используют библиотеку, учитывающую размеры, scroll и accessibility, если требования не тривиальны.

**Transitions.** `startTransition` и `useDeferredValue` в React 18 помечают update как несрочный, чтобы ввод и другие срочные действия могли оставаться отзывчивыми. Они не уменьшают объём CPU-работы и не ускоряют синхронный алгоритм; тяжёлое вычисление всё равно нужно сократить, разбить или вынести из main thread.

## Диагностика

1. Воспроизвести один пользовательский сценарий на production build.
2. В browser trace убедиться, что задержка действительно связана с scripting/React, а не сетью или layout.
3. В React Profiler найти дорогой commit и компоненты с наибольшей render cost.
4. Определить источник update и почему затронут каждый дорогой компонент.
5. Изменить одну причину и повторить запись с теми же данными.
6. Проверить видимый результат и метрику взаимодействия, а не только уменьшение числа renders.

## Пример

`<Profiler>` измеряет render указанного поддерева программно:

```tsx
const renderSamples: Array<{
  id: string;
  phase: "mount" | "update" | "nested-update";
  actualDuration: number;
  baseDuration: number;
}> = [];

function onRender(
  id: string,
  phase: "mount" | "update" | "nested-update",
  actualDuration: number,
  baseDuration: number,
) {
  renderSamples.push({ id, phase, actualDuration, baseDuration });
}

<Profiler id="OrdersTable" onRender={onRender}>
  <OrdersTable />
</Profiler>
```

`actualDuration` описывает React render поддерева для commit, но не включает весь последующий layout и paint. `<Profiler>` добавляет overhead; для production-профилирования React требует специальную profiling-сборку, а данные нужно агрегировать, а не отправлять на каждый render без ограничения.

## Ключевые уточнения

- Цель - сократить задержку пользовательского сценария, а не добиться нулевого числа renders.
- `useMemo` кеширует вычисление внутри компонента и не предотвращает render самого компонента.
- `useCallback` полезен только там, где стабильность ссылки участвует в сравнении props или dependencies.
- React Profiler и browser Performance panel отвечают на разные части цепочки; короткий commit не исключает дорогого layout.
- Transitions меняют приоритет и прерываемость несрочного React update, но не делают тяжёлый JavaScript-алгоритм дешевле.

## Связанные темы

- [Причины рендера](<../React/Причины рендера.md>)
- [Мемоизация](<../React/Мемоизация.md>)
- [useTransition и useDeferredValue](<../React/useTransition и useDeferredValue.md>)
- [Context](<../React/Context.md>)
- [Hydration](<../React/Hydration.md>)
- [Main thread long tasks и responsiveness](<../Browser Internals/Main thread long tasks и responsiveness.md>)
- [Performance диагностика и профилирование](<./Performance диагностика и профилирование.md>)

## Источники

- [React: Profiler](https://react.dev/reference/react/Profiler)
- [React: memo](https://react.dev/reference/react/memo)
- [React: useMemo](https://react.dev/reference/react/useMemo)
- [React: useTransition](https://react.dev/reference/react/useTransition)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Bundle size и loading strategy](<./Bundle size и loading strategy.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Images fonts и resource priority →](<./Images fonts и resource priority.md>)
<!-- NOTE-NAV-BOTTOM:END -->
