---
aliases:
  - transform vs position
  - CSS animations performance
  - transform
  - repaint reflow
---

#### Ответ на 60 секунд

Для анимаций в CSS обычно используют `transform` и `opacity`, а не `top`, `left`, `width`, `height` или margin. Причина в том, что изменение layout-свойств может запускать пересчет layout и repaint, а `transform` и `opacity` часто обрабатываются на compositor layer и не требуют пересчета геометрии всей страницы.

Это не значит, что `transform` всегда бесплатный. Слишком много слоев, тяжелые фильтры, большие изображения и постоянный `will-change` тоже могут ухудшить производительность. Но для движения, масштабирования и плавного появления `transform` - стандартный выбор.

#### Ключевая схема

| Что менять | Обычно дешевле |
| --- | --- |
| Позицию | `transform: translate(...)` |
| Размер визуально | `transform: scale(...)` |
| Прозрачность | `opacity` |
| Геометрию документа | `top`, `left`, `width`, `height` дороже |

#### Развернутый ответ

`top`, `left`, `width`, `height` и margin меняют геометрию layout. Браузеру может понадобиться пересчитать расположение элементов, перерисовать область и затем скомпоновать кадр. На сложной странице это легко выходит за бюджет плавного кадра.

`transform` и `opacity` часто можно обработать на compositor layer без пересчёта layout. Поэтому движение, scale и fade обычно делают через `transform`/`opacity`. Это не означает, что они бесплатны: большие слои, фильтры, тяжёлые изображения и большое количество animated layers всё равно нагружают браузер.

`will-change` подсказывает браузеру, что свойство скоро будет меняться. Он может помочь заранее подготовить слой, но постоянный `will-change` на множестве элементов расходует память и может ухудшить производительность. Его используют точечно и снимают, когда анимация закончилась.

Reflow/layout - расчёт геометрии. Repaint - отрисовка пикселей. Composite - сборка слоёв в финальный кадр. Самыми дешёвыми часто оказываются изменения, которые доходят только до composite.

Также учитывают доступность: `prefers-reduced-motion` позволяет уменьшить или отключить интенсивные движения для пользователей, которым они мешают.

> [!faq]+ Уточнения
> - Layout-свойства могут запускать layout и paint.
> - `transform` и `opacity` часто остаются на composite stage.
> - `will-change` используют точечно, а не постоянно на всём UI.
> - Compositor-анимация не бесплатна при больших слоях и тяжёлых эффектах.
> - `prefers-reduced-motion` нужен для доступности.

#### Пример

```css
.bad {
  position: relative;
  left: 100px;
}

.good {
  transform: translateX(100px);
}

.fade {
  opacity: 0;
  transition: opacity 200ms ease, transform 200ms ease;
}
```

#### Частые ошибки

- Анимировать `height: auto` и удивляться рывкам.
- Использовать `left/top` для постоянного движения.
- Ставить `will-change` на всё приложение.
- Забывать про `prefers-reduced-motion`.
- Думать, что compositor-анимация всегда бесплатна.

#### Связанные темы

- [[Конспект для подготовки/Web Basics/Critical Render Path]]
- [[Конспект для подготовки/Web Basics/Core Web Vitals]]
- [[Конспект для подготовки/JavaScript/requestAnimationFrame и requestIdleCallback]]
- [[Конспект для подготовки/CSS/Stacking context и z-index]]

#### Источники

- [MDN: transform](https://developer.mozilla.org/en-US/docs/Web/CSS/transform)
- [MDN: will-change](https://developer.mozilla.org/en-US/docs/Web/CSS/will-change)
- [MDN: prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- [web.dev: Animations guide](https://web.dev/learn/css/animations)
