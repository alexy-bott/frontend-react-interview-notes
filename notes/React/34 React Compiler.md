# React Compiler

<!-- NOTE-NAV-TOP:START -->
[← Серверные компоненты](<./33 Серверные компоненты.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [useEffectEvent →](<./35 useEffectEvent.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

React Compiler - это компилятор, который анализирует компоненты и хуки и автоматически добавляет мемоизацию там, где она безопасна. Его цель - уменьшить лишние ререндеры и повторные дорогие вычисления без ручного расставления `React.memo`, `useMemo` и `useCallback` в каждом месте.

React Compiler 1.0 стал стабильным в октябре 2025 года. Это не hook и не runtime API конкретной версии React, а build-time инструмент: он преобразует код во время сборки. По умолчанию Compiler генерирует код для React 19, но официально поддерживает React 17 и 18 через отдельный runtime-пакет и настройку `target`.

Ключевое условие: компоненты должны быть чистыми и следовать правилам React. Compiler не исправляет side effects в render, мутации props/state, неправильные зависимости эффектов или неустойчивую архитектуру состояния. Если код нарушает правила, компилятор либо не сможет его оптимизировать, либо lint/проверки должны подсветить проблему.

React Compiler переносит часть работы по memoization из рук разработчика в build step. Но он не отменяет понимание ререндеров, `key`, Context, colocated state, virtualization и профилирование. Он снижает необходимость в ручной мемоизации, но не делает тяжёлый UI бесплатным.

## Ключевая схема

| Было вручную | Что делает Compiler |
| --- | --- |
| `React.memo(Component)` | может пропустить лишний render дочерней части |
| `useMemo(expensiveFn, deps)` | может переиспользовать результат вычисления |
| `useCallback(fn, deps)` | может стабилизировать функцию там, где это безопасно |
| профилирование | всё равно нужно, чтобы понять настоящую проблему |
| правила чистоты | становятся ещё важнее |
| версия | React 19 по умолчанию; React 17/18 через `target` и compatibility runtime |

```text
component source
-> React Compiler на этапе сборки
-> анализ зависимостей и чистоты
-> автоматическая memoization
-> меньше лишней работы при update
```

## Развернутый ответ

Compiler анализирует исходный код до обычных трансформаций и пытается доказать, что компонент или hook можно безопасно оптимизировать. Если код соответствует правилам React, compiler может переиспользовать JSX, значения и функции между renders без ручных `memo`, `useMemo` и `useCallback`. Если доказать безопасность нельзя, конкретный компонент или hook пропускается, а остальной проект продолжает компилироваться.

Практическая граница: Compiler оптимизирует повторную работу, но не меняет архитектуру приложения. Если state поднят слишком высоко, Context value пересоздаётся на каждый render, список содержит тысячи DOM-узлов или render выполняет тяжёлую синхронную работу, Compiler поможет только частично. Для таких случаев всё ещё нужны colocated state, splitting context, virtualization, server state cache и профилирование.

При внедрении важны tooling-детали. Babel-плагин React Compiler должен идти первым в pipeline, чтобы анализировать исходный код до других трансформаций. Для Vite, Babel, React Router, React Native/Metro и других сборок настройка отличается. ESLint-интеграция через `eslint-plugin-react-hooks@latest` помогает увидеть, какие компоненты не оптимизируются и какие правила React нарушены.

**Чем Compiler отличается от `React.memo`?**

`React.memo` - ручная оптимизация конкретного компонента. Compiler анализирует код шире и может переиспользовать JSX, значения и функции без ручной обвязки. Это уменьшает количество шаблонного `useMemo/useCallback`, но не отменяет случаи, где нужна явная архитектурная оптимизация.

**Как подключить к React 18**

Для React 18 нужно установить `react-compiler-runtime` в обычные зависимости проекта и указать строковый target `'18'` в конфигурации Compiler. Сам `babel-plugin-react-compiler` остаётся dev dependency, потому что работает во время сборки.

```bash
npm install react-compiler-runtime@latest
npm install --save-dev babel-plugin-react-compiler@latest
```

```js
const ReactCompilerConfig = {
  target: "18",
};
```

Без runtime-пакета скомпилированный код React 18 не найдёт функции, которые в React 19 уже встроены в `react/compiler-runtime`. Версия `target` должна совпадать с основной версией React в проекте.

**Нужно ли после Compiler удалять весь `useMemo`?**

Нет. Сначала нужно включать компилятор постепенно, проверять поведение и производительность. Часть ручной мемоизации может стать лишней, но удалять её стоит после измерений и с учётом правил проекта.

**Что значит `"use memo"`?**

Это директива для annotation mode: можно компилировать только выбранные компоненты и хуки. Такой режим удобен для постепенного внедрения в большой кодовой базе.

**Что значит `"use no memo"`?**

Это директива, которой можно исключить конкретную функцию из компиляции, если есть причина не применять автоматическую memoization.

**Риски при внедрении**

Главные риски - нечистый render, мутации, нестабильные сторонние библиотеки и слишком резкое включение на весь проект. Поэтому внедряют через eslint rules, отдельные директории, annotation mode или feature flag/gating.

## Пример

До Compiler разработчик часто пишет ручную мемоизацию:

```tsx
const VisibleList = React.memo(function VisibleList({ items, onSelect }) {
  const visibleItems = useMemo(
    () => items.filter((item) => item.isVisible),
    [items],
  );

  const handleSelect = useCallback(
    (id: string) => onSelect(id),
    [onSelect],
  );

  return visibleItems.map((item) => (
    <button key={item.id} onClick={() => handleSelect(item.id)}>
      {item.title}
    </button>
  ));
});
```

С Compiler такой код часто можно писать проще, а оптимизацию доверять build step:

```tsx
function VisibleList({ items, onSelect }) {
  const visibleItems = items.filter((item) => item.isVisible);

  return visibleItems.map((item) => (
    <button key={item.id} onClick={() => onSelect(item.id)}>
      {item.title}
    </button>
  ));
}
```

Но если `items.filter` очень тяжёлый или список огромный, всё равно нужно смотреть профайлер, virtualization и структуру данных.

## Ключевые уточнения

- React Compiler является build-time оптимизатором, а не runtime API React 18 или React 19.
- React Compiler 1.0 - стабильный production-ready релиз; для React 19 используется встроенный runtime.
- Compiler требует чистого render и не исправляет side effects, мутации или неправильную state-модель.
- Для React 17/18 устанавливается `react-compiler-runtime`, а в конфигурации указывается `target: "17"` или `target: "18"`.
- Постепенное внедрение с lint и профилированием безопаснее одномоментного включения legacy-кода.
- Compiler сокращает ручную memoization, но не заменяет virtualization, стабильные keys и правильные границы state/Context.

## Связанные темы

- [Мемоизация](<./16 Мемоизация.md>)
- [Причины рендера](<./05 Причины рендера.md>)
- [useCallback](<./14 useCallback.md>)
- [Как работает React](<./02 Как работает React.md>)
- [React 18 и 19](<./32 React 18 и 19.md>)

## Источники

- [React docs: React Compiler](https://react.dev/learn/react-compiler/introduction)
- [React docs: React Compiler Installation](https://react.dev/learn/react-compiler/installation)
- [React docs: Compiler target](https://react.dev/reference/react-compiler/target)
- [React docs: Incremental Adoption](https://react.dev/learn/react-compiler/incremental-adoption)
- [React blog: React Compiler v1.0](https://react.dev/blog/2025/10/07/react-compiler-1)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Серверные компоненты](<./33 Серверные компоненты.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [useEffectEvent →](<./35 useEffectEvent.md>)
<!-- NOTE-NAV-BOTTOM:END -->
