---
aliases:
  - forms architecture
  - архитектура форм
  - form architecture frontend
---

#### Ответ на 60 секунд

Архитектура форм - это про границы ответственности. UI-компоненты должны отображать поля и ошибки, form layer управляет values/validation/state, schema описывает правила, API layer преобразует form values в DTO и отправляет запрос, backend возвращает field/form errors. Чем крупнее форма, тем важнее не смешивать JSX, бизнес-правила, API DTO и validation в одном компоненте.

Практичный подход: держать форму внутри feature, schema рядом с формой или доменной моделью, API-mapping отдельно, reusable field components в shared/ui, а server errors маппить через понятную функцию. В FSD это часто выглядит как `features/edit-profile/ui`, `model/schema`, `api/updateProfile`, а общие `TextField`, `SelectField`, `FormError` живут в shared.

#### Ключевая схема

```text
ui fields
-> form controller
-> schema validation
-> map values to DTO
-> API request
-> map server errors
-> UI feedback
```

| Часть | Где держать |
| --- | --- |
| Field UI | shared/ui или локально в feature |
| Form schema | feature/model или domain model |
| Form component | feature/ui |
| API function | feature/api или entity/api |
| DTO mapping | рядом с API boundary |
| Server error mapping | feature/model или api adapter |
| Tests | рядом со сценарием или testing layer |

#### Развернутый ответ

Form values и DTO не обязаны совпадать. Form values удобны для UI: строки из inputs, checkbox booleans, временные значения, вложенные группы. DTO - контракт API: даты в ISO, числа как number, nullable fields, renamed keys, arrays и backend-specific структура. Между ними нужен явный mapping на API boundary.

Schema хранят рядом с владельцем правила. Если schema нужна одной форме, она остаётся в feature. Если это доменный контракт для нескольких сценариев, её можно вынести ближе к entity/domain. Shared не должен становиться складом всех схем, иначе границы снова размываются.

Большую форму делят на секции, сохраняя единый submit flow и понятные ошибки. `FormProvider`/`useFormContext` помогает разнести поля по компонентам, но владение form state должно оставаться очевидным: кто создаёт `useForm`, кто вызывает submit, где mapping и где обрабатываются server errors.

Server error mapping держат рядом с API boundary или feature model. API возвращает typed error: validation, conflict, forbidden, rate limit, server error. Feature превращает validation errors в `setError`, conflict - в отдельный UI-сценарий, а form-level errors - в summary. Так форма не зависит от случайной формы backend response.

Мультишаговая форма требует решения о draft state: form library, URL/session storage, global store или backend draft. Для длинных сценариев важны сохранение прогресса, валидация текущего шага, восстановление после reload и понятное поведение при изменении backend-данных.

Тесты форм проверяют пользовательские сценарии: ввод, validation messages, disabled/pending state, submit payload, server field errors, reset или navigation после успеха. Тест фокусируется на поведении пользователя, а не на внутренних методах form library.

> [!faq]+ Уточнения
> - Form values - форма для UI, DTO - контракт API.
> - Mapping values -> DTO держат рядом с API boundary.
> - Schema одной формы живёт рядом с feature, переиспользуемая schema - ближе к domain/entity.
> - `FormProvider` помогает секционировать большую форму, но owner form state должен быть понятен.
> - Мультишаговые формы требуют стратегии draft state и восстановления.
> - Server error mapping держат рядом с feature/API boundary.

#### Пример

```text
features/edit-profile/
  api/
    updateProfile.ts
  model/
    schema.ts
    mapServerErrors.ts
  ui/
    EditProfileForm.tsx
    EditProfileFields.tsx
```

Mapping:

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
```

#### Частые ошибки

- Отправлять form values напрямую как API DTO без mapping.
- Держать schema, API request, UI и error mapping в одном огромном компоненте.
- Выносить все field-компоненты в shared до появления реального переиспользования.
- Делать form state глобальным без необходимости.
- Не продумывать server errors и optimistic/pending states.
- Тестировать implementation details вместо пользовательского поведения.

#### Связанные темы

- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Forms/Валидация форм]]
- [[Конспект для подготовки/Forms/Server errors и async validation]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/Architecture/Frontend architecture]]
- [[Конспект для подготовки/Testing/React Testing Library]]
- [[Конспект для подготовки/TypeScript/Проверка данных с backend]]

#### Источники

- [React Hook Form GitHub](https://github.com/react-hook-form/react-hook-form)
- [React Hook Form Resolvers](https://github.com/react-hook-form/resolvers)
- [Zod](https://zod.dev/)
