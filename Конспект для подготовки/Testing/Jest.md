---
aliases:
  - Jest
  - jest mocks
  - jest fake timers
  - unit tests
---

#### Ответ на 60 секунд

Jest - тестовый раннер и assertion/mocking framework для JavaScript и TypeScript. Он запускает тесты, даёт API `test`, `describe`, `expect`, поддерживает mocks, spies, fake timers, snapshots и coverage. Во frontend его часто используют для unit-тестов чистых функций, reducers, formatters, hooks и React-компонентов вместе с React Testing Library.

Jest проверяет код в тестовой среде, а не в реальном браузерном приложении. Поэтому всё подряд mocks-ами не подменяют. Тест проверяет поведение и контракт, а mocks использует только на границах: timers, network, storage, analytics, router, browser APIs. Для React UI Jest сочетают с Testing Library, а API-моки часто делают через MSW.

#### Ключевая схема

| Часть Jest | Для чего нужна |
| --- | --- |
| `test` / `it` | описать отдельную проверку |
| `describe` | сгруппировать связанные тесты |
| `expect` | assertion API |
| matchers | `toBe`, `toEqual`, `toHaveBeenCalledWith` |
| mock functions | проверить вызовы и управлять return value |
| fake timers | контролировать `setTimeout`, debounce, intervals |
| setup/teardown | подготовить и очистить окружение |
| coverage | увидеть, какой код покрыт тестами |

#### Практическая настройка

Практическая настройка Jest включает три зоны: где тесты запускаются, как проектный код преобразуется перед тестом и как тесты изолируются друг от друга. Для React это чаще всего `jsdom`, `setupFilesAfterEnv`, aliases, моки CSS/assets, transform для TypeScript/JSX и очистка mocks между тестами.

| Что настраивают | Зачем |
| --- | --- |
| `testEnvironment` | `node` для логики, `jsdom` для React/DOM |
| `setupFilesAfterEnv` | подключить jest-dom, MSW lifecycle, общие matchers |
| `transform` | обработать TypeScript, JSX, ESM или Babel/SWC pipeline |
| `moduleNameMapper` | aliases, CSS Modules, картинки, SVG mocks |
| `testMatch` / `testRegex` | где искать тесты |
| `clearMocks` / `restoreMocks` | снижать протекание состояния между тестами |
| `collectCoverageFrom` | какие файлы учитывать в coverage |
| `coverageThreshold` | минимальный coverage gate в CI |

```ts
// jest.config.ts
import type { Config } from "jest";

const config: Config = {
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/src/test/setupTests.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "\\.(css|scss)$": "identity-obj-proxy",
    "\\.(svg|png|jpg)$": "<rootDir>/src/test/fileMock.ts",
  },
  clearMocks: true,
  restoreMocks: true,
  collectCoverageFrom: ["src/**/*.{ts,tsx}", "!src/**/*.d.ts"],
};

export default config;
```

Config читается группами: `testEnvironment` даёт DOM-среду, `setupFilesAfterEnv` подключает тестовые расширения и MSW, `moduleNameMapper` синхронизирует aliases и моки файлов, `clearMocks/restoreMocks` уменьшают протекание состояния.

