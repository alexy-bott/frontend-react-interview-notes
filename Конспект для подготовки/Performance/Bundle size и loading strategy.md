---
aliases:
  - bundle size
  - loading strategy
  - code splitting
  - tree shaking
  - dependency cost
---

#### Ответ на 60 секунд

Bundle size важен не только как “сколько килобайт скачали”. JavaScript нужно скачать, распаковать, распарсить, скомпилировать и выполнить на main thread. Поэтому два файла с одинаковым gzip-size могут иметь разную runtime-стоимость на слабом устройстве. Главный фокус - initial JS и critical path: сколько кода нужно до первого полезного экрана и первого взаимодействия.

Loading strategy строится вокруг разделения кода: общий entry должен содержать только то, что нужно сразу; редкие routes, heavy widgets, charts, editors, admin-функции и модалки можно грузить через dynamic import. Tree shaking помогает убрать неиспользуемые exports, но зависит от ESM, side effects, формата пакета и импортов.

Оптимизация bundle - это trade-off. Слишком большой initial bundle ухудшает старт, но слишком много мелких chunks создаёт waterfall и задержки переходов. Поэтому анализируют bundle analyzer, Network waterfall, Coverage, route-level chunks, cache headers и реальные метрики.

#### Ключевая схема

```text
dependency graph
  -> initial chunk
  -> route/feature chunks
  -> cache strategy
  -> network + parse + execute cost
```

| Приём | Когда полезен | Риск |
| --- | --- | --- |
| Route-level splitting | разные страницы имеют разный код | delayed navigation |
| Component lazy loading | тяжёлый редкий widget | spinner/waterfall |
| Tree shaking | ESM + side-effect-safe packages | не сработает с CommonJS/side effects |
| Dependency replacement | тяжёлая библиотека ради малой функции | миграционная стоимость |
| Long-term caching | hashed assets | нужен правильный cache policy |
| Prefetch/preload | прогнозируемый следующий ресурс | можно забить сеть |

#### Развернутый ответ

Initial JS должен быть ограничен тем, что нужно для первого экрана и базовой интерактивности. Если в общий entry попадает chart library, rich text editor, admin-only SDK или огромный date library, пользователь платит эту цену всегда, даже если не открывает соответствующую фичу.

Dynamic import создаёт отдельный chunk. Это хорошо для routes, feature flags, редких модалок, сложных графиков и больших редакторов. Но lazy loading должен быть спроектирован: fallback, preload по намерению пользователя, кеширование chunks и отсутствие длинной цепочки “загрузить компонент -> он загрузил ещё три chunks”.

Tree shaking работает лучше с ESM, потому что сборщик может статически понять imports/exports. Он может не удалить код, если пакет CommonJS, импортируется namespace, есть top-level side effects или `sideEffects` в package описан некорректно. Поэтому иногда важнее выбрать библиотеку с хорошим ESM build, чем надеяться на magic.

Cache strategy важна для production. Hashed JS/CSS/assets можно кешировать долго, потому что изменение контента меняет имя файла. `index.html` обычно кешируют осторожнее, чтобы пользователь получил новую версию приложения и ссылки на актуальные chunks.

#### Где применяется во frontend

| Ситуация | Что проверить | Решение |
| --- | --- | --- |
| Первая загрузка тяжёлая | initial chunks + Coverage | вынести редкий код из entry |
| Route открывается медленно | waterfall chunks | preload/prefetch или укрупнить chunk |
| Библиотека добавила 300 KB | bundle analyzer | заменить импорт/библиотеку |
| Tree shaking не работает | формат пакета и side effects | ESM import, точечные imports |
| После deploy 404 на chunks | cache/version mismatch | atomic deploy, корректные cache headers |

> [!faq]+ Уточнения
> - Gzip/Brotli size не показывает parse/execute cost.
> - Code splitting не уменьшает общий код, а переносит часть загрузки на более поздний момент.
> - Lazy loading без продуманного UX может ухудшить perceived performance.
> - Tree shaking не гарантирован для CommonJS и side-effect-heavy пакетов.
> - Long-term caching требует content hash и аккуратного cache policy для HTML.

#### Пример

```tsx
const AdminEditor = lazy(() => import("./AdminEditor"));

function AdminPage() {
  return (
    <Suspense fallback={<EditorSkeleton />}>
      <AdminEditor />
    </Suspense>
  );
}
```

Такой splitting полезен, если editor не нужен большинству пользователей на первом экране.

#### Частые ошибки

- Смотреть только общий bundle size, а не initial route cost.
- Ленивая загрузка компонента, который нужен сразу на первом экране.
- Делить код на десятки мелких chunks без проверки waterfall.
- Импортировать всю библиотеку ради одной функции.
- Держать старый `index.html`, который ссылается на удалённые chunks.

#### Связанные темы

- [[Конспект для подготовки/Web Basics/Bundlers и code splitting]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]
- [[Конспект для подготовки/Tooling/Bundle analysis и size budgets]]
- [[Конспект для подготовки/Tooling/Vite]]
- [[Конспект для подготовки/Tooling/Webpack]]
- [[Конспект для подготовки/React/Suspense и lazy]]
- [[Конспект для подготовки/Web Basics/HTTP caching]]
- [[Конспект для подготовки/Performance/Performance диагностика и профилирование]]

#### Источники

- [web.dev: Reduce JavaScript payloads with code splitting](https://web.dev/articles/reduce-javascript-payloads-with-code-splitting)
- [Webpack: Code splitting](https://webpack.js.org/guides/code-splitting/)
- [Vite: Build options](https://vite.dev/config/build-options.html)
