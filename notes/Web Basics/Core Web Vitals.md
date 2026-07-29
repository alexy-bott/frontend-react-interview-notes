# Core Web Vitals

<!-- NOTE-NAV-TOP:START -->
[← Critical Render Path](<./Critical Render Path.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Realtime transports →](<./Realtime transports.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Core Web Vitals — три полевые метрики пользовательского опыта страницы. LCP (Largest Contentful Paint) оценивает скорость появления основного видимого контента, INP (Interaction to Next Paint) — отзывчивость на взаимодействия, CLS (Cumulative Layout Shift) — неожиданные смещения уже видимой раскладки (layout).

Текущие хорошие значения: LCP не более 2,5 с, INP не более 200 мс, CLS не более 0,1. Для оценки страницы или origin используют 75-й перцентиль посещений отдельно для мобильных и настольных устройств. Это означает, что не менее 75% измеренных посещений должны укладываться в порог каждой метрики.

Core Web Vitals показывают симптом и его масштаб, но не называют исправление. Сначала находят проблемную метрику в полевых данных реальных пользователей (field data), затем воспроизводят медленный сценарий лабораторными инструментами (lab tools), разбирают метрику на составляющие и повторно измеряют после изменения.

## Метрики и пороги

| Метрика | Good | Needs improvement | Poor |
| --- | --- | --- | --- |
| LCP | `≤ 2.5 s` | `> 2.5 s` и `≤ 4 s` | `> 4 s` |
| INP | `≤ 200 ms` | `> 200 ms` и `≤ 500 ms` | `> 500 ms` |
| CLS | `≤ 0.1` | `> 0.1` и `≤ 0.25` | `> 0.25` |

Порог применяется к распределению, а не к одному запуску. Если p75 LCP равен 2,4 секунды, 75% посещений имеют LCP не хуже 2,4 секунды, а оставшиеся 25% могут быть заметно медленнее. Поэтому полезно дополнительно смотреть p90/p95 и сегменты слабых устройств, стран, сетей и маршрутов.

Набор Core Web Vitals может эволюционировать. Например, INP заменил FID в 2024 году. Версию метрик и пороги сверяют с актуальной [официальной страницей Web Vitals](https://web.dev/articles/vitals), а не навсегда зашивают в внутренний документ без даты.

## LCP — основной контент

LCP измеряет время от начала навигации до отрисовки крупнейшего подходящего элемента контента в viewport. Кандидатом часто является:

- `<img>` или изображение внутри SVG;
- poster у `<video>`;
- фоновое изображение через CSS `url()`;
- крупный блок текста.

LCP относится к элементу, который фактически оказался крупнейшим, а не к компоненту, который команда заранее назвала hero. Кандидат способен измениться по мере загрузки страницы.

Путь LCP удобно разделить:

```text
TTFB
  -> задержка обнаружения LCP resource
  -> загрузка resource
  -> render delay после готовности
```

Медленный LCP может быть вызван сервером, поздним обнаружением image, низким приоритетом, большим файлом, blocking CSS/JS или main-thread работой перед render. Уменьшение общего bundle не поможет, если всё время потеряно до первого byte HTML; preload не поможет, если ресурс уже загружается рано и ограничение находится в render delay.

## INP — отзывчивость

INP наблюдает qualifying interactions на протяжении посещения страницы и выбирает значение, отражающее худшую или почти худшую задержку с учётом количества взаимодействий. Он оценивает клики, касания и ввод с клавиатуры; hover и прокрутка напрямую в набор таких interactions не входят.

Одна interaction может включать несколько событий, например `pointerup`, `mouseup` и `click`. Её длительность состоит из:

```text
input delay
  -> event handlers
  -> presentation delay
  -> следующий показанный кадр
```

Input delay появляется, когда основной поток уже занят. Processing duration растёт из-за тяжёлых handlers. Presentation delay включает React render/commit, style, layout и paint после обработчика.

INP заканчивается следующим визуальным кадром, а не завершением всей бизнес-операции. Кнопка может быстро показать pending state и затем ждать сеть. Если интерфейс не даёт визуальной реакции до ответа сервера, пользовательская задержка будет большой, хотя сеть сама не блокирует main thread.

## CLS — визуальная стабильность

Layout shift возникает, когда видимый элемент меняет положение между кадрами без ожидаемой пользователем причины. Его score зависит от доли viewport, затронутой смещением, и расстояния перемещения.

CLS страницы берёт наибольшую session window неожиданных shifts: окно объединяет сдвиги, если между соседними не больше секунды, и ограничено пятью секундами. Поэтому CLS не является простой суммой всех движений за бесконечно долгую вкладку.

Частые причины:

- image, video или `iframe` без зарезервированных размеров;
- реклама, banner или error message, вставленные над контентом;
- web font с сильно отличающимися метриками;
- skeleton, размер которого не совпадает с результатом;
- анимация свойств, меняющих layout.

Сдвиг вскоре после пользовательского ввода может считаться ожидаемым и исключаться из CLS по правилу recent input. Это не означает, что любой layout jump после клика имеет хороший UX. Метрика и продуктовая оценка остаются разными.

`transform` перемещает визуальный слой без пересчёта положения соседей и обычно не создаёт layout shift score, но перекрытие или неожиданная анимация всё равно может мешать пользователю.

## Field и lab data

**Field data** собирается у реальных пользователей (Real User Monitoring, RUM) или берётся из Chrome User Experience Report (CrUX). Оно включает настоящие устройства, сети, cache state, расширения и поведение пользователя.

**Lab data** получается в контролируемом запуске Lighthouse, DevTools или теста. Оно воспроизводимо и даёт trace, но представляет одно искусственное окружение.

| Вопрос | Подходящий источник |
| --- | --- |
| Сколько пользователей страдает | field distribution, p75/p90, сегменты |
| Какая task задержала interaction | Performance trace |
| Какой request является LCP resource | DevTools/PSI/Lighthouse |
| Что сдвинуло layout | Layout Shift records и field attribution |
| Появилась ли регрессия до release | lab CI и performance budgets |

Lighthouse без реального пользовательского ввода не измеряет полноценный INP и использует Total Blocking Time (TBT) как диагностический proxy. Хороший TBT повышает шанс хорошей отзывчивости, но не заменяет field INP.

CrUX обычно агрегирует данные по URL или origin за период и не знает внутренний release, аккаунт и продуктовый сценарий. Собственный RUM позволяет добавить route, app version, device class и attribution, соблюдая ограничения приватности.

## Измерение в приложении

Официальная библиотека `web-vitals` рассчитывает метрики с учётом деталей их алгоритмов:

```js
import { onCLS, onINP, onLCP } from "web-vitals";

function reportMetric(metric) {
  const body = JSON.stringify(metric);

  if (navigator.sendBeacon?.("/analytics/web-vitals", body)) {
    return;
  }

  void fetch("/analytics/web-vitals", {
    method: "POST",
    body,
    keepalive: true,
  });
}

onCLS(reportMetric);
onINP(reportMetric);
onLCP(reportMetric);
```

Production-сбор данных добавляет sampling, app version, route и необходимые attribution fields. Endpoint принимает несколько событий одной страницы, а dashboard строит распределение, а не среднее значение.

Среднее скрывает медленный хвост. Если большинство пользователей имеют быстрый LCP, а слабые телефоны — очень медленный, среднее может выглядеть приемлемо, тогда как p75 уже нарушает порог.

## Как переходить от метрики к исправлению

1. Выбрать failing metric и сегмент field data.
2. Найти конкретный URL, route или interaction.
3. Воспроизвести близкие CPU/network условия.
4. Разложить LCP, INP или CLS на причинные части.
5. Исправить одно измеренное узкое место.
6. Проверить lab trace и дождаться подтверждения field distribution.

Подробная диагностика каждой метрики находится в [Core Web Vitals LCP INP CLS](<../../Конспект для подготовки/Performance/Core Web Vitals LCP INP CLS.md>), а работа основного потока — в [Main thread long tasks и responsiveness](<../Browser Internals/Main thread long tasks и responsiveness.md>).

## Границы метрик

Core Web Vitals не измеряют всё качество приложения. Они не доказывают корректность, доступность, безопасность, успешность бизнес-сценария и полную скорость API. Быстрый визуальный ответ с неверными данными остаётся ошибкой.

Порог `good` является общим ориентиром, а не поводом прекратить оптимизацию на `2.49 s`. Для критичного редактора может быть важен latency конкретной команды, для видеосервиса — media startup, для checkout — время завершения оплаты.

## Ключевые уточнения

- LCP, INP и CLS оценивают разные пользовательские ощущения, поэтому для них нет одной общей оптимизации.
- Порог проверяется по 75-му перцентилю полевых посещений отдельно для mobile и desktop, а не по одному Lighthouse score.
- INP включает ожидание main thread, handlers и подготовку следующего кадра, но не обязан ждать завершения всей сетевой операции.
- CLS учитывает неожиданные shifts в наибольшей session window, а не любое визуальное движение страницы.
- Field data показывает масштаб и сегмент проблемы, а lab trace помогает найти конкретную причину; оба вида измерения нужны вместе.

## Связанные темы

- [Core Web Vitals LCP INP CLS](<../../Конспект для подготовки/Performance/Core Web Vitals LCP INP CLS.md>)
- [Performance диагностика и профилирование](<../../Конспект для подготовки/Performance/Performance диагностика и профилирование.md>)
- [Critical Render Path](<./Critical Render Path.md>)
- [Main thread long tasks и responsiveness](<../Browser Internals/Main thread long tasks и responsiveness.md>)
- [Rendering pipeline reflow repaint composite](<../Browser Internals/Rendering pipeline reflow repaint composite.md>)
- [HTTP caching](<./HTTP caching.md>)

## Источники

- [web.dev: Web Vitals](https://web.dev/articles/vitals)
- [web.dev: Largest Contentful Paint](https://web.dev/articles/lcp)
- [web.dev: Interaction to Next Paint](https://web.dev/articles/inp)
- [web.dev: Cumulative Layout Shift](https://web.dev/articles/cls)
- [web.dev: Measure Web Vitals in the field](https://web.dev/articles/vitals-field-measurement-best-practices)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Critical Render Path](<./Critical Render Path.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Realtime transports →](<./Realtime transports.md>)
<!-- NOTE-NAV-BOTTOM:END -->
