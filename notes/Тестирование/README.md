# Тестирование

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./01 Тестирование фронтенда.md>)

Заметок в разделе: **8**
<!-- SECTION-NAV:END -->

## Темы

- [Тестирование фронтенда](<./01 Тестирование фронтенда.md>)
- [Стратегия тестирования фронтенда](<./02 Стратегия тестирования фронтенда.md>)
- [Jest](<./03 Jest.md>)
- [React Testing Library](<./04 React Testing Library.md>)
- [MSW и моки API](<./05 MSW и моки API.md>)
- [Асинхронный UI, формы и авторизация](<./06 Асинхронный UI, формы и авторизация.md>)
- [E2E-тестирование](<./07 E2E-тестирование.md>)
- [Нестабильные тесты (Flaky Tests)](<./08 Нестабильные тесты (Flaky Tests).md>)

## Маршрут

1. Разделить unit, integration и E2E по реальным boundaries, затем сформулировать observable test oracle.
2. Построить risk-based strategy: критичные contracts, минимально достаточный уровень и regression policy.
3. Настроить Jest: environment, transforms, isolation, matchers, test doubles и fake-timer lifecycle.
4. Проверять UI через RTL: semantic queries, `userEvent`, async appearance/disappearance и test harness.
5. Понять MSW boundary: настоящий frontend HTTP-flow, controlled response и граница уверенности mock API.
6. Закрыть async scenarios: pending, `422`, race, retry, single-flight auth refresh и cleanup.
7. Проверить критичные flows в Playwright: browser/backend isolation, web-first assertions и diagnostics.
8. Устранить flaky: deterministic data/clock/state, root-cause triage, retries и временная quarantine policy.
