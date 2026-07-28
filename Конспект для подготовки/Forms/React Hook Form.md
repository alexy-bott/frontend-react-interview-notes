---
aliases:
  - React Hook Form
  - react-hook-form
  - useForm
  - register
---

#### Ответ на 60 секунд

React Hook Form - это библиотека для управления формами в React, которая делает ставку на uncontrolled inputs, регистрацию полей и точечные подписки на form state. Главные API: `useForm`, `register`, `handleSubmit`, `formState`, `watch`, `setValue`, `reset`, `setError`, `clearErrors`. Основная польза - меньше ручного boilerplate для value/onChange/errors и меньше лишних ререндеров в больших формах.

Базовый поток такой: `useForm` создаёт form controller, `register` подключает нативные поля, `handleSubmit` валидирует форму и отдаёт проверенные values, `formState.errors` хранит ошибки, `reset` сбрасывает форму. Для кастомных controlled-компонентов используют `Controller` или `useController`.

#### Ключевая схема

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

#### Развернутый ответ

React Hook Form снижает количество ререндеров за счёт uncontrolled inputs и подписок. Нативный input хранит текущее значение в DOM, а библиотека собирает значения через registration и form controller. Родительский компонент не обязан перерендериваться на каждый символ; обновляются только подписанные части `formState` или watched values.

`register("fieldName")` подключает нативное поле к форме: возвращает `name`, `ref`, handlers и validation rules. `handleSubmit` оборачивает submit handler, запускает validation и вызывает success callback только при валидной форме. Для невалидной формы можно передать error callback.

`watch` и `useWatch` нужны, когда значение поля влияет на UI до submit: условное поле, live preview, зависимая валидация, расчёт суммы. Глобальный `watch` на всю форму может увеличить ререндеры и связать UI с лишними values, поэтому подписку делают как можно уже.

`setError` используют для backend/business errors: email уже занят, неверный пароль, конфликт версии, превышен лимит, правило доступно только серверу. Field errors маппят на конкретные поля, а form-level error - на общий блок или `root`.

`defaultValues` критичны для корректного dirty state и reset. Для edit-form после загрузки данных с backend форму reset-ят актуальными server values, чтобы `isDirty` снова отражал реальные изменения пользователя.

`shouldUnregister` влияет на условные поля. По умолчанию значение размонтированного поля может сохраняться в form state; с `shouldUnregister: true` поведение ближе к нативной форме: unmounted input удаляется из submission data. Это важно для wizard-форм, conditional sections и DTO, где скрытое поле не должно отправляться.

> [!faq]+ Уточнения
> - RHF часто ререндерит меньше, потому что значения нативных inputs живут в DOM.
> - `register` подключает обычные inputs, `Controller` - controlled/custom components.
> - `handleSubmit` запускает validation и разделяет success/error callbacks.
> - `watch` создаёт подписку; для точечных мест используют `useWatch`.
> - `setError` нужен для backend field errors и form-level errors.
> - `shouldUnregister` выбирают осознанно для conditional fields.

#### Пример

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
      <input id="email" type="email" {...register("email", { required: "Email is required" })} />
      {errors.email && <p role="alert">{errors.email.message}</p>}

      <label htmlFor="password">Password</label>
      <input id="password" type="password" {...register("password", { required: "Password is required" })} />
      {errors.password && <p role="alert">{errors.password.message}</p>}

      <button type="submit" disabled={isSubmitting}>
        Sign in
      </button>
    </form>
  );
}
```

#### Частые ошибки

- Использовать React Hook Form как обычный controlled state manager без причины.
- Забывать `defaultValues`, а потом получать некорректный `isDirty` или reset.
- Подписывать весь компонент на слишком много `formState` и удивляться ререндерам.
- Использовать `watch` глобально там, где достаточно `getValues` или `useWatch`.
- Не маппить server errors через `setError`.
- Не связывать ошибки с полями доступным образом.

#### Связанные темы

- [[Конспект для подготовки/Forms/Controller и кастомные компоненты]]
- [[Конспект для подготовки/Forms/Валидация форм]]
- [[Конспект для подготовки/Forms/Server errors и async validation]]
- [[Конспект для подготовки/Forms/Form state и submit lifecycle]]
- [[Конспект для подготовки/Forms/Controlled uncontrolled и FormData]]
- [[Конспект для подготовки/React/Controlled и uncontrolled компоненты]]

#### Источники

- [React Hook Form GitHub](https://github.com/react-hook-form/react-hook-form)
- [React Hook Form: useForm docs](https://react-hook-form.com/docs/useform)
- [React Hook Form: register docs](https://react-hook-form.com/docs/useform/register)
