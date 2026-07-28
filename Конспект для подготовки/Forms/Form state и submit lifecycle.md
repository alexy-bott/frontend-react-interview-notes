---
aliases:
  - formState
  - submit lifecycle
  - dirty touched errors
  - isSubmitting
---

#### Ответ на 60 секунд

Form state описывает не только значения полей, но и состояние взаимодействия: какие поля изменились, какие были посещены, есть ли ошибки, идёт ли submit, был ли submit успешным. В React Hook Form это обычно видно через `formState`: `errors`, `isDirty`, `dirtyFields`, `touchedFields`, `isSubmitting`, `isSubmitted`, `isSubmitSuccessful`, `isValid`.

Submit lifecycle в production-форме выглядит так: пользователь вводит данные, клиент валидирует, submit блокирует повторную отправку, API возвращает успех или ошибки, ошибки мапятся на поля или общий блок, при успехе форма reset-ится или переводит пользователя дальше. UX должен быть устойчивым к двойному submit, медленной сети, server errors и partial failure.

#### Ключевая схема

```text
idle
-> editing
-> validate
-> submitting
-> success | field errors | form error
-> reset | retry | navigate
```

| Состояние | Что означает |
| --- | --- |
| `errors` | ошибки validation/manual/server |
| `isDirty` | форма отличается от default values |
| `dirtyFields` | конкретные изменённые поля |
| `touchedFields` | поля, с которыми пользователь взаимодействовал |
| `isSubmitting` | submit handler сейчас выполняется |
| `isValid` | форма валидна по текущему режиму validation |
| `isSubmitSuccessful` | последний submit завершился успешно |

#### Развернутый ответ

Dirty и touched отвечают на разные вопросы. Dirty означает, что значение изменилось относительно `defaultValues`. Touched означает, что пользователь заходил в поле. Поле может быть touched, но не dirty, если пользователь сфокусировался и ушёл без изменения.

`defaultValues` нужны для корректного dirty state и reset. Для create-form это пустые начальные значения. Для edit-form их заполняют данными с backend после загрузки, а после успешного сохранения reset-ят форму новыми server values, чтобы dirty state снова стал false.

Submit lifecycle должен учитывать pending и повторную отправку. Во время `isSubmitting` submit-кнопку обычно отключают, но backend всё равно должен безопасно обрабатывать повторный запрос: idempotency, conflict detection или защита от дублей. Disabled button - UX-защита, а не гарантия безопасности.

Ошибки делят на field-level и form-level. Field error показывают рядом с полем и связывают через `aria-describedby`. Form-level error показывают над формой или в summary. После submit с ошибками полезно сфокусировать первое проблемное поле или summary.

После успеха сценарий зависит от формы. Create-form может вызвать `reset()` и показать success. Edit-form reset-ят актуальными server values. Если после submit идёт navigation, отдельный reset может быть не нужен.

Server errors входят в submit lifecycle. `422` обычно возвращается в поля, `409/412` требует conflict-сценария, `500/503` обычно становится form-level error с retry. Это разные UX-сценарии, поэтому API-слой должен передать форме не просто `Error`, а понятный тип ошибки.

> [!faq]+ Уточнения
> - Dirty = значение отличается от default, touched = пользователь заходил в поле.
> - `defaultValues` нужны для dirty state, reset и edit-form.
> - `isSubmitting` защищает UX от двойного submit, backend всё равно должен быть устойчивым.
> - Field errors связывают с полями, form-level errors показывают в summary.
> - После успешного edit-submit reset делают server values, а не пустыми значениями.
> - `422`, `409/412` и `500/503` дают разные сценарии UI.

#### Пример

```tsx
const {
  register,
  handleSubmit,
  reset,
  setError,
  formState: { errors, isDirty, isSubmitting },
} = useForm<ProfileValues>({
  defaultValues: initialValues,
});

const onSubmit = async (values: ProfileValues) => {
  const result = await updateProfile(values);

  if (!result.ok) {
    setError("root.server", { message: "Could not save profile" });
    return;
  }

  reset(result.profile);
};

return (
  <form onSubmit={handleSubmit(onSubmit)}>
    {errors.root?.server && <p role="alert">{errors.root.server.message}</p>}

    <input {...register("name")} />

    <button type="submit" disabled={!isDirty || isSubmitting}>
      Save
    </button>
  </form>
);
```

#### Частые ошибки

- Отключать submit по `!isValid` в режиме, где validation ещё не запускалась.
- Не задавать `defaultValues` и получать странный dirty state.
- Сбрасывать форму пустыми значениями после редактирования вместо актуальных server values.
- Показывать server error только toast-ом, не связывая его с полем.
- Не блокировать или не учитывать повторный submit.
- Считать `isDirty` признаком валидности формы.

#### Связанные темы

- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Forms/Валидация форм]]
- [[Конспект для подготовки/Forms/Server errors и async validation]]
- [[Конспект для подготовки/Forms/Forms architecture]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/Testing/React Testing Library]]

#### Источники

- [React Hook Form: formState docs](https://react-hook-form.com/docs/useform/formstate)
- [React Hook Form GitHub](https://github.com/react-hook-form/react-hook-form)
