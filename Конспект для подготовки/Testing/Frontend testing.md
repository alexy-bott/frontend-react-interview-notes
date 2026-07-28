---
aliases:
  - frontend testing
  - unit tests
  - integration tests
  - e2e tests
  - React Testing Library
---

#### Ответ на 60 секунд

Frontend testing проверяет, что интерфейс работает правильно на разных уровнях. Unit tests проверяют маленькие функции или компоненты в изоляции. Integration tests проверяют связку нескольких частей: компонент, форму, запрос, состояние. E2E tests проверяют пользовательский сценарий целиком в браузере.

Для React часто используют Testing Library, потому что ее философия - тестировать поведение так, как пользователь взаимодействует с интерфейсом, а не внутреннюю реализацию компонента. Элементы ищут по роли, label, тексту и доступному имени, а не по className или внутренним state.

#### Ключевая схема

| Уровень | Что проверяет | Пример |
| --- | --- | --- |
| Unit | маленькую функцию/компонент | formatter, reducer |
| Integration | связку частей | форма отправляет данные |
| E2E | сценарий в браузере | login, checkout |
| Mock | замена внешней зависимости | API, timers, storage |

#### Развернутый ответ

Frontend tests дают разную степень уверенности на разных уровнях. Unit test быстрый и дешёвый, но проверяет маленький кусок: formatter, reducer, чистую функцию. Integration test проверяет связку: компонент, state, form validation, API response, router context. E2E test открывает браузер и проверяет весь пользовательский путь, но требует больше инфраструктуры и времени.

Компонент тестируют через публичное поведение: что пользователь видит, какие действия может выполнить, какие состояния появляются после взаимодействия. Внутренние hooks, private functions и implementation details не являются контрактом UI, поэтому такие проверки ломаются от рефакторинга без реальной регрессии.

Mocks используют на внешних границах, где зависимость делает тест медленным, нестабильным или неподконтрольным: network, timers, storage, analytics, browser APIs. API удобнее мокать на уровне сети через MSW, потому что приложение продолжает проходить настоящий request flow, а тест не привязывается к внутренней функции API-клиента.

Integration и E2E отличаются глубиной окружения. Integration обычно быстрее и работает в тестовой среде с моками внешних границ. E2E проверяет реальный браузер, routing, storage, network и часто backend-контракт. Поэтому E2E оставляют для критичных flows, а не для каждой мелкой ветки компонента.

> [!faq]+ Уточнения
> - Unit tests проверяют маленькую логику, integration - связку частей, E2E - полный путь пользователя.
> - UI-компонент тестируют через DOM-поведение, а не через внутренний state.
> - Mocks нужны на внешних границах: network, timers, storage, analytics, browser APIs.
> - MSW мокает HTTP boundary и меньше привязывает тест к структуре модулей.
> - E2E дороже, поэтому покрывает самые ценные сценарии.

#### Пример

```tsx
render(<LoginForm />);

await user.type(screen.getByLabelText(/email/i), "a@b.com");
await user.click(screen.getByRole("button", { name: /login/i }));

expect(await screen.findByText(/welcome/i)).toBeInTheDocument();
```

#### Частые ошибки

- Тестировать implementation details вместо поведения.
- Искать элементы по className, когда есть role или label.
- Мокать слишком много и терять уверенность в реальном сценарии.
- Делать все проверки только через E2E и получать медленный flaky suite.
- Не проверять accessibility-семантику форм и кнопок.

#### Связанные темы

- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]
- [[Конспект для подготовки/Testing/Jest]]
- [[Конспект для подготовки/Testing/React Testing Library]]
- [[Конспект для подготовки/Testing/MSW и моки API]]
- [[Конспект для подготовки/Testing/Async UI формы и auth]]
- [[Конспект для подготовки/Testing/E2E testing]]
- [[Конспект для подготовки/Testing/Flaky tests]]
- [[Конспект для подготовки/HTML/Accessibility]]
- [[Конспект для подготовки/React/Controlled и uncontrolled компоненты]]
- [[Конспект для подготовки/React/Error Boundaries]]
- [[Конспект для подготовки/Web Basics/HTTP запрос]]

#### Источники

- [Testing Library Guiding Principles](https://testing-library.com/docs/guiding-principles/)
- [Jest 30.4: Getting Started](https://jestjs.io/docs/getting-started)
- [MSW documentation](https://mswjs.io/docs/)
- [Playwright documentation](https://playwright.dev/docs/intro)
