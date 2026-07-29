# useRef

<!-- NOTE-NAV-TOP:START -->
[← useEffect vs useLayoutEffect](<./useEffect vs useLayoutEffect.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [useCallback →](<./useCallback.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`useRef` возвращает один стабильный объект `{ current }`, который сохраняется между renders. Изменение `ref.current` не запускает render, поэтому ref хранит данные, которые нужны обработчикам или Effects, но сами по себе не должны менять экран.

Два основных сценария:

1. получить DOM-узел, чтобы вызвать `focus()`, измерить layout или подключить сторонний widget;
2. сохранить mutable-значение: timer id, экземпляр API или последнее значение для асинхронного callback.

Если значение участвует в разметке, нужен state. State описывает UI и запускает render, ref является служебной mutable-памятью.

## Ключевая схема

| Задача | Инструмент |
| --- | --- |
| показать новое значение на экране | `useState` |
| сфокусировать input | DOM ref |
| сохранить timer id | mutable ref |
| измерить DOM до paint | ref + `useLayoutEffect` |
| хранить instance сторонней библиотеки | mutable ref + cleanup |
| передать ограниченный imperative API наружу | `forwardRef` + `useImperativeHandle` в React 18 |

## Развернутый ответ

**Стабильный контейнер**

`useRef(initialValue)` возвращает тот же объект на каждом render. Начальное значение используется только при первом создании ref. Код может менять `current`, но React не следит за этим изменением как за state и не планирует render.

Из-за этого ref нельзя использовать как скрытую замену state. Если JSX читает `ref.current`, после изменения ref экран останется прежним до какого-либо другого render.

**DOM ref**

Когда ref передан React-элементу, React устанавливает `current` во время commit после создания DOM-узла. При удалении узла React возвращает `current` в `null`. Поэтому DOM читают в event handler, Effect или layout Effect, а не рассчитывают на готовый узел во время render.

`useLayoutEffect` используют, если измерение должно скорректировать тот же видимый кадр. Для обычного focus после открытия формы часто достаточно Effect или обработчика события.

**Mutable ref**

Ref удобен, когда асинхронный callback должен получить актуальное служебное значение без пересоздания подписки. Например, ref может хранить timer id для отмены debounce. При этом ref не отменяет правила dependencies: реактивную синхронизацию по-прежнему описывает Effect.

Ref с флагом `isMounted` не является универсальным решением async-проблем. Запрос лучше отменять через `AbortController`, а библиотечную подписку - через её cleanup. Флаг только скрывает обновление и может оставить работу или ресурс незавершёнными.

**Чтение и запись во время render**

React не отслеживает изменения `ref.current` и не использует их как входные данные render. Чтение или изменение ref во время render создаёт скрытое изменяемое состояние (mutable state) вне props, state и context: повторный render может получить другой результат при тех же входных данных, а запись сохранится, даже если подготовленная render-работа не дойдёт до commit. Поэтому обычно `ref.current` читают и меняют в обработчиках событий и Effects.

Допустима предсказуемая ленивая инициализация во время render, если ветка выполняется только при `current === null`, а создаваемый результат всегда одинаков для этого компонента:

```tsx
const playerRef = useRef<VideoPlayer | null>(null);

if (playerRef.current === null) {
  playerRef.current = new VideoPlayer();
}
```

Созданный resource всё равно должен быть освобождён в cleanup, если у него есть `destroy`, `disconnect` или аналогичный метод.

**Передача ref через компонент**

Базовая версия конспекта - React 18, поэтому для function component ref принимают через `forwardRef`. `useImperativeHandle` позволяет вернуть не весь DOM-узел, а небольшой API вроде `focus()` и `reset()`.

В React 19 `ref` доступен как обычный prop. Это версионное изменение не следует переносить в описание React 18-кода.

## Пример: DOM ref и timer ref

```tsx
import { useEffect, useRef, useState } from "react";

async function sendSearch(query: string) {
  await fetch(`/api/search?q=${encodeURIComponent(query)}`);
}

export function SearchBox() {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (timerRef.current !== null) {
      window.clearTimeout(timerRef.current);
    }

    timerRef.current = window.setTimeout(() => {
      sendSearch(query);
      timerRef.current = null;
    }, 300);

    return () => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [query]);

  return (
    <input
      ref={inputRef}
      value={query}
      onChange={(event) => setQuery(event.target.value)}
    />
  );
}
```

`inputRef` указывает на DOM-элемент после commit. `timerRef` хранит идентификатор таймера, который не нужен в JSX. Изменение timer id не вызывает render, а изменение `query` вызывает.

## Пример: ограниченный imperative API в React 18

```tsx
import {
  forwardRef,
  useImperativeHandle,
  useRef,
  type Ref,
} from "react";

type SearchInputHandle = {
  focus: () => void;
  clear: () => void;
};

export const SearchInput = forwardRef(function SearchInput(
  _props: Record<string, never>,
  ref: Ref<SearchInputHandle>,
) {
  const inputRef = useRef<HTMLInputElement>(null);

  useImperativeHandle(ref, () => ({
    focus() {
      inputRef.current?.focus();
    },
    clear() {
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    },
  }), []);

  return <input ref={inputRef} />;
});
```

Родитель получает только методы `focus` и `clear`, а не полный DOM-узел.

## Ключевые уточнения

- Ref сохраняет объект между renders, но изменение `current` не обновляет UI.
- State используют для данных разметки, ref - для DOM и служебной mutable-памяти.
- React устанавливает DOM ref во время commit и очищает его при удалении узла.
- Ref читают и меняют в handlers и Effects; render остаётся чистым.
- Timer, observer, subscription и instance внешней библиотеки требуют cleanup.
- В React 18 ref передают в function component через `forwardRef`; обычный ref prop относится к React 19.
- `useImperativeHandle` уменьшает публичную imperative-поверхность компонента.

## Связанные темы

- [Хуки](<./Хуки.md>)
- [useEffect vs useLayoutEffect](<./useEffect vs useLayoutEffect.md>)
- [Lifecycle](<./Lifecycle.md>)
- [Controlled и uncontrolled компоненты](<./Controlled и uncontrolled компоненты.md>)
- [React 18 и 19](<./React 18 и 19.md>)

## Источники

- [React 18 docs: `useRef`](https://18.react.dev/reference/react/useRef)
- [React 18 docs: Manipulating the DOM with Refs](https://18.react.dev/learn/manipulating-the-dom-with-refs)
- [React 18 docs: `forwardRef`](https://18.react.dev/reference/react/forwardRef)
- [React 18 docs: `useImperativeHandle`](https://18.react.dev/reference/react/useImperativeHandle)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← useEffect vs useLayoutEffect](<./useEffect vs useLayoutEffect.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [useCallback →](<./useCallback.md>)
<!-- NOTE-NAV-BOTTOM:END -->
