# useCallback

<!-- NOTE-NAV-TOP:START -->
[← useRef](<./useRef.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [useTransition и useDeferredValue →](<./useTransition и useDeferredValue.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`useCallback` кэширует ссылку на функцию между renders, пока её dependencies не изменились. Dependencies сравниваются через `Object.is`. Hook не ускоряет выполнение тела функции и не предотвращает render компонента, в котором вызван.

Стабильная ссылка полезна главным образом в двух случаях:

1. callback передаётся в дорогой дочерний компонент с `React.memo`;
2. callback является dependency другого Hook, например Effect или custom Hook.

Если identity функции нигде не сравнивается, `useCallback` обычно не даёт пользы. Его применяют как измеренную оптимизацию, а не ко всем event handlers.

## Ключевая схема

| Инструмент | Что переиспользует |
| --- | --- |
| `useCallback(fn, deps)` | ссылку на функцию |
| `useMemo(calculate, deps)` | результат вычисления |
| `React.memo(Component)` | предыдущий render компонента при равных props |

```text
parent render
-> useCallback сравнивает dependencies через Object.is
-> dependencies те же: вернуть прежнюю функцию
-> dependencies изменились: вернуть функцию из текущего render
```

## Развернутый ответ

**Что именно кэшируется**

Функция в коде всё равно создаётся при выполнении компонента. `useCallback` либо возвращает функцию из текущего render, либо отдаёт сохранённую ссылку. Поэтому Hook помогает только там, где ссылочная идентичность влияет на дальнейшее поведение.

**Связка с `React.memo`**

`React.memo` по умолчанию сравнивает каждый prop через `Object.is`. Inline-функция получает новую ссылку на каждом render родителя, поэтому memoized child считает prop изменившимся. `useCallback` может сохранить ссылку и позволить дочернему компоненту пропустить render.

Для результата нужны сразу несколько условий:

- дочерний компонент обёрнут в `memo`;
- остальные object, array и function props тоже стабильны;
- callback имеет корректные dependencies;
- пропуск render экономит больше работы, чем добавляет мемоизация.

**Callback как dependency**

Если Effect использует функцию, сначала стоит проверить, нужна ли функция за пределами Effect. Часто проще объявить её внутри Effect и зависеть от исходных значений. `useCallback` нужен, когда одна и та же функция действительно используется в нескольких местах или является частью API custom Hook.

Нельзя удалять dependency ради стабильной ссылки. Функция замыкает значения render, в котором была создана. Неполный список dependencies оставляет старые props/state и создаёт stale closure - замыкание с устаревшими значениями.

**Функциональное обновление state**

Если callback читает state только для вычисления следующего state, dependency иногда можно убрать через updater-функцию:

```tsx
const addTodo = useCallback((title: string) => {
  setTodos((currentTodos) => [
    ...currentTodos,
    { id: crypto.randomUUID(), title },
  ]);
}, []);
```

Setter получает актуальное состояние от React, поэтому callback не замыкает `todos`.

**Это оптимизация, а не семантическая гарантия**

React сохраняет callback между renders как оптимизацию. В development кэш сбрасывается после редактирования файла; при первоначальном suspend React тоже может отбросить кэш. Бизнес-логика не должна зависеть от того, что функция навсегда сохранит identity. Если значение должно жить как часть состояния или mutable-памяти, используют state или ref.

**React Compiler**

React Compiler может автоматически стабилизировать часть функций и уменьшить потребность в ручном `useCallback`. Для React 18 это отдельный build-time инструмент с compatibility runtime, а не поведение React 18 по умолчанию.

## Пример

```tsx
import { memo, useCallback, useState } from "react";

type Item = {
  id: string;
  title: string;
};

const ItemButton = memo(function ItemButton({
  item,
  onSelect,
}: {
  item: Item;
  onSelect: (id: string) => void;
}) {
  return (
    <button type="button" onClick={() => onSelect(item.id)}>
      {item.title}
    </button>
  );
});

const items: Item[] = [
  { id: "a", title: "Alpha" },
  { id: "b", title: "Beta" },
];

export function ItemList() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [theme, setTheme] = useState<"light" | "dark">("light");

  const handleSelect = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  return (
    <section data-theme={theme}>
      <button
        type="button"
        onClick={() => setTheme((value) => (
          value === "light" ? "dark" : "light"
        ))}
      >
        Сменить тему
      </button>

      {items.map((item) => (
        <ItemButton key={item.id} item={item} onSelect={handleSelect} />
      ))}

      <p>Выбран: {selectedId ?? "ничего"}</p>
    </section>
  );
}
```

При смене темы родитель рендерится снова. `items` объявлен вне компонента, `handleSelect` сохраняет ссылку, поэтому `ItemButton` может пропустить render. Без `memo` у дочернего компонента один `useCallback` ничего бы не изменил.

## Ключевые уточнения

- `useCallback` переиспользует ссылку, но не результат вызова и не скорость функции.
- Hook полезен только там, где ссылочная идентичность участвует в сравнении или dependencies.
- Dependencies включают все реактивные значения, прочитанные callback.
- Updater-функция state помогает не замыкать текущее состояние, если оно нужно только для следующего обновления.
- Функцию, нужную только Effect, обычно проще объявить внутри Effect.
- `React.memo` не поможет, если другие props каждый раз получают новые object/array/function ссылки.
- Ручную мемоизацию добавляют после обнаружения лишней дорогой работы в React DevTools Profiler.

## Связанные темы

- [Мемоизация](<./Мемоизация.md>)
- [HOC и React memo](<./HOC и React memo.md>)
- [useEffect vs useLayoutEffect](<./useEffect vs useLayoutEffect.md>)
- [Причины рендера](<./Причины рендера.md>)
- [React Compiler](<./React Compiler.md>)

## Источники

- [React 18 docs: `useCallback`](https://18.react.dev/reference/react/useCallback)
- [React 18 docs: `memo`](https://18.react.dev/reference/react/memo)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← useRef](<./useRef.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [useTransition и useDeferredValue →](<./useTransition и useDeferredValue.md>)
<!-- NOTE-NAV-BOTTOM:END -->
