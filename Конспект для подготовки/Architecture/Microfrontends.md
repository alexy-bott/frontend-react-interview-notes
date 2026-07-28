---
aliases:
  - microfrontends
  - micro frontends
  - микрофронтенды
---

#### Ответ на 60 секунд

Microfrontends - это подход, где frontend-продукт делится на автономные части, которые могут разрабатывать и релизить разные команды. Идея похожа на microservices, но в UI: отдельные домены или vertical slices поставляются независимо и собираются в общий shell.

Главная польза microfrontends не в технологии, а в организационной независимости. Они имеют смысл, когда продукт большой, команды автономны, релизные циклы конфликтуют, а границы доменов достаточно стабильны. Цена тоже высокая: сложнее routing, shared dependencies, дизайн-система, auth, observability, performance, SSR/hydration и согласованность UX.

#### Ключевая схема

| Подход | Смысл |
| --- | --- |
| Build-time composition | части собираются вместе во время build |
| Runtime composition | shell подключает remote-приложения в runtime |
| Route-based split | разные маршруты принадлежат разным командам |
| Component-level split | remote-компоненты внутри одной страницы |
| Shared design system | общий UI-язык и контракты |

#### Развернутый ответ

Microfrontends оправданы, когда проблема находится в масштабе команд и релизной независимости, а не просто в размере bundle. Если одна команда может поддерживать модульный монолит, microfrontends часто добавляют лишнюю сложность: несколько сборок, shared dependencies, routing, auth, monitoring, performance budget и единый UX.

Реализация зависит от степени независимости и изоляции. Module Federation и runtime composition дают независимые релизы remote-приложений. Build-time packages проще для контроля версий, но релизятся вместе с shell. Iframe даёт сильную изоляцию, но усложняет UX, коммуникацию и доступность. Web Components подходят для отдельных виджетов, но не снимают вопросы state, auth и design system.

Общие зависимости должны иметь явный контракт. React, router, design system, telemetry SDK и shared utils нельзя бесконтрольно дублировать в каждом remote: это увеличивает bundle, может сломать hooks/context и создаёт разные визуальные паттерны. Shell часто отвечает за bootstrap, routing, auth context, feature flags и общие провайдеры.

Авторизация не должна держаться только на UI. Shell может передавать remote-приложениям user/session context, но backend всё равно проверяет права. Remote UI, который скрыл кнопку, не защищает API от прямого вызова.

Performance - один из главных рисков: много independent chunks, поздняя загрузка remote entry, waterfall-запросы, дублирование зависимостей, разные CSS-стратегии, SSR/hydration complexity и сложность preloading. Поэтому microfrontends требуют budget, мониторинг и договорённости между командами.

> [!faq]+ Уточнения
> - Microfrontends решают организационный масштаб и независимые релизы, а не просто “большое приложение”.
> - Module Federation, single-spa, iframe, web components и build-time packages дают разные компромиссы.
> - Shared dependencies должны быть согласованы, особенно React, router и design system.
> - Shell часто отвечает за bootstrap, routing, auth context и общие провайдеры.
> - Performance budget обязателен из-за remote entries, дублирования и waterfall.

#### Пример выбора

```text
Один продукт, одна команда, общий релиз -> модульный монолит
Несколько доменов, разные команды, независимые релизы -> microfrontends возможны
Нужна сильная изоляция внешнего виджета -> iframe или web component
Нужен общий shell с route-level ownership -> runtime composition
```

#### Частые ошибки

- Выбирать microfrontends только потому, что приложение стало большим.
- Не иметь стабильных доменных границ между командами.
- Дублировать React, design system и общие SDK в каждом remote.
- Забывать про единый monitoring, error boundary и correlation id.
- Делать независимый UI без общих accessibility и design-system правил.
- Не считать стоимость SSR, hydration и performance.

#### Связанные темы

- [[Конспект для подготовки/Architecture/Frontend architecture]]
- [[Конспект для подготовки/Architecture/Error handling и observability]]
- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]
- [[Конспект для подготовки/React/SSR и SSG]]
- [[Конспект для подготовки/React/Hydration]]

#### Источники

- [micro-frontends.org](https://micro-frontends.org/)
- [Webpack: Module Federation](https://webpack.js.org/concepts/module-federation/)
- [single-spa documentation](https://single-spa.js.org/docs/getting-started-overview/)
- [web.dev: Core Web Vitals](https://web.dev/articles/vitals)
