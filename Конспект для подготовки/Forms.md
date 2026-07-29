#### Темы

- [[Конспект для подготовки/Forms/Forms во frontend]]
- [[Конспект для подготовки/Forms/Controlled uncontrolled и FormData]]
- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Forms/Controller и кастомные компоненты]]
- [[Конспект для подготовки/Forms/Валидация форм]]
- [[Конспект для подготовки/Forms/Server errors и async validation]]
- [[Конспект для подготовки/Forms/Form state и submit lifecycle]]
- [[Конспект для подготовки/Forms/Forms architecture]]

#### Связанные разделы

- [[Конспект для подготовки/HTML/Формы]]
- [[Конспект для подготовки/TypeScript/React TypeScript типизация]]
- [[Конспект для подготовки/React/Radix UI]]
- [[Конспект для подготовки/Accessibility/Forms errors и accessibility]]
- [[Конспект для подготовки/Frontend System Design/Форма с async validation и server errors]]

#### Маршрут

1. Начать с native form contract: controls, labels, submit, `FormData`, accessibility и server validation.
2. Выбрать source of truth: controlled React state или uncontrolled DOM state.
3. Понять RHF registration, subscriptions, `defaultValues`, submit и form state.
4. Построить adapter для custom control: value conversion, blur, focus ref, label и errors.
5. Разделить HTML constraints, client schema, DTO mapping и server invariants.
6. Обработать server/async validation: typed errors, race protection, conflicts и повторную проверку при mutation.
7. Проследить lifecycle: dirty/touched/valid, pending, business result, reset и retry.
8. Закрепить архитектурные границы: feature ownership, schema, mapper, API adapter, draft и tests.
