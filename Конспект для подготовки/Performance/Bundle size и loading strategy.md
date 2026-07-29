---
aliases:
  - bundle size
  - loading strategy
  - code splitting
  - tree shaking
  - dependency cost
---

#### Быстрый ответ

Bundle - результат обхода графа модулей сборщиком: JavaScript, CSS и связанные assets объединяются или разделяются на chunks, которые браузер загружает для запуска приложения. Важен не только переданный размер: JavaScript нужно распаковать, разобрать, скомпилировать и выполнить на main thread.

Loading strategy определяет, какой код нужен при первом открытии, какой можно загрузить для route или feature позже и какие chunks стоит заранее подготовить. Цель - уменьшить критический путь без появления длинного waterfall из мелких файлов. Решение проверяют через bundle analyzer, Network, Coverage, CPU trace и пользовательские метрики, а не по общему числу килобайт.

#### Ключевая схема

```text
entry points + imports
-> module graph
-> tree shaking и transforms
-> initial chunks + async chunks
-> content hashes и cache headers
-> download + parse + execute
```

| Механизм | Что меняет | Основной компромисс |
| --- | --- | --- |
| Code splitting | переносит часть кода в отдельный chunk | дополнительный запрос при использовании |
| Tree shaking | исключает статически неиспользуемые exports | зависит от формата модулей и side effects |
| Long-term caching | повторно использует неизменившийся hashed asset | HTML должен своевременно ссылаться на новую версию |
| Preload/prefetch | начинает загрузку до обычного обнаружения или использования | конкуренция за сеть и бесполезный трафик |
| Замена зависимости | снижает transfer и CPU cost | стоимость миграции и возможная потеря возможностей |

#### Базовая модель

**Initial chunk** содержит код, необходимый для запуска текущей страницы. **Async chunk** создаётся на границе динамического `import()` и загружается при достижении этой ветки либо раньше по отдельной подсказке. Code splitting обычно не уменьшает весь код приложения; он меняет момент, когда пользователь оплачивает его загрузку и выполнение.

**Tree shaking** - исключение неиспользуемого кода на основе статической структуры ES modules. Сборщик должен видеть imports/exports и понимать, можно ли удалить модуль без потери побочного эффекта. Dynamic property access, CommonJS и неверно объявленные package side effects могут ограничить анализ.

**Content hash** в имени asset меняется вместе с содержимым. Такой файл можно кешировать надолго как immutable. HTML и manifest кешируют осторожнее, потому что они содержат ссылки на актуальные hashed chunks.

#### Развернутый ответ

**Критический путь.** Сначала измеряют код, необходимый для первого полезного экрана и раннего взаимодействия. Rich text editor, charting SDK или admin feature не должны автоматически попадать в общий entry, если большинство пользователей не использует их в этом сценарии.

**Граница splitting.** Route-level splitting даёт крупные предсказуемые chunks. Component-level splitting полезен для тяжёлого редкого виджета, но может создать последовательность: route chunk загружен, после render обнаружен widget chunk, затем его data request. Такой waterfall исправляют переносом границы, параллельной загрузкой данных и кода или предварительной загрузкой по обоснованному пользовательскому намерению.

**Стоимость dependency.** Анализируют не только package целиком, но и конкретный import, дублирование версий, локали, polyfills и код, который действительно вошёл в chunk. Маленький transfer после Brotli может всё равно означать дорогой parse/execute. Замена библиотеки оправдана измеримым вкладом, а не её репутацией.

**Cache и deploy.** После релиза открытая вкладка может содержать старый HTML/runtime и запросить lazy chunk, уже удалённый с CDN. Надёжная схема использует atomic deployment, хранит старые hashed assets дольше максимальной жизни клиента и обрабатывает ошибку загрузки chunk контролируемым предложением обновить приложение. Простое бесконечное auto-reload может создать цикл.

**Budget.** CI может ограничивать initial JS, отдельный chunk или изменение размера относительно main. Budget останавливает известную регрессию до merge, но не заменяет runtime-проверку: он не видит задержку backend, layout и конкретные пользовательские данные.

#### Диагностика

| Симптом | Проверка | Возможное решение |
| --- | --- | --- |
| Медленный первый экран | состав initial chunks и Coverage | вынести редкую feature из entry |
| Route ждёт цепочку chunks | Network initiator waterfall | изменить границу splitting или загрузить зависимости параллельно |
| Tree shaking не удаляет модуль | output analyzer, ESM/CJS, `sideEffects` | исправить import или metadata пакета |
| Один package встречается несколько раз | версии и dependency graph | выровнять версии или deduplicate |
| После deploy возникает chunk 404 | версия HTML и наличие старого asset | atomic deploy и retention hashed assets |
| Transfer небольшой, CPU высокий | Performance trace на слабом CPU | сократить выполняемый код, а не только сжатый размер |

#### Пример

В React 18 `lazy` использует динамический import для компонента, который не нужен на основном route:

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

Сборщик может создать отдельный chunk для `AdminEditor`. Это улучшает initial route только при условии, что редактор действительно не нужен сразу; задержка его открытия и fallback становятся частью нового UX-компромисса.

#### Ключевые уточнения

- Общий bundle size не равен стоимости первого route. Сначала анализируют initial chunks и критический путь.
- Code splitting переносит работу на более поздний момент; он не удаляет код и способен ухудшить первое открытие lazy feature.
- Tree shaking опирается на статический анализ и корректно описанные side effects, а не удаляет любой неисполненный код автоматически.
- Сжатый размер не отражает parse и execute cost, поэтому Network дополняют CPU trace.
- Long-term cache безопасен для content-hashed assets, но старые clients требуют согласованной deploy-стратегии и сохранения прежних chunks.

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
- [webpack: Code Splitting](https://webpack.js.org/guides/code-splitting/)
- [webpack: Tree Shaking](https://webpack.js.org/guides/tree-shaking/)
- [Vite: Build Options](https://vite.dev/config/build-options.html)
