#### Темы

- [[Конспект для подготовки/Performance/Performance диагностика и профилирование]]
- [[Конспект для подготовки/Performance/Core Web Vitals LCP INP CLS]]
- [[Конспект для подготовки/Performance/Bundle size и loading strategy]]
- [[Конспект для подготовки/Performance/React performance profiling]]
- [[Конспект для подготовки/Performance/Images fonts и resource priority]]
- [[Конспект для подготовки/JavaScript/Оптимизация фронтенда]]

#### Маршрут

1. Начать с диагностики: какая метрика или пользовательский сценарий реально страдает.
2. Разобрать Core Web Vitals: LCP, INP, CLS и причины регрессий.
3. Проверить loading: JS/CSS bundle, chunks, dependency cost, cache, waterfall.
4. Проверить runtime: main thread, long tasks, React renders, layout/paint.
5. Проверить ресурсы: изображения, fonts, preload/preconnect/fetchpriority.
6. После исправления сравнить lab-замеры и field/RUM, чтобы не улучшить одну метрику ценой другой.

#### Когда открывать раздел

- Если вопрос звучит как “как бы ты ускорил приложение”.
- Если просят объяснить LCP, INP, CLS или Core Web Vitals.
- Если нужно разобрать bundle size, code splitting, lazy loading.
- Если тормозит React-экран, таблица, форма, поиск или dashboard.
- Если нужно рассказать, как доказывать эффект оптимизации.
