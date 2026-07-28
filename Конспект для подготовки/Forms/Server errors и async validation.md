---
aliases:
  - server errors forms
  - async validation forms
  - backend field errors
  - 422 forms
---

#### Ответ на 60 секунд

Server errors и async validation закрывают правила, которые нельзя надёжно проверить только на клиенте: уникальность email, права доступа, конфликт версии, промокод, лимиты, бизнес-ограничения, состояние ресурса на backend. Client validation даёт быстрый UX, но backend остаётся источником истины.

Типичный flow такой: форма проходит client/schema validation, отправляет DTO в API, backend возвращает success или структурированную ошибку. Field errors мапятся на конкретные поля через `setError("email", ...)`, общая ошибка формы - в `root`/error summary. Для `422` удобно иметь единый error shape: `field`, `code`, `message`. UI не должен парсить человеческий текст ошибки как бизнес-код.

Async validation на каждый символ делают осторожно: debounce, abort, request id, cache и проверка race conditions. Часто проверку уникальности запускают на blur или после submit, а не на каждый `onChange`. Если старый запрос пришёл позже нового, UI не должен показать устаревшую ошибку.

#### Ключевая схема

```text
client validation
-> submit DTO
-> API response
-> 422 field errors | 409 conflict | root error
-> setError / error summary
-> focus first relevant error
```

| Сценарий | Где обрабатывать |
| --- | --- |
| Пустое обязательное поле | HTML/schema validation |
| Неверный формат email | HTML/schema validation |
| Email уже занят | backend -> field error |
| Нет доступа | API layer -> form-level error или redirect |
| Конфликт версии | API layer -> conflict UI |
| Превышен лимит | API layer -> root error/retry hint |
| Невалидный backend response | runtime validation на API boundary |

#### Развернутый ответ

Ошибки формы делятся на field-level и form-level. Field-level ошибка относится к конкретному control: email уже занят, password слишком короткий, дата вне диапазона. Form-level ошибка относится ко всему действию: нет доступа, конфликт версии, сервер временно недоступен, неверная комбинация email/password, операция больше невозможна.

Для API удобно возвращать структурированные ошибки. Например, `422 Unprocessable Content` с массивом field errors: `field`, `code`, `message`. `field` нужен для привязки к input, `code` - для стабильной логики/локализации, `message` - для отображения или fallback. Если backend возвращает только строку, frontend не может надёжно понять, куда её показать.

В React Hook Form server errors обычно ставят через `setError`. Для поля используют имя поля: `setError("email", { type: "server", message })`. Для общей ошибки можно использовать `setError("root.server", { type: "server", message })` или собственный state для error summary. Если нужен focus, `shouldFocus` работает только для зарегистрированного и не disabled поля с доступным ref.

Async validation нужно проектировать как сетевой сценарий. Проверка username/email на каждый `onChange` без debounce создаёт лишнюю нагрузку и гонки. Для устойчивого UX используют debounce, `AbortController`, request id, cache результата или проверку на blur/submit. Если значение изменилось после старта запроса, ответ старого запроса игнорируют.

Conflict errors отличаются от validation errors. `422` говорит, что значения формы семантически невалидны. `409` или `412` часто означают конфликт состояния: данные редактировали параллельно, версия устарела, ресурс уже изменился. UI должен показать сценарий обновления данных, повторной загрузки или ручного выбора, а не просто подсветить одно поле.

> [!faq]+ Уточнения
> - Client validation ускоряет обратную связь, backend validation остаётся обязательной.
> - `422` обычно мапится в field errors, `409/412` - в conflict сценарий.
> - Для общей ошибки используют `root`/error summary, а не случайное поле.
> - Async validation требует debounce/abort/race protection.
> - `message` показывают пользователю, `code` используют для стабильной логики.

#### Пример

```ts
type ApiFieldError = {
  field: string;
  code: string;
  message: string;
};

type ValidationErrorBody = {
  type: "validation_error";
  errors: ApiFieldError[];
};

function applyServerErrors<TFieldName extends string>(
  errorBody: ValidationErrorBody,
  setError: (
    name: TFieldName | "root.server",
    error: { type: string; message?: string },
    options?: { shouldFocus?: boolean },
  ) => void,
) {
  for (const error of errorBody.errors) {
    setError(error.field as TFieldName, {
      type: error.code,
      message: error.message,
    });
  }
}
```

React Hook Form:

```tsx
const onSubmit = async (values: ProfileValues) => {
  const result = await updateProfile(values);

  if (result.type === "validation_error") {
    applyServerErrors(result, setError);
    return;
  }

  if (result.type === "conflict") {
    setError("root.server", {
      type: "conflict",
      message: "Profile was changed on the server. Refresh and try again.",
    });
    return;
  }

  reset(result.profile);
};
```

#### Частые ошибки

- Парсить human-readable `message` как машинный код.
- Показывать все backend errors одним toast-ом без связи с полями.
- Запускать async validation на каждый символ без debounce и отмены.
- Не защищаться от race condition: старый ответ перетирает новый state.
- Считать `422`, `409` и `500` одинаковой ошибкой формы.
- Терять server errors после `reset` или смены default values без понятного UX.
- Не фокусировать поле/summary после submit с ошибками.

#### Связанные темы

- [[Конспект для подготовки/Forms/Валидация форм]]
- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Forms/Form state и submit lifecycle]]
- [[Конспект для подготовки/Forms/Forms architecture]]
- [[Конспект для подготовки/Web Basics/HTTP status codes и ошибки API]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/JavaScript/Fetch и работа с API]]
- [[Конспект для подготовки/Testing/Async UI формы и auth]]

#### Источники

- [React Hook Form: setError docs](https://react-hook-form.com/docs/useform/seterror)
- [React Hook Form: useForm docs](https://react-hook-form.com/docs/useform)
- [MDN: Client-side form validation](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation)
