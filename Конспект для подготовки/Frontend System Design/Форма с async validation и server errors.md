---
aliases:
  - проектирование формы
  - form system design
  - async validation form
  - server errors form
---

#### Ответ на 60 секунд

Форма проектируется вокруг жизненного цикла submit: values, touched/dirty, sync validation, async validation, pending state, API request, server errors, success state и reset/navigation. Для крупной формы важно разделить UI полей, form state, schema, mapping values -> DTO, API request и mapping backend errors -> field/form errors.

Async validation нужна, когда правило зависит от сервера или внешнего состояния: уникальность email, доступность username, промокод, права пользователя. Её нельзя смешивать с каждым keystroke без debounce/cancellation, иначе появятся race conditions и лишняя нагрузка. Server errors после submit нужно маппить в поля или form-level summary.

Хорошая форма отвечает на вопросы: где живёт draft, что валидируется на клиенте, что на сервере, как показываются ошибки, что блокируется во время submit, как работает accessibility и как тестируется сценарий.

#### Ключевая схема

```text
field UI
-> form state
-> sync schema validation
-> async validation
-> map values to DTO
-> submit request
-> map server errors
-> success/reset/navigation
```

| Часть | Что решить |
| --- | --- |
| Form state | values, touched, dirty, errors |
| Sync validation | required, format, min/max, local rules |
| Async validation | debounce, cancellation, stale response |
| Submit | pending, disabled, retry, idempotency |
| Server errors | field errors, form errors, conflict |
| Accessibility | labels, aria-invalid, describedby, focus |
| Testing | user flow, validation, server errors |

#### Развернутый ответ

Form values не всегда совпадают с API DTO. Input почти всегда даёт строки, а API может ждать number, ISO date, nullable field, enum или nested object. Поэтому mapping values -> DTO держат на границе submit/API, а не размазывают по JSX.

Client validation закрывает быстрые правила: required, format, min length, range, matching fields. Server validation остаётся источником истины для уникальности, прав, конфликтов, бизнес-ограничений и данных, которые могли измениться после открытия формы.

Async validation требует контроля гонок. Если пользователь вводит username, запрос на `alex` может вернуться позже запроса на `alex1`. UI не должен показывать устаревшую ошибку. Используют debounce, request id, AbortController или возможности form/query library.

Server errors нужно нормализовать. `422` может содержать field errors, `409` - conflict, `403` - access denied, network error - retry/fallback. Field errors мапятся в конкретные поля, form-level errors показываются в summary, а критичные ошибки могут вести к отдельному экрану.

Для accessibility ошибка должна быть связана с полем: label, `aria-invalid`, `aria-describedby`, понятный текст, focus на первую ошибку после submit. Disabled submit должен не мешать screen reader feedback; pending state должен быть видимым.

#### Где применяется во frontend

| Ситуация в проекте | Что проектируется | Конкретное решение |
| --- | --- | --- |
| Username должен быть уникальным | async validation зависит от backend | debounce + cancellation + показ stale-safe результата |
| Backend возвращает `{ field: "email", message: "Already used" }` | ошибку нужно показать у поля | mapper server errors -> `setError("email", ...)` |
| Форма редактирует профиль из API | DTO и form values отличаются | `mapUserToFormValues` и `mapFormValuesToDto` |
| Submit занимает несколько секунд | пользователь должен видеть процесс | pending state, disabled duplicate submit, spinner/text |
| Мультишаговая форма переживает reload | draft state должен сохраняться | store/session storage/backend draft, стратегия восстановления |
| После ошибки submit фокус остаётся неизвестно где | accessibility ломается | focus на первую ошибку или error summary |

> [!faq]+ Уточнения
> - Client validation улучшает UX, server validation остаётся источником истины.
> - Async validation требует debounce и защиты от stale responses.
> - Server errors делят на field-level и form-level.
> - Form values и API DTO лучше маппить явно.
> - Большую форму делят на секции, но owner form state должен быть понятен.
> - Тестировать нужно пользовательское поведение, а не внутренности form library.

#### Пример

```ts
type ProfileFormValues = {
  displayName: string;
  birthday: string;
};

type UpdateProfileDto = {
  display_name: string;
  birthday_iso: string | null;
};

function mapProfileFormToDto(values: ProfileFormValues): UpdateProfileDto {
  return {
    display_name: values.displayName.trim(),
    birthday_iso: values.birthday || null,
  };
}

function mapServerErrorsToFormErrors(error: ApiValidationError) {
  return error.fields.map(fieldError => ({
    name: fieldError.path,
    message: fieldError.message,
  }));
}
```

#### Частые ошибки

- Отправлять form values как DTO без mapping.
- Делать async validation на каждый символ без debounce/cancellation.
- Показывать stale error от старого запроса.
- Смешивать field errors и form-level errors.
- Блокировать submit без понятного pending feedback.
- Не связывать error text с полем через accessibility-атрибуты.

#### Связанные темы

- [[Конспект для подготовки/Forms/Forms architecture]]
- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Forms/Валидация форм]]
- [[Конспект для подготовки/Forms/Server errors и async validation]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/TypeScript/Проверка данных с backend]]
- [[Конспект для подготовки/Testing/Async UI формы и auth]]
- [[Конспект для подготовки/React/Controlled и uncontrolled компоненты]]

#### Источники

- [React Hook Form docs](https://react-hook-form.com/)
- [MDN: Client-side form validation](https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation)
- [WAI: Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/)