```ts
// src/test/setupTests.ts
import "@testing-library/jest-dom";

import { server } from "./mswServer";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

| Нюанс | Риск |
| --- | --- |
| `jsdom` не настоящий браузер | layout, canvas, observers и часть browser APIs могут требовать polyfill/mock |
| aliases надо синхронизировать | `tsconfig`, bundler и Jest должны резолвить импорты одинаково |
| CSS/assets мокают отдельно | тесту не нужен реальный CSS bundle, но imports не должны ломаться |
| fake timers очищают после теста | таймеры легко протекают в соседние тесты |
| coverage не равен качеству | 90% coverage может проверять слабые assertions |
| Vite plugin pipeline не работает в Jest автоматически | Jest настраивают отдельно или выбирают Vitest |

#### Развернутый ответ

Jest запускает тесты и даёт базовые инструменты проверки: `test`, `describe`, `expect`, matchers, mocks, spies, fake timers, snapshots и coverage. В React-проектах Jest обычно отвечает за раннер и окружение, а React Testing Library - за работу с DOM и пользовательскими действиями.

В Vite-native проектах важно помнить, что Jest не использует Vite plugin pipeline автоматически. На 16 июля 2026 актуальные docs Jest 30.4 указывают, что Vite plugin system не поддерживается Jest напрямую. Поэтому такие проекты часто выбирают Vitest, а если остаются на Jest, настраивают отдельный transform: Babel, SWC или ts-jest, aliases через `moduleNameMapper`, test environment и моки CSS/assets/browser APIs.

Matchers выбирают по смыслу проверки. `toBe` использует `Object.is`, поэтому подходит для primitives и ссылочного равенства. `toEqual` сравнивает структуру объектов и массивов. Для DOM-проверок с Testing Library используют matchers из `@testing-library/jest-dom`: `toBeInTheDocument`, `toBeVisible`, `toHaveAccessibleName`, `toBeDisabled`.

Mocks, spies и fake timers нужны на контролируемых границах. `jest.fn()` заменяет функцию и фиксирует вызовы, `jest.spyOn()` наблюдает за существующей функцией, fake timers управляют `setTimeout`, debounce, throttle, intervals и retry delay. С async UI timers, promises и React updates требуют аккуратного `await` и очистки после теста.

Изоляция тестов критична. Если один тест меняет mocks, timers, DOM, localStorage или global state, это сбрасывают после теста. Иначе появляется order-dependent flakiness: тест проходит отдельно, но падает внутри suite.

> [!faq]+ Уточнения
> - Jest - раннер, assertions, mocks, timers и coverage; RTL проверяет DOM-поведение React.
> - В Vite-проекте Jest настраивают отдельно или выбирают Vitest.
> - `toBe` проверяет `Object.is`, `toEqual` сравнивает структуру.
> - Fake timers подходят для debounce/throttle/retry, но требуют очистки.
> - Snapshots полезны точечно, но огромные snapshots редко объясняют реальное поведение.

#### Пример

```ts
import { describe, expect, jest, test } from "@jest/globals";

function debounce(fn: () => void, delay: number) {
  let timer: ReturnType<typeof setTimeout>;

  return () => {
    clearTimeout(timer);
    timer = setTimeout(fn, delay);
  };
}

describe("debounce", () => {
  test("calls function after delay", () => {
    jest.useFakeTimers();

    const callback = jest.fn();
    const run = debounce(callback, 300);

    run();
    run();

    expect(callback).not.toHaveBeenCalled();

    jest.advanceTimersByTime(300);

    expect(callback).toHaveBeenCalledTimes(1);

    jest.useRealTimers();
  });
});
```

В реальном проекте real timers возвращают в `afterEach`, чтобы состояние fake timers не протекало в другие тесты.

#### Частые ошибки

- Мокать внутреннюю реализацию вместо внешней границы.
- Проверять, что вызвалась private function, а не результат поведения.
- Использовать `toBe` для сравнения объектов.
- Не очищать mocks/timers между тестами.
- Делать snapshots огромных компонентов вместо осмысленных assertions.
- Тестировать implementation details React-компонента вместо DOM-поведения.
- Считать coverage процентом качества тестов.
- Использовать Jest в Vite-проекте без понимания отдельной настройки transform/plugins.

#### Связанные темы

- [[Конспект для подготовки/Testing/Frontend testing]]
- [[Конспект для подготовки/Testing/React Testing Library]]
- [[Конспект для подготовки/Testing/MSW и моки API]]
- [[Конспект для подготовки/Testing/Async UI формы и auth]]
- [[Конспект для подготовки/Testing/Flaky tests]]
- [[Конспект для подготовки/DevOps/Frontend pipeline]]
- [[Конспект для подготовки/Tooling/Vite]]

#### Источники

- [Jest 30.4: Getting Started](https://jestjs.io/docs/getting-started)
- [Jest: Configuration](https://jestjs.io/docs/configuration)
- [Jest: Mock Functions](https://jestjs.io/docs/mock-functions)
- [Jest: Timer Mocks](https://jestjs.io/docs/timer-mocks)
- [Jest: Testing Asynchronous Code](https://jestjs.io/docs/asynchronous)
- [Jest: Expect](https://jestjs.io/docs/expect)
