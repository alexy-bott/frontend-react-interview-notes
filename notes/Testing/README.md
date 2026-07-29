# Testing

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Frontend testing.md>)

Заметок в разделе: **8**
<!-- SECTION-NAV:END -->

## Темы

- [Frontend testing](<./Frontend testing.md>)
- [Стратегия тестирования frontend](<./Стратегия тестирования frontend.md>)
- [Jest](<./Jest.md>)
- [React Testing Library](<./React Testing Library.md>)
- [MSW и моки API](<./MSW и моки API.md>)
- [Async UI формы и auth](<./Async UI формы и auth.md>)
- [E2E testing](<./E2E testing.md>)
- [Flaky tests](<./Flaky tests.md>)

## Маршрут

1. Разделить unit, integration и E2E по реальным boundaries, затем сформулировать observable test oracle.
2. Построить risk-based strategy: критичные contracts, минимально достаточный уровень и regression policy.
3. Настроить Jest: environment, transforms, isolation, matchers, test doubles и fake-timer lifecycle.
4. Проверять UI через RTL: semantic queries, `userEvent`, async appearance/disappearance и test harness.
5. Понять MSW boundary: настоящий frontend HTTP-flow, controlled response и граница уверенности mock API.
6. Закрыть async scenarios: pending, `422`, race, retry, single-flight auth refresh и cleanup.
7. Проверить критичные flows в Playwright: browser/backend isolation, web-first assertions и diagnostics.
8. Устранить flaky: deterministic data/clock/state, root-cause triage, retries и временная quarantine policy.
