---
aliases:
  - async await
  - async function
  - await
  - асинхронные функции
---

#### Быстрый ответ

`async/await` - синтаксис поверх Promise для последовательного описания асинхронного кода. `async`-функция всегда возвращает Promise: обычный `return` задаёт успешное значение, а необработанный `throw` - причину отклонения.

Код `async`-функции выполняется синхронно до первого достигнутого `await`. `await` принимает любое значение, обрабатывает его как Promise, приостанавливает эту функцию и освобождает текущий стек вызовов. После завершения ожидаемого Promise продолжение ставится в очередь микрозадач, даже если Promise уже был выполнен.

`await` не блокирует поток, но и не делает вычисления параллельными. Тяжёлый цикл до или после `await` по-прежнему занимает основной поток.

Последовательные `await` нужны зависимым шагам. Независимые операции запускают до ожидания и затем объединяют через `Promise.all` или другой подходящий комбинатор.

#### Ключевая схема

```text
вызвать async-функцию
→ выполнить синхронный участок
→ встретить await
→ вернуть вызывающему коду Promise
→ освободить стек вызовов
→ дождаться результата
→ поставить продолжение в очередь микрозадач
→ продолжить функцию
→ return = успешное выполнение / throw = отклонение
```

```js
async function example() {
  console.log("A");
  await 0;
  console.log("C");
}

example();
console.log("B");

// A
// B
// C
```

`await 0` не ждёт сеть, но всё равно переносит продолжение в микрозадачу. Поэтому `C` появляется после текущего синхронного кода.

#### Что возвращает async function

Результат вызова всегда является новым Promise:

```js
async function getNumber() {
  return 42;
}

const result = getNumber();
console.log(result instanceof Promise); // true
console.log(await result); // 42
```

`throw` превращается в отклонение Promise:

```js
async function fail() {
  throw new Error("failed");
}

fail().catch(console.error);
```

Если вернуть Promise или thenable-объект с методом `then`, итоговый Promise `async`-функции примет его состояние. При этом возвращается не тот же объект Promise:

```js
const original = Promise.resolve(42);

async function passThrough() {
  return original;
}

console.log(passThrough() === original); // false
```

Вызывающий код всегда получает Promise и не должен ожидать, что `throw` из тела `async`-функции выйдет из обычного вызова синхронно.

#### Что делает `await`

`await expression` сначала вычисляет выражение, а затем обрабатывает его результат как Promise:

- обычное значение становится успешным результатом;
- Promise ожидается;
- thenable-объект обрабатывается по процедуре разрешения Promise;
- отклонение превращается в `throw` в точке `await`.

```js
async function read() {
  const first = await 10;
  const second = await Promise.resolve(20);
  return first + second;
}

console.log(await read()); // 30
```

Приостанавливается конкретная `async`-функция, а не вся среда JavaScript. Пока она ждёт, event loop может выполнять другие задачи и микрозадачи.

#### Ошибки

```js
async function loadUser() {
  try {
    const response = await fetch("/api/user");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error("Cannot load user", { cause: error });
  }
}
```

`catch` получает и синхронный `throw` до `await`, и отклонение ожидаемого Promise. Но он не получит ошибку Promise, который был запущен и забыт без `await` или `return`:

```js
async function incorrect() {
  try {
    saveAnalytics(); // Promise потерян.
  } catch (error) {
    // Не обработает будущий rejection saveAnalytics().
  }
}
```

Асинхронную операцию нужно включить в контракт:

```js
await saveAnalytics();
// или
void saveAnalytics().catch(reportError);
```

Второй вариант явно обозначает fire-and-forget, то есть намеренно запущенную без ожидания операцию, и всё равно обрабатывает её ошибку.

#### `return promise` и `return await promise`

Оба варианта дают вызывающему коду Promise с тем же итоговым состоянием. Но внутри `try...catch` конструкция `return await` нужна, если локальный `catch` должен обработать отклонение:

```js
async function withoutAwait() {
  try {
    return loadData();
  } catch (error) {
    return fallbackData;
  }
}
```

Здесь `try` возвращает Promise до его отклонения, поэтому локальный `catch` не срабатывает.

```js
async function withAwait() {
  try {
    return await loadData();
  } catch (error) {
    return fallbackData;
  }
}
```

Здесь отклонение возобновляет функцию как `throw` внутри `try`. Вне локального `try...catch/finally` дополнительный `await` перед `return` выбирают по читаемости и качеству стека ошибки, а не из-за устаревшего правила «он всегда создаёт лишний Promise».

#### Последовательное и параллельное начало операций

Этот код выполняет шаги последовательно:

```js
const user = await loadUser();
const permissions = await loadPermissions(user.id);
```

Второй запрос зависит от `user.id`, поэтому последовательность необходима.

