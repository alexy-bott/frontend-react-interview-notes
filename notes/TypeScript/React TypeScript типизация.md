# React TypeScript типизация

<!-- NOTE-NAV-TOP:START -->
[← Проверка данных с backend](<./Проверка данных с backend.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

TypeScript в React описывает публичные контракты компонентов и hooks: props, children, callbacks, events, state, reducer actions, context и refs. Хороший тип разрешает поддерживаемые сценарии и запрещает невозможные комбинации, а не просто устраняет ошибку компилятора.

Большинство типов выводится автоматически. Явные типы нужны на границах: у props, вынесенного обработчика события, state со значением `null`, context без настоящего значения по умолчанию, действий reducer, переиспользуемого generic-компонента и обёртки над DOM-элементом.

Материал ниже ориентирован на React 18. Для передачи `ref` в function component используется `forwardRef`; модель React 19 с `ref` как обычным prop в эту карточку намеренно не смешивается.

## Props: контракт компонента

```tsx
type UserCardProps = {
  id: string;
  name: string;
  avatarUrl?: string;
  onOpen: (id: string) => void;
};

function UserCard({ id, name, avatarUrl, onOpen }: UserCardProps) {
  return (
    <button onClick={() => onOpen(id)}>
      {avatarUrl && <img src={avatarUrl} alt="" />}
      {name}
    </button>
  );
}
```

`type` и `interface` одинаково подходят для простой формы объекта. Union-варианты естественно описываются через `type`. Возвращаемый тип JSX-компонента обычно выводится, поэтому вручную писать `JSX.Element` для каждой функции не требуется.

`React.FC<Props>` допустим, но не обязателен. Прямая аннотация параметра проще показывает, какие props принимает функция, и не требует отдельного типа компонента. Выбор фиксируют стилем проекта, а не считают один вариант универсально правильным.

## Children: вложенное содержимое

| Требование компонента | Тип |
| --- | --- |
| Любой допустимый JSX-контент | `React.ReactNode` |
| Один React element | `React.ReactElement` |
| Render function | явная функция, например `(item: T) => ReactNode` |
| Children не поддерживается | поле `children` не объявляется |

```tsx
import type { ReactNode } from "react";

type PanelProps = {
  title: string;
  children: ReactNode;
};
```

`ReactNode` включает elements, строки, числа, `null`, `undefined`, booleans, fragments и коллекции допустимых узлов. `ReactElement` уже и описывает созданный элемент.

TypeScript не всегда способен гарантировать конкретный тип JSX-child вроде «только `Option` внутри `Select`», потому что результат JSX-выражения представлен React element, а не nominal identity исходного компонента. Для строгого API надёжнее передавать типизированные данные через props.

## Взаимоисключающие props

Если компонент работает в нескольких режимах, набор необязательных полей разрешает неверные комбинации. Discriminated union, или размеченное объединение, задаёт их явно:

```tsx
type ActionProps =
  | {
      kind: "button";
      onClick: () => void;
      href?: never;
    }
  | {
      kind: "link";
      href: string;
      onClick?: never;
    };

function Action(props: ActionProps) {
  if (props.kind === "link") {
    return <a href={props.href}>Открыть</a>;
  }

  return <button onClick={props.onClick}>Выполнить</button>;
}
```

Проверка `kind` сужает props. `never` у чужого поля запрещает передать его в другом режиме.

## Обёртка над нативным элементом

Не стоит вручную переписывать `disabled`, `type`, `aria-*`, `onClick` и остальные HTML props. React types уже описывают их:

```tsx
import type {
  ComponentPropsWithoutRef,
  ReactNode,
} from "react";

type ButtonProps = Omit<
  ComponentPropsWithoutRef<"button">,
  "children"
> & {
  variant: "primary" | "secondary";
  children: ReactNode;
};

function Button({ variant, children, ...buttonProps }: ButtonProps) {
  return (
    <button {...buttonProps} data-variant={variant}>
      {children}
    </button>
  );
}
```

`ComponentPropsWithoutRef<"button">` берёт props нативной кнопки без `ref`. При конфликте собственного prop с нативным ключ сначала исключают через `Omit`, затем задают свою семантику.

Для polymorphic `as`-компонентов типы быстро усложняются. Такой API оправдан в design system, но для обычного приложения отдельные `Button` и `Link` часто понятнее одной универсальной abstraction.

## События React

Inline handler получает тип из контекста:

```tsx
<input onChange={event => console.log(event.currentTarget.value)} />
```

После выноса функции тип события задают явно:

```tsx
import type { ChangeEvent } from "react";

function handleChange(event: ChangeEvent<HTMLInputElement>) {
  console.log(event.currentTarget.value);
}
```

Частые типы: `ChangeEvent<HTMLInputElement>`, `FormEvent<HTMLFormElement>`, `MouseEvent<HTMLButtonElement>`, либо готовые `ChangeEventHandler<HTMLInputElement>`.

`currentTarget` — элемент, на котором зарегистрирован handler, поэтому generic React event относится к нему. `target` — исходный источник события и может быть вложенным элементом; его тип менее специфичен.

## `useState` и модель состояния

Простой state выводится:

```tsx
const [enabled, setEnabled] = useState(false);
// boolean
```

Если initial value не выражает весь контракт, generic задают явно:

```tsx
type User = { id: string; name: string };

const [user, setUser] = useState<User | null>(null);
```

Для нескольких взаимоисключающих состояний лучше union:

```tsx
type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };

const [state, setState] = useState<RequestState<User>>({
  status: "idle",
});
```

Так `data` нельзя прочитать до проверки `status`, а невозможные сочетания статуса и полей не создаются.

## `useReducer`

```tsx
type State = { count: number };

type Action =
  | { type: "increment" }
  | { type: "set"; value: number };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "increment":
      return { count: state.count + 1 };
    case "set":
      return { count: action.value };
  }
}

const [state, dispatch] = useReducer(reducer, { count: 0 });
```

Типизированный reducer связывает допустимые actions с их данными. Добавление нового варианта можно усилить исчерпывающей проверкой (exhaustive check) через `never`.

## Context без фиктивного значения по умолчанию

Если настоящего default нет, не нужно создавать фиктивный объект через assertion:

```tsx
import { createContext, useContext } from "react";

type AuthContextValue = {
  userId: string;
  logout(): void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);

  if (value === null) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return value;
}
```

Проверка в custom hook превращает отсутствие Provider в раннюю понятную ошибку, а consumers получают `AuthContextValue` без повторных `null`-проверок.

## Refs в React 18

DOM ref обычно nullable до commit и после unmount:

```tsx
const inputRef = useRef<HTMLInputElement>(null);

function focusInput() {
  inputRef.current?.focus();
}

return <input ref={inputRef} />;
```

Для передачи ref через function component в React 18 используется `forwardRef`:

```tsx
import { forwardRef } from "react";
import type { ComponentPropsWithoutRef } from "react";

type InputProps = ComponentPropsWithoutRef<"input"> & {
  label: string;
};

const LabeledInput = forwardRef<HTMLInputElement, InputProps>(
  function LabeledInput({ label, ...inputProps }, ref) {
    return (
      <label>
        {label}
        <input ref={ref} {...inputProps} />
      </label>
    );
  }
);
```

В type arguments `forwardRef` сначала идёт тип ref, затем props; в функции параметры расположены как `props, ref`.

## Generic-компоненты

```tsx
import type { ReactNode } from "react";

type ListProps<T> = {
  items: readonly T[];
  getKey: (item: T) => string;
  renderItem: (item: T) => ReactNode;
};

function List<T>({ items, getKey, renderItem }: ListProps<T>) {
  return (
    <ul>
      {items.map(item => (
        <li key={getKey(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}
```

`T` связывает элементы с `getKey` и `renderItem`. Для arrow function в `.tsx` иногда пишут `<T,>`: запятая помогает parser отличить generic от JSX-tag.

## Границы типизации React

TypeScript проверяет использование компонента в исходном коде, но не валидирует API response, URL, storage и сообщения между окнами. Эти данные проверяют до передачи в props или state.

Тип также не гарантирует правильную accessibility, порядок Effects, отсутствие лишних renders или корректную бизнес-логику. Для этого нужны архитектура, tests и runtime-инструменты.

## Ключевые уточнения

- Материал использует модель React 18; `forwardRef` здесь является актуальным способом передать ref через function component.
- Props описывают публичный контракт; `type`, `interface` и `React.FC` являются средствами записи, а не целью типизации.
- `ReactNode` шире `ReactElement`, а `children` не следует добавлять компоненту автоматически.
- Нативные props лучше получать через `ComponentPropsWithoutRef`/`ComponentPropsWithRef`, чем переписывать вручную.
- `currentTarget` типизирован как элемент handler, `target` может быть вложенным источником события.
- Nullable state и ref должны отражать реальные фазы жизненного цикла, а не скрываться через `!`.
- Generic API клиента и props не заменяют runtime validation внешних данных.

## Связанные темы

- [type vs interface](<./type vs interface.md>)
- [Unions intersections discriminated unions](<./Unions intersections discriminated unions.md>)
- [Generics](<./Generics.md>)
- [Variance и совместимость функций](<./Variance и совместимость функций.md>)
- [Проверка данных с backend](<./Проверка данных с backend.md>)
- [Хуки](<../React/Хуки.md>)
- [Controlled и uncontrolled компоненты](<../React/Controlled и uncontrolled компоненты.md>)

## Источники

- [React 18 documentation](https://18.react.dev/)
- [React 18: forwardRef](https://18.react.dev/reference/react/forwardRef)
- [React: Using TypeScript](https://react.dev/learn/typescript)
- [TypeScript Handbook: JSX](https://www.typescriptlang.org/docs/handbook/jsx.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Проверка данных с backend](<./Проверка данных с backend.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-BOTTOM:END -->
