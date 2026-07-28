---
aliases:
  - forms frontend
  - формы frontend
  - frontend forms
---

#### Ответ на 60 секунд

Форма во frontend - это сценарий сбора, проверки и отправки пользовательских данных. Надёжная форма начинается не с библиотеки, а с нативной HTML-семантики: `<form>`, связанные `label` и controls, корректные `name`, submit по Enter, доступные ошибки и понятная связь с backend-контрактом.

В React формы обычно строятся тремя способами: controlled state, uncontrolled DOM state или библиотека вроде React Hook Form, которая использует uncontrolled-подход и точечные подписки ради производительности. Выбор зависит от задачи: простая форма может жить на `FormData`, форма с live-логикой может быть controlled, большая продуктовая форма чаще выигрывает от React Hook Form и schema validation.

#### Ключевая схема

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

#### Развернутый ответ

Форма до React уже имеет много поведения из браузера: submit по Enter, фокус, autocomplete, constraint validation, `FormData`, связь `label` и control. Если заменить это набором `div` и `onClick`, приложение теряет доступность, предсказуемое поведение и часть встроенного UX.

Базовые требования: `label` связан с полем, у отправляемого поля есть `name`, submit проходит через `<form onSubmit>`, кнопки внутри формы имеют явный `type`, ошибки связаны с полями через доступное описание. Placeholder не заменяет label, потому что исчезает при вводе и не является стабильным доступным именем.

Для ошибок важна не только визуальная подсветка. Поле помечают `aria-invalid`, текст ошибки связывают через `aria-describedby`, а после неуспешного submit фокус переводят на первое проблемное поле или error summary. Тогда форма остаётся понятной для клавиатуры и screen reader.

Выбор подхода зависит от сценария. Простая форма, где значения нужны только при отправке, может использовать нативный submit и `FormData`. Форма с live-логикой, масками или зависимыми полями может быть controlled. Большая продуктовая форма с dirty/touched state, server errors, schema validation и кастомными контролами часто выигрывает от React Hook Form.

Validation делится по ответственности. Client-side validation даёт быстрый UX-feedback, но server-side validation остаётся обязательной для безопасности, прав, уникальности и бизнес-правил. После server response ошибки маппят на конкретные поля или общий form-level error.

Production-ready форма учитывает pending state, защиту от двойного submit, нормализацию payload, обработку backend field errors, reset или navigation после успеха, фокус на первом проблемном поле и тесты ключевых сценариев.

> [!faq]+ Уточнения
> - `label`, `name`, `<form onSubmit>` и `button type` важны до выбора React-библиотеки.
> - Placeholder не заменяет label.
> - `FormData` подходит для submit-only данных и файлов.
> - Client validation помогает UX, backend validation защищает данные.
> - Server errors нужно возвращать в поля или общий error summary.

#### Пример

```tsx
function LoginForm() {
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const payload = Object.fromEntries(formData);

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

#### Частые ошибки

- Делать форму из `div` и `onClick`, теряя нативный submit.
- Забывать `name`, из-за чего поле не попадает в `FormData`.
- Использовать placeholder вместо label.
- Делать все поля controlled без необходимости и получать лишние ререндеры.
- Полагаться только на клиентскую валидацию.
- Показывать ошибку визуально, но не связывать её с конкретным полем.

#### Связанные темы

- [[Конспект для подготовки/HTML/Формы]]
- [[Конспект для подготовки/Forms/Controlled uncontrolled и FormData]]
- [[Конспект для подготовки/Forms/React Hook Form]]
- [[Конспект для подготовки/Forms/Валидация форм]]
- [[Конспект для подготовки/Accessibility/Forms errors и accessibility]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]

#### Источники

- [MDN: Web forms](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms)
- [React: input](https://react.dev/reference/react-dom/components/input)
- [MDN: FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [MDN: aria-invalid](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-invalid)
- [MDN: aria-describedby](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-describedby)
