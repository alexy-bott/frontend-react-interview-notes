#### Темы

- [[Конспект для подготовки/Architecture/Frontend architecture]]
- [[Конспект для подготовки/Architecture/FSD]]
- [[Конспект для подготовки/Architecture/State management]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/Architecture/Error handling и observability]]
- [[Конспект для подготовки/Architecture/Feature flags]]
- [[Конспект для подготовки/Architecture/Microfrontends]]

#### Маршрут

1. Начать с общей модели: boundaries, ownership, dependency direction и проверка локальности изменений.
2. Рассмотреть FSD как конкретную методологию layers/slices/segments, а не как единственный вариант архитектуры.
3. Определить владельцев local, URL, form, server и global client state до выбора библиотеки.
4. Построить API boundary: transport, runtime validation, DTO mapping, errors, cancellation и retries.
5. Продолжить production-границей: recovery, Error Boundaries, source maps, telemetry и privacy.
6. Разобрать feature flags как временное разделение deploy/release с lifecycle и безопасной evaluation.
7. Завершить microfrontends: сначала организационная причина, затем contracts, runtime failures и общие budgets.

#### Практическое продолжение

- [[Конспект для подготовки/Frontend System Design/Проектирование frontend фичи]]
- [[Конспект для подготовки/Principles/SOLID во frontend]]
- [[Конспект для подготовки/Patterns/Adapter и Facade во frontend]]
- [[Конспект для подготовки/Web Basics/OpenAPI и Swagger]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
