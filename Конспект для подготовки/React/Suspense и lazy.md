---
aliases:
  - Suspense
  - React lazy
  - lazy loading
  - code splitting React
---

#### Быстрый ответ

`React.lazy` позволяет лениво загрузить компонент через dynamic import, а `<Suspense>` показывает fallback, пока этот компонент или другая suspense-aware зависимость ещё не готова. Это основной способ связать React-компоненты с code splitting: не грузить тяжёлую часть приложения в initial bundle, а скачать её при переходе на route, открытии модалки или достижении нужной ветки UI.

Важно понимать: `Suspense` - это не универсальный loading spinner для любого `useEffect`. Он работает с механизмами, которые умеют “suspend”: lazy-компоненты, framework data fetching, streaming SSR и специальные библиотеки. Границы Suspense нужно ставить осознанно: слишком высоко - исчезает большой кусок UI, слишком низко - появляется много мелких loaders.

#### Ключевая схема

```text
render lazy component
-> dynamic import starts
-> component suspends
-> nearest Suspense shows fallback
-> module loaded
-> React renders real component
```

| Инструмент | Роль |
| --- | --- |
| `lazy(() => import("./Page"))` | загрузить компонент по требованию |
| `<Suspense fallback={...}>` | граница ожидания |
| fallback | временный UI |
| Error Boundary | ловит ошибку загрузки chunk |
| route-level splitting | частый production-сценарий |

#### Развернутый ответ

`React.lazy` решает задачу code splitting: компонент не попадает в начальный bundle, а загружается отдельным chunk через dynamic import. Пока модуль не загружен, компонент suspends, а ближайший `<Suspense>` показывает fallback. После загрузки модуля React повторяет render и показывает реальный компонент.

`lazy` объявляют на уровне модуля, а не внутри компонента: повторное создание lazy-компонента во время render может сбрасывать его state. Функция загрузки должна вернуть Promise модуля с `default` export React-компонента. React кеширует Promise и результат загрузки.

Suspense шире, чем `lazy`, но не магический. Он работает только с тем, что интегрировано с механизмом suspend: lazy-компоненты, framework-level data fetching, streaming SSR, некоторые cache/data библиотеки. Обычный `fetch` внутри `useEffect` не suspends, потому что эффект запускается уже после commit. Для такого кода нужен локальный loading state или data layer, который умеет работать с Suspense.

Граница Suspense - это UX-граница ожидания. Если поставить её слишком высоко, один маленький chunk или запрос может скрыть всю страницу. Если поставить слишком низко, интерфейс распадётся на множество loaders. Практичный вариант - ставить boundary вокруг route, крупной вкладки, панели или виджета, который может ожидать независимо от остального UI. Fallback должен сохранять размеры и структуру, чтобы не создавать layout shift.

Ошибки и ожидание разделены. Suspense показывает fallback, пока зависимость грузится, но ошибку загрузки chunk должен обработать Error Boundary. Поэтому route-level lazy loading обычно проектируют парой: Suspense для ожидания, Error Boundary для failed chunk/network error.

В React 18 Suspense стал важен для streaming SSR и transitions. Сервер может отдавать готовые части HTML раньше, а transition может удерживать старый UI на экране, пока новая часть suspends. В React 19 и framework-сценариях Suspense также связан с `use`, Server Components и data fetching, но конкретное поведение зависит от фреймворка.

#### Пример

```tsx
import { lazy, Suspense } from "react";

const SettingsPage = lazy(() => import("./SettingsPage"));

export function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SettingsPage />
    </Suspense>
  );
}
```

Route-level сценарий:

```tsx
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Reports = lazy(() => import("./pages/Reports"));
```

Suspense boundary - UX-граница ожидания, а не просто техническая обёртка. Fallback должен минимизировать layout shift: skeleton часто понятнее голого текста. Error Boundary нужен рядом, чтобы chunk load error не ломал всё приложение.

Если уже показанное содержимое снова suspends, React может заменить его fallback и очистить layout Effects скрытого дерева. Transition или deferred value позволяют сохранить прежний UI во время подготовки нового содержимого, когда это соответствует UX.

Lazy loading подходит для редко используемых и тяжёлых частей, но не для всего подряд. Preload/prefetch могут улучшить route transition, если пользователь вероятно скоро перейдёт дальше. В SSR/streaming Suspense помогает отдавать части UI по мере готовности, но поведение зависит от framework.

#### Ключевые уточнения

- Suspense реагирует только на интегрированный механизм suspension; `fetch` из `useEffect` запускается после commit и не относится к нему.
- `lazy` объявляется вне компонента и ожидает модуль с `default` export.
- Граница ожидания соответствует независимой UX-части и не должна без причины скрывать всю страницу.
- Error Boundary обрабатывает ошибку загрузки chunk, а Suspense - период ожидания.
- Размер fallback должен уменьшать layout shift, а количество chunks - не создавать waterfall.

#### Связанные темы

- [[Конспект для подготовки/JavaScript/ES modules]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]
- [[Конспект для подготовки/React/Error Boundaries]]
- [[Конспект для подготовки/React/Hydration]]
- [[Конспект для подготовки/React/React Router]]

#### Источники

- [React 18: Suspense](https://18.react.dev/reference/react/Suspense)
- [React 18: lazy](https://18.react.dev/reference/react/lazy)
