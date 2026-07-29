# ArrayBuffer TypedArray DataView

<!-- NOTE-NAV-TOP:START -->
[← RegExp](<./RegExp.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [ES modules →](<./ES modules.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`ArrayBuffer` представляет область бинарной памяти в байтах. Сам буфер не задаёт числовую интерпретацию; данные читают и записывают через представление (`view`).

TypedArray, например `Uint8Array` или `Float32Array`, интерпретирует буфер как плотную последовательность элементов одного числового типа с порядком байтов платформы. `DataView` читает разные типы по произвольным смещениям и позволяет явно выбрать порядок байтов (`endianness`).

Один буфер может иметь несколько представлений без копирования. Изменение байтов через одно представление видно другим. `slice` буфера создаёт копию, а передача переносимого объекта в Worker перемещает владение и отсоединяет исходный буфер.

Эти API нужны для файлов, Canvas, аудио, бинарных кадров WebSocket, кодеков, криптографии и разбора протоколов. Для обычного списка предметных объектов используют Array, а не TypedArray.

## Ключевая схема

```text
ArrayBuffer: необработанные байты
├─ Uint8Array view      → байты 0..255
├─ Uint32Array view     → 32-битные беззнаковые целые
├─ Float32Array view    → 32-битные числа с плавающей точкой
└─ DataView             → разные типы + явный порядок байтов
```

```js
const buffer = new ArrayBuffer(8);
const bytes = new Uint8Array(buffer);
const view = new DataView(buffer);
```

## Буфер и представление

```js
const buffer = new ArrayBuffer(4);
const bytes = new Uint8Array(buffer);

bytes[0] = 255;
console.log(buffer.byteLength); // 4
console.log(bytes.byteLength);  // 4
console.log(bytes.length);      // 4 элемента
```

Буфер задаёт память, а представление - способ её интерпретации. TypedArray имеет `length` в элементах и `byteLength` в байтах.

Представление может покрывать только часть буфера:

```js
const buffer = new ArrayBuffer(16);
const middle = new Uint8Array(buffer, 4, 8);

console.log(middle.byteOffset); // 4
console.log(middle.byteLength); // 8
```

Смещение должно соответствовать выравниванию типа элемента: например, `Uint32Array` требует смещение, кратное четырём.

## TypedArray types

| Представление | Элемент |
| --- | --- |
| `Int8Array`, `Uint8Array`, `Uint8ClampedArray` | 8-bit integers |
| `Int16Array`, `Uint16Array` | 16-bit integers |
| `Int32Array`, `Uint32Array` | 32-bit integers |
| `BigInt64Array`, `BigUint64Array` | 64-bit BigInt integers |
| `Float32Array`, `Float64Array` | floating-point numbers |

Длина TypedArray обычно фиксирована размером представления. У неё нет `push` и `pop`: для другой длины создают новый буфер и представление.

Присваивание преобразует значение к типу элемента. Переполнение целого может привести к остатку по модулю диапазона, а `Uint8ClampedArray` ограничивает значение диапазоном и применяет специальные правила округления.

```js
const values = new Uint8Array(1);
values[0] = 300;
console.log(values[0]); // 44
```

Это не проверка корректности. Перед записью поля протокола проверяют допустимый диапазон.

## Общая память представлений

```js
const buffer = new ArrayBuffer(4);
const bytes = new Uint8Array(buffer);
const words = new Uint32Array(buffer);

bytes[0] = 1;
console.log(words[0]); // зависит от порядка байтов платформы
```

Представления не копируют данные и работают с одними байтами. Последняя строка зависит от порядка байтов платформы, поэтому TypedArray не подходит для разбора протокола с фиксированным сетевым порядком байтов без отдельного контроля.

## `DataView` и порядок байтов

Порядок байтов определяет расположение байтов многобайтового числа. Методы DataView принимают флаг `littleEndian`; без него используется порядок big-endian.

```js
const buffer = new ArrayBuffer(4);
const view = new DataView(buffer);

view.setUint32(0, 0x12345678, false); // big-endian

view.getUint16(0, false); // 0x1234
view.getUint16(2, false); // 0x5678
```

DataView подходит для бинарного заголовка, где рядом лежат `uint16`, `uint32`, число с плавающей точкой и флаги. TypedArray удобнее для однородного набора числовых данных.

Выход за границы представления выбрасывает `RangeError`.

## Копия, представление и перенос

```js
const original = new Uint8Array([1, 2, 3]);

const sharedView = original.subarray(1);
const copied = original.slice(1);
```

`subarray` создаёт представление того же буфера. `slice` TypedArray создаёт новый TypedArray с копией элементов.

```js
sharedView[0] = 9;
console.log(original[1]); // 9

copied[0] = 7;
console.log(original[1]); // 9
```

При `postMessage` ArrayBuffer обычно копируется по алгоритму structured clone. Список переноса перемещает лежащую в основе память без копирования:

```js
worker.postMessage({ buffer }, [buffer]);
console.log(buffer.byteLength); // 0 после отсоединения
```

После переноса отправитель больше не может использовать буфер. Переход владения должен быть явным в архитектуре.

## Кодирование текста

Строка и байты - разные представления:

```js
const bytes = new TextEncoder().encode("Привет");
// Uint8Array UTF-8

const text = new TextDecoder("utf-8").decode(bytes);
```

Нельзя считать каждый JavaScript-символ одним байтом. UTF-8 использует переменную длину, а строковый API JavaScript основан на кодовых единицах UTF-16.

Для потокового декодирования `TextDecoder` поддерживает параметр `{ stream: true }`, чтобы многобайтовый символ, разделённый между частями данных, не повреждался.

## Fetch, files и WebSocket

```js
const response = await fetch("/file.bin");
const buffer = await response.arrayBuffer();
const header = new DataView(buffer, 0, 16);
```

Для большого ответа чтение всего ArrayBuffer сразу увеличивает пиковое потребление памяти. Если протокол позволяет, данные обрабатывают частями через `response.body`.

`Blob` представляет неизменяемую последовательность байтов и удобен для файлов, скачивания и object URL. `File` добавляет имя и метаданные. `FileReader` - старый событийный API; современные методы Blob `arrayBuffer()`, `text()` и streams часто проще.

Свойство WebSocket `binaryType` определяет получение бинарного сообщения как `Blob` или `ArrayBuffer`.

## SharedArrayBuffer и Atomics

`SharedArrayBuffer` позволяет нескольким агентам, например Window и Worker, видеть одну область памяти. Для синхронизации используются `Atomics`; обычные чтения и записи сами по себе не образуют безопасный протокол конкурентного доступа.

Из-за риска атак по побочным каналам браузер требует заголовки cross-origin isolation для доступности SharedArrayBuffer. Это специальный инструмент для чувствительных к производительности алгоритмов, а не обычный способ обмена состоянием с Worker.

Передача сообщений с переносом владения обычно проще и безопаснее по модели данных.

## Где применяется во frontend

- Worker получает большой ArrayBuffer через `transfer` без копирования.
- Parser читает бинарный протокол через DataView с явным порядком байтов.
- Canvas, аудио и ML API используют TypedArrays для плотных числовых данных.
- TextEncoder и TextDecoder переводят между строкой и байтами UTF-8.
- Поток ответа Fetch обрабатывает большие данные частями вместо полной загрузки в память.
- Blob и File используются для загрузки, предпросмотра и скачивания файлов.

## Ключевые уточнения

- ArrayBuffer хранит байты, а представление задаёт их числовую интерпретацию.
- Несколько представлений одного буфера разделяют память; изменение видно всем.
- TypedArray имеет фиксированный тип элемента и не является обычным динамическим массивом.
- DataView нужен для полей разных типов и явного порядка байтов.
- `subarray` разделяет буфер, а `slice` копирует элементы.
- Перенос отсоединяет исходный буфер и меняет владельца.
- Длина строки не равна длине в байтах; кодирование выполняется явно.
- Общая память требует Atomics и изоляции безопасности, а не только общего буфера.

## Связанные темы

- [Строки Unicode и кодировки](<./Строки Unicode и кодировки.md>)
- [Копирование объектов](<./Копирование объектов.md>)
- [Fetch и работа с API](<./Fetch и работа с API.md>)
- [Web Workers](<../Web Basics/Web Workers.md>)
- [WebSocket](<../Web Basics/WebSocket.md>)

## Источники

- [ECMAScript: Structured Data](https://tc39.es/ecma262/multipage/structured-data.html)
- [MDN: ArrayBuffer](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer)
- [MDN: TypedArray](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypedArray)
- [MDN: DataView](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/DataView)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← RegExp](<./RegExp.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [ES modules →](<./ES modules.md>)
<!-- NOTE-NAV-BOTTOM:END -->
