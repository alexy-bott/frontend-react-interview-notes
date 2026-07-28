---
aliases:
  - useEffect vs useLayoutEffect
  - layout effect
  - passive effect
---

#### Быстрый ответ

`useEffect` синхронизирует компонент с внешней системой после commit: создаёт подписку, управляет соединением, вызывает browser API или отправляет аналитику. Обычно React даёт браузеру нарисовать обновлённый экран перед выполнением `useEffect`, но это не жёсткая гарантия: Effect от пользовательского взаимодействия React 18 может запустить до paint.

`useLayoutEffect` выполняет setup после изменения DOM, но до того, как браузер покажет кадр. Он нужен, когда компонент должен измерить layout и синхронно скорректировать разметку, чтобы пользователь не увидел промежуточное положение. Код и обновления state внутри него блокируют paint, поэтому для большинства эффектов выбирают `useEffect`.

Оба Hook выполняются только на клиенте. На сервере layout измерить невозможно.

#### Ключевая схема

```text
render
-> commit: React изменяет DOM
-> useLayoutEffect setup
-> синхронные обновления из layout effect
-> browser paint
-> useEffect setup обычно выполняется после paint
```

| Hook | Момент | Основные задачи |
| --- | --- | --- |
| `useEffect` | после commit, обычно после paint | подписки, соединения, analytics, browser APIs |
| `useLayoutEffect` | после DOM mutation, до paint | измерение DOM и синхронная коррекция layout |
| `useInsertionEffect` | до layout Effects | вставка стилей внутри CSS-in-JS библиотек |

#### Развернутый ответ

**Что общего**

Effect нужен не для вычисления данных из props/state, а для синхронизации React с системой вне чистого render: DOM API, сетью, таймером, подпиской, сторонним widget или хранилищем браузера.

У Effect есть жизненный цикл setup и cleanup:

1. После commit React запускает setup.
2. При изменении dependencies сначала выполняется cleanup со старыми значениями, затем новый setup.
3. При unmount выполняется последний cleanup.

В Strict Mode React 18 в development дополнительно выполняет цикл setup → cleanup → setup перед обычной работой. Это проверяет, полностью ли cleanup отменяет setup. В production дополнительного цикла нет.

**Когда нужен `useEffect`**

`useEffect` подходит, если внешнюю систему можно синхронизировать без блокировки первого кадра. Примеры: WebSocket-подписка, `document.title`, отправка analytics, работа с таймером.

Фразу «`useEffect` всегда после paint» использовать нельзя. Для Effect, не вызванного взаимодействием, React обычно позволяет браузеру сначала отрисовать экран. Для Effect, вызванного кликом или другим interaction, React может выполнить его раньше, чтобы результат был доступен event system. Отдельная task через `setTimeout` может дать браузеру возможность выполнить paint, но строгий порядок с кадром задают только browser scheduling APIs и проверка конкретного сценария.

Есть ещё один случай: если `useLayoutEffect` синхронно обновил state, React выполняет оставшиеся Effects этого обновления до paint. Поэтому обычный Effect не используют как точный browser lifecycle callback.

**Когда нужен `useLayoutEffect`**

`useLayoutEffect` нужен для двухпроходного render:

1. компонент появляется в предварительном положении;
2. layout Effect измеряет DOM;
3. Effect синхронно обновляет state;
4. React повторяет render до paint;
5. пользователь видит уже скорректированное положение.

Типичные случаи - tooltip, popover, восстановление scroll и интеграция с imperative-библиотекой, которая должна изменить layout до кадра. Если эту задачу можно решить CSS или заранее известными размерами, Effect не нужен.

**Почему `useLayoutEffect` дороже**

Браузер не может показать кадр, пока layout Effect и вызванные им синхронные обновления не завершены. Чтение геометрии после записи стилей также может вызвать forced layout. Поэтому внутри layout Effect оставляют только короткое измерение и необходимую коррекцию.

**SSR**

Effects не выполняются во время server render. Компонент, которому для корректного первого вида обязательно нужен layout Effect, не может полноценно отобразиться на сервере. Обычно его показывают только после hydration, заменяют server-safe разметкой или перестраивают так, чтобы layout определял CSS.

#### Пример: позиционирование tooltip

```tsx
import {
  useLayoutEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

type TooltipProps = {
  targetRect: DOMRect;
  children: ReactNode;
};

export function Tooltip({ targetRect, children }: TooltipProps) {
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState(0);

  useLayoutEffect(() => {
    const nextHeight = tooltipRef.current?.getBoundingClientRect().height ?? 0;
    setHeight(nextHeight);
  }, []);

  const top =
    targetRect.top >= height
      ? targetRect.top - height
      : targetRect.bottom;

  return (
    <div
      ref={tooltipRef}
      style={{
        position: "fixed",
        left: targetRect.left,
        top,
      }}
      role="tooltip"
    >
      {children}
    </div>
  );
}
```

Первый render ещё не знает высоту tooltip. `useLayoutEffect` измеряет элемент и обновляет позицию до paint, поэтому пользователь не видит скачок с нижней позиции на верхнюю.

#### Ключевые уточнения

- `useEffect` и `useLayoutEffect` запускаются после commit и никогда не выполняются на сервере.
- `useEffect` является выбором по умолчанию для синхронизации с внешней системой.
- `useEffect` обычно выполняется после paint, но React 18 не гарантирует это для каждого interaction update.
- State update внутри `useLayoutEffect` может заставить React выполнить оставшиеся Effects до paint.
- `useLayoutEffect` используют только тогда, когда результат измерения должен изменить тот же видимый кадр.
- Setup и cleanup описывают одну симметричную операцию: подписаться/отписаться, создать/уничтожить, запустить/остановить.
- Тяжёлая работа и лишние state updates в layout Effect напрямую задерживают paint.
- Данные, которые можно вычислить из props/state во время render, не требуют Effect.

#### Связанные темы

- [[Конспект для подготовки/React/Хуки]]
- [[Конспект для подготовки/React/useRef]]
- [[Конспект для подготовки/React/Lifecycle]]
- [[Конспект для подготовки/React/Hydration]]

#### Источники

- [React 18 docs: `useEffect`](https://18.react.dev/reference/react/useEffect)
- [React 18 docs: `useLayoutEffect`](https://18.react.dev/reference/react/useLayoutEffect)
- [React 18 docs: `useInsertionEffect`](https://18.react.dev/reference/react/useInsertionEffect)
