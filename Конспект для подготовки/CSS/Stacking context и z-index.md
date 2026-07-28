---
aliases:
  - stacking context
  - z-index
  - контекст наложения
---

#### Ответ на 60 секунд

Stacking context - это локальный контекст наложения элементов по оси z. `z-index` работает не глобально по всей странице, а внутри своего stacking context. Поэтому элемент с огромным `z-index` может все равно оказаться под другим элементом, если его родитель находится в более низком контексте.

Stacking context создают не только `position` плюс `z-index`, но и `transform`, `opacity < 1`, `filter`, `isolation: isolate`, `position: fixed/sticky`, некоторые значения `contain` и другие свойства. Проблемы с overlay, dropdown и modal часто решаются не увеличением `z-index`, а анализом родительских контекстов.

#### Ключевая схема

| Создает stacking context | Пример |
| --- | --- |
| positioned + `z-index` не `auto` | `position: relative; z-index: 1` |
| `opacity < 1` | `opacity: 0.99` |
| `transform` | `transform: translateZ(0)` |
| `filter`, `perspective` | visual effects |
| `isolation: isolate` | явная изоляция |
| `position: fixed/sticky` | отдельные случаи |

#### Развернутый ответ

`z-index` сравнивается внутри stacking context, а не по всей странице. Если родительский stacking context находится ниже соседнего контекста, дочерний элемент с `z-index: 9999` не сможет выйти поверх него одним увеличением числа.

Stacking context создаётся разными свойствами: positioned element с `z-index` не `auto`, `opacity < 1`, `transform`, `filter`, `perspective`, `isolation: isolate`, `position: fixed/sticky`, некоторые значения `contain` и другие свойства. Поэтому проблема overlay часто находится не на самом overlay, а на его предках.

`z-index` работает для positioned elements (`relative`, `absolute`, `fixed`, `sticky`) и flex/grid items в некоторых случаях. Если элемент находится в обычном потоке без нужного контекста, `z-index` может не дать ожидаемого эффекта.

Для modal/dropdown проверяют родителей на `transform`, `opacity`, `overflow`, `position`, `z-index` и `contain`. В React overlays часто выносят через Portal ближе к `body`, чтобы не зависеть от локальных stacking/overflow ограничений.

> [!faq]+ Уточнения
> - `z-index` не глобален, он работает внутри stacking context.
> - `transform` и `opacity < 1` могут создать новый stacking context.
> - `overflow: hidden` может обрезать dropdown даже при большом `z-index`.
> - Portal помогает вынести overlay из локальных ограничений.
> - Stacking context отличается от block formatting context.

#### Пример

```css
.page {
  transform: translateZ(0);
}

.modal {
  position: fixed;
  z-index: 1000;
}
```

Если `.page` создал stacking context, modal внутри него может проиграть элементу из другого контекста.

#### Частые ошибки

- Увеличивать `z-index` бесконечно вместо анализа контекстов.
- Не замечать, что `transform` на родителе создал новый stacking context.
- Путать stacking context и block formatting context.
- Забывать про `overflow: hidden`, который может обрезать dropdown.
- Не использовать portal для overlays в React.

#### Связанные темы

- [[Конспект для подготовки/CSS/Позиционирование]]
- [[Конспект для подготовки/React/Portal]]
- [[Конспект для подготовки/CSS/Анимации transform vs position]]
- [[Конспект для подготовки/CSS/Box Model]]

#### Источники

- [MDN: Stacking context](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_positioned_layout/Stacking_context)
- [MDN: z-index](https://developer.mozilla.org/en-US/docs/Web/CSS/z-index)
- [MDN: transform](https://developer.mozilla.org/en-US/docs/Web/CSS/transform)
