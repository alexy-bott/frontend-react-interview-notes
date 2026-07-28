---
aliases:
  - React Testing Library
  - Testing Library
  - RTL
  - screen
  - user-event
---

#### Ответ на 60 секунд

React Testing Library помогает тестировать React-компоненты через DOM и пользовательское поведение, а не через внутренности компонента. Основная идея: чем сильнее тест похож на то, как пользователь взаимодействует с интерфейсом, тем больше уверенности он даёт. Поэтому элементы ищут по role, accessible name, label, text, alt text, а `data-testid` оставляют для случаев, где нормального пользовательского селектора нет.

Типичный тест: render компонента, найти элементы через `screen`, выполнить действия через `userEvent`, затем проверить видимый результат или доступное состояние. Для async UI используют `findBy...` или `waitFor`, потому что результат может появиться после promise, запроса, debounce или rerender. Проверяют не `setState` и не вызов внутренней функции, а то, что пользователь увидит: сообщение, disabled button, error alert, navigation, отправленные данные.

RTL хорошо сочетается с MSW: компонент делает настоящий `fetch` или запрос через клиент, а тест перехватывает сеть на boundary. Так тест остаётся похожим на приложение и не превращается в набор моков внутренних функций.

#### Ключевая схема

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

#### Развернутый ответ

React Testing Library строится вокруг пользовательского контракта компонента. Тест не должен знать, как компонент устроен внутри: какой hook вызвался, как называется private function, какой className у элемента или сколько раз произошёл промежуточный render. Он проверяет DOM-результат и доступное поведение.

Приоритет queries связан с accessibility. Первый выбор - `getByRole` с accessible name, потому что он проверяет роль элемента и его доступное имя. Для форм часто подходит `getByLabelText`, для изображений - `getByAltText`, для текста - `getByText`. Если элемент невозможно найти пользовательским способом, это может указывать на проблему семантики.

`getBy`, `queryBy` и `findBy` отличаются ожиданием и ошибками. `getBy` сразу бросает ошибку, если элемента нет. `queryBy` возвращает `null` и подходит для проверки отсутствия. `findBy` ждёт асинхронного появления элемента и возвращает promise, поэтому подходит для UI после запроса, debounce или rerender.

`userEvent` моделирует пользовательские действия выше уровнем: typing, click, tab, keyboard, pointer. `fireEvent` отправляет отдельное DOM-событие и полезен для низкоуровневых случаев. В современных тестах `userEvent` обычно требует `await`, потому что действие может состоять из нескольких событий и обновлений.

> [!faq]+ Уточнения
> - RTL проверяет DOM-поведение, а не внутреннюю реализацию React-компонента.
> - `getByRole(..., { name })` одновременно проверяет семантику и доступное имя.
> - `getBy` - синхронное наличие, `queryBy` - отсутствие, `findBy` - асинхронное появление.
> - `userEvent` ближе к действиям пользователя, `fireEvent` - к отдельному DOM event.
> - `data-testid` оставляют для мест без нормального пользовательского селектора.

#### Пример

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

#### Частые ошибки

- Искать элементы по `className` вместо role/label/name.
- Проверять implementation details компонента.
- Использовать `getByText` для кнопки, где подходит `getByRole("button", { name })`.
- Забывать `await` для `userEvent` и async UI.
- Использовать `waitFor` там, где достаточно `findBy`.
- Массово добавлять `data-testid`, скрывая проблемы семантики.

#### Связанные темы

- [[Конспект для подготовки/Testing/Frontend testing]]
- [[Конспект для подготовки/Testing/Jest]]
- [[Конспект для подготовки/Testing/MSW и моки API]]
- [[Конспект для подготовки/Testing/Async UI формы и auth]]
- [[Конспект для подготовки/HTML/Accessibility]]
- [[Конспект для подготовки/React/Controlled и uncontrolled компоненты]]

#### Источники

- [Testing Library: Guiding Principles](https://testing-library.com/docs/guiding-principles/)
- [Testing Library: About Queries](https://testing-library.com/docs/queries/about/)
