# Forms во frontend

<!-- NOTE-NAV-TOP:START -->
[↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Controlled uncontrolled и FormData →](<./Controlled uncontrolled и FormData.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Форма — это полный пользовательский сценарий: ввод данных, validation, submit, server response, показ ошибок и успешное завершение. Основа задаётся HTML: `<form>`, связанные `label`, корректные `name`, submit button и keyboard behavior. React или form library управляют состоянием и UX, но не заменяют нативную семантику и server-side validation.

В React формы обычно строятся тремя способами: controlled state, uncontrolled DOM state или библиотека вроде React Hook Form, которая использует uncontrolled-подход и точечные подписки ради производительности. Выбор зависит от задачи: простая форма может жить на `FormData`, форма с live-логикой может быть controlled, большая продуктовая форма чаще выигрывает от React Hook Form и schema validation.

## Ключевая схема

```text
user input
-> native form semantics
-> client validation
-> normalize payload
-> submit request
-> handle server response
-> show success/errors
```

| Слой | За что отвечает |
| --- | --- |
| HTML | семантика, submit, `label`, `name`, accessibility |
| React | controlled/uncontrolled state, UI updates |
| Form library | registration, validation, errors, dirty/touched |
| Schema | правила и типы payload |
| API layer | DTO, request, server errors |
| UX | loading, disabled, focus, error summary |

## Базовая модель

Форма до React уже имеет много поведения из браузера: submit по Enter, фокус, autocomplete, constraint validation, `FormData`, связь `label` и control. Если заменить это набором `div` и `onClick`, приложение теряет доступность, предсказуемое поведение и часть встроенного UX.

Базовые требования: `label` связан с полем, у отправляемого поля есть `name`, submit проходит через `<form onSubmit>`, кнопки внутри формы имеют явный `type`, ошибки связаны с полями через доступное описание. Placeholder не заменяет label, потому что исчезает при вводе и не является стабильным доступным именем.

## Развернутый ответ

Для ошибок важна не только визуальная подсветка. Поле помечают `aria-invalid`, текст ошибки связывают через `aria-describedby`, а после неуспешного submit фокус переводят на первое проблемное поле или error summary. Тогда форма остаётся понятной для клавиатуры и screen reader.

Выбор подхода зависит от сценария. Простая форма, где значения нужны только при отправке, может использовать нативный submit и `FormData`. Форма с live-логикой, масками или зависимыми полями может быть controlled. Большая продуктовая форма с dirty/touched state, server errors, schema validation и кастомными контролами часто выигрывает от React Hook Form.

Validation делится по ответственности. Client-side validation даёт быстрый UX-feedback, но server-side validation остаётся обязательной для безопасности, прав, уникальности и бизнес-правил. После server response ошибки маппят на конкретные поля или общий form-level error.

Payload не равен внутреннему form state автоматически. `FormData` содержит строки и `File`, допускает несколько значений с одним `name`, не включает disabled controls и отражает только successful controls. Перед API request данные нормализуют в DTO: числа/boolean приводят к нужным типам, повторяющиеся values сохраняют через `getAll`, пустые optional fields преобразуют по server contract.

Production-ready форма учитывает pending state, повторный submit и idempotency операции, обработку backend field errors, reset/navigation после успеха, сохранение введённых значений при failure, focus management и тесты ключевых сценариев. Простого `disabled` недостаточно для критичной mutation: server также должен корректно обрабатывать повторный request.

## Пример

```tsx
function LoginForm() {
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const payload = {
      email: String(formData.get("email") ?? ""),
      password: String(formData.get("password") ?? ""),
    };

    console.log(payload);
  }

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="email">Email</label>
      <input id="email" name="email" type="email" autoComplete="email" required />

      <label htmlFor="password">Password</label>
      <input id="password" name="password" type="password" autoComplete="current-password" required />

      <button type="submit">Sign in</button>
    </form>
  );
}
```

## Ключевые уточнения

- Native form обеспечивает submit, Enter, autocomplete и участие controls в `FormData`; библиотека должна сохранять эти guarantees.
- `label` создаёт accessible name, placeholder показывает подсказку и не заменяет label.
- Client validation ускоряет feedback, server validation защищает data integrity и права доступа.
- Field error связывают с control, form-level error показывают отдельно; после failure введённые данные не должны исчезать без причины.
- `FormData` не является typed DTO: значения нужно явно прочитать и нормализовать.
- Защита от повторной критичной mutation реализуется и в UI, и на server через подходящий idempotency/contract.

## Связанные темы

- [Формы](<../HTML/Формы.md>)
- [Controlled uncontrolled и FormData](<./Controlled uncontrolled и FormData.md>)
- [React Hook Form](<./React Hook Form.md>)
- [Валидация форм](<./Валидация форм.md>)
- [Forms errors и accessibility](<../Accessibility/Forms errors и accessibility.md>)
- [API слой и контракты](<../Architecture/API слой и контракты.md>)

## Источники

- [MDN: Web forms](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms)
- [React: input](https://react.dev/reference/react-dom/components/input)
- [MDN: FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [MDN: aria-invalid](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-invalid)
- [MDN: aria-describedby](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-describedby)

---

<!-- NOTE-NAV-BOTTOM:START -->
[↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Controlled uncontrolled и FormData →](<./Controlled uncontrolled и FormData.md>)
<!-- NOTE-NAV-BOTTOM:END -->
