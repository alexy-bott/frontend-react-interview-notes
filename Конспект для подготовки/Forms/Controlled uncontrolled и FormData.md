---
aliases:
  - controlled forms
  - uncontrolled forms
  - FormData в React
  - controlled uncontrolled forms
---

#### Ответ на 60 секунд

Controlled form хранит значения в React state: input получает `value`, а `onChange` синхронно обновляет состояние. Это удобно, когда ввод должен сразу влиять на UI: live search, mask, dependent fields, calculated values, validation на каждом изменении. Минус - каждый ввод может вызывать React-render.

Uncontrolled form хранит значения в DOM. React задаёт начальные значения через `defaultValue`/`defaultChecked`, а данные читает при submit через `FormData`, ref или form library. Это проще и часто производительнее для больших форм, где значения не нужны React на каждый символ. Главное - не смешивать режимы одного поля: input не должен переключаться между controlled и uncontrolled за время жизни.

#### Ключевая схема

| Подход | Source of truth | Читать значение | Когда выбирать |
| --- | --- | --- | --- |
| Controlled | React state | state | live UI, masks, dependent fields |
| Uncontrolled | DOM | `FormData`, ref | простые/большие формы, submit-only данные |
| React Hook Form | DOM + form registry | `handleSubmit`, `watch`, `getValues` | большие формы с validation/errors |
| FormData | DOM form controls | `new FormData(form)` | нативный submit, file upload |

#### Развернутый ответ

Controlled подход оправдан, когда значение поля нужно приложению прямо сейчас: заблокировать кнопку, посчитать стоимость, отфильтровать список, показать live preview, применить маску, синхронизировать с URL/store или менять другие поля. Источник правды находится в React state, поэтому каждый ввод может вызывать render.

Uncontrolled подход подходит, когда значения нужны только при submit или форма большая. DOM уже хранит текущее значение, а React читает его через `FormData`, ref или form library. Это снижает количество лишних renders и хорошо сочетается с нативным поведением формы.

`FormData` собирает значения controls по `name`. Поле без `name` не попадёт в payload. Disabled controls в обычную отправку не включаются. File inputs естественно работают через `FormData`, потому что туда попадают `File` и `Blob`.

Режим input должен быть стабильным. Если поле сначала без `value`, а потом получает `value`, React видит переключение uncontrolled -> controlled. Частая причина - `undefined`. Controlled input требует стабильного значения, например `value={name ?? ""}`.

Reset зависит от режима. Controlled форму сбрасывают через state. Uncontrolled форму можно сбросить через `form.reset()`, смену `key` или методы form library. В React Hook Form обычно используют `reset()` с актуальными значениями.

> [!faq]+ Уточнения
> - Controlled нужен для live UI, masks, derived values, URL/store sync.
> - Uncontrolled подходит для submit-only данных и больших форм.
> - `FormData` требует `name` у полей.
> - Disabled controls не попадают в form submission.
> - Controlled поле не должно получать `undefined` как `value`.

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

#### Частые ошибки

- Передавать `value` без `onChange` и делать input read-only.
- Использовать `value={undefined}` для controlled поля.
- Ожидать, что изменение `defaultValue` обновит значение после mount.
- Забывать `name` и не получать поле в `FormData`.
- Делать большую форму controlled на верхнем уровне без мемоизации/разбиения.
- Использовать `disabled`, когда значение всё равно должно отправиться.

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
