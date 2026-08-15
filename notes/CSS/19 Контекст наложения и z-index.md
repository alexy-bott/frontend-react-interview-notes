# Контекст наложения и z-index

<!-- NOTE-NAV-TOP:START -->
[← Позиционирование](<./18 Позиционирование.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Анимации — transform или position →](<./20 Анимации — transform или position.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Stacking context, или контекст наложения, - это локальная группа элементов, которая участвует в порядке отрисовки как единое целое. Значения `z-index` сравниваются внутри соответствующего контекста, поэтому потомок с `z-index: 9999` не может обойти соседний stacking context, если весь его родительский контекст расположен ниже.

Stacking context создают не только positioned element с `z-index`, но и `fixed`/`sticky`, flex/grid item с `z-index`, `opacity < 1`, `transform`, `filter`, `isolation: isolate`, некоторые виды `contain` и другие свойства. Отдельно `overflow` может обрезать overlay, хотя сам по себе не обязан создавать stacking context.

## Ключевая схема

| Создает stacking context | Пример |
| --- | --- |
| positioned + `z-index` не `auto` | `position: relative; z-index: 1` |
| `opacity < 1` | `opacity: 0.99` |
| `transform` | `transform: translateZ(0)` |
| `filter`, `perspective` | visual effects |
| `isolation: isolate` | явная изоляция |
| `position: fixed/sticky` | отдельные случаи |

## Базовая модель

Сначала браузер определяет дерево stacking contexts. Затем содержимое каждого контекста рисуется в установленном порядке, после чего весь контекст рассматривается родителем как атомарный элемент. Число `z-index` ребёнка не сравнивается напрямую с числами в соседнем родительском контексте.

Clipping - отдельная граница. Если предок обрезает содержимое через `overflow`, `clip-path` или `contain: paint`, увеличение `z-index` не позволяет нарисовать потомка за этой границей.

## Развернутый ответ

`z-index` сравнивается внутри stacking context, а не по всей странице. Если родительский stacking context находится ниже соседнего контекста, дочерний элемент с `z-index: 9999` не сможет выйти поверх него одним увеличением числа.

Stacking context создаётся разными свойствами: positioned element с `z-index` не `auto`, `opacity < 1`, `transform`, `filter`, `perspective`, `isolation: isolate`, `position: fixed/sticky`, некоторые значения `contain` и другие свойства. Поэтому проблема overlay часто находится не на самом overlay, а на его предках.

`z-index` применим к positioned elements, а также к flex и grid items без обязательного `position`. Он задаёт stack level элемента в текущем контексте и в некоторых случаях одновременно создаёт новый stacking context. Финальный paint order учитывает не только число, но и категории вроде отрицательного, `auto`/нулевого и положительного stack level.

Для modal и dropdown проверяют предков на `transform`, `opacity`, `overflow`, `position`, `z-index`, `contain` и `isolation`. React Portal может перенести DOM-узел ближе к `body` и вывести его из локального clipping/stacking context. Но Portal сам не гарантирует верхний слой: нативные `<dialog>` и Popover API могут помещать элементы в browser top layer, который расположен поверх обычных stacking contexts.

## Пример

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

## Диагностика

В DevTools нужно подняться от проблемного элемента по DOM и найти ближайшие stacking contexts и clipping ancestors. Если элемент находится ниже, исправляют уровень нужного родительского контекста или переносят overlay в подходящий контейнер. Если он обрезан, проверяют `overflow`, `clip-path`, `contain: paint` и геометрию; увеличение `z-index` эту проблему не решит.

## Ключевые уточнения

- Stacking context атомарен относительно родителя; `z-index` потомка не становится глобальным.
- `overflow` и stacking context - разные механизмы: первый может обрезать, второй определяет paint order.
- `transform` и `opacity < 1` способны создать неожиданный локальный контекст.
- Portal меняет место DOM-узла, но не отменяет stacking contexts вокруг нового контейнера.
- Browser top layer находится над обычными stacking contexts и используется, например, открытым modal `<dialog>`.
- Block formatting context управляет layout, а stacking context - порядком отрисовки.

## Связанные темы

- [Позиционирование](<./18 Позиционирование.md>)
- [Порталы](<../React/22 Порталы.md>)
- [Анимации — transform или position](<./20 Анимации — transform или position.md>)
- [Блочная модель (Box Model)](<./04 Блочная модель (Box Model).md>)

## Источники

- [MDN: Stacking context](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_positioned_layout/Stacking_context)
- [MDN: z-index](https://developer.mozilla.org/en-US/docs/Web/CSS/z-index)
- [MDN: transform](https://developer.mozilla.org/en-US/docs/Web/CSS/transform)
- [MDN: Top layer](https://developer.mozilla.org/en-US/docs/Glossary/Top_layer)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Позиционирование](<./18 Позиционирование.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Анимации — transform или position →](<./20 Анимации — transform или position.md>)
<!-- NOTE-NAV-BOTTOM:END -->
