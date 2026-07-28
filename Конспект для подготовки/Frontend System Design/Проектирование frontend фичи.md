---
aliases:
  - frontend system design
  - проектирование frontend фичи
  - frontend feature design
  - system design frontend
---

#### Ответ на 60 секунд

Frontend system design - это проектирование пользовательского сценария целиком: какие данные нужны, где они живут, как грузятся, кешируются и обновляются, какие состояния видит пользователь, как обрабатываются ошибки, как работает доступность, performance, безопасность и тестирование. Это не выбор одной библиотеки, а связная архитектура фичи.

Хороший разбор начинается с требований и ограничений: кто пользователь, что он делает, какие данные приходят с backend, какие действия меняют состояние, нужен ли realtime, offline, роли, права, большие списки, SSR или SEO. После этого выбирают state ownership: local state, URL state, form state, server state, global client state. Затем проектируют API-контракт, UI states, error model, optimistic/pessimistic updates, performance и тесты.

На frontend-собеседовании важно показать не “я бы взял React Query и Redux”, а почему данные относятся к server state, почему filters лежат в URL, почему ошибки разделены, почему форма не отправляет DTO напрямую и как решение будет поддерживаться.

#### Ключевая схема

```text
requirements
-> data model and API contract
-> state ownership
-> UI states and interactions
-> errors and permissions
-> performance and accessibility
-> testing and observability
```

| Зона | Вопрос |
| --- | --- |
| Requirements | кто пользователь, какой сценарий, какие ограничения |
| Data | какие сущности, DTO/domain model, volume, freshness |
| State | local/server/URL/form/global |
| API | endpoints, cache key, cancellation, retries, errors |
| UI states | loading, empty, error, pending, disabled, success |
| UX/a11y | keyboard, focus, labels, responsive, feedback |
| Performance | list size, memoization, virtualization, code splitting |
| Testing | unit, integration, E2E, mocks, edge cases |

#### Развернутый ответ

Проектирование фичи начинается с границ. Например, “таблица пользователей” может быть простой страницей со списком, а может включать server-side filtering, роли доступа, bulk actions, realtime updates, экспорт, сохранение фильтров, deep links и audit log. Без уточнения требований легко выбрать неправильную архитектуру.

Дальше определяется владелец данных. Данные с backend обычно являются server state и живут в query/cache layer. Параметры страницы, которыми нужно поделиться ссылкой, живут в URL. Draft формы живёт в form state. Временное открытие dropdown - local state. Auth snapshot, theme или wizard progress могут быть global client state. Это защищает от одного большого store со всем подряд.

API-контракт проектируют вместе с UI. Для коллекций нужны pagination, filtering, sorting, search и стабильный cache key. Для mutations нужны pending state, optimistic или pessimistic update, rollback, invalidation и обработка server errors. Для внешних данных нужен mapping DTO -> domain/view model.

UI states должны быть явными. Фича должна понимать, что показывать при первой загрузке, refetch, пустом результате, ошибке сети, ошибке доступа, validation error, conflict, disabled action и успешном сохранении. Если эти состояния не описаны, они появляются случайно и по-разному на разных экранах.

Senior-level часть - trade-offs. Можно держать filters локально, но тогда нельзя поделиться ссылкой. Можно делать optimistic update, но нужен rollback. Можно взять WebSocket, но появятся reconnect, protocol versioning и cache synchronization. Можно сделать универсальный компонент, но он может стать сложнее локальных реализаций.

#### Где применяется во frontend

| Ситуация в проекте | Что проектируется | Что нужно явно решить |
| --- | --- | --- |
| Новый экран списка | коллекция, query params, cache, table/list UI | pagination, sorting, filters, loading/empty/error, URL state |
| Большая форма | form state, validation, submit, server errors | schema, async validation, DTO mapping, pending, disabled, focus errors |
| Protected area | auth, roles, route guards | refresh flow, redirect, access denied, cache cleanup |
| Realtime dashboard | snapshot + event stream | transport, reconnect, stale data, cache updates, throttling |
| Design-system компонент | behavior + visual API | accessibility, controlled/uncontrolled, composition, testing |
| Feature rollout | flags and fallback behavior | flag source, kill switch, analytics, test matrix |

> [!faq]+ Уточнения
> - System design frontend-фичи начинается с требований, а не с выбора библиотеки.
> - State ownership важнее, чем название state manager.
> - URL state используют для состояния страницы, которым нужно поделиться ссылкой.
> - Server state лучше держать в query/cache layer, а не дублировать в global store.
> - Ошибки нужно разделять: network, HTTP status, validation, domain conflict, permission.
> - Performance оценивают по размеру данных, частоте обновлений и месту выполнения операции.

#### Пример

Короткая рамка для проектирования фичи:

```text
1. User scenario: кто и что делает?
2. Data: какие сущности и объём данных?
3. API: какие запросы, mutations, ошибки, cache key?
4. State: что local/server/URL/form/global?
5. UI states: loading, empty, error, pending, success?
6. Edge cases: permissions, race conditions, stale data?
7. Performance: большие списки, expensive calculations, bundle?
8. Tests: что покрыть unit/integration/E2E?
```

#### Частые ошибки

- Начинать ответ с библиотеки без требований.
- Складывать весь state в Redux/Zustand.
- Не различать DTO, domain model и view model.
- Забывать URL state для фильтров и пагинации.
- Не описывать error states и access denied.
- Не думать о race conditions и cancellation.
- Не связывать design с тестами и observability.

#### Связанные темы

- [[Конспект для подготовки/Architecture/Frontend architecture]]
- [[Конспект для подготовки/Architecture/State management]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/Principles/SOLID во frontend]]
- [[Конспект для подготовки/Patterns/Adapter и Facade во frontend]]
- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]

#### Источники

- [React docs: Thinking in React](https://react.dev/learn/thinking-in-react)
- [web.dev: Core Web Vitals](https://web.dev/articles/vitals)
- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
