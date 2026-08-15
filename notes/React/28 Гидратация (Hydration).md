# Гидратация (Hydration)

<!-- NOTE-NAV-TOP:START -->
[← SSR и SSG](<./27 SSR и SSG.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Suspense и lazy →](<./29 Suspense и lazy.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Hydration (гидратация) - это первый клиентский render поверх HTML, который уже был создан на сервере. React сопоставляет результат компонентов с существующим DOM, подключает к нему клиентскую логику и после этого может обрабатывать события и обновлять интерфейс. В React 18 корень гидратируют через `hydrateRoot`.

Пользователь может увидеть server HTML до загрузки JavaScript, но эта часть страницы ещё не обязательно интерактивна. Стоимость hydration зависит от размера client bundle и количества клиентских компонентов: JavaScript нужно загрузить, разобрать, выполнить и сопоставить с DOM.

Первый клиентский результат должен совпадать с серверным. Различие называется hydration mismatch. Типичные причины - текущее время, случайные значения, разные locale или данные, обращение к `window` во время render, неправильная HTML-вложенность и изменение DOM расширением браузера.

## Ключевая схема

```text
server render
-> HTML приходит в браузер
-> браузер разбирает и показывает HTML
-> загружается JavaScript клиентских компонентов
-> hydrateRoot выполняет первый client render
-> React сопоставляет результат с существующим DOM
-> commit подключает React-логику
-> Effects запускаются только на клиенте
```

| Механизм | Что делает |
| --- | --- |
| SSR | создаёт HTML до выполнения приложения в браузере |
| hydration | делает существующий HTML частью работающего React-дерева |
| client render | создаёт новый DOM в браузере через `createRoot` |
| mismatch | означает, что server HTML и первый client render различаются |
| selective hydration | позволяет React 18 гидратировать Suspense-границы с учётом готовности кода и действий пользователя |

## Развернутый ответ

**Чем hydration отличается от обычного render**

При обычном client render контейнер пуст, и React создаёт необходимые DOM-узлы. При hydration узлы уже существуют. React выполняет компоненты на клиенте, восстанавливает внутреннее дерево и ожидает, что результат соответствует server HTML.

Фразу «React просто навешивает обработчики» полезно считать сокращением, но не полной моделью. Во время hydration React также выполняет компоненты, создаёт state, восстанавливает refs и готовит дальнейшие обновления. Внутренне события React обычно работают через делегирование, поэтому речь не обязательно идёт об отдельном `addEventListener` на каждый элемент.

**Почему server и client render должны совпасть**

Hydration рассчитана на одинаковый первоначальный результат. React не проверяет и не исправляет каждое различие как штатный diff: полная валидация сделала бы hydration слишком дорогой. В development React сообщает о mismatch. В зависимости от места ошибки он может восстановить часть дерева, заменить границу клиентским render или отказаться от hydration всего root. Исправление атрибутов при mismatch не гарантируется.

Распространённые причины:

- вызов `new Date()` или `Math.random()` прямо в render;
- разный язык, timezone или форматирование на сервере и клиенте;
- данные изменились между SSR и hydration;
- ветвление по `typeof window !== "undefined"`, которое меняет разметку;
- чтение `localStorage`, ширины окна или media query во время первого render;
- неправильная вложенность HTML, которую браузер исправляет при разборе;
- сторонний скрипт или расширение изменило DOM до запуска React.

**Как сделать первый render детерминированным**

Данные, использованные сервером, передают клиенту как тот же snapshot. Случайный или текущий идентификатор не генерируют независимо на обеих сторонах; для связанных HTML-атрибутов используют `useId`. Локальные браузерные настройки читают после hydration в Effect либо через корректный external-store механизм.

Если интерфейс должен измениться только в браузере, первый client render оставляют таким же, как server render, а затем обновляют состояние в `useEffect`. Это создаёт дополнительный render и может вызвать заметную смену контента, поэтому для больших частей страницы лучше выбрать подходящую server/client boundary.

**React 18: streaming и selective hydration**

Streaming SSR позволяет отправлять HTML частями по мере готовности Suspense boundaries. Hydration тоже не обязана выполняться как одна монолитная задача: React может гидратировать границы по мере загрузки их кода. Если пользователь взаимодействует с ещё не гидратированной частью, React повышает её приоритет и пытается обработать событие после hydration.

Это уменьшает блокировку первого экрана, но не устраняет стоимость JavaScript. Большой bundle и тяжёлый render всё равно занимают main thread.

**RSC и hydration**

Server Components не гидратируются: их код не отправляется клиенту. Гидратация нужна Client Components, которые присутствуют в полученном UI. Поэтому уменьшение клиентских границ в RSC-приложении может уменьшить объём работы в браузере.

## Пример

Клиентский entry point для React 18:

```tsx
import { StrictMode } from "react";
import { hydrateRoot } from "react-dom/client";
import { App } from "./App";

const container = document.getElementById("root");

if (container) {
  hydrateRoot(
    container,
    <StrictMode>
      <App />
    </StrictMode>,
    {
      onRecoverableError(error) {
        console.error("Hydration recovered from an error", error);
      },
    },
  );
}
```

Проблемный компонент:

```tsx
function Clock() {
  return <time>{new Date().toLocaleTimeString()}</time>;
}
```

Сервер и браузер могут получить разное время и locale. Надёжнее передать использованное сервером значение:

```tsx
import { useEffect, useState } from "react";

function Clock({ initialIsoTime }: { initialIsoTime: string }) {
  const [isoTime, setIsoTime] = useState(initialIsoTime);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setIsoTime(new Date().toISOString());
    }, 1000);

    return () => window.clearInterval(timer);
  }, []);

  return <time dateTime={isoTime}>{isoTime}</time>;
}
```

Первый server render и первый client render используют один `initialIsoTime`. Обновление текущего времени начинается после hydration.

## Escape hatch: `suppressHydrationWarning`

`suppressHydrationWarning` скрывает предупреждение для неизбежно различающегося текста или атрибута на один уровень глубины. Это узкий escape hatch, а не способ исправить архитектурную причину mismatch. React не обязан автоматически исправлять подавленное различие.

## Ключевые уточнения

- Hydration переиспользует server HTML, но выполняет клиентские компоненты и восстанавливает React-дерево.
- Server HTML и первый client render должны давать одинаковую структуру и значения.
- Effects не выполняются на сервере; они запускаются после клиентского commit.
- SSR улучшает доставку HTML, а размер client bundle и сложность hydration по-прежнему влияют на INP и отзывчивость.
- React 18 может гидратировать Suspense-границы выборочно и учитывать приоритет пользовательского взаимодействия.
- `useId` помогает согласовать идентификаторы, но не исправляет произвольные различия данных.
- `suppressHydrationWarning` используют только для локального неизбежного различия.
- В RSC-приложении гидратируются Client Components, а не Server Components.

## Связанные темы

- [SSR и SSG](<./27 SSR и SSG.md>)
- [Серверные компоненты](<./33 Серверные компоненты.md>)
- [Suspense и lazy](<./29 Suspense и lazy.md>)
- [Как работает React](<./02 Как работает React.md>)
- [Критический путь рендеринга (Critical Render Path)](<../Основы веб-платформы/20 Критический путь рендеринга (Critical Render Path).md>)
- [Core Web Vitals](<../Основы веб-платформы/21 Core Web Vitals.md>)

## Источники

- [React 18 docs: `hydrateRoot`](https://18.react.dev/reference/react-dom/client/hydrateRoot)
- [React 18 working group: New Suspense SSR Architecture](https://github.com/reactwg/react-18/discussions/37)
- [React 19: improved hydration errors](https://react.dev/blog/2024/12/05/react-19)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← SSR и SSG](<./27 SSR и SSG.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Suspense и lazy →](<./29 Suspense и lazy.md>)
<!-- NOTE-NAV-BOTTOM:END -->
