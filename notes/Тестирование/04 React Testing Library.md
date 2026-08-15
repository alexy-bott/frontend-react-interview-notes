# React Testing Library

<!-- NOTE-NAV-TOP:START -->
[← Jest](<./03 Jest.md>) · [↑ Тестирование](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [MSW и моки API →](<./05 MSW и моки API.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

React Testing Library помогает тестировать React-компоненты через DOM и пользовательское поведение, а не через внутренности компонента. Основная идея: чем сильнее тест похож на то, как пользователь взаимодействует с интерфейсом, тем больше уверенности он даёт. Поэтому элементы ищут по role, accessible name, label, text, alt text, а `data-testid` оставляют для случаев, где нормального пользовательского селектора нет.

Типичный тест: render компонента, найти элементы через `screen`, выполнить действия через `userEvent`, затем проверить видимый результат или доступное состояние. Для async UI используют `findBy...` или `waitFor`, потому что результат может появиться после promise, запроса, debounce или rerender. Проверяют не `setState` и не вызов внутренней функции, а то, что пользователь увидит: сообщение, disabled button, error alert, navigation, отправленные данные.

RTL хорошо сочетается с MSW: компонент делает настоящий `fetch` или запрос через клиент, а тест перехватывает сеть на boundary. Так тест остаётся похожим на приложение и не превращается в набор моков внутренних функций.

## Ключевая схема

```text
render UI
-> query by accessible selectors
-> userEvent interaction
-> assert visible behavior
```

| Query | Когда использовать |
| --- | --- |
| `getByRole` | кнопки, ссылки, headings, dialogs |
| `getByLabelText` | поля формы |
| `getByText` | видимый текст |
| `findBy...` | элемент появится асинхронно |
| `queryBy...` | проверить отсутствие |
| `getByTestId` | крайний случай без пользовательского селектора |

## Базовая модель

React Testing Library строится вокруг пользовательского контракта компонента. Тест не должен знать, как компонент устроен внутри: какой hook вызвался, как называется private function, какой className у элемента или сколько раз произошёл промежуточный render. Он проверяет DOM-результат и доступное поведение.

`render` должен окружать component теми же public providers/router contexts, которые нужны сценарию. Custom `renderWithApp` полезен как test harness, пока не скрывает initial route, store state и network assumptions.

## Развернутый ответ

Приоритет queries связан с accessibility. Первый выбор - `getByRole` с accessible name, потому что он проверяет роль элемента и его доступное имя. Для форм часто подходит `getByLabelText`, для изображений - `getByAltText`, для текста - `getByText`. Если элемент невозможно найти пользовательским способом, это может указывать на проблему семантики.

`getBy`, `queryBy` и `findBy` отличаются ожиданием и ошибками. `getBy` сразу бросает ошибку, если элемента нет. `queryBy` возвращает `null` и подходит для проверки отсутствия. `findBy` ждёт асинхронного появления элемента и возвращает promise, поэтому подходит для UI после запроса, debounce или rerender.

Для исчезновения используют `waitForElementToBeRemoved` либо `waitFor` с assertion. Callback `waitFor` должен бросать assertion до выполнения условия; возвращённый `false` не запускает retry. Внутри `waitFor` не выполняют click/submit повторно, иначе polling само создаёт дополнительные side effects.

`userEvent` моделирует пользовательские действия выше уровнем: typing, click, tab, keyboard, pointer. `fireEvent` отправляет отдельное DOM-событие и полезен для низкоуровневых случаев. В современных тестах `userEvent` обычно требует `await`, потому что действие может состоять из нескольких событий и обновлений.

## Пример

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

test("logs in user", async () => {
  const user = userEvent.setup();

  render(<LoginForm />);

  await user.type(screen.getByLabelText(/email/i), "a@b.com");
  await user.type(screen.getByLabelText(/password/i), "secret");
  await user.click(screen.getByRole("button", { name: /sign in/i }));

  expect(await screen.findByText(/welcome/i)).toBeInTheDocument();
});
```

## Ключевые уточнения

- Query выбирают по пользовательскому/accessibility contract: role + accessible name, label, text, alt; test id — явный технический contract последней очереди.
- `getBy` проверяет текущее наличие, `queryBy` — текущее отсутствие, `findBy` retry-ит асинхронное появление.
- Для исчезновения loader/dialog используют `waitForElementToBeRemoved`, а не немедленный `queryBy` после action.
- `userEvent` создают через `setup()` и await-ят; `fireEvent` оставляют для отдельного low-level event.
- `waitFor` повторяет assertion, а не пользовательское действие.
- Семантический locator делает тест ближе к доступному UI, но не заменяет полный accessibility audit в real browser.
- Custom render helper должен явно показывать значимые router/store/auth defaults.

## Связанные темы

- [Тестирование фронтенда](<./01 Тестирование фронтенда.md>)
- [Jest](<./03 Jest.md>)
- [MSW и моки API](<./05 MSW и моки API.md>)
- [Асинхронный UI, формы и авторизация](<./06 Асинхронный UI, формы и авторизация.md>)
- [Доступность HTML](<../HTML/03 Доступность HTML.md>)
- [Управляемые и неуправляемые компоненты](<../React/18 Управляемые и неуправляемые компоненты.md>)

## Источники

- [Testing Library: Guiding Principles](https://testing-library.com/docs/guiding-principles/)
- [Testing Library: About Queries](https://testing-library.com/docs/queries/about/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Jest](<./03 Jest.md>) · [↑ Тестирование](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [MSW и моки API →](<./05 MSW и моки API.md>)
<!-- NOTE-NAV-BOTTOM:END -->
