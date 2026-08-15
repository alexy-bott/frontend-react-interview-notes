# Архитектура

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./01 Архитектура фронтенда.md>)

Заметок в разделе: **7**
<!-- SECTION-NAV:END -->

## Темы

- [Архитектура фронтенда](<./01 Архитектура фронтенда.md>)
- [Feature-Sliced Design (FSD)](<./02 Feature-Sliced Design (FSD).md>)
- [Управление состоянием](<./03 Управление состоянием.md>)
- [API-слой и контракты](<./04 API-слой и контракты.md>)
- [Обработка ошибок и наблюдаемость](<./05 Обработка ошибок и наблюдаемость.md>)
- [Флаги функциональности (Feature Flags)](<./06 Флаги функциональности (Feature Flags).md>)
- [Микрофронтенды](<./07 Микрофронтенды.md>)

## Маршрут

1. Начать с общей модели: boundaries, ownership, dependency direction и проверка локальности изменений.
2. Рассмотреть FSD как конкретную методологию layers/slices/segments, а не как единственный вариант архитектуры.
3. Определить владельцев local, URL, form, server и global client state до выбора библиотеки.
4. Построить API boundary: transport, runtime validation, DTO mapping, errors, cancellation и retries.
5. Продолжить production-границей: recovery, Error Boundaries, source maps, telemetry и privacy.
6. Разобрать feature flags как временное разделение deploy/release с lifecycle и безопасной evaluation.
7. Завершить microfrontends: сначала организационная причина, затем contracts, runtime failures и общие budgets.

## Практическое продолжение

- [Проектирование фронтенд-фичи](<../Системный дизайн фронтенда/01 Проектирование фронтенд-фичи.md>)
- [SOLID во фронтенде](<../Принципы разработки/01 SOLID во фронтенде.md>)
- [Адаптер и фасад](<../Паттерны/02 Адаптер и фасад.md>)
- [OpenAPI и Swagger](<../Основы веб-платформы/09 OpenAPI и Swagger.md>)
- [CI-CD-пайплайн фронтенда](<../DevOps/07 CI-CD-пайплайн фронтенда.md>)
