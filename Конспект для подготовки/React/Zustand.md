---
aliases:
  - Zustand
  - Zustand store
  - zustand state management
---

#### Быстрый ответ

Zustand - небольшая библиотека для client state с внешним store и React Hooks. Состояние и actions описываются в store, а компонент через selector подписывается только на нужное значение. При изменении store Zustand повторно запускает selector и по умолчанию сравнивает результат через `Object.is`.

В отличие от Redux Toolkit, Zustand не требует reducers и action objects. В отличие от Context, обновление store не проходит через новый Provider value: обновляются подписчики, у которых изменился выбранный slice. Provider обычно не нужен, но полезен для dependency injection, тестов и отдельного store на экземпляр дерева.

Zustand используют для глобального client state: настройки интерфейса, auth snapshot, состояние сложного wizard, выбранные элементы, UI preferences, кросс-компонентные панели. Server state не складывают в Zustand вручную без причины: для данных с backend нужны cache, stale state, refetch, invalidation и mutations, поэтому там уместнее RTK Query, TanStack Query или loader-слой фреймворка.

#### Ключевая схема

```text
create store -> state + actions -> selector in component -> rerender only when selected value changes
```

| Вопрос | Zustand |
| --- | --- |
| Основная модель | global store + hooks/selectors |
| Provider | не обязателен; нужен для scoped/per-request store |
| Boilerplate | низкий |
| Обновления | через `set`, часто action functions |
| Ререндеры | selector + `Object.is` или явно выбранная equality |
| Side effects | можно в actions, но без превращения store в API-слой |
| Persist | через middleware `persist` |
| Server state | query/cache библиотека |

#### Развернутый ответ

Zustand даёт store без обязательного Provider и большого boilerplate. Компонент вызывает hook с selector и подписывается на конкретный slice. После обновления store компонент рендерится, только если выбранное значение изменилось по equality-проверке. Это отличается от широкого Context, где новый provider value обновляет всех consumers этого Context.

С Redux Toolkit сравнение упирается в требования к дисциплине. Redux сильнее, когда нужна строгая модель actions/reducers, middleware pipeline, time-travel/devtools-подход, большая команда и сложные доменные workflows. Zustand проще и быстрее для умеренного global client state, но его простота не означает, что весь state должен жить в одном store.

Selector - ключ к производительности. Компонент выбирает минимальный slice: `state.user.name`, `state.theme`, `state.setTheme`. Selector вида `state => ({ theme: state.theme, setTheme: state.setTheme })` каждый раз создаёт новый объект. Для такого выбора используют `useShallow` либо делают две простые подписки. Вложенные данные Zustand автоматически не сравнивает глубоко.

Actions обычно лежат рядом с состоянием в store. `set` принимает partial state или updater, а `get` читает текущее состояние внутри action. Async action технически допустим, но API cache, retry, invalidation и optimistic updates отделяют в query/API слой, чтобы store не превратился в самописный server-state cache.

`persist` подходит для небольших и безопасных client preferences: theme, layout, last selected organization. При изменении shape задают `version` и `migrate`, а через `partialize` сохраняют только нужные поля. Hydration persisted state происходит отдельно от server HTML и должна быть учтена, чтобы не получить визуальный скачок или hydration mismatch. Tokens, чувствительные данные, большие объекты и server cache сохранять рискованно.

`set` по умолчанию shallow-merge-ит state только на верхнем уровне. Вложенный объект обновляют явно или через Immer middleware. Если передать replace-режим, можно заменить весь state и случайно стереть actions.

Для TypeScript часто пишут `create<Store>()(...)`, чтобы корректно типизировать state и actions. В Next.js module-level singleton подходит только для общего client-only state. Если store создаётся или заполняется на сервере данными запроса, нужен новый store на каждый request и одинаковый initial snapshot для server render и hydration; иначе возможны утечка данных между пользователями и mismatch.

#### Пример

```ts
import { create } from "zustand";

type Theme = "light" | "dark";

type UiStore = {
  theme: Theme;
  sidebarOpen: boolean;
  setTheme: (theme: Theme) => void;
  toggleSidebar: () => void;
};

export const useUiStore = create<UiStore>((set) => ({
  theme: "light",
  sidebarOpen: true,
  setTheme: theme => set({ theme }),
  toggleSidebar: () =>
    set(state => ({
      sidebarOpen: !state.sidebarOpen,
    })),
}));
```

```tsx
function ThemeButton() {
  const theme = useUiStore(state => state.theme);
  const setTheme = useUiStore(state => state.setTheme);

  return (
    <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
      {theme}
    </button>
  );
}
```

Компонент подписан только на `theme` и `setTheme`, а не на весь store. Это уменьшает лишние обновления UI.

#### Ключевые уточнения

- Zustand хранит shared client state, а server data остаются в query/cache слое.
- Компонент подписывают на минимальный slice вместо всего store.
- Selector result по умолчанию сравнивается через `Object.is`; новый object result требует `useShallow` или изменения selector.
- Store разделяют по доменным границам и не дублируют URL или query cache.
- `persist` сохраняет только безопасные поля и учитывает version, migration и hydration.
- `set` shallow-merge-ит верхний уровень; вложенные структуры обновляют явно.
- Module singleton на сервере не хранит request-specific state; для него создают per-request store.
- Async actions допустимы, но retries, deduplication и invalidation не появляются автоматически.

#### Связанные темы

- [[Конспект для подготовки/Architecture/State management]]
- [[Конспект для подготовки/React/Состояние в React]]
- [[Конспект для подготовки/React/Context]]
- [[Конспект для подготовки/React/Redux и Flux]]
- [[Конспект для подготовки/React/Redux Toolkit]]
- [[Конспект для подготовки/React/RTK Query]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]

#### Источники

- [Zustand docs](https://zustand.docs.pmnd.rs/)
- [Zustand docs: Next.js guide](https://zustand.docs.pmnd.rs/guides/nextjs)
- [Zustand docs: Prevent rerenders with useShallow](https://zustand.docs.pmnd.rs/guides/prevent-rerenders-with-use-shallow)
- [Zustand docs: Persisting store data](https://zustand.docs.pmnd.rs/integrations/persisting-store-data)
- [Zustand GitHub README](https://github.com/pmndrs/zustand)
