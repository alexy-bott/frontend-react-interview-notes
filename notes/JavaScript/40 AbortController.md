# AbortController

<!-- NOTE-NAV-TOP:START -->
[← async и await](<./39 async и await.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Fetch и работа с API →](<./41 Fetch и работа с API.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`AbortController` и `AbortSignal` - Web API для согласованной отмены операций. Контроллер инициирует отмену через `abort(reason)`, а сигнал передаётся операциям и сообщает им, что продолжать работу больше не нужно.

Сам сигнал ничего принудительно не останавливает. Операция должна поддерживать этот протокол: `fetch` реагирует на отмену сам, а пользовательская функция должна проверять `signal.aborted`, вызывать `signal.throwIfAborted()` или слушать событие `abort`.

Отмена полезна для устаревших запросов, тайм-аутов и групп связанных операций. Она останавливает ожидание на клиенте и ту часть работы, которую API умеет отменять, но не гарантирует откат действия, уже начатого на backend.

## Ключевая схема

```text
AbortController
├─ signal ───────────────→ fetch / stream / пользовательская функция
└─ abort(reason)
      ↓
signal.aborted = true
signal.reason = reason
операции получают уведомление об отмене
```

У контроллера одна роль - инициировать отмену. Сигнал можно передать потребителям без права самостоятельно отменить чужую группу операций.

## Как работает отмена

`new AbortController()` создаёт контроллер со связанным `signal`. До отмены `signal.aborted` равен `false`, а `signal.reason` - `undefined`.

Первый вызов `controller.abort(reason)` переводит сигнал в отменённое состояние, сохраняет причину и отправляет событие `abort`. Состояние необратимо: для следующей независимой операции нужен новый контроллер.

```js
const controller = new AbortController();

controller.signal.addEventListener("abort", () => {
  console.log(controller.signal.reason);
});

controller.abort("user left the page");

console.log(controller.signal.aborted); // true
```

Если причина не передана, создаётся `DOMException` с именем `AbortError`. Причина может быть любым JavaScript-значением, поэтому код не должен предполагать, что это всегда объект `Error`.

Повторный `abort()` не меняет сохранённую причину и не запускает отмену заново. Поэтому контроллер одноразовый.

## Отмена `fetch`

Сигнал передают в `fetch` через настройку `signal`. После отмены Promise запроса отклоняется с причиной из `signal.reason`. Если тело ответа уже начали читать, отмена также может прервать это чтение.

```js
const controller = new AbortController();

try {
  const response = await fetch("/api/users", {
    signal: controller.signal,
  });

  const users = await response.json();
  console.log(users);
} catch (error) {
  if (controller.signal.aborted) {
    console.log("Request cancelled:", controller.signal.reason);
    return;
  }

  throw error;
}
```

Проверка `signal.aborted` надёжнее одной проверки `error.name === "AbortError"`: вызывающий код мог передать собственную причину отмены.

Если сигнал был отменён ещё до вызова `fetch`, запрос не выполняется, а возвращённый Promise отклоняется. Синхронного `throw` из `fetch` из-за уже отменённого сигнала ожидать не следует.

## Пользовательская отменяемая функция

Функция принимает `signal` как необязательную настройку. Проверка в начале обрабатывает уже отменённый сигнал, а повторные проверки создают точки, в которых длительный алгоритм может остановиться.

```js
async function processItems(items, { signal } = {}) {
  const result = [];

  for (const item of items) {
    signal?.throwIfAborted();
    result.push(await transform(item));
  }

  return result;
}
```

`throwIfAborted()` выбрасывает именно `signal.reason`. Для API на основе событий можно подписаться на `abort`, но обработчик нужно удалить после завершения операции, чтобы не удерживать лишние ссылки.

## Таймаут и объединение причин

`AbortSignal.timeout(ms)` создаёт сигнал, который отменяется по тайм-ауту с `DOMException` по имени `TimeoutError`.

```js
const response = await fetch("/api/report", {
  signal: AbortSignal.timeout(5000),
});
```

`AbortSignal.any(signals)` создаёт общий сигнал, который отменяется при первой отмене любого входного сигнала и получает его причину. Это позволяет объединить тайм-аут с ручной отменой:

```js
const controller = new AbortController();
const signal = AbortSignal.any([
  controller.signal,
  AbortSignal.timeout(5000),
]);

const response = await fetch("/api/report", { signal });
```

Если приложение поддерживает старые браузеры, совместимость статических методов проверяют заранее или используют вспомогательную функцию либо polyfill. Ручной тайм-аут остаётся понятной альтернативой:

```js
async function fetchWithTimeout(url, timeout = 5000) {
  const controller = new AbortController();
  const timerId = setTimeout(() => {
    controller.abort(new DOMException("Timeout", "TimeoutError"));
  }, timeout);

  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timerId);
  }
}
```

`Promise.race` с отклоняющимся таймером меняет только результат ожидания. Без `abort()` проигравший `fetch` продолжит выполняться.

## Устаревший запрос в интерфейсе

Пусть пользователь открыл карточку пользователя `1`, а затем сразу карточку `2`. Если первый запрос завершится позже второго, он может перезаписать актуальные данные. Отмена старого запроса уменьшает лишнюю работу и не даёт его обычной цепочке обработки продолжиться.

В React контроллер создают для конкретного запуска Effect, а функция очистки отменяет именно эту операцию:

```jsx
import { useEffect, useState } from "react";

function UserView({ id }) {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadUser() {
      try {
        const response = await fetch(`/api/users/${id}`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        setUser(await response.json());
      } catch (error) {
        if (!controller.signal.aborted) {
          setError(error);
        }
      }
    }

    loadUser();

    return () => controller.abort("effect cleanup");
  }, [id]);

  if (error) return <p>Не удалось загрузить пользователя</p>;
  return <pre>{JSON.stringify(user, null, 2)}</pre>;
}
```

При смене `id` очистка предыдущего Effect отменяет старый сигнал, после чего новый запуск создаёт отдельный контроллер. Если библиотека или промежуточный слой не передаст сигнал до реальной операции, одной отмены внешнего ожидания будет недостаточно.

## Групповая отмена

Один сигнал можно передать нескольким операциям. Это удобно, когда данные принадлежат одному экрану или одной пользовательской команде:

```js
const controller = new AbortController();

const requests = [
  fetch("/api/profile", { signal: controller.signal }),
  fetch("/api/permissions", { signal: controller.signal }),
];

controller.abort("screen closed");
```

Общая отмена оправдана только при общем жизненном цикле. Независимым операциям нужны разные контроллеры, иначе отмена одной задачи неожиданно остановит остальные.

## Граница с backend

Abort - протокол отмены между вызывающим кодом и поддерживающим его API. Если HTTP-запрос уже дошёл до сервера, backend мог начать запись в базу, отправку письма или оплату. Закрытие соединения не является командой отката такой операции.

Для согласованности на сервере применяют другие механизмы: идемпотентные операции, idempotency key, отдельный endpoint отмены, статусы долгой задачи или транзакцию на backend. `AbortController` не заменяет ни один из них.

## Где применяется во frontend

- При смене поискового запроса отменяется предыдущий `fetch`, чтобы устаревший ответ не обновил интерфейс.
- Функция очистки React Effect отменяет работу, принадлежащую предыдущим props или уже закрытому экрану.
- Таймаут ограничивает время ожидания медленного внешнего сервиса.
- Один сигнал завершает группу запросов, относящихся к одной отменённой пользовательской операции.
- Пользовательский алгоритм проверяет `throwIfAborted()` между дорогими этапами и освобождает ресурсы раньше.

## Ключевые уточнения

- `AbortController` инициирует отмену, а `AbortSignal` сообщает о ней потребителям.
- Сигнал не останавливает произвольный код сам: операция должна поддерживать протокол отмены.
- После `abort()` сигнал навсегда остаётся отменённым; контроллер не переиспользуют.
- Причина отмены хранится в `signal.reason` и не обязана быть `AbortError`.
- Отмена `fetch` не гарантирует откат уже начатого действия на backend.
- Таймаут через `Promise.race` без `abort()` не останавливает сетевой запрос.
- Один сигнал объединяет жизненный цикл нескольких операций, поэтому групповую отмену применяют намеренно.

## Связанные темы

- [Fetch и работа с API](<./41 Fetch и работа с API.md>)
- [Promise](<./37 Promise.md>)
- [Комбинаторы Promise](<./38 Комбинаторы Promise.md>)
- [Цикл событий (Event Loop)](<./35 Цикл событий (Event Loop).md>)
- [useEffect и useLayoutEffect](<../React/12 useEffect и useLayoutEffect.md>)

## Источники

- [WHATWG DOM Standard: Aborting ongoing activities](https://dom.spec.whatwg.org/#aborting-ongoing-activities)
- [WHATWG Fetch Standard](https://fetch.spec.whatwg.org/)
- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [MDN: AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← async и await](<./39 async и await.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Fetch и работа с API →](<./41 Fetch и работа с API.md>)
<!-- NOTE-NAV-BOTTOM:END -->
