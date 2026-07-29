# Microfrontends

<!-- NOTE-NAV-TOP:START -->
[← Feature flags](<./Feature flags.md>) · [↑ Architecture](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Microfrontends разделяют frontend-продукт на vertical slices, которыми независимо владеют команды и которые собираются в единый пользовательский интерфейс. Основная задача - организационная автономия: команда изменяет, тестирует и выпускает свой business domain с минимальной координацией общего релиза.

Независимость оплачивается runtime и governance-сложностью: routing, versioned contracts, auth context, design system, accessibility, shared dependencies, telemetry, loading failures и performance budgets. Если одна команда и общий pipeline способны развивать модульный монолит, microfrontends обычно не решают дополнительной проблемы.

## Ключевая схема

```text
stable business boundaries + team ownership
-> integration contract
-> independent build/deploy
-> shell/runtime composition
-> shared UX and platform policies
-> end-to-end observability and fallback
```

| Способ композиции | Автономия | Основной компромисс |
| --- | --- | --- |
| Route-level | высокая, простой ownership URL | переходы и shared shell нужно согласовать |
| Runtime modules / Module Federation | независимый deploy внутри SPA | version skew, remote loading и shared scope |
| Build-time packages | простой runtime и type checking | consumer rebuild связывает releases |
| Web Components | framework-neutral element contract | state/SSR/forms/style integration остаются |
| iframe | сильная runtime/style isolation | communication, navigation и accessibility сложнее |

## Базовая модель

Граница проходит по business capability, а не по техническому элементу. Команда checkout владеет UI, data access, tests и release checkout; отдельная команда «кнопок» не создаёт самостоятельный user value и вынуждена координироваться со всеми.

Shell обычно владеет bootstrap, top-level routing, session context, navigation, global error handling и подключением remotes. Remote экспортирует versioned entry contract и не обращается к внутренностям соседа. Общие действия проходят через URL, typed events или platform services с явной семантикой.

Independent repository или build ещё не гарантирует независимый release. Если любое изменение remote требует синхронно обновить shell и другие remotes, система остаётся распределённым монолитом с более дорогой сборкой.

## Развернутый ответ

**Границы команд.** Microfrontend оправдан устойчивым domain ownership, разными release cadences и возможностью команды самостоятельно поддерживать production. Нестабильные границы приводят к частому переносу кода и cross-remote calls.

**Contracts и version skew.** Shell и remote могут работать в версиях, выпущенных в разные дни. Contract эволюционирует backward-compatible: optional capabilities, version negotiation или coordinated deprecation. TypeScript в одном build не проверяет remote, загруженный позже, поэтому runtime boundary всё равно валидируется.

**Shared dependencies.** Module Federation может делить React, router и design system через shared scope, но singleton/version settings требуют согласованности. Две копии React способны нарушить assumptions hooks/context; принудительный singleton с несовместимой версией тоже ломает remote. Dependency policy тестируют как часть integration contract.

**State.** Один global mutable store для всех remotes создаёт сильную связанность схемы и release. Shell передаёт минимальный session/platform context, server state получает каждый domain через API/cache, а cross-domain event содержит business fact, не внутренний reducer action.

**Failure isolation.** Remote entry или chunk может не загрузиться независимо от shell. Нужны timeout, Error Boundary, fallback, retry и telemetry с remote name/version. Предыдущая совместимая версия или route-level недоступность часто безопаснее падения всего приложения.

**UX и accessibility.** Design system задаёт tokens и primitives, но не гарантирует одинаковый сценарий. Команды согласуют navigation, focus transfer, overlays, localization и error language. E2E проверяет переходы через boundaries.

**Performance.** Каждая автономная сборка способна добавить framework, SDK и CSS. Общий budget считают на user route, включая shell и remotes, а waterfall проверяют на cold cache и слабом device. Независимый deploy не освобождает от общего Core Web Vitals результата.

## Пример выбора

| Контекст | Предпочтительный старт | Причина |
| --- | --- | --- |
| Одна команда, один release | модульный монолит | меньше operational overhead |
| Несколько domain-команд, routes независимы | route-level composition | ясные boundaries и failure isolation |
| Remote component нужен внутри общей page | runtime composition | независимый deploy ценой сложного contract |
| Внешний недоверенный widget | iframe | сильнее изоляция origin/runtime |
| Общая библиотека обновляется синхронно | build-time package | независимый runtime не требуется |

Решение принимают после описания ownership, release requirement, failure model и performance budget. Сам размер codebase не является достаточным критерием.

## Ключевые уточнения

- Microfrontends оптимизируют автономию команд и releases, а не автоматически скорость страницы или качество modules.
- Runtime composition требует backward-compatible contract, потому что host и remote живут в разных версиях.
- Shared singleton уменьшает duplication только при совместимых версиях и корректной initialization; это не бесплатная настройка.
- Общий store и deep imports превращают remotes в распределённый монолит.
- Failure, accessibility и performance оцениваются для целого user journey, даже если ownership разделён.

## Связанные темы

- [Frontend architecture](<./Frontend architecture.md>)
- [Error handling и observability](<./Error handling и observability.md>)
- [API слой и контракты](<./API слой и контракты.md>)
- [Bundlers и code splitting](<../Web Basics/Bundlers и code splitting.md>)
- [Bundle size и loading strategy](<../Performance/Bundle size и loading strategy.md>)
- [Hydration](<../React/Hydration.md>)

## Источники

- [Martin Fowler: Micro Frontends](https://martinfowler.com/articles/micro-frontends.html)
- [webpack: Module Federation](https://webpack.js.org/concepts/module-federation/)
- [single-spa: Recommended Setup](https://single-spa.js.org/docs/recommended-setup/)
- [micro-frontends.org](https://micro-frontends.org/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Feature flags](<./Feature flags.md>) · [↑ Architecture](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-BOTTOM:END -->
