# Next.js

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →](<./Next.js 14.md>)

Заметок в разделе: **7**
<!-- SECTION-NAV:END -->

## Темы

- [Next.js 14](<./Next.js 14.md>)
- [App Router](<./App Router.md>)
- [Server и Client Components](<./Server и Client Components.md>)
- [SSR SSG ISR Streaming](<./SSR SSG ISR Streaming.md>)
- [Data fetching cache revalidation](<./Data fetching cache revalidation.md>)
- [Server Actions и Route Handlers](<./Server Actions и Route Handlers.md>)
- [Deployment env Docker](<./Deployment env Docker.md>)

## Маршрут

1. Зафиксировать baseline Next.js 14 и отделить его React/cache model от новых versions framework.
2. Разобрать App Router: route segments, layouts/templates, loading/error boundaries и специальные route files.
3. Проследить Server/Client boundary: module graphs, RSC Payload, initial HTML, hydration и serializable data.
4. Разделить static/dynamic rendering, ISR и streaming: время render, хранение route output и порядок доставки chunks.
5. Собрать cache model из Request Memoization, Data Cache, Full Route Cache и client Router Cache, затем понять revalidation.
6. Сравнить Server Actions и Route Handlers как UI mutation adapter и самостоятельный HTTP contract.
7. Закрыть production: static export или server runtime, standalone Docker, build/runtime env, shared cache и rollout нескольких replicas.
