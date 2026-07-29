---
aliases:
  - useEffectEvent
  - Effect Event
  - Effect Events
---

#### Быстрый ответ

`useEffectEvent` - это hook из React 19.2 для логики, которая вызывается из эффекта как событие, но должна видеть свежие props/state без повторного запуска самого эффекта. Он помогает разделить реактивную часть эффекта и нереактивную event-логику.

Классический пример: эффект подключается к chat room по `roomId`, а внутри обработчика `connected` нужно показать уведомление с текущей `theme`. Если добавить `theme` в зависимости эффекта, смена темы будет переподключать чат. Если убрать зависимость вручную, можно получить stale closure и сломать lint. `useEffectEvent` позволяет обработчику видеть актуальную `theme`, а эффекту зависеть только от `roomId`.

Это не универсальный способ “обмануть exhaustive-deps”. Effect Event нужно вызывать только из эффекта или другого Effect Event, не передавать детям и не использовать для обычных click handlers.

#### Ключевая схема

| Что есть в эффекте | Где должно быть |
| --- | --- |
| подключиться к комнате по `roomId` | обычный `useEffect`, зависит от `roomId` |
| показать уведомление с текущей `theme` | `useEffectEvent`, видит свежую `theme` |
| обработчик клика пользователя | обычная функция/handler, не `useEffectEvent` |
| попытка убрать deps ради тишины lint | ошибка |

```text
useEffect
-> синхронизирует компонент с внешней системой
-> вызывает Effect Event при событии внешней системы
-> Effect Event читает свежие props/state без resubscribe
```

#### Развернутый ответ

`useEffectEvent` нужен там, где эффект синхронизирует компонент с внешней системой, а внутри этой синхронизации есть callback-событие. Сама синхронизация должна зависеть от одного набора значений, а callback должен читать актуальные props/state без пересоздания подписки.

Ключевое различие - реактивная и нереактивная часть эффекта. Если изменение значения должно пересоздать подключение, подписку или timer, оно остаётся в dependencies эффекта. Если значение нужно только в callback-е, который сработает позже по событию внешней системы, его можно читать через Effect Event.

`useCallback` не решает эту задачу полностью. Он стабилизирует ссылку только относительно dependencies, но если в callback нужна свежая `theme`, `locale` или `cart`, эти значения попадут в dependencies и снова будут менять ссылку. Effect Event даёт callback-у актуальные значения без добавления его самого в dependencies эффекта.

Effect Event является локальной частью конкретной синхронизации. Он читает актуальные props и state из последнего commit, но изменение этих значений само по себе не перезапускает Effect.

Функция Effect Event намеренно не имеет стабильной идентичности и не включается в dependency array. Поэтому её вызывают только из Effects или других Effect Events того же компонента или custom Hook. Передача наружу скрыла бы, какому Effect принадлежит эта логика, и позволила бы другому коду ошибочно обращаться с ней как с обычным стабильным callback. Это ограничение также проверяет `eslint-plugin-react-hooks`.

Это не способ выключить `exhaustive-deps`. Если эффект реально использует значение для синхронизации, значение должно остаться dependency. Effect Event используют для event-логики внутри эффекта: `connected`, `message`, `visibilitychange`, completion callback, observer notification.

#### Пример

```tsx
import { useEffect, useEffectEvent } from "react";

function ChatRoom({ roomId, theme }) {
  const onConnected = useEffectEvent(() => {
    showNotification("Connected", theme);
  });

  useEffect(() => {
    const connection = createConnection(roomId);

    connection.on("connected", () => {
      onConnected();
    });

    connection.connect();

    return () => {
      connection.disconnect();
    };
  }, [roomId]);

  return null;
}
```

Смена `roomId` переподключает чат. Смена `theme` не переподключает чат, но следующее уведомление будет показано с актуальной темой.

#### Ключевые уточнения

- `useEffectEvent` относится к React 19.2 и не применяется в базовом проекте React 18.
- Значение, которое должно пересинхронизировать Effect, остаётся dependency и не прячется в Effect Event.
- Effect Event вызывается из Effect того же компонента или Hook, а не из JSX-handler и не через prop потомка.
- Effect Event не заменяет `useCallback`: его назначение связано с event-логикой внешней синхронизации.
- Для корректных lint-правил требуется версия `eslint-plugin-react-hooks`, поддерживающая Effect Events.

#### Связанные темы

- [[Конспект для подготовки/React/useEffect vs useLayoutEffect]]
- [[Конспект для подготовки/React/Хуки]]
- [[Конспект для подготовки/React/Правила хуков]]
- [[Конспект для подготовки/React/React 18 и 19]]
- [[Конспект для подготовки/React/useCallback]]

#### Источники

- [React docs: useEffectEvent](https://react.dev/reference/react/useEffectEvent)
- [React 19.2: useEffectEvent](https://react.dev/blog/2025/10/01/react-19-2)
