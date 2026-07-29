# Forms

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Forms во frontend.md>)

Заметок в разделе: **8**
<!-- SECTION-NAV:END -->

## Темы

- [Forms во frontend](<./Forms во frontend.md>)
- [Controlled uncontrolled и FormData](<./Controlled uncontrolled и FormData.md>)
- [React Hook Form](<./React Hook Form.md>)
- [Controller и кастомные компоненты](<./Controller и кастомные компоненты.md>)
- [Валидация форм](<./Валидация форм.md>)
- [Server errors и async validation](<./Server errors и async validation.md>)
- [Form state и submit lifecycle](<./Form state и submit lifecycle.md>)
- [Forms architecture](<./Forms architecture.md>)

## Связанные разделы

- [Формы](<../HTML/Формы.md>)
- [React TypeScript типизация](<../TypeScript/React TypeScript типизация.md>)
- [Radix UI](<../React/Radix UI.md>)
- [Forms errors и accessibility](<../Accessibility/Forms errors и accessibility.md>)
- [Форма с async validation и server errors](<../Frontend System Design/Форма с async validation и server errors.md>)

## Маршрут

1. Начать с native form contract: controls, labels, submit, `FormData`, accessibility и server validation.
2. Выбрать source of truth: controlled React state или uncontrolled DOM state.
3. Понять RHF registration, subscriptions, `defaultValues`, submit и form state.
4. Построить adapter для custom control: value conversion, blur, focus ref, label и errors.
5. Разделить HTML constraints, client schema, DTO mapping и server invariants.
6. Обработать server/async validation: typed errors, race protection, conflicts и повторную проверку при mutation.
7. Проследить lifecycle: dirty/touched/valid, pending, business result, reset и retry.
8. Закрепить архитектурные границы: feature ownership, schema, mapper, API adapter, draft и tests.
