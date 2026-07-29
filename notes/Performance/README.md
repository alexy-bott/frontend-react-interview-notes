# Performance

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Performance диагностика и профилирование.md>)

Заметок в разделе: **5**
<!-- SECTION-NAV:END -->

## Темы

- [Performance диагностика и профилирование](<./Performance диагностика и профилирование.md>)
- [Core Web Vitals LCP INP CLS](<./Core Web Vitals LCP INP CLS.md>)
- [Bundle size и loading strategy](<./Bundle size и loading strategy.md>)
- [React performance profiling](<./React performance profiling.md>)
- [Images fonts и resource priority](<./Images fonts и resource priority.md>)

## Маршрут

1. Начать с процесса диагностики: определить сценарий и метрику, снять baseline и найти крупнейший вклад в задержку.
2. Разобрать Core Web Vitals как три разные пользовательские характеристики и научиться раскладывать каждую метрику на причины.
3. Проверить загрузку кода: initial chunks, динамические imports, tree shaking, cache и deploy старых assets.
4. Отдельно профилировать React render и browser work, чтобы не принять layout или paint за проблему фреймворка.
5. Завершить ресурсами: responsive images, web fonts и точечные priority hints.

В любой карточке сохраняется один порядок: измерение -> узкое место -> изменение -> повторное измерение. Оптимизация без подтверждённой причины не считается результатом.

## Когда открывать раздел

- Если вопрос звучит как “как бы ты ускорил приложение”.
- Если просят объяснить LCP, INP, CLS или Core Web Vitals.
- Если нужно разобрать bundle size, code splitting, lazy loading.
- Если тормозит React-экран, таблица, форма, поиск или dashboard.
- Если нужно рассказать, как доказывать эффект оптимизации.

## Связанная карточка

- [Оптимизация фронтенда](<../JavaScript/Оптимизация фронтенда.md>)
