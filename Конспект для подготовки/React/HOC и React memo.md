---
aliases:
  - HOC и React memo
  - Higher-Order Component
  - React memo
---

#### Быстрый ответ

Компонент высшего порядка (Higher-Order Component, HOC) - функция, которая принимает компонент и возвращает новый компонент с дополнительным поведением или преобразованием props. HOC используют для обвязок доступа, feature flags, адаптеров библиотек и legacy-кода. Он создаёт новый тип компонента и дополнительный уровень композиции; исходный компонент не изменяется.

`React.memo` решает другую задачу: это оптимизация, которая обычно пропускает render function component при render родителя, если props не изменились. По умолчанию React сравнивает каждый prop через `Object.is`. Собственный state и используемый context по-прежнему могут обновить компонент. HOC добавляет поведение, `memo` пытается сократить повторную render work; эти инструменты не заменяют друг друга.

#### Ключевая схема

| Инструмент | Назначение | Влияние на дерево |
| --- | --- | --- |
| HOC | добавить обвязку или преобразовать props | возвращает новый component type и обычно добавляет wrapper |
| Custom Hook | переиспользовать stateful-логику | не добавляет компонент сам по себе |
| Wrapper component | явно скомпоновать UI через `children` | структура видна в JSX места использования |
| `React.memo` | пропустить часть renders при равных props | возвращает memoized component без нового UI-wrapper |
| `arePropsEqual` | заменить стандартное сравнение props | требует полного и дешёвого сравнения поведения компонента |

#### Базовая модель

HOC следует форме `withSomething(Component) -> EnhancedComponent`. Он не вызывается как обычный компонент и не изменяет переданный объект компонента. Полученный тип создают на уровне модуля, а не внутри render: повторное создание HOC во время render даст новый component type и сбросит state поддерева.

`memo(Component)` возвращает компонент, для которого React может пропустить повторный вызов при прежних props. По умолчанию сравнивается каждый prop через `Object.is`: primitives с тем же значением равны, а новый объект, массив или функция обычно отличаются по ссылке.

Мемоизация остаётся подсказкой производительности, а не гарантией и не условием корректности. Компонент обязан возвращать правильный результат и без `memo`.

#### Развернутый ответ

##### HOC и правила композиции

HOC должен передавать props, не относящиеся к его собственной обвязке, в wrapped component. Для диагностики задают `displayName`, например `withLoading(UserRow)`. Статические поля wrapped component не копируются автоматически; если библиотечный контракт на них опирается, требуется явное копирование подходящим инструментом.

В React 18 `ref` не является обычным prop. Если HOC должен передавать ref к wrapped component, контракт проектируют через `forwardRef`. Без этого ref указывает на wrapper или вообще не поддерживается.

Custom Hook обычно проще, когда нужно переиспользовать только логику внутри function component. HOC полезен, когда внешний код должен получить уже обёрнутый component type, изменить входные props или работать с API библиотеки, построенной вокруг HOCs.

##### Что именно сравнивает `React.memo`

По умолчанию `memo` сравнивает каждый предыдущий и новый prop через `Object.is`. Это часто называют поверхностным сравнением: React не проходит рекурсивно поля объектов. Новый `{ id, name }` не равен прежнему объекту, даже если его поля совпадают.

Стабильность ссылки нужна только тогда, когда она позволяет избежать измеренной дорогой работы или необходима другому контракту. Иногда лучше передать отдельные primitive props вместо большого объекта или перенести state ближе к дочернему компоненту, чем добавлять `useMemo` и `useCallback` вокруг каждого значения.

##### Custom comparator

Второй аргумент `memo` - функция `arePropsEqual(previousProps, nextProps)`. Значение `true` означает, что компонент с новыми props будет вести себя и выглядеть так же, поэтому render можно пропустить.

Comparator обязан учитывать каждый prop, включая функции. Функция может замыкать прежний state; если comparator проигнорирует её изменение, обработчик увидит устаревшие данные. Глубокое сравнение неизвестной структуры опасно по стоимости и может зависнуть после роста данных. Пользу comparator проверяют в production build через Profiler.

#### Пример

HOC добавляет состояние загрузки, а `memo` отдельно оптимизирует строку пользователя с primitive props.

```tsx
import { type ComponentType, memo } from "react";

type UserRowProps = {
  name: string;
  onSelect: () => void;
};

type LoadingProps = UserRowProps & {
  isLoading: boolean;
};

function withLoading(Component: ComponentType<UserRowProps>) {
  function WithLoading({ isLoading, ...props }: LoadingProps) {
    if (isLoading) {
      return <p role="status">Loading...</p>;
    }

    return <Component {...props} />;
  }

  WithLoading.displayName = `withLoading(${Component.displayName ?? Component.name})`;
  return WithLoading;
}

const UserRow = memo(function UserRow({ name, onSelect }: UserRowProps) {
  return <button onClick={onSelect}>{name}</button>;
});

export const UserRowWithLoading = withLoading(UserRow);
```

`withLoading` отвечает только за fallback и передаёт остальные props строке. `memo` может пропустить `UserRow`, если `name` и `onSelect` сохранились по `Object.is`. Если родитель создаёт новую `onSelect` на каждом render, пропуск обычно не сработает; это исправляют только при подтверждённой стоимости.

#### Где применяется во frontend

| Ситуация | Инструмент | Почему |
| --- | --- | --- |
| Legacy-библиотека предоставляет `connect()` | HOC | библиотека возвращает настроенный component type |
| Route требует общей проверки доступа | HOC или wrapper | обвязка применяется к целому экрану |
| Несколько компонентов используют одну подписку | custom Hook | переиспользуется логика без дополнительного wrapper |
| Тяжёлая строка таблицы часто получает прежние props | `React.memo` после профилирования | повторную render work можно пропустить |
| Большой object prop пересоздаётся без изменения данных | изменить props API или стабилизировать значение | стандартное сравнение видит новую ссылку |

#### Ключевые уточнения

- HOC создают вне render и не мутируют переданный компонент.
- HOC добавляет поведение или преобразует props; `React.memo` только оптимизирует повторный render.
- `memo` по умолчанию сравнивает каждый prop через `Object.is`, но state и context имеют собственные причины обновления.
- Custom comparator учитывает функции и все данные, влияющие на результат, иначе UI или обработчик устареет.
- Мемоизацию добавляют после измерения, потому что сравнение props также имеет стоимость.

#### Связанные темы

- [[Конспект для подготовки/React/Мемоизация]]
- [[Конспект для подготовки/React/useCallback]]
- [[Конспект для подготовки/React/Причины рендера]]
- [[Конспект для подготовки/React/Context]]
- [[Конспект для подготовки/Patterns/Compound Components и Headless UI]]
- [[Конспект для подготовки/Principles/Composition over inheritance]]
- [[Конспект для подготовки/Performance/React performance profiling]]

#### Источники

- [React 18: memo](https://18.react.dev/reference/react/memo)
- [React legacy docs: Higher-Order Components](https://legacy.reactjs.org/docs/higher-order-components.html)
- [React 18: forwardRef](https://18.react.dev/reference/react/forwardRef)
