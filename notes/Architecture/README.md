# Architecture

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Frontend architecture.md>)

Заметок в разделе: **7**
<!-- SECTION-NAV:END -->

## Темы

- [Frontend architecture](<./Frontend architecture.md>)
- [FSD](<./FSD.md>)
- [State management](<./State management.md>)
- [API слой и контракты](<./API слой и контракты.md>)
- [Error handling и observability](<./Error handling и observability.md>)
- [Feature flags](<./Feature flags.md>)
- [Microfrontends](<./Microfrontends.md>)

## Маршрут

1. Начать с общей модели: boundaries, ownership, dependency direction и проверка локальности изменений.
2. Рассмотреть FSD как конкретную методологию layers/slices/segments, а не как единственный вариант архитектуры.
3. Определить владельцев local, URL, form, server и global client state до выбора библиотеки.
4. Построить API boundary: transport, runtime validation, DTO mapping, errors, cancellation и retries.
5. Продолжить production-границей: recovery, Error Boundaries, source maps, telemetry и privacy.
6. Разобрать feature flags как временное разделение deploy/release с lifecycle и безопасной evaluation.
7. Завершить microfrontends: сначала организационная причина, затем contracts, runtime failures и общие budgets.

## Практическое продолжение

- [Проектирование frontend фичи](<../Frontend System Design/Проектирование frontend фичи.md>)
- [SOLID во frontend](<../Principles/SOLID во frontend.md>)
- [Adapter и Facade во frontend](<../Patterns/Adapter и Facade во frontend.md>)
- [OpenAPI и Swagger](<../Web Basics/OpenAPI и Swagger.md>)
- [Frontend pipeline](<../DevOps/Frontend pipeline.md>)
