---
aliases:
  - useTransition
  - useDeferredValue
  - startTransition
  - concurrent rendering
---

#### Быстрый ответ

`useTransition` и `useDeferredValue` - concurrent hooks из React 18+. Они помогают разделять срочные и несрочные обновления UI. Срочные обновления - ввод текста, клик, фокус - должны ощущаться мгновенно. Несрочные - тяжёлый список результатов, фильтрация, переключение большой вкладки - можно отложить, чтобы интерфейс не зависал.

`useTransition` помечает конкретное обновление state как transition через `startTransition`. React может отдать приоритет срочному UI и позже завершить тяжёлый render. `useDeferredValue` берёт значение и возвращает его отложенную версию: input уже обновился, а дорогая часть интерфейса ещё может показывать старые результаты, пока React готовит новые.

#### Ключевая схема

```text
urgent update: input value, focus, click feedback
transition update: expensive results, route content, heavy tab
deferred value: lagging copy of a fast-changing value
```

| Инструмент | Когда использовать |
| --- | --- |
| `useTransition` | код контролирует state update и может пометить его несрочным |
| `startTransition` | оборачивает setState для transition |
| `isPending` | показывает, что transition ещё идёт |
| `useDeferredValue` | нужно отложить производное значение, которое пришло сверху |

#### Развернутый ответ

`useTransition` работает там, где в одном сценарии есть срочная и несрочная часть. Например, input должен обновиться сразу, а тяжёлый список результатов может догонять позже. `startTransition` помечает обновления внутри callback как несрочные, и React может прервать их ради более важного ввода, клика или фокуса.

`useDeferredValue` решает похожую задачу с другой стороны. Если компонент уже получил быстро меняющееся значение, но не контролирует место, где оно обновляется, можно взять deferred-копию. Тогда исходное значение обновляется сразу, а тяжёлая часть UI использует слегка отстающую версию и не блокирует срочный интерфейс.

В React 18 callback `startTransition` выполняется синхронно. React помечает как transition только setters, вызванные во время этого callback. Обновление после `await` нужно снова обернуть в `startTransition`; автоматическая поддержка async Actions относится к React 19.

Эти hooks не ускоряют сам алгоритм и не оптимизируют сеть. Они управляют приоритетом render-работы внутри React. Если тяжёлый CPU-цикл выполняется прямо в event handler, transition не поможет: вычисление уже заблокировало main thread до того, как React получил шанс планировать render. Для таких случаев нужны оптимизация алгоритма, web worker, virtualization, debounce/abort для запросов и нормальная архитектура данных.

Transition может быть прерван более свежим обновлением. Поэтому render должен оставаться чистым: без side effects, мутаций DOM, запросов и записи во внешнее состояние. `isPending` нужен, чтобы показать состояние обновления, не скрывая уже видимый UI.

> [!faq]+ Уточнения
> - Transition не debounce: debounce ждёт паузу по таймеру, transition меняет приоритет React render.
> - `useTransition` применяют, когда событие запускает срочное и тяжёлое несрочное обновление.
> - `useDeferredValue` применяют, когда значение уже приходит сверху, а дорогую часть UI можно обновлять позже.
> - Сетевые запросы оптимизируют debounce, abort, cache, server state или route-level data loading; transition управляет render-приоритетом.
> - Срочные обновления нельзя бездумно переводить в transition, иначе интерфейс начнёт запаздывать там, где нужна мгновенная реакция.

#### Пример

```tsx
import { memo, useDeferredValue, useState, useTransition } from "react";

const products = ["React", "Redux Toolkit", "RTK Query", "TypeScript"];

const Results = memo(function Results({ query }: { query: string }) {
  const normalizedQuery = query.toLowerCase();
  const visibleProducts = products.filter((product) =>
    product.toLowerCase().includes(normalizedQuery),
  );

  return (
    <ul>
      {visibleProducts.map((product) => <li key={product}>{product}</li>)}
    </ul>
  );
});

export function SearchWithTransition() {
  const [input, setInput] = useState("");
  const [resultsQuery, setResultsQuery] = useState("");
  const [isPending, startTransition] = useTransition();

  function handleChange(nextValue: string) {
    setInput(nextValue);

    startTransition(() => {
      setResultsQuery(nextValue);
    });
  }

  return (
    <>
      <input
        value={input}
        onChange={(event) => handleChange(event.target.value)}
      />
      {isPending && <span>Обновление результатов...</span>}
      <Results query={resultsQuery} />
    </>
  );
}
```

`input` обновляется срочно, а `resultsQuery` - как transition. `memo` позволяет дорогому списку пропустить срочный render, пока его `query` не изменился. В реальном сценарии преимущество заметно, когда `Results` действительно содержит дорогую работу.

Тот же UX через deferred value:

```tsx
export function SearchWithDeferredValue() {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const isStale = query !== deferredQuery;

  return (
    <>
      <input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />
      <div style={{ opacity: isStale ? 0.6 : 1 }}>
        <Results query={deferredQuery} />
      </div>
    </>
  );
}
```

Transitions не делают вычисления дешевле, они меняют приоритет и позволяют React не блокировать срочный UI. Если тяжёлая работа находится вне React render, например синхронный CPU-цикл в event handler, transition не спасёт. Для больших списков часто нужны вместе: virtualization, memoization, deferred value и правильная архитектура данных.

`isPending` помогает показать, что UI обновляется, не скрывая старый контент. Transition может быть прерван более свежим обновлением, поэтому render должен оставаться чистым. Для network search debounce/abort всё ещё нужны; transition решает другую часть проблемы.

`useDeferredValue` не использует фиксированную задержку. На initial render он возвращает исходное значение. После изменения исходного значения React сначала может показать новый срочный UI с прежним deferred value, а затем подготовить background render. Hook не предотвращает сетевой запрос: он откладывает render части UI, а не network I/O.

#### Ключевые уточнения

- Transition меняет приоритет render work, а debounce ждёт паузу по таймеру.
- State, управляющий текстовым input, остаётся срочным; transition используют для зависимой тяжёлой части UI.
- В React 18 обновления после `await` требуют нового `startTransition`.
- Deferred value не уменьшает число запросов и не имеет фиксированного времени задержки.
- Дорогой child с deferred prop обычно мемоизируют, чтобы он пропустил срочный render с прежним deferred value.
- Concurrent Hooks не делают алгоритм дешевле, поэтому результат проверяют профилированием.

#### Связанные темы

- [[Конспект для подготовки/React/React 18 и 19]]
- [[Конспект для подготовки/React/Мемоизация]]
- [[Конспект для подготовки/React/Причины рендера]]
- [[Конспект для подготовки/JavaScript/Debounce и throttle]]
- [[Конспект для подготовки/JavaScript/Event Loop]]

#### Источники

- [React 18: useTransition](https://18.react.dev/reference/react/useTransition)
- [React 18: useDeferredValue](https://18.react.dev/reference/react/useDeferredValue)
- [React 19: Actions](https://react.dev/blog/2024/12/05/react-19#actions)
