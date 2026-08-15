# Radix UI

<!-- NOTE-NAV-TOP:START -->
[← React Router](<./30 React Router.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [React 18 и 19 →](<./32 React 18 и 19.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Radix UI Primitives - низкоуровневые React-компоненты для сложных интерфейсных паттернов: Dialog, Select, Dropdown Menu, Tabs, Tooltip и других. Они дают поведение и основу доступности: ARIA roles/attributes, управление фокусом (focus management) и управление с клавиатуры. Готовый визуальный стиль почти отсутствует, поэтому Primitives используют как основу собственной дизайн-системы.

Radix Themes - другой продукт: готовая стилизованная библиотека поверх дизайн-токенов. Поэтому сначала уточняют, идёт ли речь о Primitives или Themes.

Radix снимает сложность механики, но не гарантирует доступность итогового экрана автоматически. Проект всё равно задаёт понятные labels, title/description, сообщения об ошибках, contrast, focus styles и проверяет компонент клавиатурой и accessibility-тестами.

## Ключевая схема

| Radix Primitives предоставляет | Проект определяет |
| --- | --- |
| keyboard interactions по паттерну | текст и доступное имя control |
| focus management для overlay | визуальный focus indicator |
| ARIA roles и state attributes | error/help messages и связь с полем |
| controlled/uncontrolled API | владелец state и бизнес-правила |
| Portal и positioning primitives | stacking, размеры, animation и responsive styles |
| `asChild` для composition | корректный DOM-элемент, props и ref |

## Развернутый ответ

**Почему не всегда достаточно самописного компонента**

Внешне Dialog или Select выглядят просто, но должны поддерживать много сценариев. Modal Dialog переводит фокус внутрь, удерживает tab navigation в окне, закрывается по `Escape`, возвращает фокус на trigger и делает фон недоступным для interaction. Select обрабатывает стрелки, `Enter`, `Space`, typeahead search, disabled options и возврат фокуса.

Radix реализует поведение по WAI-ARIA patterns там, где это возможно. Это уменьшает риск, но команда по-прежнему должна выбрать правильный primitive: Tooltip не заменяет Dialog, Dropdown Menu не является обычным Select для формы.

**Controlled и uncontrolled режимы**

Uncontrolled-компонент хранит state внутри Radix:

```tsx
<Dialog.Root defaultOpen={false}>...</Dialog.Root>
```

Controlled-компонент получает значение и callback от приложения:

```tsx
<Dialog.Root open={isOpen} onOpenChange={setIsOpen}>...</Dialog.Root>
```

Controlled mode нужен, если открытие зависит от URL, form state, analytics или внешней команды. Одновременно управлять одним значением через `defaultOpen` и `open` не следует: нужно выбрать одного владельца state.

**Compound Components**

Primitive состоит из частей: `Dialog.Root`, `Dialog.Trigger`, `Dialog.Portal`, `Dialog.Content`, `Dialog.Title`. Это pattern Compound Components: части совместно используют внутренний context, а проект контролирует DOM-структуру и стили.

Часть нельзя бездумно удалить. Например, у Dialog должен быть Title. Если visual title не нужен, его скрывают через `VisuallyHidden`, сохраняя доступное имя.

**Portal**

`Portal` переносит overlay ближе к `document.body`, чтобы выйти из `overflow: hidden` и локального stacking context. Он не отменяет CSS: нужно настроить `z-index`, размеры, scroll для длинного content и safe area на мобильном экране.

React events и Context продолжают идти по React tree, а не по физическому DOM-положению Portal. Это важно для обработчиков клика и providers.

**`asChild`**

При `asChild` Radix не создаёт стандартный DOM-элемент, а клонирует единственного child и передаёт ему props, handlers и ref. В React 18 leaf component должен:

- spread переданные props на реальный DOM-узел;
- передать ref через `forwardRef`;
- сохранить подходящую семантику и keyboard behavior.

Замена button на `div` ломает доступность, даже если визуально всё осталось прежним. Пользовательский handler также не должен случайно отменить Radix behavior через `preventDefault`.

**Стилизация**

Radix добавляет атрибуты вроде `data-state="open"`, `data-disabled` и CSS custom properties для позиционирования. По ним удобно стилизовать состояния и animation. Состояние открытия не нужно дублировать отдельным class вручную.

Если primitives устанавливаются отдельными `@radix-ui/react-*` packages, их обновляют согласованно. Современная документация также рекомендует tree-shakeable package `radix-ui`, который уменьшает риск несовместимых shared dependencies.

**Интеграция с React Hook Form**

Radix Select, Checkbox и Radio Group не обязаны выдавать нативный `event.target.value`. `Controller` адаптирует `value` и `onValueChange`. Дополнительно передают `name`, `ref`, `onBlur` и связывают trigger с label и error message.

## Пример: Radix Select и React Hook Form

```tsx
import { Controller, useForm } from "react-hook-form";
import { Select } from "radix-ui";

type FormValues = {
  status: "draft" | "published";
};

export function ArticleStatusForm() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: { status: "draft" },
  });

  return (
    <form onSubmit={handleSubmit((values) => console.log(values))}>
      <label id="status-label">Статус статьи</label>

      <Controller
        name="status"
        control={control}
        rules={{ required: "Выберите статус" }}
        render={({ field }) => (
          <Select.Root
            name={field.name}
            value={field.value}
            onValueChange={field.onChange}
          >
            <Select.Trigger
              ref={field.ref}
              onBlur={field.onBlur}
              aria-labelledby="status-label"
              aria-invalid={Boolean(errors.status)}
              aria-describedby={errors.status ? "status-error" : undefined}
            >
              <Select.Value />
            </Select.Trigger>

            <Select.Portal>
              <Select.Content position="popper">
                <Select.Viewport>
                  <Select.Item value="draft">
                    <Select.ItemText>Черновик</Select.ItemText>
                  </Select.Item>
                  <Select.Item value="published">
                    <Select.ItemText>Опубликована</Select.ItemText>
                  </Select.Item>
                </Select.Viewport>
              </Select.Content>
            </Select.Portal>
          </Select.Root>
        )}
      />

      {errors.status && (
        <p id="status-error" role="alert">
          {errors.status.message}
        </p>
      )}

      <button type="submit">Сохранить</button>
    </form>
  );
}
```

Визуальные class names здесь опущены, чтобы пример показывал contract. В production trigger, content, active item, disabled state и focus-visible получают стили дизайн-системы.

## Ключевые уточнения

- Radix Primitives даёт поведение без готового дизайна; Radix Themes даёт стилизованный слой.
- Готовые ARIA-механизмы не заменяют accessible name, error text и ручную проверку сценария.
- Controlled state имеет одного внешнего владельца; uncontrolled state инициализируется через `defaultValue/defaultOpen`.
- Portal меняет DOM-положение overlay, но сохраняет React Context и event propagation.
- `asChild` требует одного доступного child, который принимает props и ref.
- Compound parts формируют contract primitive; обязательный Title/Label не удаляют ради внешнего вида.
- Form adapter передаёт value, change, blur, name/ref и accessibility-связи.
- Отдельные Radix packages обновляют совместно, чтобы не дублировать shared dependencies.

## Связанные темы

- [Доступность HTML](<../HTML/03 Доступность HTML.md>)
- [Доступность диалогов, выпадающих элементов и оверлеев](<../Доступность/03 Доступность диалогов, выпадающих элементов и оверлеев.md>)
- [Клавиатурная навигация и управление фокусом](<../Доступность/02 Клавиатурная навигация и управление фокусом.md>)
- [Порталы](<./22 Порталы.md>)
- [Compound Components и Headless UI](<../Паттерны/05 Compound Components и Headless UI.md>)
- [Управляемые и неуправляемые компоненты](<./18 Управляемые и неуправляемые компоненты.md>)
- [Controller и пользовательские компоненты](<../Формы/04 Controller и пользовательские компоненты.md>)
- [React Hook Form](<../Формы/03 React Hook Form.md>)
- [React Testing Library](<../Тестирование/04 React Testing Library.md>)

## Источники

- [Radix Primitives: Introduction](https://www.radix-ui.com/primitives/docs/overview/introduction)
- [Radix Primitives: Composition](https://www.radix-ui.com/primitives/docs/guides/composition)
- [Radix Primitives: Select](https://www.radix-ui.com/primitives/docs/components/select)
- [Radix Primitives: Dialog](https://www.radix-ui.com/primitives/docs/components/dialog)
- [Radix Themes: Getting started](https://www.radix-ui.com/themes/docs/overview/getting-started)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← React Router](<./30 React Router.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [React 18 и 19 →](<./32 React 18 и 19.md>)
<!-- NOTE-NAV-BOTTOM:END -->
