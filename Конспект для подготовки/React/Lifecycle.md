---
aliases:
  - Lifecycle
  - Жизненный цикл React-компонента
  - Жизненный цикл Effect
---

#### Быстрый ответ

Компонент проходит три состояния жизненного цикла: монтируется при добавлении в дерево, обновляется при обработке нового render и размонтируется при удалении. Функция компонента выполняется во время render phase и должна оставаться чистой. После commit Effects синхронизируют уже отображённый компонент с внешними системами: создают подписку, управляют browser API или сторонним widget и при необходимости возвращают cleanup.

Жизненный цикл Effect отличается от жизненного цикла компонента. Effect начинает синхронизацию, затем останавливает её перед повторным запуском с новыми dependencies или при unmount. Поэтому `useEffect([])` не является универсальной заменой `componentDidMount`, а `useLayoutEffect` не является эквивалентом `getSnapshotBeforeUpdate`: layout Effect запускается после DOM mutation, тогда как class-метод читает DOM непосредственно до неё.

#### Ключевая схема

| Часть | Когда выполняется | Что в ней делают |
| --- | --- | --- |
| Render функции компонента | initial render и последующие обновления | чисто вычисляют JSX из props, state и context |
| Commit | после завершения нужной render work | React применяет изменения к DOM |
| `useLayoutEffect` | после DOM mutation, до browser paint | измеряют layout и при необходимости синхронно корректируют DOM |
| `useEffect` | после commit; обычно не должен блокировать paint | синхронизируются с внешней системой |
| Cleanup Effect | перед следующим setup с изменёнными dependencies и при unmount | закрывают ресурс, созданный setup |
| Event handler | в ответ на конкретное действие пользователя | выполняют вызванный этим действием side effect |

#### Базовая модель

Во время mount React впервые вызывает компонент, создаёт необходимые DOM-узлы и добавляет их во время commit. Во время update React снова вызывает затронутые компоненты, вычисляет необходимые изменения и применяет их в commit. При unmount React удаляет поддерево, запускает cleanup Effects и уничтожает связанный state.

Render может быть повторён или для concurrent-обновления отброшен, поэтому в теле компонента нельзя открывать соединения, менять DOM или отправлять запросы. Внешняя синхронизация выполняется только для результата, который дошёл до commit.

Effect не обязан совпадать с фазами компонента «один к одному». Один Effect описывает один процесс синхронизации:

```text
setup с текущими dependencies -> cleanup старой синхронизации -> новый setup -> cleanup при unmount
```

Если ресурс не создаётся, cleanup не нужен. Вычисление derived value из props или state также не требует Effect.

#### Развернутый ответ

##### Жизненный цикл Effect

Dependencies определяют, когда текущая синхронизация перестала соответствовать UI. Например, при изменении `roomId` соединение со старой комнатой нужно закрыть, а с новой - открыть. React сначала вызывает cleanup предыдущего Effect, затем запускает setup с новыми значениями.

Пустой массив `[]` означает, что Effect не использует reactive values из компонента. В development-режиме Strict Mode React 18 после первого mount выполняет дополнительный цикл `setup -> cleanup -> setup`, чтобы обнаружить отсутствующую или неполную очистку. В production этого проверочного цикла нет.

`useLayoutEffect` использует тот же setup/cleanup-контракт, но выполняется синхронно после изменения DOM и до того, как браузер покажет результат. Он подходит для измерений tooltip или синхронной коррекции scroll, но блокирует paint и поэтому не нужен для обычных подписок или запросов.

##### Событие и Effect

Side effect, вызванный конкретным действием пользователя, обычно остаётся в event handler. Например, POST-запрос «Купить» относится к нажатию кнопки. Effect нужен, если синхронизация обусловлена тем, что компонент отображается с определёнными props/state, например соединение с комнатой должно соответствовать текущему `roomId` независимо от причины перехода.

Такое разделение предотвращает повторную отправку пользовательского действия из-за повторного запуска Effect.

