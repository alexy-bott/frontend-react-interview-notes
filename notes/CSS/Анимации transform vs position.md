# Анимации transform vs position

<!-- NOTE-NAV-TOP:START -->
[← Stacking context и z-index](<./Stacking context и z-index.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Для движения и появления элементов обычно анимируют `transform` и `opacity`: их изменение не требует пересчитывать layout, а браузер нередко может выполнить его на стадии compositing. Анимация `top`, `left`, `width`, `height` или margin меняет геометрию и может запустить layout и paint для затронутой части страницы.

Compositor-анимация не гарантируется и не является бесплатной. Большой rasterized layer, сложный paint, слишком много layers или постоянный `will-change` расходуют память и время. Правильный выбор проверяют в Performance/Rendering tools на целевом устройстве.

## Ключевая схема

| Что менять | Обычно дешевле |
| --- | --- |
| Позицию | `transform: translate(...)` |
| Размер визуально | `transform: scale(...)` |
| Прозрачность | `opacity` |
| Геометрию документа | `top`, `left`, `width`, `height` дороже |

## Базовая модель

Упрощённый путь обновления кадра:

```text
style -> layout -> paint -> composite
                  paint -> composite
                           composite
```

Изменение геометрии может потребовать все последующие стадии. Изменение цвета обычно требует paint и composite. `transform` и `opacity` могут ограничиться composite, если браузер подготовил подходящий слой. Реальный pipeline определяется движком и содержимым, поэтому это модель стоимости, а не абсолютная гарантия.

## Развернутый ответ

`top`, `left`, `width`, `height` и margin меняют геометрию layout. Браузеру может понадобиться пересчитать расположение элементов, перерисовать область и затем скомпоновать кадр. На сложной странице это легко выходит за бюджет плавного кадра.

`transform` меняет визуальное представление box после расчёта layout. Соседи продолжают занимать места так, будто transform не изменил исходную геометрию. Поэтому translate подходит для overlay, drag preview и визуального движения, но не для анимации, где соседние элементы должны плавно перераспределять место.

`will-change` сообщает о вероятном будущем изменении и позволяет браузеру заранее подготовить оптимизацию. Это последняя мера после обнаруженной задержки: свойство включают незадолго до анимации на ограниченном числе элементов и убирают после неё. Само наличие `will-change` не доказывает, что элемент получит отдельный compositor layer.

Layout рассчитывает геометрию box. Paint записывает команды отрисовки пикселей для областей. Composite собирает подготовленные слои в кадр. Термин reflow часто используют как синоним повторного layout, но в спецификациях и DevTools обычно встречается `layout`.

`prefers-reduced-motion: reduce` сигнализирует, что пользователь предпочитает меньше необязательного движения. Интерфейс должен сохранить состояние и обратную связь, но заменить интенсивное перемещение на короткое затухание или убрать декоративную анимацию.

## Пример

```css
.moves-layout-box {
  position: relative;
  left: 100px;
}

.moves-visually {
  transform: translateX(100px);
}

.fade {
  opacity: 0;
  transition: opacity 200ms ease, transform 200ms ease;
}

@media (prefers-reduced-motion: reduce) {
  .fade {
    transition-duration: 0.01ms;
  }
}
```

Оба первых правила визуально смещают элемент, но только изменение `left` участвует в positioned layout. `transform` сохраняет исходное место box для соседей. Media query не скрывает результат действия, а почти убирает движение.

## Ключевые уточнения

- `transform` меняет визуальную геометрию, но не перераспределяет место между соседями.
- `transform` и `opacity` не запускают layout, однако paint/compositor cost и создание layer зависят от браузера и содержимого.
- `will-change` применяют временно и после измерения, а не как глобальную оптимизацию.
- Анимация должна сохранять понятный конечный результат при `prefers-reduced-motion`.
- Плавность оценивают по реальному frame timeline, long tasks, paint area и памяти, а не только по названию CSS-свойства.

## Связанные темы

- [Critical Render Path](<../../Конспект для подготовки/Web Basics/Critical Render Path.md>)
- [Core Web Vitals](<../../Конспект для подготовки/Web Basics/Core Web Vitals.md>)
- [requestAnimationFrame и requestIdleCallback](<../JavaScript/requestAnimationFrame и requestIdleCallback.md>)
- [Stacking context и z-index](<./Stacking context и z-index.md>)

## Источники

- [MDN: transform](https://developer.mozilla.org/en-US/docs/Web/CSS/transform)
- [MDN: will-change](https://developer.mozilla.org/en-US/docs/Web/CSS/will-change)
- [MDN: prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- [web.dev: Animations guide](https://web.dev/learn/css/animations)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Stacking context и z-index](<./Stacking context и z-index.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- NOTE-NAV-BOTTOM:END -->
