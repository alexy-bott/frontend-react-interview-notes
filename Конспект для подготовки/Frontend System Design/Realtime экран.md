---
aliases:
  - realtime screen design
  - проектирование realtime
  - WebSocket system design frontend
  - SSE system design frontend
---

#### Ответ на 60 секунд

Realtime-экран проектируют не с выбора WebSocket, а с требований к данным: направление событий, частота, задержка, критичность доставки, объём, восстановление после reconnect и связь с cache. Для server -> client событий часто подходит SSE, для двустороннего канала - WebSocket, для редких обновлений - polling/refetch.

Надёжная схема обычно строится как snapshot + events: начальное состояние загружается обычным HTTP-запросом, затем realtime-события обновляют cache/store или инвалидируют данные. После reconnect клиент догоняет состояние через last event id, timestamp, cursor или повторный snapshot.

Главные темы: auth соединения, reconnect с backoff, heartbeat, versioned message protocol, validation payload, duplicate events, ordering, throttling updates, cleanup при unmount/logout и тестирование edge cases.

#### Ключевая схема

```text
initial HTTP snapshot
-> open realtime connection
-> receive events
-> validate message
-> update cache/store or invalidate query
-> reconnect and resync on failure
```

| Часть | Что решить |
| --- | --- |
| Transport | WebSocket, SSE, polling |
| Protocol | `type`, `version`, payload, id |
| Recovery | reconnect, backoff, last event id, snapshot |
| State sync | cache update, invalidation, local buffer |
| Performance | throttling, batching, backpressure |
| Lifecycle | auth changes, logout, tab visibility, cleanup |

#### Развернутый ответ

Первый вопрос - направление данных. Если клиент только получает события, SSE проще: HTTP-based, server -> client, automatic reconnect. Если клиент активно отправляет сообщения и получает ответы с низкой задержкой, нужен WebSocket. Если данные обновляются редко, polling через query-библиотеку может быть дешевле и проще.

Snapshot + events защищает от потери состояния. Realtime-событие может не прийти из-за reconnect, спящей вкладки или сетевой ошибки. Поэтому экран сначала получает актуальный snapshot, а события применяет как изменения поверх него. После reconnect можно запросить snapshot заново или догнать события по cursor/id.

Message protocol должен быть явным. Сообщение обычно содержит `type`, `version`, `id`, `timestamp`, `payload`. Frontend валидирует payload перед применением. Если пришёл unknown type или unsupported version, безопаснее запросить snapshot или проигнорировать событие с логированием.

State updates должны быть связаны с cache policy. Если событие содержит полный payload, можно точечно обновить query cache. Если событие только сообщает “entity changed”, проще инвалидировать query и получить свежие данные. Для высокочастотных событий нужны throttling, batching или aggregation, чтобы не перерендеривать UI сотни раз в секунду.

Lifecycle особенно важен: соединение открывается при наличии auth/session, закрывается при logout, пересоздаётся при смене workspace/user, отписывается при unmount. Для WebSocket нужно следить за reconnect storm и backoff. Для SSE - за лимитами соединений и proxy buffering.

#### Где применяется во frontend

| Ситуация в проекте | Что проектируется | Конкретное решение |
| --- | --- | --- |
| Live чат | двусторонние сообщения | WebSocket, optimistic send, ack, retry, ordering |
| Логи выполнения job | server -> client поток | SSE, append events, reconnect через last event id |
| Dashboard обновляет метрики раз в 30 секунд | realtime не критичен | polling/refetch interval |
| После события `post.updated` нужно обновить список | синхронизация cache | invalidate query или patch cache по id |
| Соединение оборвалось на минуту | возможны пропущенные события | reconnect + повторный snapshot или cursor catch-up |
| Событий очень много | UI может перерендериваться слишком часто | throttle/batch updates, aggregate events |

> [!faq]+ Уточнения
> - WebSocket не является универсальным ответом для realtime.
> - Snapshot + events надёжнее, чем только stream.
> - Reconnect должен идти с backoff и восстанавливать подписки.
> - Realtime event обычно обновляет cache/store, а не напрямую DOM.
> - Message payload нужно валидировать как внешние данные.
> - При logout нужно закрывать connection и очищать приватный cache.

#### Пример

```ts
socket.addEventListener("message", event => {
  const message = JSON.parse(event.data) as {
    type: string;
    payload: unknown;
  };

  if (message.type === "post.updated") {
    queryClient.invalidateQueries({ queryKey: ["posts"] });
  }
});
```

Если payload содержит валидный полный объект, cache можно обновить точечно:

```ts
queryClient.setQueryData(["post", post.id], post);
```

#### Частые ошибки

- Выбирать WebSocket без требований к двустороннему каналу.
- Полагаться только на stream без initial snapshot.
- Не проектировать reconnect и восстановление подписок.
- Обновлять React state на каждое высокочастотное событие.
- Не валидировать message payload.
- Не закрывать соединение при logout или смене пользователя.
- Не версионировать protocol сообщений.

#### Связанные темы

- [[Конспект для подготовки/Web Basics/Realtime transports]]
- [[Конспект для подготовки/Web Basics/WebSocket]]
- [[Конспект для подготовки/Web Basics/SSE]]
- [[Конспект для подготовки/Patterns/Observer PubSub и события]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/React/Server state и React Query]]
- [[Конспект для подготовки/React/RTK Query]]
- [[Конспект для подготовки/JavaScript/Debounce и throttle]]
- [[Конспект для подготовки/Testing/Async UI формы и auth]]

#### Источники

- [MDN: WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [MDN: EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [MDN: Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
