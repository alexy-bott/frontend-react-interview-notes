---
aliases:
  - RHF Controller
  - Controller react-hook-form
  - кастомные поля формы
  - Radix UI forms
---

#### Быстрый ответ

`Controller` адаптирует controlled component к React Hook Form, когда обычный `register` нельзя подключить к native `ref`/events. Он получает field state от RHF и переводит его в API компонента: `value`, change callback, `onBlur`, `name`, `disabled` и focusable `ref`. Это типично для Radix Select, DatePicker, masked input и composite controls.

Идея простая: React Hook Form хранит поле в своём form controller, а `Controller` отдаёт кастомному компоненту `value`, `onChange`, `onBlur`, `name` и `ref`. Нативные input/select/textarea подключают через `register`; controlled/custom UI - через `Controller` или `useController`.

#### Ключевая схема

| Компонент | Обычно подключать |
| --- | --- |
| `<input>` | `register` |
| `<textarea>` | `register` |
| native `<select>` | `register` |
| Radix Select | `Controller` |
| Radix Checkbox | `Controller` или adapter |
| DatePicker | `Controller` |
| Masked input | зависит от API, часто `Controller` |
| Custom file uploader | adapter + `setValue`/`Controller` |

#### Базовая модель

`register` ожидает нативную механику поля: `ref`, `name`, `onChange`, `onBlur` и значение из DOM/input event. Кастомный компонент может не иметь реального input, не отдавать ref наружу или использовать callback вроде `onValueChange`. В таких случаях нужен `Controller`, `useController` или adapter, который переводит API компонента в API формы.

Adapter-компонент должен явно прокинуть `value`, change handler, blur handler, disabled/error state, ref/focus target и доступные атрибуты. Control без label, keyboard support, aria-связей и focus management теряет доступность, даже если снаружи выглядит как обычное поле.

#### Развернутый ответ

Radix Select удобно подключать через `Controller`, потому что он controlled через `value` и `onValueChange`. `field.value` передаётся в `value`, `field.onChange` - в `onValueChange`, а ошибка и description связываются с trigger через доступные атрибуты.

Checkbox требует проверки типа значения. Нативный checkbox в form submission может дать `"on"`, controlled checkbox обычно работает с boolean, а Radix Checkbox поддерживает `checked`, `onCheckedChange` и indeterminate-состояние. Adapter должен привести это к типу, который ожидает schema и DTO.

`field.ref` направляют на элемент, который реально можно сфокусировать при validation error. `field.onBlur` обязателен, если validation/touched state использует blur. Компонент не регистрируют второй раз через `{...register(name)}`: `Controller` уже выполняет registration.

Общий `FormField` может связывать label, control, description и error message, но не должен скрывать data conversion. UI Select часто хранит строку, DatePicker — `Date | null`, checkbox — `boolean | "indeterminate"`, а API DTO ожидает другое представление. Conversion выполняют в adapter или mapper и покрывают test.

#### Пример

```tsx
import { Controller, useForm } from "react-hook-form";
import { Select } from "radix-ui";

type FormValues = {
  role: "user" | "admin";
};

function RoleForm() {
  const { control, handleSubmit } = useForm<FormValues>({
    defaultValues: {
      role: "user",
    },
  });

  return (
    <form onSubmit={handleSubmit(console.log)}>
      <Controller
        name="role"
        control={control}
        rules={{ required: "Role is required" }}
        render={({ field, fieldState }) => (
          <div>
            <span id="role-label">Role</span>
            <Select.Root
              name={field.name}
              value={field.value}
              disabled={field.disabled}
              onValueChange={field.onChange}
            >
              <Select.Trigger
                ref={field.ref}
                onBlur={field.onBlur}
                aria-labelledby="role-label"
                aria-invalid={fieldState.invalid}
                aria-describedby={fieldState.error ? "role-error" : undefined}
              >
                <Select.Value />
              </Select.Trigger>
              <Select.Content>
                <Select.Item value="user">
                  <Select.ItemText>User</Select.ItemText>
                </Select.Item>
                <Select.Item value="admin">
                  <Select.ItemText>Admin</Select.ItemText>
                </Select.Item>
              </Select.Content>
            </Select.Root>
            {fieldState.error && <p id="role-error">{fieldState.error.message}</p>}
          </div>
        )}
      />

      <button type="submit">Save</button>
    </form>
  );
}
```

#### Ключевые уточнения

- Native input подключают через `register`; `Controller` добавляют только при несовместимом controlled API.
- `Controller` уже регистрирует field, поэтому повторный `{...register(name)}` создаёт конфликт handlers/refs.
- `value`/`defaultValue` не должны быть `undefined`; empty representation согласуют с component и schema.
- `onBlur` передают для touched/onBlur validation, `ref` — на фактический focus target.
- Custom control сохраняет accessible name, keyboard behavior и связь с description/error.
- Adapter явно преобразует UI value в form/domain type, включая checkbox indeterminate и date/timezone semantics.
- `shouldUnregister` осторожно используют вместе с reordered field arrays, где unmount/remount является частью operation.

#### Связанные темы

- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Forms/Валидация форм]]
- [[Конспект для подготовки/Forms/Form state и submit lifecycle]]
- [[Конспект для подготовки/React/Radix UI]]
- [[Конспект для подготовки/HTML/Accessibility]]
- [[Конспект для подготовки/Accessibility/Forms errors и accessibility]]
- [[Конспект для подготовки/React/Portal]]

#### Источники

- [React Hook Form: Controller docs](https://react-hook-form.com/docs/usecontroller/controller)
- [Radix UI: Select](https://www.radix-ui.com/primitives/docs/components/select)
- [Radix UI: Checkbox](https://www.radix-ui.com/primitives/docs/components/checkbox)
- [Radix UI: Form](https://www.radix-ui.com/primitives/docs/components/form)
