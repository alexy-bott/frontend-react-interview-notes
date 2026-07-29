#### Темы

- [[Конспект для подготовки/Next.js/Next.js 14]]
- [[Конспект для подготовки/Next.js/App Router]]
- [[Конспект для подготовки/Next.js/Server и Client Components]]
- [[Конспект для подготовки/Next.js/SSR SSG ISR Streaming]]
- [[Конспект для подготовки/Next.js/Data fetching cache revalidation]]
- [[Конспект для подготовки/Next.js/Server Actions и Route Handlers]]
- [[Конспект для подготовки/Next.js/Deployment env Docker]]

#### Маршрут

1. Зафиксировать baseline Next.js 14 и отделить его React/cache model от новых versions framework.
2. Разобрать App Router: route segments, layouts/templates, loading/error boundaries и специальные route files.
3. Проследить Server/Client boundary: module graphs, RSC Payload, initial HTML, hydration и serializable data.
4. Разделить static/dynamic rendering, ISR и streaming: время render, хранение route output и порядок доставки chunks.
5. Собрать cache model из Request Memoization, Data Cache, Full Route Cache и client Router Cache, затем понять revalidation.
6. Сравнить Server Actions и Route Handlers как UI mutation adapter и самостоятельный HTTP contract.
7. Закрыть production: static export или server runtime, standalone Docker, build/runtime env, shared cache и rollout нескольких replicas.
