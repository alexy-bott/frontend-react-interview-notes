---
aliases:
  - RHF Controller
  - Controller react-hook-form
  - кастомные поля формы
  - Radix UI forms
---

#### Ответ на 60 секунд

`Controller` в React Hook Form нужен для компонентов, которые не похожи на обычный `<input {...register(...)}`. Например, Radix Select, custom DatePicker, masked input, complex checkbox group или компонент, который отдаёт значение через `onValueChange`, а не через стандартный `event.target.value`.

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

#### Развернутый ответ

`register` ожидает нативную механику поля: `ref`, `name`, `onChange`, `onBlur` и значение из DOM/input event. Кастомный компонент может не иметь реального input, не отдавать ref наружу или использовать callback вроде `onValueChange`. В таких случаях нужен `Controller`, `useController` или adapter, который переводит API компонента в API формы.

Adapter-компонент должен явно прокинуть `value`, change handler, blur handler, disabled/error state, ref/focus target и доступные атрибуты. Control без label, keyboard support, aria-связей и focus management теряет доступность, даже если снаружи выглядит как обычное поле.

Radix Select удобно подключать через `Controller`, потому что он controlled через `value` и `onValueChange`. `field.value` передаётся в `value`, `field.onChange` - в `onValueChange`, а ошибка и description связываются с trigger через доступные атрибуты.

Checkbox требует проверки типа значения. Нативный checkbox в form submission может дать `"on"`, controlled checkbox обычно работает с boolean, а Radix Checkbox поддерживает `checked`, `onCheckedChange` и indeterminate-состояние. Adapter должен привести это к типу, который ожидает schema и DTO.

Общий `FormField` может связывать `label`, control, description и error message, но не должен скрывать логику настолько, что нельзя понять, какое поле, какой value и какой payload реально отправляются. Общий wrapper полезен после появления повторяющегося паттерна.

> [!faq]+ Уточнения
> - `register` подходит для нативных inputs, `Controller` - для controlled/custom UI.
> - Adapter переводит API компонента в `value/onChange/onBlur/ref` и связывает ошибку через `aria-describedby`.
> - Custom control должен сохранять label, focus, keyboard и aria-связи.
> - Checkbox/select values нужно приводить к типу schema/DTO.
> - Общий Field wrapper полезен, если не скрывает контракт поля.

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
        render={({ field, fieldState }) => (
          <Select.Root value={field.value} onValueChange={field.onChange}>
            <Select.Trigger
              ref={field.ref}
              aria-label="Role"
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
            {fieldState.error && (
              <p id="role-error" role="alert">
                {fieldState.error.message}
              </p>
            )}
          </Select.Root>
        )}
      />

      <button type="submit">Save</button>
    </form>
  );
}
```

#### Частые ошибки

- Использовать `Controller` для обычного input без причины.
- Не передавать `onBlur`, если форма использует touched/onBlur validation.
- Не задавать `defaultValues` для controlled custom field.
- Терять ref/focus management, из-за чего `setFocus` или focus-on-error не работают.
- Не связывать label/error с custom control.
- Неправильно преобразовывать value checkbox/select и отправлять не тот тип.

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
