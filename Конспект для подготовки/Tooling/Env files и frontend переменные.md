---
aliases:
  - env files frontend
  - .env во frontend
  - VITE env
  - NEXT_PUBLIC
  - frontend env variables
---

#### Ответ на 60 секунд

Env-файлы во frontend нужны, чтобы подставлять разные значения для разных окружений: API URL, base path, feature flags, Sentry DSN, build metadata. Но frontend env не являются настоящими секретами: всё, что попало в клиентский bundle или публичный runtime config, может увидеть пользователь.

В Vite клиенту доступны только переменные с prefix `VITE_*`, например `VITE_API_URL`. В Next.js переменные с prefix `NEXT_PUBLIC_*` встраиваются в client bundle, а обычные env-переменные доступны на серверной стороне: Server Components, Route Handlers, Server Actions, build/runtime server code.

Ключевая мысль: `.env.local` и `.env.*.local` обычно не коммитят, а публичные frontend-переменные не используют для токенов, паролей и приватных API keys. Если значение должно быть секретным, оно должно оставаться на backend/server side.

#### Ключевая схема

| Файл/переменная | Зачем |
| --- | --- |
| `.env` | общие дефолты для проекта |
| `.env.local` | локальные значения разработчика, обычно в `.gitignore` |
| `.env.development` | значения для dev mode |
| `.env.production` | значения для production build |
| `.env.staging` | значения для staging mode |
| `VITE_*` | публичные переменные Vite, попадают в клиент |
| `NEXT_PUBLIC_*` | публичные переменные Next.js, попадают в клиент |
| server-only env | секреты и приватные значения на backend/SSR side |
| CI/CD variables | значения, которые pipeline передаёт во время build/deploy |

#### Развернутый ответ

**Env во frontend часто является build-time конфигурацией.**
В Vite `import.meta.env` статически подставляется во время dev/build. В Next.js публичные `NEXT_PUBLIC_*` переменные тоже могут быть встроены в клиентский bundle. Поэтому изменение значения после сборки не всегда меняет уже собранные JS assets, если приложение не читает переменную на сервере в runtime.

**Prefix нужен как защита от случайной утечки.**
Vite не отдаёт в клиент все env-переменные подряд: по умолчанию наружу попадают только `VITE_*`. Next.js использует `NEXT_PUBLIC_*` для переменных, которые должны быть доступны в браузере. Это не делает значения секретными; наоборот, prefix означает “это можно показать клиенту”.

**Все env values приходят строками.**
`VITE_FEATURE_ENABLED=false` в коде может быть строкой `"false"`, которая truthy. Поэтому boolean, number, URL, enum-like values лучше парсить и валидировать в одном месте.

**`.env.local` не должен быть способом хранить секреты frontend-а.**
Локальный файл может содержать private значения для server-side кода, но если переменная используется в клиентском bundle, она станет видимой. Для настоящих secrets нужен backend endpoint, serverless/edge function, BFF, Route Handler или другой server-side слой.

**В CI важно понимать момент подстановки.**
Если `VITE_API_URL` или `NEXT_PUBLIC_API_URL` подставляется во время build, то Docker image или static artifact уже содержит это значение. Для разных окружений нужно либо собирать отдельные artifacts, либо иметь runtime-конфигурацию через server/CDN/HTML injection, если проект это поддерживает.

#### Где применяется во frontend

| Ситуация | Что важно |
| --- | --- |
| API URL | публичный base URL можно класть в `VITE_*` / `NEXT_PUBLIC_*` |
| Feature flag | публичный flag не должен раскрывать секретную бизнес-логику |
| Sentry DSN | часто публичный, но auth tokens для upload sourcemaps - секреты CI |
| OAuth client id | часто публичный, client secret - только server-side |
| Next.js SSR | обычные env можно читать на сервере |
| Static SPA | env чаще всего зашиты во время build |
| Docker image | build-time env и runtime env могут отличаться |

#### Если уточнили

> - **Почему нельзя положить API token в `VITE_API_TOKEN`?** Потому что значение попадёт в клиентский JS bundle и будет доступно пользователю.
> - **Чем `mode` отличается от `NODE_ENV` в Vite?** `mode` выбирает env-файлы вроде `.env.staging`, а `NODE_ENV` влияет на development/production поведение экосистемы.
> - **Почему env поменяли, а приложение всё ещё ходит на старый API?** Если значение было встроено на build step, нужно пересобрать artifact или использовать runtime-config подход.
> - **Нужно ли типизировать env?** Да. Лучше иметь модуль `config/env.ts`, который читает, парсит и валидирует значения.

#### Пример

```ts
// config/env.ts
const rawApiUrl = import.meta.env.VITE_API_URL;

if (!rawApiUrl) {
  throw new Error("VITE_API_URL is required");
}

export const env = {
  apiUrl: rawApiUrl,
  enableMockApi: import.meta.env.VITE_ENABLE_MOCK_API === "true",
};
```

Такой подход лучше, чем читать `import.meta.env` по всему приложению: правила парсинга и fallback-логика находятся в одном месте.

#### Частые ошибки

- Класть secrets в `VITE_*` или `NEXT_PUBLIC_*`.
- Думать, что `.env.local` автоматически безопасен для клиентского кода.
- Не парсить boolean/number env values.
- Менять runtime env после build и ожидать, что static bundle сам изменится.
- Коммитить `.env.local` или `.env.production.local`.
- Разбрасывать чтение env по всему приложению.

#### Связанные темы

- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]
- [[Конспект для подготовки/Tooling/Vite]]
- [[Конспект для подготовки/Next.js/Deployment env Docker]]
- [[Конспект для подготовки/DevOps/Env variables и секреты]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/Security/Token storage XSS CSRF tradeoffs]]

#### Источники

- [Vite Docs: Env Variables and Modes](https://vite.dev/guide/env-and-mode)
- [Next.js Docs: Environment Variables](https://nextjs.org/docs/app/guides/environment-variables)
- [npm Docs: package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json/)
