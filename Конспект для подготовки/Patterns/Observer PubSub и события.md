---
aliases:
  - Observer pattern
  - PubSub
  - Publish Subscribe
  - Event Bus
  - события frontend
---

#### Ответ на 60 секунд

Observer - это паттерн, где объект-источник уведомляет подписчиков об изменениях. PubSub похож, но часто добавляет посредника: publisher публикует событие в channel/topic, subscriber подписывается на этот topic, а стороны не знают друг о друге напрямую.

Во frontend это встречается постоянно: DOM events, `addEventListener`, store subscriptions, WebSocket messages, EventSource/SSE, BroadcastChannel, custom event bus, observable streams, form watchers. Главная тема не только “как подписаться”, но и как отписаться, не создать memory leak и не потерять связь с React/Vue lifecycle.

Паттерн полезен для событий и внешних источников данных, но опасен как скрытая глобальная коммуникация. Если всё приложение общается через event bus без явных связей, поток данных становится трудно отлаживать.

#### Ключевая схема

| Подход | Кто знает кого | Frontend-пример |
| --- | --- | --- |
| Observer | source хранит subscribers | store subscription |
| PubSub | publisher и subscriber связаны через broker/topic | event bus, message channel |
| DOM events | browser event target уведомляет listeners | `addEventListener` |
| Realtime | server присылает события | WebSocket/SSE |

```text
source/event channel
-> subscriber callback
-> update state/cache/UI
-> cleanup on unmount
```

#### Развернутый ответ

Observer подходит, когда есть источник изменений и несколько потребителей. Например, store сообщает компонентам, что state изменился. Компонент подписывается, получает обновление и перерендеривается или обновляет локальное состояние.

PubSub удобен, когда отправитель события не должен знать конкретных получателей. Например, WebSocket layer публикует `notification:new`, а разные части приложения могут реагировать: badge обновляет счётчик, toast показывает сообщение, cache invalidation обновляет запрос.

Главный риск - скрытый поток данных. Если событие публикуется из одного места, а последствия размазаны по десятку подписчиков, становится сложно понять, почему UI изменился. Поэтому PubSub используют точечно: realtime, cross-tab communication, analytics, plugin-like extension points, интеграция с внешней системой.

Во frontend lifecycle критичен. Подписка должна иметь cleanup: `removeEventListener`, `unsubscribe`, `socket.off`, `abort`, закрытие stream. Иначе компонент размонтировался, а callback продолжает держать ссылки на state, DOM или closures.

#### Где применяется во frontend

| Ситуация в проекте | Что является событием | Что важно учесть |
| --- | --- | --- |
| Компонент слушает resize/scroll | DOM event | throttling/debounce и `removeEventListener` при unmount |
| Store сообщает об изменении state | store subscription | selector, unsubscribe, защита от лишних render |
| WebSocket присылает новое сообщение | server event | обработать reconnect, duplicate messages, cache update |
| Несколько вкладок должны синхронизировать logout | cross-tab event | BroadcastChannel/storage event и cleanup |
| Analytics слушает user actions | domain event | не смешивать analytics с бизнес-логикой UI |
| Form library отслеживает поле | form watch/subscription | отписаться и не перерендеривать всю форму без причины |

> [!faq]+ Уточнения
> - Observer обычно подразумевает прямую подписку на source, PubSub - обмен через topic/broker.
> - В React подписки на внешние источники требуют cleanup в effect.
> - Event bus удобен точечно, но может сделать поток данных скрытым.
> - WebSocket/SSE события нужно связывать с cache/state policy.
> - Частые events вроде scroll/input требуют debounce, throttle или scheduling.

#### Пример

```ts
type Listener<T> = (event: T) => void;

function createEventBus<T>() {
  const listeners = new Set<Listener<T>>();

  return {
    subscribe(listener: Listener<T>) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    publish(event: T) {
      listeners.forEach(listener => listener(event));
    },
  };
}
```

Использование в React:

```tsx
useEffect(() => {
  const unsubscribe = notificationsBus.subscribe(notification => {
    setNotifications(prev => [notification, ...prev]);
  });

  return unsubscribe;
}, []);
```

#### Частые ошибки

- Подписаться в effect и забыть cleanup.
- Использовать event bus вместо явных props/state там, где достаточно обычного data flow.
- Публиковать слишком общие события вроде `"changed"` без payload-контракта.
- Не типизировать payload события.
- Не учитывать частоту событий и перегружать render.
- Не обрабатывать reconnect/duplicates для realtime-событий.

#### Связанные темы

- [[Конспект для подготовки/JavaScript/DOM events]]
- [[Конспект для подготовки/Web Basics/WebSocket]]
- [[Конспект для подготовки/Web Basics/SSE]]
- [[Конспект для подготовки/Web Basics/Realtime transports]]
- [[Конспект для подготовки/React/useEffect vs useLayoutEffect]]
- [[Конспект для подготовки/React/Context]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/Architecture/State management]]

#### Источники

- [MDN: EventTarget](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget)
- [MDN: WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Martin Fowler: Event Aggregator](https://martinfowler.com/eaaDev/EventAggregator.html)
