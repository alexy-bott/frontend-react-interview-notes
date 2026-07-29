# Forms architecture

<!-- NOTE-NAV-TOP:START -->
[← Form state и submit lifecycle](<./Form state и submit lifecycle.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Архитектура форм - это про границы ответственности. UI-компоненты должны отображать поля и ошибки, form layer управляет values/validation/state, schema описывает правила, API layer преобразует form values в DTO и отправляет запрос, backend возвращает field/form errors. Чем крупнее форма, тем важнее не смешивать JSX, бизнес-правила, API DTO и validation в одном компоненте.

Практичный подход: держать форму внутри feature, schema рядом с формой или доменной моделью, API-mapping отдельно, reusable field components в shared/ui, а server errors маппить через понятную функцию. В FSD это часто выглядит как `features/edit-profile/ui`, `model/schema`, `api/updateProfile`, а общие `TextField`, `SelectField`, `FormError` живут в shared.

## Ключевая схема

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

## Базовая модель

Form values и DTO не обязаны совпадать. Form values удобны для UI: строки из inputs, checkbox booleans, временные значения, вложенные группы. DTO - контракт API: даты в ISO, числа как number, nullable fields, renamed keys, arrays и backend-specific структура. Между ними нужен явный mapping на API boundary.

Владельцем form state остаётся конкретный user scenario. Shared fields предоставляют UI/accessibility contract, но не знают endpoint, domain rules или server error shape.

## Развернутый ответ

Schema хранят рядом с владельцем правила. Если schema нужна одной форме, она остаётся в feature. Если это доменный контракт для нескольких сценариев, её можно вынести ближе к entity/domain. Shared не должен становиться складом всех схем, иначе границы снова размываются.

Большую форму делят на секции, сохраняя единый submit flow и понятные ошибки. `FormProvider`/`useFormContext` помогает разнести поля по компонентам, но владение form state должно оставаться очевидным: кто создаёт `useForm`, кто вызывает submit, где mapping и где обрабатываются server errors.

Server error mapping держат рядом с API boundary или feature model. API возвращает typed error: validation, conflict, forbidden, rate limit, server error. Feature превращает validation errors в `setError`, conflict - в отдельный UI-сценарий, а form-level errors - в summary. Так форма не зависит от случайной формы backend response.

Мультишаговая форма требует решения о draft state: form library, URL/session storage, global store или backend draft. Для длинных сценариев важны сохранение прогресса, валидация текущего шага, восстановление после reload и понятное поведение при изменении backend-данных.

Тесты форм проверяют пользовательские сценарии: ввод, validation messages, disabled/pending state, submit payload, server field errors, reset или navigation после успеха. Тест фокусируется на поведении пользователя, а не на внутренних методах form library.

## Пример

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

## Ключевые уточнения

- Form values оптимизированы для UI editing, DTO — для API contract; mapping является явной boundary.
- Schema принадлежит владельцу rules: feature-local rule не выносят в shared ради формального reuse.
- `FormProvider` разделяет UI на sections, но не размывает ownership submit/reset/error mapping.
- Global store нужен только при lifetime формы за пределами route/component, а не из-за размера JSX.
- Multi-step flow заранее определяет draft storage, versioning, restore и conflict behavior.
- Tests проверяют input → validation → request → server response → recovery/success как пользовательский scenario.

## Связанные темы

- [React Hook Form](<./React Hook Form.md>)
- [Валидация форм](<./Валидация форм.md>)
- [Server errors и async validation](<./Server errors и async validation.md>)
- [API слой и контракты](<../Architecture/API слой и контракты.md>)
- [Frontend architecture](<../Architecture/Frontend architecture.md>)
- [React Testing Library](<../Testing/React Testing Library.md>)
- [Проверка данных с backend](<../TypeScript/Проверка данных с backend.md>)

## Источники

- [React Hook Form GitHub](https://github.com/react-hook-form/react-hook-form)
- [React Hook Form Resolvers](https://github.com/react-hook-form/resolvers)
- [Zod](https://zod.dev/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Form state и submit lifecycle](<./Form state и submit lifecycle.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-BOTTOM:END -->
