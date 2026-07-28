---
aliases:
  - ESLint и Prettier
  - eslint config
  - prettier config
  - code quality configs
  - lint и format
---

#### Ответ на 60 секунд

ESLint и Prettier решают разные задачи. ESLint анализирует код и ищет проблемы: потенциальные баги, неправильное использование React hooks, неиспользуемые переменные, нарушения командных правил. Prettier форматирует код: переносы, отступы, кавычки, trailing commas. Поэтому ESLint - про качество и правила, Prettier - про единый стиль форматирования.

В современных проектах ESLint часто настраивают через `eslint.config.js`/`eslint.config.mjs`, а Prettier - через `.prettierrc`, `prettier.config.*` или поле `prettier` в `package.json`. В CI обычно запускают отдельные команды: `lint`, `format:check`, иногда `typecheck`.

Главная практическая идея: форматирование должно быть автоматическим и предсказуемым, а lint-правила должны ловить реальные проблемы, не превращая проект в набор случайных запретов.

#### Ключевая схема

| Инструмент | За что отвечает | Типичная команда |
| --- | --- | --- |
| ESLint | статический анализ и правила кода | `eslint .` |
| Prettier | форматирование | `prettier . --check` |
| TypeScript | проверка типов | `tsc --noEmit` |
| Husky/lint-staged | проверки перед commit | `lint-staged` |
| CI | обязательные проверки MR | `lint`, `typecheck`, `test`, `build` |

#### Развернутый ответ

**ESLint смотрит на смысл кода.**
Он может подсветить неправильные зависимости в React hooks, неиспользуемый импорт, опасный `any`, запрещённый import path, нарушение FSD boundary или командного соглашения. ESLint можно расширять plugins: React, React Hooks, TypeScript ESLint, import rules, accessibility rules.

**Prettier убирает споры о стиле.**
Он не пытается понять архитектуру приложения. Его задача - стабильно отформатировать код так, чтобы команда не обсуждала отступы, кавычки и переносы в review. Prettier лучше запускать автоматически в editor/pre-commit и отдельно проверять в CI.

**ESLint и Prettier не должны конфликтовать.**
Если ESLint пытается форматировать то же, что Prettier, команда получает шумные правки и раздражающие конфликты. Поэтому форматирование обычно отдают Prettier, а ESLint оставляют для качества, best practices и командных правил.

**TypeScript не заменяет ESLint.**
TypeScript проверяет типы, но не все правила качества. Например, он не обязан запрещать конкретные import boundaries, не контролирует стиль hooks так же, как eslint-plugin-react-hooks, и не заменяет accessibility lint rules.

**CI должен запускать проверки в том же виде, что команда локально.**
Если локально разработчики форматируют Prettier, а CI проверяет другим config, будут ложные падения. Если aliases настроены в Vite/TS, ESLint тоже должен понимать module resolution, иначе он может ругаться на валидные imports.

#### Где применяется во frontend

| Ситуация | Что проверяет |
| --- | --- |
| React hooks | правила hooks и dependencies |
| FSD/import boundaries | запрет imports через неправильные слои |
| Accessibility | часть ошибок JSX/ARIA можно ловить lint rules |
| TypeScript проект | `@typescript-eslint` правила поверх typecheck |
| Code review | меньше споров о стиле, больше внимания к логике |
| CI quality gate | MR не проходит без lint/format/typecheck |

#### Если уточнили

> - **Чем ESLint отличается от Prettier?** ESLint ищет проблемы и нарушения правил, Prettier форматирует код.
> - **Можно ли использовать только Prettier?** Можно для форматирования, но он не заменяет правила качества и React/TypeScript checks.
> - **Можно ли использовать только ESLint?** Можно, но форматирование через ESLint часто даёт больше конфликтов и хуже отделяет стиль от качества.
> - **Почему lint проходит локально, но падает в CI?** Часто отличаются версии Node/package manager, lock-файл, config, working directory или glob patterns.

#### Пример scripts

```json
{
  "scripts": {
    "lint": "eslint .",
    "format": "prettier . --write",
    "format:check": "prettier . --check",
    "typecheck": "tsc --noEmit"
  }
}
```

Такой набор разделяет проверки: lint не отвечает за форматирование, Prettier не отвечает за типы, TypeScript не отвечает за командные lint-правила.

#### Частые ошибки

- Считать ESLint и Prettier одним и тем же.
- Дублировать форматирующие правила ESLint и Prettier.
- Не запускать `format:check` в CI.
- Настроить aliases в Vite/TS, но не настроить resolver для ESLint.
- Отключать lint-правила глобально вместо точечного решения.
- Заменять `typecheck` одним ESLint.

#### Связанные темы

- [[Конспект для подготовки/Tooling/Файлы frontend проекта]]
- [[Конспект для подготовки/Tooling/package.json и lock-файлы]]
- [[Конспект для подготовки/Tooling/Build config и production сборка]]
- [[Конспект для подготовки/TypeScript/tsconfig и strict mode]]
- [[Конспект для подготовки/React/Правила хуков]]
- [[Конспект для подготовки/Architecture/FSD]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]

#### Источники

- [ESLint Docs: Configuration Files](https://eslint.org/docs/latest/use/configure/configuration-files)
- [Prettier Docs: Configuration File](https://prettier.io/docs/configuration)
- [TypeScript Docs: tsconfig.json](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html)
