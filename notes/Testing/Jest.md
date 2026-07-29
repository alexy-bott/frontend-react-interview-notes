# Jest

<!-- NOTE-NAV-TOP:START -->
[← Стратегия тестирования frontend](<./Стратегия тестирования frontend.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [React Testing Library →](<./React Testing Library.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Jest — test runner с assertions, test doubles, fake timers, snapshots и coverage для JavaScript/TypeScript. Он управляет discovery, isolation и lifecycle tests, но не является реальным browser и не определяет полезность сценария. Для React Jest обычно предоставляет runner/jsdom, React Testing Library — DOM interaction, MSW — network boundary.

Jest проверяет код в тестовой среде, а не в реальном браузерном приложении. Поэтому всё подряд mocks-ами не подменяют. Тест проверяет поведение и контракт, а mocks использует только на границах: timers, network, storage, analytics, router, browser APIs. Для React UI Jest сочетают с Testing Library, а API-моки часто делают через MSW.

## Ключевая схема

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

## Практическая настройка

Практическая настройка Jest включает три зоны: где тесты запускаются, как проектный код преобразуется перед тестом и как тесты изолируются друг от друга. Для React это чаще всего `jsdom`, `setupFilesAfterEnv`, aliases, моки CSS/assets, transform для TypeScript/JSX и очистка mocks между тестами.

| Что настраивают | Зачем |
| --- | --- |
| `testEnvironment` | `node` для логики, `jsdom` для React/DOM |
| `setupFilesAfterEnv` | подключить jest-dom, MSW lifecycle, общие matchers |
| `transform` | выполнить TypeScript/JSX/ESM transform через Babel/SWC/ts-jest |
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

## Базовая модель

Jest запускает тесты и даёт базовые инструменты проверки: `test`, `describe`, `expect`, matchers, mocks, spies, fake timers, snapshots и coverage. В React-проектах Jest обычно отвечает за раннер и окружение, а React Testing Library - за работу с DOM и пользовательскими действиями.

`testEnvironment: "node"` подходит pure/server logic, `jsdom` эмулирует DOM APIs для component tests. jsdom не выполняет layout/paint как browser, поэтому размеры, CSS, observers, canvas и navigation требуют отдельной реализации, mock или browser test.

## Развернутый ответ

В Vite-native проекте Jest не использует Vite plugin pipeline автоматически. Поэтому либо выбирают Vitest для общей transform/config model, либо отдельно настраивают Babel/SWC/ts-jest, ESM mode, aliases и asset mocks. Transpile TypeScript не всегда выполняет полный typecheck; `tsc --noEmit` остаётся отдельным CI gate.

Matchers выбирают по смыслу проверки. `toBe` использует `Object.is`, поэтому подходит для primitives и ссылочного равенства. `toEqual` сравнивает структуру объектов и массивов. Для DOM-проверок с Testing Library используют matchers из `@testing-library/jest-dom`: `toBeInTheDocument`, `toBeVisible`, `toHaveAccessibleName`, `toBeDisabled`.

Mocks, spies и fake timers нужны на контролируемых границах. `jest.fn()` заменяет функцию и фиксирует вызовы, `jest.spyOn()` наблюдает за существующей функцией, fake timers управляют `setTimeout`, debounce, throttle, intervals и retry delay. С async UI timers, promises и React updates требуют аккуратного `await` и очистки после теста.

Изоляция тестов критична. Если один тест меняет mocks, timers, DOM, localStorage или global state, это сбрасывают после теста. Иначе появляется order-dependent flakiness: тест проходит отдельно, но падает внутри suite.

## Пример

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
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  test("calls function after delay", () => {
    const callback = jest.fn();
    const run = debounce(callback, 300);

    run();
    run();

    expect(callback).not.toHaveBeenCalled();

    jest.advanceTimersByTime(300);

    expect(callback).toHaveBeenCalledTimes(1);

  });
});
```

`afterEach` выполняется и при падении assertion. Pending timers flush-ятся до возврата real timers, чтобы callbacks third-party code не потерялись. Для `userEvent` с fake timers передают `userEvent.setup({ advanceTimers: jest.advanceTimersByTime })`.

## Ключевые уточнения

- Jest управляет test execution; jsdom не заменяет проверку layout и browser integration.
- `toBe` использует `Object.is`, `toEqual` сравнивает структуру, специализированный matcher лучше объясняет contract.
- `clearMocks` очищает call history, `resetMocks` также сбрасывает implementation, `restoreMocks` возвращает spied/replaced property — policy выбирают осознанно.
- Fake timers восстанавливают в `afterEach`; с `userEvent` синхронизируют advance timers.
- Transform TypeScript/JSX не гарантирует typecheck, если выбранный transformer только transpiles.
- Snapshot полезен для небольшого стабильного output; важные behaviors подтверждают явными assertions.
- Coverage threshold предотвращает резкое падение coverage, но не измеряет качество scenarios.

## Связанные темы

- [Frontend testing](<./Frontend testing.md>)
- [React Testing Library](<./React Testing Library.md>)
- [MSW и моки API](<./MSW и моки API.md>)
- [Async UI формы и auth](<./Async UI формы и auth.md>)
- [Flaky tests](<./Flaky tests.md>)
- [Frontend pipeline](<../DevOps/Frontend pipeline.md>)
- [Vite](<../Tooling/Vite.md>)

## Источники

- [Jest 30.4: Getting Started](https://jestjs.io/docs/getting-started)
- [Jest: Configuration](https://jestjs.io/docs/configuration)
- [Jest: Mock Functions](https://jestjs.io/docs/mock-functions)
- [Jest: Timer Mocks](https://jestjs.io/docs/timer-mocks)
- [Jest: Testing Asynchronous Code](https://jestjs.io/docs/asynchronous)
- [Jest: Expect](https://jestjs.io/docs/expect)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Стратегия тестирования frontend](<./Стратегия тестирования frontend.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [React Testing Library →](<./React Testing Library.md>)
<!-- NOTE-NAV-BOTTOM:END -->
