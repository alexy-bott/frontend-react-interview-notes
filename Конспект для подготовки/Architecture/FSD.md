---
aliases:
  - FSD
  - Feature-Sliced Design
  - feature sliced design
  - слои FSD
  - slices segments public api
---

#### Ответ на 60 секунд

FSD, или Feature-Sliced Design, - это методология организации frontend-приложения вокруг бизнес-смысла и правил зависимостей. Она помогает не просто разложить файлы по папкам, а удерживать границы: где app setup, где страницы, где крупные виджеты, где пользовательские фичи, где доменные entities, где shared-инфраструктура.

Основные понятия FSD - layers, slices и segments. Layers задают уровень ответственности: `app`, `pages`, `widgets`, `features`, `entities`, `shared`; `processes` в актуальной версии считается deprecated. Slices делят слой по бизнес-доменам, например `user`, `article`, `cart`. Segments делят slice по назначению кода: `ui`, `model`, `api`, `lib`, `config`.

Главное правило зависимостей: модуль может импортировать только слои ниже себя. `features` может использовать `entities` и `shared`, но не другую `feature` напрямую и не `pages`. Это снижает циклы, скрытую связность и хаос при росте продукта. Для доступа наружу slice обычно открывает public API через `index.ts`, а внутренности slice не импортируются напрямую.

#### Ключевая схема

```text
app
pages
widgets
features
entities
shared
```

| Уровень | Что хранит | Пример |
| --- | --- | --- |
| `app` | providers, router, global styles, app init | `app/providers`, `app/router` |
| `pages` | route-level screens | `pages/profile` |
| `widgets` | крупные самостоятельные блоки страницы | `widgets/header`, `widgets/profile-card` |
| `features` | пользовательские действия с бизнес-ценностью | `features/update-profile`, `features/add-to-cart` |
| `entities` | доменные сущности | `entities/user`, `entities/product` |
| `shared` | инфраструктура без знания бизнеса | `shared/ui`, `shared/api`, `shared/lib` |

```text
slice/
  ui/
  model/
  api/
  lib/
  index.ts
```

#### Развернутый ответ

FSD решает проблему роста связности. В маленьком проекте технические папки `components`, `hooks`, `api`, `utils` могут работать нормально. В большом продукте они часто размазывают одну фичу по всему `src`: UI лежит в одном месте, запросы в другом, state в третьем, типы в четвёртом. Изменение сценария становится поиском по проекту. FSD собирает логически связанные части ближе друг к другу и ограничивает направление зависимостей.

Layers отвечают на вопрос “какой уровень ответственности у этого кода?”. `shared` не знает бизнес-сценариев. `entities` описывает доменные модели и базовые операции с ними. `features` реализует действия пользователя. `widgets` собирает несколько фич/entities в крупный блок. `pages` композиционно собирает экран маршрута. `app` соединяет роутинг, провайдеры и глобальную инициализацию.

Slices отвечают на вопрос “к какой бизнес-области относится код?”. Например, `entities/user` содержит код вокруг пользователя, а `features/update-profile` - конкретное действие обновления профиля. Slices одного слоя не должны импортировать друг друга напрямую, потому что это создаёт горизонтальную связность. Если двум slices нужен общий код, его поднимают ниже по слоям или выделяют отдельный контракт.

Segments отвечают на вопрос “какая техническая роль у файла внутри slice?”. `ui` хранит отображение, `model` - состояние и бизнес-правила, `api` - запросы и DTO, `lib` - локальные helpers, `config` - настройки. Названия segments должны помогать искать назначение кода. Поэтому `components`, `hooks`, `types` как универсальные корзины часто дают меньше пользы, чем `ui`, `model`, `api`.

Public API защищает slice от импорта внутренних файлов. Внешний код импортирует из `features/update-profile`, а не из `features/update-profile/model/internalStore`. Это позволяет менять внутреннюю структуру slice без массового рефакторинга потребителей. Public API должен быть узким: наружу выводят только то, что действительно является контрактом slice.

FSD не требует использовать все слои в каждом проекте. Для небольшого приложения может хватить `app`, `pages`, `features` и `shared`, а `widgets` или `entities` появятся позже. Методология полезна, когда проект растёт, фич много, команда меняется, а границы между модулями начинают расплываться.

> [!faq]+ Уточнения
> - FSD - это архитектурная методология, а не библиотека и не state manager.
> - Слои стандартизированы; новые слои добавляют редко, потому что ломается общий смысл и import rule.
> - `processes` в FSD v2.1 считается deprecated.
> - `shared` и `app` не делятся на slices, они делятся сразу на segments.
> - Public API slice обычно делают через `index.ts`.
> - FSD можно внедрять постепенно: сначала `app/shared`, затем pages/widgets, потом features/entities и исправление import violations.

#### Пример

```text
src/
  app/
    providers/
    router/
    styles/

  pages/
    profile/
      ui/
      index.ts

  widgets/
    profile-card/
      ui/
      model/
      index.ts

  features/
    update-profile/
      ui/
      model/
      api/
      index.ts

  entities/
    user/
      model/
      api/
      index.ts

  shared/
    api/
    config/
    lib/
    ui/
```

Допустимая зависимость:

```ts
// features/update-profile/model/useUpdateProfile.ts
import { userApi } from "@/entities/user";
import { apiClient } from "@/shared/api";
```

Проблемная зависимость:

```ts
// features/update-profile/model/useUpdateProfile.ts
import { useDeleteAccount } from "@/features/delete-account/model/useDeleteAccount";
```

Здесь одна feature лезет во внутренности другой feature. Обычно такой сценарий решают через композицию выше по слою, общий domain contract в `entities` или явный public API, если связь действительно нужна.

#### Частые ошибки

- Считать FSD простой схемой папок без правил зависимостей.
- Делать `shared` складом всего, что некуда положить.
- Импортировать внутренности slice вместо public API.
- Создавать slices по техническому признаку, а не по бизнес-домену.
- Делать feature слишком большой и смешивать несколько пользовательских сценариев.
- Выносить код в `entities`, когда это действие пользователя, а не доменная сущность.
- Внедрять FSD резко во всём legacy-проекте без промежуточных правил и линтинга.

#### Связанные темы

- [[Конспект для подготовки/Architecture/Frontend architecture]]
- [[Конспект для подготовки/Architecture/State management]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/Architecture/Feature flags]]
- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]
- [[Конспект для подготовки/React/Redux Toolkit]]
- [[Конспект для подготовки/React/RTK Query]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]

#### Источники

- [Feature-Sliced Design: Overview](https://feature-sliced.design/docs/get-started/overview)
- [Feature-Sliced Design: Layers](https://feature-sliced.design/docs/reference/layers)
- [Feature-Sliced Design: Slices and segments](https://feature-sliced.design/docs/reference/slices-segments)
