#### Темы

- [[Конспект для подготовки/Testing/Frontend testing]]
- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]
- [[Конспект для подготовки/Testing/Jest]]
- [[Конспект для подготовки/Testing/React Testing Library]]
- [[Конспект для подготовки/Testing/MSW и моки API]]
- [[Конспект для подготовки/Testing/Async UI формы и auth]]
- [[Конспект для подготовки/Testing/E2E testing]]
- [[Конспект для подготовки/Testing/Flaky tests]]

#### Маршрут

1. Разделить unit, integration и E2E по реальным boundaries, затем сформулировать observable test oracle.
2. Построить risk-based strategy: критичные contracts, минимально достаточный уровень и regression policy.
3. Настроить Jest: environment, transforms, isolation, matchers, test doubles и fake-timer lifecycle.
4. Проверять UI через RTL: semantic queries, `userEvent`, async appearance/disappearance и test harness.
5. Понять MSW boundary: настоящий frontend HTTP-flow, controlled response и граница уверенности mock API.
6. Закрыть async scenarios: pending, `422`, race, retry, single-flight auth refresh и cleanup.
7. Проверить критичные flows в Playwright: browser/backend isolation, web-first assertions и diagnostics.
8. Устранить flaky: deterministic data/clock/state, root-cause triage, retries и временная quarantine policy.
