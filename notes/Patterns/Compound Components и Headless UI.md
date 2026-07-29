# Compound Components и Headless UI

<!-- NOTE-NAV-TOP:START -->
[← Factory Singleton и lifecycle](<./Factory Singleton и lifecycle.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Compound Components («составные компоненты») - способ спроектировать API сложного UI как набор согласованных частей, например `Tabs.Root`, `Tabs.List`, `Tabs.Trigger` и `Tabs.Content`. Вызывающий код управляет композицией частей, а общий owner связывает их состоянием и контрактом.

Headless-компонент предоставляет состояние и поведение, включая keyboard navigation и accessibility, но не навязывает готовый визуальный стиль. Эти идеи независимы и часто используются вместе: библиотека может дать headless Tabs через compound API, а приложение добавит собственные CSS-классы и design tokens.

## Ключевая схема

| Вопрос | Compound Components | Headless UI |
| --- | --- | --- |
| Что отделяется | монолитный компонент на связанные части | поведение от визуального оформления |
| Что контролирует consumer | состав и расположение частей | стили, tokens и часто разметку в разрешённых границах |
| Что остаётся у реализации | связи частей и общий state | state machine, события, focus и ARIA-контракт |
| Можно ли использовать отдельно | да | да |

```text
Root владеет state/context
-> parts получают общий contract
-> primitive обеспечивает поведение
-> design system добавляет внешний вид
```

## Базовая модель

Монолитный API вида `<Tabs items={items} />` прост, пока структура всех tabs одинакова. Когда экрану нужно добавить badge в trigger, расположить панели по-другому или вставить дополнительные элементы, число специальных props начинает расти. Compound API отдаёт композицию consumer, сохраняя связь частей через `Root`.

Headless-подход решает другую задачу. Поведение `Dialog`, `Select` или `Tabs` сложнее их внешнего вида: нужно управлять focus, клавиатурой, ролями, состояниями и связями между элементами. Реализация предоставляет этот контракт, а проект задаёт цвет, размеры, spacing и анимацию.

Для простого `Button`, у которого мало частей и стабильная разметка, compound API обычно не нужен. Headless primitive особенно полезен для интерактивных виджетов с нетривиальным accessibility-контрактом, но его ограничения нужно принять: полностью произвольная разметка может нарушить поведение.

## Развернутый ответ

**Связь частей.** `Root` может хранить state внутри или получать `value/onValueChange` для controlled-режима. Context передаёт состояние, id и callbacks вложенным частям без ручного прокидывания props через каждый уровень. Часть, используемая вне своего `Root`, должна выдавать понятную ошибку.

**Контракт Tabs.** Вкладки - не только `aria-selected`. Trigger имеет роль tab и связан с panel, активный tab участвует в tab order, а стрелки перемещают focus в соответствии с выбранной моделью активации. Самодельный сокращённый пример легко пропускает эти правила, поэтому для production разумно использовать проверенный primitive и стилизовать его.

**Controlled и uncontrolled.** Uncontrolled primitive сам хранит выбранное значение и удобен для локального сценария. Controlled-вариант получает значение от consumer и нужен, когда state синхронизируется с URL, формой или другой частью приложения. Поддержка обоих режимов увеличивает API, поэтому она должна соответствовать реальным сценариям design system.

**Композиция DOM.** API наподобие Radix `asChild` позволяет primitive передать поведение пользовательскому элементу вместо создания собственного DOM-узла. В React 18 такой компонент должен передать полученные props и `ref` реальному DOM-элементу; иначе потеряются обработчики, ARIA-атрибуты или управление focus.

**Граница ответственности.** Headless primitive не гарантирует доступность итоговой композиции независимо от consumer. Приложение всё ещё обязано добавить видимый focus, читаемый label, достаточный контраст и корректно использовать части. Свобода переставлять элементы ограничена структурным контрактом виджета.

## Где применяется во frontend

| Компонент | Что связывают compound parts | Что обычно закрывает headless-слой |
| --- | --- | --- |
| Tabs | list, triggers и panels | выбор, focus, keyboard navigation, ARIA-связи |
| Dialog | trigger, overlay, content, title | portal, focus, Escape, возврат focus |
| Select/Combobox | trigger, input, list и options | навигация, selection, focus и роли |
| Accordion | items, headers и panels | open state и keyboard interaction |
| Form field | label, control, description и error | id-связи и состояние invalid |

В Vue похожую управляемую композицию дают slots и scoped slots, а переиспользуемое поведение можно вынести в composable. Это не точная копия React Context API, но решается та же задача разделения поведения и представления.

## Пример

Radix Tabs уже реализует compound API и headless-поведение; проект добавляет только структуру и стили:

```tsx
import * as Tabs from "@radix-ui/react-tabs";

function AccountTabs() {
  return (
    <Tabs.Root defaultValue="profile" className="tabs">
      <Tabs.List aria-label="Настройки аккаунта" className="tabsList">
        <Tabs.Trigger value="profile" className="tabsTrigger">
          Профиль
        </Tabs.Trigger>
        <Tabs.Trigger value="security" className="tabsTrigger">
          Безопасность
        </Tabs.Trigger>
      </Tabs.List>

      <Tabs.Content value="profile">Настройки профиля</Tabs.Content>
      <Tabs.Content value="security">Настройки безопасности</Tabs.Content>
    </Tabs.Root>
  );
}
```

Части можно расположить и оформить в рамках API primitive, а общее значение и keyboard interaction остаются согласованными. Для синхронизации с URL вместо `defaultValue` используют controlled props `value` и `onValueChange`.

## Ключевые уточнения

- Compound Components описывают форму API, а headless-подход - разделение поведения и визуального слоя. Один компонент может использовать оба решения.
- Context является частой реализацией связи частей, но не определением паттерна; связь можно построить и другими способами.
- Headless не означает «без DOM» или «автоматически доступно при любой композиции». Consumer обязан соблюдать контракт primitive и добавить доступные стили.
- `asChild` и slot composition требуют корректно передавать props, handlers и `ref`; иначе внешний вид сохранится, а поведение сломается.
- Гибкий API имеет цену в виде дополнительных частей и правил. Для простого компонента явные props могут быть понятнее.

## Связанные темы

- [Composition over inheritance](<../Principles/Composition over inheritance.md>)
- [Adapter и Facade во frontend](<./Adapter и Facade во frontend.md>)
- [Context](<../React/Context.md>)
- [Radix UI](<../React/Radix UI.md>)
- [Portal](<../React/Portal.md>)
- [Controller и кастомные компоненты](<../Forms/Controller и кастомные компоненты.md>)
- [Slots](<../Vue/Slots.md>)
- [Accessibility](<../HTML/Accessibility.md>)

## Источники

- [React: Passing data deeply with context](https://react.dev/learn/passing-data-deeply-with-context)
- [Radix Primitives: Introduction](https://www.radix-ui.com/primitives/docs/overview/introduction)
- [Radix Primitives: Tabs](https://www.radix-ui.com/primitives/docs/components/tabs)
- [WAI-ARIA APG: Tabs Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)
- [Vue: Slots](https://vuejs.org/guide/components/slots.html)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Factory Singleton и lifecycle](<./Factory Singleton и lifecycle.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-BOTTOM:END -->
