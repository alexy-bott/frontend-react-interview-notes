---
aliases:
  - Controlled и uncontrolled компоненты
  - Controlled input
  - Uncontrolled input
  - Управляемые и неуправляемые компоненты
---

#### Быстрый ответ

Управляемое поле (controlled input) получает текущее значение из React через `value` или `checked` и сообщает об изменении через `onChange`. Источник истины находится в props/state владельца, поэтому React может сразу валидировать ввод, менять связанный UI или синхронизировать значение с URL.

Неуправляемое поле (uncontrolled input) хранит текущее значение в DOM. React может задать только начальное значение через `defaultValue` или `defaultChecked`, а актуальные данные читаются при необходимости через `FormData` или ref. Поле не должно переключаться между режимами в течение своей жизни: строковый controlled input с самого начала получает строку, а checkbox - boolean в `checked`.

#### Ключевая схема

| Аспект | Controlled | Uncontrolled |
| --- | --- | --- |
| Источник текущего значения | React props/state | DOM-элемент |
| Текстовое поле | `value` + `onChange` | `defaultValue` или нативное начальное значение |
| Checkbox/radio | `checked` + `onChange` | `defaultChecked` |
| Чтение значения | из state владельца | `FormData`, submit event или ref |
| Программное изменение | обновить state/prop | DOM API, `form.reset()` или remount |
| Типичный случай | значение влияет на UI при вводе | значение требуется преимущественно при submit |

#### Базовая модель

Controlled-компонент получает значение снаружи и сообщает о намерении его изменить. Сам input не становится владельцем данных: после `onChange` владелец обновляет state, React рендерит новое `value`, и DOM отражает его.

Uncontrolled input после mount управляется браузером. Изменение `defaultValue` не заменяет уже введённый пользователем текст. Если родитель должен программно менять текущее значение после mount, поле делают controlled либо явно сбрасывают форму.

Контроль может находиться не только в локальном `useState`. Значение может приходить от родителя, form-библиотеки или store. Критерий - кто задаёт текущее значение, а не где физически вызван Hook.

#### Развернутый ответ

##### Когда нужен controlled input

Controlled-режим подходит, когда каждый ввод должен немедленно участвовать в логике React: фильтровать список, менять preview, включать зависимые поля, применять маску или синхронизироваться с URL. Владелец всегда знает актуальное значение и может передать его нескольким компонентам.

Цена зависит от структуры компонента, а не только от режима. Если state большой формы хранится в её верхнем компоненте, каждый символ может рендерить всё поддерево. Colocation, разделение полей и form-библиотека могут ограничить эту работу. Controlled-форма не обязана быть медленной.

##### Когда подходит uncontrolled input

Uncontrolled-режим удобен, когда браузер может хранить значение до submit и React не должен реагировать на каждый символ. Нативный `FormData` читает значения элементов с `name`, а `form.reset()` возвращает их к initial/default values.

`<input type="file">` является uncontrolled: browser API не позволяет приложению программно установить выбранный файл через `value`. Выбранные файлы читаются из `input.files` или `FormData`.

##### Переключение режима

Текстовый input становится controlled, когда получает определённый `value`; checkbox и radio - когда получают `checked`. В controlled-режиме текущее значение задаёт React, а в uncontrolled-режиме его хранит DOM.

Один input не должен менять владельца данных в течение своей жизни. Переход от `value={undefined}` к строке переключает поле из uncontrolled в controlled, нарушает единый источник истины и вызывает предупреждение React. Поэтому начальное controlled-значение задают как `""` для текста и `false` для checkbox.

Передача `value` без `onChange` делает поле read-only. Это допустимо только намеренно с `readOnly`; иначе пользователь видит редактируемый элемент, значение которого React немедленно возвращает назад.

##### Controlled и uncontrolled как общий паттерн

Термины применяются не только к native input. Например, controlled modal получает `open` и `onOpenChange`, а uncontrolled modal хранит состояние внутри и принимает `defaultOpen`. Хороший reusable-компонент явно документирует оба режима и не смешивает внутренний state с внешним `open` без определённого приоритета.

#### Пример

Имя является controlled, потому что сразу отображается в preview. Email остаётся uncontrolled и читается через `FormData` при submit.

```tsx
import { type FormEvent, useState } from "react";

export default function ProfileForm() {
  const [name, setName] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") ?? "");

    console.log({ name, email });
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Name
        <input
          name="name"
          value={name}
          onChange={event => setName(event.target.value)}
        />
      </label>

      <p>Preview: {name || "Anonymous"}</p>

      <label>
        Email
        <input name="email" type="email" defaultValue="user@example.com" />
      </label>

      <button type="submit">Save</button>
    </form>
  );
}
```

Изменение `name` обновляет React state и preview. Email изменяется в DOM без отдельного state; его актуальное значение появляется в `FormData` при отправке формы.

#### Где применяется во frontend

| Ситуация | Подход | Причина |
| --- | --- | --- |
| Search input фильтрует список | controlled | каждый символ меняет связанный UI |
| Checkbox включает дополнительные поля | controlled через `checked` | React должен сразу изменить структуру формы |
| Простая форма отправляется нативно | uncontrolled + `FormData` | значения нужны в момент submit |
| Большая форма с React Hook Form | преимущественно подписки библиотеки/uncontrolled | отдельные поля обновляются без render всей формы |
| File input | uncontrolled | выбранными файлами управляет браузер |
| Reusable Dialog | `open`/`onOpenChange` или `defaultOpen` | компонент явно поддерживает внешний или внутренний owner state |

#### Ключевые уточнения

- Controlled означает внешний источник текущего значения, а не обязательно локальный `useState`.
- Для текста используется `value`, для checkbox и radio - `checked`.
- `defaultValue` и `defaultChecked` задают начальное значение, но не управляют полем после mount.
- Режим поля сохраняется на протяжении его жизни; `undefined` не используют как начальное controlled-значение.
- Производительность формы зависит от границ state и подписок, поэтому uncontrolled не является автоматически лучшим выбором.

#### Связанные темы

- [[Конспект для подготовки/React/useRef]]
- [[Конспект для подготовки/React/Состояние в React]]
- [[Конспект для подготовки/HTML/Формы]]
- [[Конспект для подготовки/Forms/Controlled uncontrolled и FormData]]
- [[Конспект для подготовки/Forms/React Hook Form]]

#### Источники

- [React 18: input](https://18.react.dev/reference/react-dom/components/input)
- [React 18: Sharing State Between Components](https://18.react.dev/learn/sharing-state-between-components)
- [MDN: FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
