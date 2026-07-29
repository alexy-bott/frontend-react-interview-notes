---
aliases:
  - FSD
  - Feature-Sliced Design
  - feature sliced design
  - слои FSD
  - slices segments public api
---

#### Быстрый ответ

Feature-Sliced Design (FSD) - методология организации frontend-кода по бизнес-смыслу и направлению зависимостей. Она задаёт три уровня структуры: layers определяют масштаб ответственности, slices разделяют слой по domain/feature, segments группируют код slice по назначению.

Стандартный import rule разрешает module импортировать slices только из строго нижних layers. Например, `features/add-to-cart` использует `entities/product` и `shared/api`, но не внутренности другой feature или page. Slice открывает узкий public API, поэтому consumers не зависят от его файловой реализации.

#### Ключевая схема

```text
app
pages
widgets
features
entities
shared
```

Зависимости направлены сверху вниз. Не каждый проект и не каждая feature обязаны использовать все промежуточные layers.

| Структура | Отвечает на вопрос | Пример |
| --- | --- | --- |
| Layer | какой масштаб ответственности? | `features` |
| Slice | к какой бизнес-области относится? | `add-to-cart` |
| Segment | какую роль играет код внутри slice? | `ui`, `model`, `api` |
| Public API | что разрешено использовать снаружи? | `features/add-to-cart/index.ts` |

#### Базовая модель

`app` содержит bootstrap, providers, routing и global configuration. `pages` собирает route-level screens. `widgets` представляет крупные самостоятельные UI-блоки. `features` реализует значимое действие пользователя. `entities` описывает business entities и связанное с ними представление/данные. `shared` хранит инфраструктуру и UI, не знающие конкретного бизнеса.

В `pages`, `widgets`, `features` и `entities` обычно находятся slices по business domain. `app` и `shared` не делятся на business slices: у `shared/ui`, `shared/api` и `app/providers` сразу технические segments. Это исключение следует из назначения крайних layers.

Segments не являются жёстко закрытым списком, но называются по назначению: `ui`, `model`, `api`, `lib`, `config`. Корзины `components`, `hooks`, `types` сообщают формат файла хуже, чем роль кода, и часто размазывают одну feature.

#### Развернутый ответ

**Import rule.** Slice может зависеть от lower layers и собственного внутреннего кода. Горизонтальный import между slices одного layer запрещён, потому что скрывает composition и создаёт cycles. Две features обычно связываются в widget/page; общий domain contract опускается в entity/shared, если он действительно общий.

**Public API.** Внешний код импортирует только экспортируемый контракт slice, например `@/features/update-profile`. Deep import `@/features/update-profile/model/internal-store` привязывает consumer к внутренностям. Не следует создавать один barrel на весь layer: он увеличивает риск cycles и скрывает реальные dependencies.

**Cross-import entities.** Для неизбежной связи двух entities FSD описывает специальный `@x` public API, который явно делает cross-reference видимым. Это controlled exception, а не способ свободно импортировать любые same-layer slices.

**Granularity.** Feature формулируется как пользовательское действие с business value: `add-to-cart`, `change-password`. Entity - существительное предметной области: `product`, `user`. Не каждую кнопку выделяют в feature, а большой end-to-end flow не помещают целиком в одну entity.

**Внедрение.** Legacy-проект мигрируют постепенно: фиксируют aliases и import boundaries, выделяют `app/shared`, затем route pages и наиболее изменяемые business modules. Массовое перемещение файлов без ограничения новых imports создаёт новый каталог с прежней связностью.

#### Пример

```text
src/
  app/
    providers/
    router/
  pages/
    product/
      ui/
      index.ts
  widgets/
    product-details/
      ui/
      index.ts
  features/
    add-to-cart/
      ui/
      model/
      index.ts
  entities/
    product/
      api/
      model/
      ui/
      index.ts
  shared/
    api/
    lib/
    ui/
```

`pages/product` может собрать widget и feature. `features/add-to-cart` импортирует `entities/product`, но entity не знает о feature. Public API экспортирует только компоненты, types и actions, являющиеся контрактом slice.

#### Версии и совместимость

В актуальной документации используются layers `app`, `pages`, `widgets`, `features`, `entities`, `shared`. Layer `processes`, встречающийся в старых материалах FSD, deprecated; долгие сценарии теперь моделируют composition существующих slices и состоянием подходящего owner.

#### Ключевые уточнения

- FSD задаёт boundaries и import rule, а не только одинаковые названия папок.
- Layers описывают уровень ответственности, slices - business domain, segments - назначение кода; эти оси нельзя взаимозаменять.
- Same-layer composition поднимают выше, а общий контракт опускают ниже только при реальной общей ответственности.
- Public API защищает внутренности одного slice; giant barrel всего layer эту задачу не решает.
- Небольшой проект использует только нужные layers и усложняет структуру по мере появления реальной связности.

#### Связанные темы

- [[Конспект для подготовки/Architecture/Frontend architecture]]
- [[Конспект для подготовки/Architecture/State management]]
- [[Конспект для подготовки/Architecture/API слой и контракты]]
- [[Конспект для подготовки/Frontend System Design/Проектирование frontend фичи]]
- [[Конспект для подготовки/Testing/Стратегия тестирования frontend]]

#### Источники

- [Feature-Sliced Design: Overview](https://feature-sliced.design/docs/get-started/overview)
- [Feature-Sliced Design: Layers](https://feature-sliced.design/docs/reference/layers)
- [Feature-Sliced Design: Slices and segments](https://feature-sliced.design/docs/reference/slices-segments)
- [Feature-Sliced Design: Public API](https://feature-sliced.design/docs/reference/public-api)
