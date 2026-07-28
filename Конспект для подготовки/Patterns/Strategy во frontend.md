---
aliases:
  - Strategy pattern
  - стратегия
  - strategy frontend
  - strategy pattern React
---

#### Ответ на 60 секунд

Strategy - это паттерн, где семейство вариантов поведения выносится в отдельные взаимозаменяемые функции или объекты, а основной код выбирает нужную стратегию через конфиг, props или key. Вместо большого `if/else` внутри компонента появляется явный контракт: “вот алгоритм сортировки”, “вот валидатор”, “вот renderer”, “вот способ форматирования”.

Во frontend Strategy часто встречается в таблицах, формах, фильтрах, форматтерах, feature flags, вариантах оплаты, авторизации, analytics providers и UI-компонентах с разным поведением. Паттерн полезен, когда вариантов уже несколько и они будут добавляться дальше.

Главная граница: Strategy не нужна для одного-двух простых условий. Если абстракция сложнее самого `if`, код станет менее понятным. Strategy применяют, когда поведение реально меняется по одному контракту и основной код не должен знать детали каждого варианта.

#### Ключевая схема

| Часть | Роль |
| --- | --- |
| Context | код, который использует стратегию |
| Strategy contract | общий интерфейс поведения |
| Concrete strategy | конкретная реализация |
| Strategy selection | выбор стратегии по props/config/key |

```text
Table
-> получает sortStrategy
-> вызывает sortStrategy(rows)
-> не знает детали конкретной сортировки
```

#### Развернутый ответ

Strategy отделяет “что нужно сделать” от “каким способом это сделать”. Компонент или service знает общий контракт, но не содержит все варианты поведения внутри себя. Это помогает соблюдать OCP: новый вариант добавляется новой стратегией, а стабильный код не переписывается.

Во frontend Strategy часто выглядит как обычная функция. Например, `sortByName`, `sortByDate`, `sortByPriority` могут иметь одинаковую сигнатуру `(items) => sortedItems`. Таблица принимает нужную функцию через props или выбирает её из словаря по key.

Похожий подход работает для validation. Форма может принимать схему или набор validators, а не хранить внутри себя правила для login, profile, checkout и admin-сценария. UI показывает ошибки, submit lifecycle остаётся общим, а business rules меняются снаружи.

Strategy также помогает тестированию. Конкретную стратегию можно протестировать отдельно от UI, а компонент можно проверить с простой mock-стратегией. Это особенно полезно, когда алгоритм сортировки, фильтрации или pricing logic сложнее обычного render.

#### Где применяется во frontend

| Ситуация в проекте | Что меняется | Strategy-решение |
| --- | --- | --- |
| Таблица сортирует users, orders и invoices разными правилами | алгоритм сортировки зависит от экрана | передать `sortStrategy(rows, sortState)` или выбрать strategy из `sortStrategies[type]` |
| Одна форма используется для разных ролей пользователя | validation rules зависят от роли | передать validation schema/validator вместо `if (role === ...)` внутри формы |
| Цена считается по разным тарифам | business calculation зависит от plan/country/feature flag | вынести `pricingStrategy.calculate(input)` |
| Один analytics event отправляется в разные providers | транспорт и формат события разные | сделать `analyticsProvider.track(event)` с реализациями для Amplitude/GA/mock |
| Таблица имеет разные render-ы ячеек | отображение зависит от типа колонки | columns config содержит `renderCell(row)` |
| Auth flow отличается для password, OAuth и SSO | способ входа разный, результат похожий | `authStrategy.login(credentials)` возвращает общий результат |

> [!faq]+ Уточнения
> - Strategy часто реализуется простой функцией, не обязательно классом.
> - Паттерн полезен, когда вариантов поведения несколько и они будут расширяться.
> - Если условие одно и оно понятно, Strategy может быть лишней.
> - Strategy хорошо сочетается с OCP: новый вариант добавляется без переписывания context-кода.
> - В React strategy часто передают через props, config, hook parameters или context.

#### Пример

```ts
type SortStrategy<T> = (items: T[]) => T[];

const sortByName: SortStrategy<User> = users =>
  [...users].sort((a, b) => a.name.localeCompare(b.name));

const sortByCreatedAt: SortStrategy<User> = users =>
  [...users].sort((a, b) => b.createdAt.localeCompare(a.createdAt));

function UserTable({
  users,
  sortStrategy,
}: {
  users: User[];
  sortStrategy: SortStrategy<User>;
}) {
  const sortedUsers = useMemo(
    () => sortStrategy(users),
    [users, sortStrategy],
  );

  return <Table rows={sortedUsers} />;
}
```

`UserTable` не знает, какая сортировка нужна конкретному экрану. Экран передаёт стратегию.

#### Частые ошибки

- Делать Strategy ради одного простого условия.
- Прятать выбор стратегии в глобальном singleton, из-за чего код трудно тестировать.
- Не определить общий контракт и получить стратегии с разными входами/выходами.
- Передавать inline strategy без memoization в memoized child.
- Называть Strategy любой callback, даже если нет семейства вариантов поведения.

#### Связанные темы

- [[Конспект для подготовки/Principles/SOLID во frontend]]
- [[Конспект для подготовки/Principles/DRY KISS YAGNI]]
- [[Конспект для подготовки/Patterns/Adapter и Facade во frontend]]
- [[Конспект для подготовки/Algorithms/Сложность Array методов]]
- [[Конспект для подготовки/Forms/Валидация форм]]
- [[Конспект для подготовки/React/Мемоизация]]

#### Источники

- Design Patterns: Elements of Reusable Object-Oriented Software
- [React docs: Passing props to a component](https://react.dev/learn/passing-props-to-a-component)