##### Как соотносятся class lifecycle и Hooks

| Class API | Ближайшая функциональная модель |
| --- | --- |
| `render` | вызов функции компонента во время render phase |
| `componentDidMount` + `componentDidUpdate` + `componentWillUnmount` | один `useEffect` или `useLayoutEffect`, описывающий setup и cleanup конкретной синхронизации |
| `shouldComponentUpdate` | `React.memo` для props и подходящая архитектура state; точного соответствия нет |
| `getDerivedStateFromProps` | обычно вычисление значения во время render или controlled-компонент; API нужен редко |
| `getSnapshotBeforeUpdate` | точного Hook-эквивалента нет; метод читает DOM до mutation |
| `componentDidCatch` / `getDerivedStateFromError` | class Error Boundary или библиотечная обёртка |
| `UNSAFE_componentWill...` | не использовать в новом коде; render может не дойти до commit |

Class lifecycle организован вокруг экземпляра компонента. Hooks группируют код по процессу синхронизации, поэтому один большой `componentDidUpdate` обычно превращается в несколько независимых Effects, а не в один общий callback на любое обновление.

#### Пример

Effect поддерживает ровно одно соединение, соответствующее текущему `roomId`.

```tsx
import { useEffect } from "react";

type Connection = {
  connect(): void;
  disconnect(): void;
};

declare function createConnection(roomId: string): Connection;

export default function ChatRoom({ roomId }: { roomId: string }) {
  useEffect(() => {
    const connection = createConnection(roomId);
    connection.connect();

    return () => connection.disconnect();
  }, [roomId]);

  return <h2>Room: {roomId}</h2>;
}
```

При mount соединение открывается. При изменении `roomId` React закрывает прежнее соединение и открывает новое. При unmount выполняется последний cleanup. Дополнительный цикл Strict Mode в development безопасен, если `connect` и `disconnect` действительно зеркальны.

#### Где применяется во frontend

| Ситуация | Подход | Причина |
| --- | --- | --- |
| WebSocket зависит от `roomId` | `useEffect` с cleanup | соединение соответствует текущей комнате |
| `ResizeObserver` следит за DOM-узлом | Effect создаёт observer и вызывает `disconnect` | старый observer не удерживает узел |
| Tooltip нужно измерить до показа | `useLayoutEffect` + ref | корректировка выполняется до paint |
| POST отправляется по кнопке | event handler | действие вызвано конкретным событием, а не отображением компонента |
| Ошибка потомка должна показать fallback | Error Boundary | обычный Effect не перехватывает ошибку render |

#### Ключевые уточнения

- Функция компонента относится к render phase; Effects запускаются только для результата, дошедшего до commit.
- Effect синхронизирует внешний ресурс, а не служит универсальным обработчиком каждого mount или update.
- Cleanup выполняется и при unmount, и перед повторным setup после изменения dependencies.
- `useLayoutEffect` работает после DOM mutation; у `getSnapshotBeforeUpdate` нет точного Hook-эквивалента.
- Event handler описывает конкретное действие пользователя, а Effect - состояние внешней системы относительно текущего UI.

#### Связанные темы

- [[Конспект для подготовки/React/Хуки]]
- [[Конспект для подготовки/React/useEffect vs useLayoutEffect]]
- [[Конспект для подготовки/React/useRef]]
- [[Конспект для подготовки/React/Error Boundaries]]
- [[Конспект для подготовки/React/Правила хуков]]
- [[Конспект для подготовки/React/Как работает React]]

#### Источники

- [React 18: Synchronizing with Effects](https://18.react.dev/learn/synchronizing-with-effects)
- [React 18: Lifecycle of Reactive Effects](https://18.react.dev/learn/lifecycle-of-reactive-effects)
- [React 18: Component API](https://18.react.dev/reference/react/Component)
- [React 18: useLayoutEffect](https://18.react.dev/reference/react/useLayoutEffect)
