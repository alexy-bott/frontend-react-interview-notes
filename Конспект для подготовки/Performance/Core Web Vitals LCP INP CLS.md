---
aliases:
  - Core Web Vitals
  - LCP
  - INP
  - CLS
  - Web Vitals diagnostics
---

#### Ответ на 60 секунд

Core Web Vitals - это три пользовательские метрики: LCP показывает скорость появления главного контента, INP - отзывчивость на взаимодействия, CLS - стабильность layout. Хорошие ориентиры: LCP до 2.5 s, INP до 200 ms, CLS до 0.1 на 75-м перцентиле реальных пользователей, отдельно по mobile и desktop.

LCP диагностируют через путь главного элемента: TTFB, задержка начала загрузки LCP-ресурса, длительность загрузки ресурса и задержка render после загрузки. INP разбирают через input delay, обработчики событий, main thread, React render, layout и следующий paint. CLS ищут через элементы, которые двигают layout: изображения/iframe без размеров, web fonts, banners, ads, skeletons и динамические вставки.

Главная мысль: Core Web Vitals нельзя чинить одной универсальной техникой. Для LCP может помочь server response, image priority или critical CSS; для INP - уменьшение JS и long tasks; для CLS - стабильная геометрия. Решение выбирают по конкретной причине метрики.

#### Ключевая схема

| Метрика | Что измеряет | Частые причины |
| --- | --- | --- |
| LCP | появление главного контента | TTFB, LCP image, blocking CSS/JS, hydration |
| INP | задержка до следующего paint после interaction | long tasks, handlers, render, layout |
| CLS | неожиданные layout shifts | images/iframes без размеров, fonts, dynamic inserts |

#### Развернутый ответ

**LCP**

Первый шаг - найти LCP element. Это может быть hero image, крупный текст, poster video или главный блок контента. После этого смотрят, где теряется время: сервер долго отдаёт HTML, браузер поздно обнаруживает ресурс, ресурс долго грузится, или ресурс загрузился, но элемент поздно отрисовался из-за CSS/JS/hydration.

**INP**

INP измеряет не весь async-сценарий до конца, а задержку до ближайшего визуального ответа после взаимодействия. Если пользователь нажал кнопку, а main thread занят длинной задачей, обработчик стартует поздно. Если обработчик тяжёлый, paint тоже задержится. Если после handler большой React render или layout, пользователь опять увидит задержку.

**CLS**

CLS появляется, когда уже видимый контент неожиданно меняет позицию. Часто причина не в скорости JS, а в отсутствии заранее зарезервированного места. Поэтому для изображений, iframe, embeds, ads, skeletons и динамических блоков важны размеры, aspect-ratio и стабильная высота.

**Lab vs field**

Lab может показать проблему на выбранном устройстве и сети, но field важнее для оценки качества релиза. Например, desktop может проходить Core Web Vitals, а mobile - нет. Или новая версия ухудшила INP только у пользователей с тяжёлыми таблицами.

#### Где применяется во frontend

| Ситуация | Метрика | Что проверять |
| --- | --- | --- |
| Hero image поздно появляется | LCP | `preload`, `fetchpriority`, формат, размеры, CDN |
| Кнопка “Сохранить” лагает | INP | handler, validation, render, pending UI |
| Форма прыгает при ошибке | CLS | зарезервировано ли место под error text |
| SSR-страница долго оживает | LCP/INP | hydration cost, client JS, server response |
| Dashboard с графиками тормозит | INP | long tasks, chart render, workers, virtualization |

> [!faq]+ Уточнения
> - INP заменил FID как Core Web Vital, потому что учитывает взаимодействия по всей жизни страницы, а не только первое.
> - LCP не всегда картинка; иногда это крупный текстовый блок.
> - `preload` полезен для действительно критичного LCP-ресурса, но вреден при использовании для всего подряд.
> - CLS считается для неожиданных shifts; пользовательское действие может менять layout без штрафа, если изменение ожидаемо.
> - Оптимизация одной метрики может ухудшить другую, поэтому проверяют весь набор.

#### Пример

```html
<link rel="preload" as="image" href="/hero.avif" fetchpriority="high">

<img
  src="/hero.avif"
  width="1200"
  height="640"
  fetchpriority="high"
  decoding="async"
  alt="Product dashboard"
>
```

Здесь браузеру проще рано обнаружить главный image-resource, а размеры помогают избежать layout shift.

#### Частые ошибки

- Улучшать общий bundle size, когда LCP упирается в TTFB или hero image.
- Чинить INP только debounce-ом, хотя проблема в большом render/commit.
- Не задавать размеры images/iframes и получать CLS.
- Смотреть только desktop Lighthouse.
- Путать lab score и реальные field-метрики.

#### Связанные темы

- [[Конспект для подготовки/Web Basics/Core Web Vitals]]
- [[Конспект для подготовки/Web Basics/Critical Render Path]]
- [[Конспект для подготовки/Performance/Performance диагностика и профилирование]]
- [[Конспект для подготовки/Performance/Images fonts и resource priority]]
- [[Конспект для подготовки/Browser Internals/Main thread long tasks и responsiveness]]
- [[Конспект для подготовки/React/Hydration]]

#### Источники

- [web.dev: Web Vitals](https://web.dev/articles/vitals)
- [web.dev: Interaction to Next Paint](https://web.dev/articles/inp)
- [web.dev: Optimize LCP](https://web.dev/articles/optimize-lcp)
- [web.dev: Optimize CLS](https://web.dev/articles/optimize-cls)
