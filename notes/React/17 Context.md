# Context

<!-- NOTE-NAV-TOP:START -->
[← Мемоизация](<./16 Мемоизация.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Управляемые и неуправляемые компоненты →](<./18 Управляемые и неуправляемые компоненты.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

React Context передаёт значение через поддерево без ручной передачи prop на каждом промежуточном уровне. Provider задаёт значение для своих потомков, а `useContext(SomeContext)` читает значение ближайшего соответствующего Provider выше в React tree. Это подходит для окружения целого поддерева: theme, locale, текущего пользователя, permissions или конфигурации design system.

Context не хранит состояние сам: значение обычно приходит из state, reducer или внешнего store. Когда Provider получает другое `value` по сравнению `Object.is`, React обновляет компоненты, которые читают этот context; `React.memo` не блокирует такое обновление. Поэтому Context разделяют по ответственности, а объект `value` стабилизируют только тогда, когда его содержимое не изменилось.

## Ключевая схема

| Часть | Роль |
| --- | --- |
| `createContext(defaultValue)` | создаёт объект context и статичное fallback-значение |
| `<SomeContext.Provider value={value}>` | задаёт значение для поддерева |
| `useContext(SomeContext)` | читает ближайший Provider выше вызывающего компонента |
| `Object.is(previousValue, nextValue)` | определяет, изменилось ли значение Provider |
| State или store | хранит и обновляет данные, переданные через Context |
| Custom Hook | скрывает проверку отсутствующего Provider и предоставляет предметный API |

## Базовая модель

Без Context общий параметр передаётся через props по всей цепочке компонентов. Это называют пробросом props (prop drilling). Сам prop drilling не является ошибкой: явная передача через один-два уровня часто проще и показывает зависимости компонента.

Context полезен, когда одно значение относится ко всему поддереву и промежуточные компоненты не должны знать о нём. `useContext` ищет Provider вверх от компонента, который вызывает Hook. Provider, возвращённый из этого же компонента ниже вызова `useContext`, на него не влияет.

Если Provider отсутствует, возвращается `defaultValue` из `createContext`. Оно является статичным fallback и не меняется после создания context. Для обязательного Provider удобно использовать `null` и custom Hook, который выдаёт понятную ошибку конфигурации.

## Развернутый ответ

### Как распространяется обновление

Когда компонент с Provider рендерится, React сравнивает прежнее и новое `value` через `Object.is`. Для primitive сравнивается значение, для объекта или функции - ссылка. Если значение отличается, React рендерит потребителей этого context, даже если они обёрнуты в `React.memo`.

Новый объект `{ theme, setTheme }` создаётся при каждом render. Если Provider может рендериться по причинам, не связанным с `theme`, `useMemo` сохраняет ссылку при прежнем содержимом. Однако при реальном изменении `theme` потребители всё равно должны обновиться. Мемоизация не превращает один context в selectors.

### Как выбирать границы Context

Если один объект содержит theme, текущего пользователя, фильтры и часто меняющийся progress, любое изменение объекта уведомляет всех его потребителей. Разделение на независимые contexts уменьшает область обновления и делает зависимости явными.

Context может обновляться часто, если Provider расположен близко к потребителям и render дешёвый. Правило «Context только для редко меняющихся данных» слишком жёсткое. Важны размер области, частота обновлений и стоимость затронутых компонентов.

### Context и state manager

Context отвечает за доставку одного текущего значения. Он не предоставляет selectors, нормализацию, middleware, историю actions, cache policy или самостоятельный контракт внешней подписки. Для небольшого общего client state сочетания reducer и Context может быть достаточно. Store становится полезен, когда нужны независимые подписки на фрагменты данных, развитая диагностика или обновления вне React tree.

Server state имеет другой жизненный цикл: cache, stale data, retry, deduplication и invalidation. Передача query client через Provider может использовать Context внутри библиотеки, но сами серверные данные управляются query cache, а не Context как таковым.

## Пример

Provider хранит state, Context передаёт его, а custom Hook задаёт безопасный API чтения.

```tsx
import {
  createContext,
  type ReactNode,
  useContext,
  useMemo,
  useState,
} from "react";

type Theme = "light" | "dark";
type ThemeContextValue = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");
  const value = useMemo(() => ({ theme, setTheme }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (context === null) {
    throw new Error("useTheme must be used within ThemeProvider");
  }

  return context;
}
```

`setTheme` имеет стабильную идентичность, поэтому dependency `theme` достаточен для объекта `value`. Если Provider не найден, Hook отличает ошибку конфигурации от обычного значения theme.

## Где применяется во frontend

| Ситуация | Подходит ли Context | Обоснование |
| --- | --- | --- |
| Theme или locale для поддерева | да | одно окружение читают удалённые потомки |
| Auth user и permissions | часто | есть единый владелец сессии и много потребителей |
| Состояние одного dropdown | обычно нет | локальный state проще и ограничивает область render |
| Фильтр большой таблицы на каждый ввод | зависит от границы | локальный Provider допустим, глобальный context затронет лишних потребителей |
| Cache данных backend | не самостоятельно | нужны retry, invalidation и stale policy query-библиотеки |
| Конфигурация component library | да | Provider задаёт единые настройки поддерева |

## Ключевые уточнения

- Context передаёт значение, а state, reducer или store хранит и изменяет его.
- Provider выбирается по ближайшему совпадающему Context выше потребителя в React tree.
- Изменение определяется через `Object.is`; выражение «новая ссылка» относится к объектам и функциям.
- `React.memo` не блокирует обновление context, который компонент читает напрямую.
- Разделение contexts полезно по независимым причинам изменения, а не ради количества файлов.

## Связанные темы

- [Состояние в React](<./06 Состояние в React.md>)
- [Причины рендера](<./05 Причины рендера.md>)
- [Redux и Flux](<./23 Redux и Flux.md>)
- [Серверное состояние и React Query](<./07 Серверное состояние и React Query.md>)
- [Zustand](<./26 Zustand.md>)

## Источники

- [React 18: Passing Data Deeply with Context](https://18.react.dev/learn/passing-data-deeply-with-context)
- [React 18: useContext](https://18.react.dev/reference/react/useContext)
- [React 18: Scaling Up with Reducer and Context](https://18.react.dev/learn/scaling-up-with-reducer-and-context)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Мемоизация](<./16 Мемоизация.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Управляемые и неуправляемые компоненты →](<./18 Управляемые и неуправляемые компоненты.md>)
<!-- NOTE-NAV-BOTTOM:END -->
