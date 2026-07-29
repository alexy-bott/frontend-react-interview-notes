# Frontend testing

<!-- NOTE-NAV-TOP:START -->
[↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Стратегия тестирования frontend →](<./Стратегия тестирования frontend.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Frontend tests дают доказательства о наблюдаемом поведении системы. Unit test изолирует небольшую логику, integration test соединяет несколько реальных частей приложения и контролирует внешние boundaries, E2E запускает пользовательский flow в browser через frontend и обычно реальный test backend. Уровень определяется не размером файла, а количеством настоящих boundaries в проверяемом пути.

Для React часто используют Testing Library, потому что ее философия - тестировать поведение так, как пользователь взаимодействует с интерфейсом, а не внутреннюю реализацию компонента. Элементы ищут по роли, label, тексту и доступному имени, а не по className или внутренним state.

## Ключевая схема

| Уровень | Что проверяет | Пример |
| --- | --- | --- |
| Unit | маленькую функцию/компонент | formatter, reducer |
| Integration | связку частей | форма отправляет данные |
| E2E | сценарий в браузере | login, checkout |
| Test double | контролируемая замена boundary | API, clock, analytics |

## Базовая модель

Frontend tests дают разную степень уверенности на разных уровнях. Unit test быстрый и дешёвый, но проверяет маленький кусок: formatter, reducer, чистую функцию. Integration test проверяет связку: компонент, state, form validation, API response, router context. E2E test открывает браузер и проверяет весь пользовательский путь, но требует больше инфраструктуры и времени.

Каждый тест состоит из состояния, действия и **oracle** — наблюдаемого условия, которое отличает правильное поведение от ошибки. Слабое assertion вроде «component отрендерился» не доказывает submit flow; сильное проверяет payload/response effect и то, что увидит пользователь.

## Развернутый ответ

Компонент тестируют через публичное поведение: что пользователь видит, какие действия может выполнить, какие состояния появляются после взаимодействия. Внутренние hooks, private functions и implementation details не являются контрактом UI, поэтому такие проверки ломаются от рефакторинга без реальной регрессии.

Test doubles используют на внешних границах, где зависимость делает тест медленным, нестабильным или неподконтрольным: network, clock, analytics, browser APIs. Stub возвращает заданный result, spy наблюдает вызовы, fake реализует упрощённое рабочее поведение, mock обычно задаёт ожидаемые interactions. Термины часто смешивают в инструментах, поэтому важнее понимать, что именно заменено и какую интеграцию тест больше не доказывает.

Integration и E2E отличаются глубиной окружения. Integration обычно быстрее и работает в тестовой среде с моками внешних границ. E2E проверяет реальный браузер, routing, storage, network и часто backend-контракт. Поэтому E2E оставляют для критичных flows, а не для каждой мелкой ветки компонента.

## Пример

```tsx
render(<LoginForm />);

await user.type(screen.getByLabelText(/email/i), "a@b.com");
await user.click(screen.getByRole("button", { name: /login/i }));

expect(await screen.findByText(/welcome/i)).toBeInTheDocument();
```

## Ключевые уточнения

- Test level определяется реальными dependencies в пути, а не названием `unit` в папке.
- Assertion проверяет business/UI contract; сам факт render или вызова private function обычно недостаточен.
- Чем глубже boundary заменён, тем меньше интеграции подтверждает тест.
- Semantic queries одновременно делают тест устойчивее и проверяют часть accessibility contract.
- Integration tests дают основной баланс скорости и уверенности, E2E подтверждает небольшое число критичных flows.
- Успешный test suite не доказывает отсутствие bugs; он даёт ровно ту уверенность, которую выражают scenarios и assertions.

## Связанные темы

- [Стратегия тестирования frontend](<./Стратегия тестирования frontend.md>)
- [Jest](<./Jest.md>)
- [React Testing Library](<./React Testing Library.md>)
- [MSW и моки API](<./MSW и моки API.md>)
- [Async UI формы и auth](<./Async UI формы и auth.md>)
- [E2E testing](<./E2E testing.md>)
- [Flaky tests](<./Flaky tests.md>)
- [Accessibility](<../HTML/Accessibility.md>)
- [Controlled и uncontrolled компоненты](<../React/Controlled и uncontrolled компоненты.md>)
- [Error Boundaries](<../React/Error Boundaries.md>)
- [HTTP запрос](<../Web Basics/HTTP запрос.md>)

## Источники

- [Testing Library Guiding Principles](https://testing-library.com/docs/guiding-principles/)
- [Jest 30.4: Getting Started](https://jestjs.io/docs/getting-started)
- [MSW documentation](https://mswjs.io/docs/)
- [Playwright documentation](https://playwright.dev/docs/intro)

---

<!-- NOTE-NAV-BOTTOM:START -->
[↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Стратегия тестирования frontend →](<./Стратегия тестирования frontend.md>)
<!-- NOTE-NAV-BOTTOM:END -->
