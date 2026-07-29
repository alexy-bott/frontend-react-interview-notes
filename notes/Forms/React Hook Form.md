# React Hook Form

<!-- NOTE-NAV-TOP:START -->
[← Controlled uncontrolled и FormData](<./Controlled uncontrolled и FormData.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Controller и кастомные компоненты →](<./Controller и кастомные компоненты.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

React Hook Form (RHF) управляет registration, values, validation, errors и submit lifecycle без отдельного React state для каждого нативного input. Нативные fields обычно остаются uncontrolled, а components подписываются только на нужные части form state. Это уменьшает boilerplate и изолирует renders в больших формах, но не заменяет HTML semantics, schema/API contract и server validation.

Базовый поток такой: `useForm` создаёт form controller, `register` подключает нативные поля, `handleSubmit` валидирует форму и отдаёт проверенные values, `formState.errors` хранит ошибки, `reset` сбрасывает форму. Для кастомных controlled-компонентов используют `Controller` или `useController`.

## Ключевая схема

| API | Зачем нужен |
| --- | --- |
| `useForm` | создать управление формой |
| `register` | подключить нативный input/select/textarea |
| `handleSubmit` | обработать submit после validation |
| `formState.errors` | ошибки полей |
| `watch` | подписаться на значения |
| `getValues` | прочитать значения без подписки |
| `setValue` | программно изменить поле |
| `reset` | сбросить values и state |
| `setError` | показать server/manual error |
| `Controller` | подключить controlled/custom component |

## Базовая модель

React Hook Form снижает количество ререндеров за счёт uncontrolled inputs и подписок. Нативный input хранит текущее значение в DOM, а библиотека собирает значения через registration и form controller. Родительский компонент не обязан перерендериваться на каждый символ; обновляются только подписанные части `formState` или watched values.

`register("fieldName")` подключает нативное поле к форме: возвращает `name`, `ref`, handlers и validation rules. `handleSubmit` оборачивает submit handler, запускает validation и вызывает success callback только при валидной форме. Для невалидной формы можно передать error callback.

## Развернутый ответ

`formState` обёрнут в Proxy и включает подписку при чтении свойства во время render. Если component читает только `errors.email` и `isSubmitting`, ему не нужен render на каждое изменение остальных fields. `useFormState` и `useWatch` позволяют перенести подписку ближе к конкретному field/section. Глобальный `watch()` всей формы снова делает dependency широкой.

`watch` и `useWatch` нужны, когда значение поля влияет на UI до submit: conditional field, live preview, dependent validation, расчёт суммы. `getValues` только читает snapshot и не создаёт subscription; он подходит для event handler, но не заставит UI обновляться.

`setError` используют для backend/business errors: email уже занят, неверный пароль, конфликт версии, превышен лимит, правило доступно только серверу. Field errors маппят на конкретные поля, а form-level error - на общий блок или `root`.

`defaultValues` являются baseline для dirty comparison и кешируются form instance. Для edit-form данные либо передают как async `defaultValues`, либо после загрузки вызывают `reset(serverValues)`. Значение `undefined` не используют как default controlled field: оно конфликтует с ожидаемым стабильным value.

`shouldUnregister` влияет на условные поля. По умолчанию значение размонтированного поля может сохраняться в form state; с `shouldUnregister: true` поведение ближе к нативной форме: unmounted input удаляется из submission data. Это важно для wizard-форм, conditional sections и DTO, где скрытое поле не должно отправляться.

`handleSubmit` управляет validation и `isSubmitting`, но не скрывает exception из async submit callback. Ожидаемые API errors перехватывают, переводят в field/root errors и сохраняют введённые values; неожиданные ошибки передают application error boundary/logging layer.

## Пример

```tsx
import { useForm } from "react-hook-form";

type LoginFormValues = {
  email: string;
  password: string;
};

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (values: LoginFormValues) => {
    await login(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        aria-invalid={Boolean(errors.email)}
        aria-describedby={errors.email ? "email-error" : undefined}
        {...register("email", { required: "Email is required" })}
      />
      {errors.email && <p id="email-error">{errors.email.message}</p>}

      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        aria-invalid={Boolean(errors.password)}
        aria-describedby={errors.password ? "password-error" : undefined}
        {...register("password", { required: "Password is required" })}
      />
      {errors.password && <p id="password-error">{errors.password.message}</p>}

      <button type="submit" disabled={isSubmitting}>
        Sign in
      </button>
    </form>
  );
}
```

## Ключевые уточнения

- `register` подключает native field, `Controller`/`useController` адаптирует controlled custom component.
- Производительность RHF опирается на DOM values и узкие subscriptions; глобальный `watch` может вернуть широкие renders.
- `defaultValues` задают baseline для `isDirty`; после загрузки edit data этот baseline обновляют через `reset`.
- `getValues` читает snapshot без subscription, `useWatch` обновляет UI при изменении выбранных fields.
- Validation mode выбирают по UX: проверка каждого `onChange` даёт ранний feedback, но запускает больше работы.
- `setError` отображает server field/root error, но server response сначала маппят в стабильный frontend contract.
- `handleSubmit` не заменяет обработку rejected request и неожиданных exceptions.

## Связанные темы

- [Controller и кастомные компоненты](<./Controller и кастомные компоненты.md>)
- [Валидация форм](<./Валидация форм.md>)
- [Server errors и async validation](<./Server errors и async validation.md>)
- [Form state и submit lifecycle](<./Form state и submit lifecycle.md>)
- [Controlled uncontrolled и FormData](<./Controlled uncontrolled и FormData.md>)
- [Controlled и uncontrolled компоненты](<../React/Controlled и uncontrolled компоненты.md>)

## Источники

- [React Hook Form GitHub](https://github.com/react-hook-form/react-hook-form)
- [React Hook Form: useForm docs](https://react-hook-form.com/docs/useform)
- [React Hook Form: register docs](https://react-hook-form.com/docs/useform/register)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Controlled uncontrolled и FormData](<./Controlled uncontrolled и FormData.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Controller и кастомные компоненты →](<./Controller и кастомные компоненты.md>)
<!-- NOTE-NAV-BOTTOM:END -->