Если зависимости нет, два последовательных `await` создают лишнее ожидание:

```js
const profile = await loadProfile();
const settings = await loadSettings();
```

Параллельное начало:

```js
const profilePromise = loadProfile();
const settingsPromise = loadSettings();

const [profile, settings] = await Promise.all([
  profilePromise,
  settingsPromise,
]);
```

Или короче:

```js
const [profile, settings] = await Promise.all([
  loadProfile(),
  loadSettings(),
]);
```

`Promise.all` не запускает функции сам: они запускаются при вычислении элементов массива до вызова комбинатора. Метод только координирует результаты.

Параллельность не всегда лучше. Ограничения backend, порядок побочных эффектов, лимит запросов и память могут требовать последовательного выполнения или пула с ограниченным числом одновременных операций.

#### Циклы и `forEach`

`for...of` с `await` выполняет итерации последовательно и действительно ждёт каждую:

```js
for (const id of ids) {
  await saveUser(id);
}
```

`forEach` не ожидает Promise, возвращённый callback, и сам возвращает `undefined`:

```js
ids.forEach(async (id) => {
  await saveUser(id);
});

console.log("finished"); // До завершения saveUser.
```

Для независимых операций:

```js
await Promise.all(ids.map((id) => saveUser(id)));
```

Для последовательных операций используют `for...of`, для большого набора - очередь или пул с лимитом. Выбор выражает правила выполнения, а не стиль синтаксиса.

#### Await в условии и обработчике

Пока функция ждала, данные могли устареть: пользователь сменил маршрут, поисковый запрос или выбранный объект. `async`-функция не получает автоматическую транзакционность.

```js
const requestId = ++latestRequestId;
const result = await loadResults(query);

if (requestId !== latestRequestId) {
  return;
}

renderResults(result);
```

Операцию, которая поддерживает сигнал, лучше дополнительно отменить через `AbortController`. Проверка актуальности всё равно нужна для API без отмены и для побочных эффектов после `await`.

#### Отмена

Promise и `async`-функция не имеют встроенного метода `cancel`. Отменяемой должна быть сама операция:

```js
async function load(url, { signal } = {}) {
  signal?.throwIfAborted();

  const response = await fetch(url, { signal });
  return response.json();
}
```

Сигнал передаётся до низкоуровневого API. Простое игнорирование возвращённого Promise не останавливает сетевой запрос, таймер или Worker.

#### Top-level await

`await` на верхнем уровне разрешён только в ES module. Он задерживает выполнение модулей, которые зависят от текущего:

```js
// config.js
export const config = await loadConfig();
```

Это удобно для обязательной инициализации, но медленная операция задерживает весь зависимый граф модулей. Для необязательных данных часто понятнее экспортировать `async`-функцию и явно показать состояние загрузки.

#### Где применяется во frontend

- Последовательная отправка формы: проверить данные, отправить запрос, обработать ответ и обновить интерфейс.
- Параллельная загрузка независимых данных через `Promise.all`.
- Отмена запроса и проверка актуальности результата после `await` при смене маршрута или поискового запроса.
- Явный `try...catch` на уровне, который знает, какое состояние ошибки и сообщение показать пользователю.
- Динамический `import()` для ленивой загрузки модуля с обработкой состояний загрузки и ошибки.

#### Ключевые уточнения

- `async`-функция начинает выполняться синхронно и всегда возвращает Promise.
- `await` приостанавливает функцию, а не основной поток; продолжение выполняется как микрозадача.
- Даже `await` обычного значения переносит продолжение за текущий синхронный стек.
- Независимые операции нужно запустить до общего ожидания, если допустимо одновременное выполнение.
- `forEach` не ждёт `async`-callback; порядок выражают через `for...of`, `Promise.all` или пул.
- Локальный `catch` видит отклонение только того Promise, который ожидается через `await` внутри `try`.
- `async/await` не предоставляет автоматической отмены, транзакции и защиты от устаревшего результата.
- Тяжёлое вычисление остаётся синхронным независимо от наличия `async` в сигнатуре.

#### Связанные темы

- [[Конспект для подготовки/JavaScript/Promise]]
- [[Конспект для подготовки/JavaScript/Promise combinators]]
- [[Конспект для подготовки/JavaScript/Event Loop]]
- [[Конспект для подготовки/JavaScript/Обработка ошибок]]
- [[Конспект для подготовки/JavaScript/AbortController]]
- [[Конспект для подготовки/JavaScript/ES modules]]

#### Источники

- [ECMAScript: Async Function Definitions](https://tc39.es/ecma262/multipage/ecmascript-language-functions-and-classes.html#sec-async-function-definitions)
- [ECMAScript: Await](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#await)
- [MDN: async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [MDN: await](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await)
