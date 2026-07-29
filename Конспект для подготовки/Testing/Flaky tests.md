---
aliases:
  - flaky tests
  - нестабильные тесты
  - test flakiness
---

#### Быстрый ответ

Flaky test - это тест, который иногда проходит, а иногда падает без изменения кода. Для frontend это особенно частая проблема из-за асинхронности, DOM-обновлений, network, timers, animations, shared state и реального браузера. Опасность flaky не только в красном CI: команда перестаёт доверять тестам, начинает перезапускать pipeline и пропускает настоящие регрессии.

Основной принцип борьбы - убрать неопределённость. Тест должен ждать конкретное состояние, а не фиксированное время; каждый тест должен сам готовить данные и чистить за собой; network и timers должны быть контролируемыми; selectors должны быть стабильными; параллельные тесты не должны делить один и тот же mutable state. Для E2E нужны trace, screenshot, video и логи, чтобы быстро понять причину падения.

Retries могут быть временной страховкой, но не лечением. Для flaky-теста классифицируют причину: race condition, нестабильный selector, нестабильные данные, timeout, external dependency, animation, timezone, random, leak между тестами. После фикса полезно добавить регрессионную проверку или улучшить test helper.

#### Ключевая схема

```text
flaky failure
-> reproduce or inspect trace
-> classify cause
-> remove nondeterminism
-> keep test independent
```

| Причина | Что делать |
| --- | --- |
| fixed sleep | ждать роль/текст/network/URL |
| shared data | seed + cleanup + unique ids |
| real network | mock, test backend, contract |
| timers/debounce | fake timers или явное ожидание |
| animation | отключить или ждать финальное состояние |
| bad selector | role/name/test id |
| timezone/random | зафиксировать clock/random |

#### Базовая модель

Flaky появляется, когда тест зависит от неопределённого фактора: времени, порядка выполнения, сети, общего состояния, анимации, timezone, random, leakage между тестами или внешнего сервиса. Такой тест опасен не только падениями CI, но и потерей доверия к проверкам.

Flakiness бывает и в обратную сторону: test иногда проходит при наличии bug из-за слабого assertion или race. Поэтому цель — deterministic preconditions, action и oracle, а не только устранение случайных красных запусков.

#### Развернутый ответ

`sleep` не решает синхронизацию. `wait 1000 ms` может быть слишком длинным на быстром окружении и слишком коротким на медленном CI. Вместо фиксированного времени тест ждёт конкретное условие: элемент виден, кнопка enabled, URL изменился, request завершился, loader исчез, toast появился.

Изоляция тестов убирает зависимость от порядка. Для E2E это отдельный пользователь или уникальные данные, reset storage/cookies, очистка созданных сущностей и отсутствие общего mutable state. Для Jest/RTL - очистка DOM, mocks, timers, localStorage и handlers между тестами.

Диагностика должна сохранять контекст падения. Для E2E нужны trace, screenshots, video, console/network logs. Для component/integration tests помогают `screen.debug()`, понятные custom render helpers, явное логирование mock handlers и воспроизводимые fake timers.

Retries допустимы как временная защита от инфраструктурного шума, но flaky-тест должен попадать в triage. Если просто увеличить timeout или число retries, suite становится медленнее, а настоящая причина остаётся.

Retry может помочь обнаружить flaky: первый run упал, retry прошёл. Такой результат маркируют и учитывают в качестве suite, а не считают полностью успешным. Quarantine допустим только временно, с owner и сроком исправления; удалённая из blocking suite проверка больше не защищает release.

#### Диагностика

| Симптом | Где искать причину |
| --- | --- |
| Падает только в CI | скорость окружения, headless browser, timezone, ресурсы runner-а |
| Падает только в suite | протекание mocks, timers, DOM, storage или shared user data |
| Падает на ожидании | неправильное условие ожидания, loader, network, animation |
| Падает после параллелизации | общая база, общий аккаунт, одинаковые ids |
| Падает редко | race condition, retry/backoff, непредсказуемый backend response |

#### Ключевые уточнения

- Ожидание привязывают к observable condition, а timeout ограничивает failure, но не синхронизирует flow.
- Test data, clock, timezone, locale, random seed и external responses делают воспроизводимыми там, где они влияют на result.
- Параллельные tests не делят mutable account/entity; unique namespace важнее очистки после аварийного падения.
- Retry фиксирует симптом и собирает diagnostics, но passing retry не делает test надёжным.
- Quarantine имеет owner/deadline и снижает protection, поэтому не становится постоянным архивом.
- Root cause ищут по trace/logs и воспроизводят стрессом/повторами, а не маскируют увеличением timeout.

#### Связанные темы

- [[Конспект для подготовки/Testing/Jest]]
- [[Конспект для подготовки/Testing/E2E testing]]
- [[Конспект для подготовки/Testing/MSW и моки API]]
- [[Конспект для подготовки/Testing/React Testing Library]]
- [[Конспект для подготовки/JavaScript/Event Loop]]

#### Источники

- [Playwright: Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright: Trace Viewer](https://playwright.dev/docs/trace-viewer)
- [Testing Library: Async Methods](https://testing-library.com/docs/dom-testing-library/api-async/)
- [Testing Library: Using Fake Timers](https://testing-library.com/docs/using-fake-timers/)
