---
aliases:
  - Compound Components
  - Headless UI
  - compound components React
  - headless components
  - UI patterns
---

#### Ответ на 60 секунд

Compound Components - это UI-паттерн, где один компонент состоит из связанных частей: например, `Tabs.Root`, `Tabs.List`, `Tabs.Trigger`, `Tabs.Content`. Части собираются снаружи, но связаны общим состоянием через context. Headless UI - подход, где компонент даёт поведение, accessibility и state machine, но почти не навязывает внешний вид.

Во frontend эти паттерны важны для design system и сложных компонентов: tabs, accordion, dialog, select, dropdown, combobox, tooltip, table, form field. Они позволяют отделить поведение от visual layer и дать разработчику гибкость композиции.

Главная сложность - контракт. Compound/headless-компоненты должны явно описывать, какие части обязательны, как передаются state/props/ref, какие ARIA-связи сохраняются и где проходит граница ответственности.

#### Ключевая схема

| Паттерн | Что даёт | Пример |
| --- | --- | --- |
| Compound Components | связанный набор UI-частей | `Tabs.Root`, `Tabs.Trigger`, `Tabs.Content` |
| Headless UI | поведение без жёсткого внешнего вида | Radix Select/Dialog |
| Context внутри | общее состояние частей | active tab, open state |
| `asChild` / slots | заменить DOM-элемент своим компонентом | Radix + design system button |

```text
Root owns state/context
-> child parts consume context
-> caller controls composition and markup
```

#### Развернутый ответ

Compound Components помогают, когда один компонент логически состоит из нескольких частей, но пользователь библиотеки должен контролировать разметку. Tabs - хороший пример: есть общий active value, список триггеров и контентные панели. Если всё спрятать в один монолитный `<Tabs items={...} />`, кастомизация станет трудной. Если отдать части наружу, API становится гибче.

Headless UI отделяет поведение от стилей. Например, Dialog должен управлять focus trap, Escape, aria, portal и scroll lock. Но цвет, spacing, animation и tokens зависят от дизайн-системы проекта. Headless component закрывает сложное поведение, а внешний слой задаёт внешний вид.

В React compound-компоненты часто строятся через context: `Root` хранит состояние, `Trigger` меняет его, `Content` читает и решает, показываться или нет. В Vue похожая гибкость достигается через slots/scoped slots и composables.

Риск этих паттернов - неявность. Если child-компонент работает только внутри `Root`, нужно явно бросать ошибку или документировать контракт. Если custom child используется через `asChild`, он должен принимать `ref`, event handlers и accessibility props, иначе поведение сломается.

#### Где применяется во frontend

| Ситуация в проекте | Что нужно контролировать | Паттерн |
| --- | --- | --- |
| Design system Tabs должен поддерживать разную верстку | порядок и markup частей меняется от экрана | compound components |
| Dialog должен быть доступным, но выглядеть по-разному в продуктах | focus/ARIA/keyboard общие, стили разные | headless component |
| Select должен интегрироваться с формой и кастомным trigger | поведение сложное, внешний вид проектный | headless Select + adapter/Controller |
| Accordion состоит из связанных item/header/panel | части разделены, но state общий | compound components + context |
| Vue-компонент списка отдаёт родителю render item | данные внутри child, markup у parent | scoped slots |
| Radix `asChild` используется с design-system Button | нужно сохранить поведение Radix и стиль проекта | child-компонент должен forwardRef/props |

> [!faq]+ Уточнения
> - Compound Components дают гибкость сборки связанных частей.
> - Headless UI отделяет behavior/accessibility от визуального слоя.
> - Context часто связывает части compound-компонента.
> - В Vue аналогичную гибкость часто дают slots/scoped slots.
> - `asChild` требует, чтобы кастомный компонент принимал props и ref.
> - Эти паттерны нужны для сложных UI, а не для каждой маленькой кнопки.

#### Пример

Упрощённая идея compound tabs:

```tsx
const TabsContext = createContext<{
  value: string;
  setValue(value: string): void;
} | null>(null);

function TabsRoot({ value, onChange, children }: TabsRootProps) {
  return (
    <TabsContext.Provider value={{ value, setValue: onChange }}>
      {children}
    </TabsContext.Provider>
  );
}

function TabsTrigger({ value, children }: TabsTriggerProps) {
  const tabs = useContext(TabsContext);
  if (!tabs) throw new Error("TabsTrigger must be used inside TabsRoot");

  return (
    <button
      aria-selected={tabs.value === value}
      onClick={() => tabs.setValue(value)}
    >
      {children}
    </button>
  );
}
```

Пользователь собирает UI сам:

```tsx
<TabsRoot value={tab} onChange={setTab}>
  <TabsTrigger value="profile">Profile</TabsTrigger>
  <TabsTrigger value="security">Security</TabsTrigger>
</TabsRoot>
```

#### Частые ошибки

- Делать compound API для простого компонента без реальной гибкости.
- Не проверять, что child используется внутри нужного `Root`.
- Прятать accessibility props и ломать keyboard navigation.
- Использовать `asChild` с компонентом, который не прокидывает `ref` и handlers.
- Смешивать headless behavior с жёсткими стилями так, что переиспользование теряет смысл.

#### Связанные темы

- [[Конспект для подготовки/Principles/Composition over inheritance]]
- [[Конспект для подготовки/Patterns/Adapter и Facade во frontend]]
- [[Конспект для подготовки/React/Context]]
- [[Конспект для подготовки/React/Radix UI]]
- [[Конспект для подготовки/React/Portal]]
- [[Конспект для подготовки/Forms/Controller и кастомные компоненты]]
- [[Конспект для подготовки/Vue/Slots]]
- [[Конспект для подготовки/HTML/Accessibility]]

#### Источники

- [React docs: Passing JSX as children](https://react.dev/learn/passing-props-to-a-component#passing-jsx-as-children)
- [React docs: useContext](https://react.dev/reference/react/useContext)
- [Radix Primitives: Introduction](https://www.radix-ui.com/primitives/docs/overview/introduction)
- [Vue docs: Slots](https://vuejs.org/guide/components/slots.html)
