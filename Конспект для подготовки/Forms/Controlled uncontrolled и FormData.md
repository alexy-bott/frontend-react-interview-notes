---
aliases:
  - controlled forms
  - uncontrolled forms
  - FormData в React
  - controlled uncontrolled forms
---

#### Быстрый ответ

Controlled field получает текущее `value`/`checked` из React state и обновляет его синхронно в `onChange`. React становится source of truth, поэтому значение удобно использовать для dependent UI, formatting и live behavior. Uncontrolled field хранит текущее значение в DOM; React задаёт initial `defaultValue`/`defaultChecked`, а данные читает при submit через `FormData`, ref или form library.

Uncontrolled form хранит значения в DOM. React задаёт начальные значения через `defaultValue`/`defaultChecked`, а данные читает при submit через `FormData`, ref или form library. Это проще и часто производительнее для больших форм, где значения не нужны React на каждый символ. Главное - не смешивать режимы одного поля: input не должен переключаться между controlled и uncontrolled за время жизни.

#### Ключевая схема

| Подход | Source of truth | Читать значение | Когда выбирать |
| --- | --- | --- | --- |
| Controlled | React state | state | live UI, masks, dependent fields |
| Uncontrolled | DOM | `FormData`, ref | простые/большие формы, submit-only данные |
| React Hook Form | DOM + form registry | `handleSubmit`, `watch`, `getValues` | большие формы с validation/errors |
| FormData | DOM form controls | `new FormData(form)` | нативный submit, file upload |

#### Базовая модель

Controlled подход оправдан, когда значение поля нужно приложению прямо сейчас: заблокировать кнопку, посчитать стоимость, отфильтровать список, показать live preview, применить маску, синхронизировать с URL/store или менять другие поля. Источник правды находится в React state, поэтому каждый ввод может вызывать render.

Uncontrolled подход подходит, когда значения нужны только при submit или форма большая. DOM уже хранит текущее значение, а React читает его через `FormData`, ref или form library. Это снижает количество лишних renders и хорошо сочетается с нативным поведением формы.

#### Развернутый ответ

`FormData` собирает successful controls по `name`. Поле без `name` и disabled control не попадут в payload; readonly field попадёт. Несколько checkbox или multi-select могут создать несколько entries с одним key, поэтому `Object.fromEntries` сохранит только последнее значение. Для таких fields используют `getAll`. File input в React остаётся uncontrolled, а `FormData` передаёт `File` без преобразования в JSON.

Режим input должен быть стабильным. Если поле сначала не получает `value`, а затем получает строку, React видит переключение uncontrolled → controlled. Controlled text input использует строку, а checkbox/radio — boolean `checked`; `undefined`/`null` не должны временно означать отсутствие control state. `defaultValue` задаёт только initial DOM value и не синхронизирует последующие prop changes.

Reset зависит от режима. Controlled форму сбрасывают через state. Uncontrolled форму можно сбросить через `form.reset()`, смену `key` или методы form library. В React Hook Form обычно используют `reset()` с актуальными значениями.

Render на каждый keystroke не делает controlled field автоматически медленным. Сначала state локализуют рядом с form, не перерисовывают тяжёлый unrelated subtree и измеряют. Uncontrolled/RHF особенно полезны, когда большое число fields не влияет на UI до submit, но выбор определяется data flow, а не только количеством inputs.

#### Пример

Controlled:

```tsx
const [email, setEmail] = useState("");

<input
  name="email"
  value={email}
  onChange={event => setEmail(event.target.value)}
/>;
```

Uncontrolled + `FormData`:

```tsx
function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
  event.preventDefault();

  const formData = new FormData(event.currentTarget);
  const payload = Object.fromEntries(formData.entries());

  console.log(payload);
}

return (
  <form onSubmit={handleSubmit}>
    <input name="email" type="email" defaultValue="" />
    <button type="submit">Save</button>
  </form>
);
```

#### Ключевые уточнения

- Controlled field требует синхронного `onChange`; иначе browser не сможет отразить ввод и поле станет read-only.
- Text value и checkbox/radio checked должны иметь стабильный тип на всём lifecycle.
- `defaultValue` задаёт initial value uncontrolled field, а не команду обновить DOM после mount.
- Disabled control не отправляется; readonly control отправляется, но остаётся доступным для focus/selection.
- Repeated names читают через `FormData.getAll`, иначе часть values можно потерять.
- File input контролируется пользователем/browser и читается как `FileList`/`FormData`, а не через programmatic `value`.
- Controlled/uncontrolled выбирают по тому, когда React нужен current value и кто должен быть source of truth.

#### Связанные темы

- [[Конспект для подготовки/React/Controlled и uncontrolled компоненты]]
- [[Конспект для подготовки/HTML/Формы]]
- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Forms/Form state и submit lifecycle]]
- [[Конспект для подготовки/React/Состояние в React]]

#### Источники

- [React: input](https://react.dev/reference/react-dom/components/input)
- [React: select](https://react.dev/reference/react-dom/components/select)
- [MDN: FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
