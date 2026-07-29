---
aliases:
  - formState
  - submit lifecycle
  - dirty touched errors
  - isSubmitting
---

#### Быстрый ответ

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
| `isSubmitSuccessful` | submit callback завершился без необработанной ошибки |

#### Базовая модель

Dirty и touched отвечают на разные вопросы. Dirty означает, что значение изменилось относительно `defaultValues`. Touched означает, что пользователь заходил в поле. Поле может быть touched, но не dirty, если пользователь сфокусировался и ушёл без изменения.

`isValid`, `isSubmitting` и business result также отвечают на разные вопросы: корректны ли текущие values, выполняется ли callback и принял ли backend операцию. Ни один flag не заменяет остальные.

#### Развернутый ответ

`defaultValues` нужны для корректного dirty state и reset. Для create-form это пустые начальные значения. Для edit-form их заполняют данными с backend после загрузки, а после успешного сохранения reset-ят форму новыми server values, чтобы dirty state снова стал false.

Submit lifecycle должен учитывать pending и повторную отправку. Во время `isSubmitting` submit-кнопку обычно отключают, но backend всё равно должен безопасно обрабатывать повторный запрос: idempotency, conflict detection или защита от дублей. Disabled button - UX-защита, а не гарантия безопасности.

Ошибки делят на field-level и form-level. Field error показывают рядом с полем и связывают через `aria-describedby`. Form-level error показывают над формой или в summary. После submit с ошибками полезно сфокусировать первое проблемное поле или summary.

После успеха сценарий зависит от формы. Create-form может вызвать `reset()` и показать success. Edit-form reset-ят актуальными server values. Если после submit идёт navigation, отдельный reset может быть не нужен.

Server errors входят в submit lifecycle. `422` обычно возвращается в поля, `409/412` требует conflict-сценария, `500/503` обычно становится form-level error с retry. Это разные UX-сценарии, поэтому API-слой должен передать форме не просто `Error`, а понятный тип ошибки.

`isSubmitSuccessful` — технический flag RHF, а не подтверждение domain success. Если callback поймал API error, вызвал `setError` и завершился обычным `return`, отдельный application result всё ещё должен определить success/failure. Аналогично `setError` показывает manual/server error, но `isValid` вычисляется validation rules формы.

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

#### Ключевые уточнения

- Dirty сравнивает values с `defaultValues`, touched фиксирует interaction, valid отражает validation result.
- `isSubmitSuccessful` не заменяет business result от API.
- После успешного edit-submit `reset(serverValues)` делает сохранённый server state новым baseline.
- Pending UI ограничивает повторное действие, а backend обеспечивает idempotency/conflict safety.
- Field и form errors остаются видимыми до исправления/retry и доступны для focus/navigation.
- Submit button policy учитывает validation mode: `!isValid` до первой проверки может блокировать сценарий без понятной причины.

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
