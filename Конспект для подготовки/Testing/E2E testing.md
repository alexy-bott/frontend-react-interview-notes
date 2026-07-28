---
aliases:
  - E2E
  - end-to-end testing
  - Playwright
  - Cypress
  - browser tests
---

#### Ответ на 60 секунд

E2E testing проверяет полный пользовательский сценарий в браузере: открыть приложение, выполнить действия, пройти routing, отправить запросы, увидеть результат. В отличие от unit и integration тестов, E2E даёт уверенность, что frontend, browser APIs, routing, network, storage и backend-контракт работают вместе. Цена этой уверенности - скорость, инфраструктура и риск flaky.

Для E2E выбирают небольшое число критичных flows: login, checkout, создание сущности, изменение прав, восстановление после ошибки, основной happy path продукта. Проверки маленьких состояний компонентов дешевле держать в integration-тестах. Стабильный E2E использует locators по role/text/test id, контролируемые test data, изолированное состояние и понятную очистку.

Playwright и Cypress решают похожую задачу: запускают браузер, управляют страницей и дают assertions. Playwright часто выбирают за автожидания, поддержку нескольких браузеров и удобную работу с contexts. Важно не название инструмента, а дисциплина: независимые тесты, предсказуемые данные, минимум sleep, диагностика через trace/video/screenshot и запуск в CI.

#### Ключевая схема

```text
real browser
-> user flow
-> app + routing + network + storage
-> assert visible business result
```

| Проверять в E2E | Не переносить в E2E |
| --- | --- |
| критичный пользовательский путь | каждую ветку маленького компонента |
| интеграцию frontend/backend | private function |
| routing/auth/permissions | все варианты formatter-а |
| smoke после деплоя | внутренний state |
| payment/order/login flow | мелкий CSS-класс |

#### Развернутый ответ

E2E проверяет приложение в наиболее близком к пользователю окружении: браузер, routing, storage, network, cookies, permissions и backend-контракт. Поэтому он даёт высокую уверенность, но стоит дороже. Стратегия E2E должна быть узкой: smoke, критичные business flows, auth/permissions, checkout/order, создание и сохранение ключевых сущностей.

Locators выбирают по пользовательскому смыслу: role, accessible name, label, text. `data-testid` полезен для технически сложных мест, где пользовательский селектор нестабилен или отсутствует, но он не должен заменять семантику везде.

Test data должны быть контролируемыми. Тест сам готовит данные через API/fixtures/seed или работает с известным окружением. Зависимость от результата предыдущего теста делает suite хрупким, особенно при параллельном запуске.

Network можно проверять через тестовый backend или перехватывать на уровне E2E-инструмента. Реальный backend-контракт полезен для smoke/acceptance сценариев. Routing/mocks удобны для редких ошибок, отказов интеграций и состояний, которые сложно стабильно подготовить в backend.

Flaky в E2E часто появляется из-за `sleep`, гонок, общего состояния, анимаций, нестабильной сети и неочищенных данных. Тест ждёт конкретное состояние: visible heading, enabled button, URL, response, toast, исчезновение loader. Trace/video/screenshot помогают быстро понять, где путь сломался.

> [!faq]+ Уточнения
> - E2E покрывает критичные пользовательские flows, а не каждую ветку компонента.
> - Locators строят вокруг role, accessible name, label и text.
> - Test data должны быть изолированы и подготовлены самим тестом или seed-ом.
> - Реальный backend полезен для smoke, network routing - для редких ошибок и edge cases.
> - `waitForTimeout` заменяют ожиданием конкретного UI/network состояния.

#### Пример Playwright

```ts
import { expect, test } from "@playwright/test";

test("user can log in", async ({ page }) => {
  await page.goto("/login");

  await page.getByLabel("Email").fill("user@example.com");
  await page.getByLabel("Password").fill("secret");
  await page.getByRole("button", { name: /sign in/i }).click();

  await expect(page.getByRole("heading", { name: /dashboard/i })).toBeVisible();
});
```

#### Частые ошибки

- Покрывать E2E слишком много мелких случаев.
- Использовать `waitForTimeout` вместо ожидания конкретного UI-состояния.
- Делать тесты зависимыми от порядка выполнения.
- Использовать нестабильные selectors.
- Не сохранять trace/video/screenshot для диагностики падений.
- Тестировать production-like flow без контроля данных и окружения.

#### Связанные темы

- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]
- [[Конспект для подготовки/Testing/Flaky tests]]
- [[Конспект для подготовки/HTML/Accessibility]]
- [[Конспект для подготовки/Web Basics/Cookies и авторизация]]

#### Источники

- [Playwright documentation](https://playwright.dev/docs/intro)
