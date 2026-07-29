---
aliases:
  - ESLint и Prettier
  - eslint config
  - prettier config
  - code quality configs
  - lint и format
---

#### Быстрый ответ

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

#### Базовая модель

TypeScript, ESLint и Prettier анализируют разные contracts: типовую корректность, статические правила поведения/архитектуры и deterministic formatting. Один зелёный инструмент не доказывает результат остальных.

#### Развернутый ответ

**ESLint смотрит на смысл кода.**
Он может подсветить неправильные зависимости в React hooks, неиспользуемый импорт, опасный `any`, запрещённый import path, нарушение FSD boundary или командного соглашения. ESLint можно расширять plugins: React, React Hooks, TypeScript ESLint, import rules, accessibility rules.

Некоторые TypeScript ESLint rules используют type information и требуют parser project/service configuration. Они ловят больше semantic ошибок, но работают медленнее; быстрый local lint и полный type-aware CI lint можно разделить осознанно.

**Prettier убирает споры о стиле.**
Он не пытается понять архитектуру приложения. Его задача - стабильно отформатировать код так, чтобы команда не обсуждала отступы, кавычки и переносы в review. Prettier лучше запускать автоматически в editor/pre-commit и отдельно проверять в CI.

**ESLint и Prettier не должны конфликтовать.**
Если ESLint пытается форматировать то же, что Prettier, команда получает шумные правки и раздражающие конфликты. Поэтому форматирование обычно отдают Prettier, а ESLint оставляют для качества, best practices и командных правил.

**TypeScript не заменяет ESLint.**
TypeScript проверяет типы, но не все правила качества. Например, он не обязан запрещать конкретные import boundaries, не контролирует стиль hooks так же, как eslint-plugin-react-hooks, и не заменяет accessibility lint rules.

**CI должен запускать проверки в том же виде, что команда локально.**
Если локально разработчики форматируют Prettier, а CI проверяет другим config, будут ложные падения. Если aliases настроены в Vite/TS, ESLint тоже должен понимать module resolution, иначе он может ругаться на валидные imports.

#### Практическое применение

| Ситуация | Что проверяет |
| --- | --- |
| React hooks | правила hooks и dependencies |
| FSD/import boundaries | запрет imports через неправильные слои |
| Accessibility | часть ошибок JSX/ARIA можно ловить lint rules |
| TypeScript проект | `@typescript-eslint` правила поверх typecheck |
| Code review | меньше споров о стиле, больше внимания к логике |
| CI quality gate | MR не проходит без lint/format/typecheck |

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

#### Ключевые уточнения

- Prettier форматирует syntax tree, но не подтверждает correctness/accessibility/architecture.
- ESLint rules имеют owner/rationale; global disable требует изменения policy, точечный disable — комментария причины.
- Type-aware lint дополняет, но не заменяет `tsc --noEmit` и application tests.
- Flat config, plugins и resolver должны соответствовать версии ESLint и module model проекта.
- Pre-commit даёт быстрый feedback только по staged files; CI проверяет repository целиком в clean environment.
- Aliases/import boundaries синхронизируют с actual TypeScript/bundler resolution, иначе lint создаёт false signals.
- Auto-fix запускают на контролируемом diff: fixable rule способен изменить semantics.

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
