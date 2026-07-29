# Patterns

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Strategy во frontend.md>)

Заметок в разделе: **5**
<!-- SECTION-NAV:END -->

## Темы

- [Strategy во frontend](<./Strategy во frontend.md>)
- [Adapter и Facade во frontend](<./Adapter и Facade во frontend.md>)
- [Observer PubSub и события](<./Observer PubSub и события.md>)
- [Factory Singleton и lifecycle](<./Factory Singleton и lifecycle.md>)
- [Compound Components и Headless UI](<./Compound Components и Headless UI.md>)

## Маршрут

1. Начать со Strategy: отделить семейство взаимозаменяемых алгоритмов от обычного callback и простого условия.
2. Сравнить Adapter и Facade: первый согласует два контракта, второй упрощает работу с подсистемой.
3. Разобрать Observer и PubSub через участников, доставку события, lifecycle подписки и явность потока данных.
4. Разделить Factory, scope экземпляра и lifecycle: особенно важно для SPA, SSR и изоляции тестов.
5. Завершить UI-паттернами: Compound Components определяют форму API, а Headless UI отделяет поведение от оформления.

Для каждого паттерна сначала определяется решаемая проблема и граница применения. Узнавание знакомой структуры кода без этой связи недостаточно: один и тот же callback, context или wrapper может выполнять другую роль.
