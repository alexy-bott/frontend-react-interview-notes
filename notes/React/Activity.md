# Activity

<!-- NOTE-NAV-TOP:START -->
[← useEffectEvent](<./useEffectEvent.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Правила хуков →](<./Правила хуков.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

`<Activity>` - компонент React 19.2 для скрытия и восстановления части UI с сохранением внутреннего состояния. В режиме `hidden` React визуально прячет children, очищает их эффекты и обрабатывает их обновления с более низким приоритетом. Когда Activity снова становится `visible`, React возвращает UI с прежним state и заново запускает эффекты.

Это полезно для интерфейсов, где часть экрана скоро может понадобиться снова: вкладки, боковые панели, предыдущие маршруты, предварительно подготовленный экран. В отличие от обычного условного рендера `{isOpen && <Panel />}`, Activity не выбрасывает состояние скрытого поддерева.

Activity не просто “новый display none”. Он управляет lifecycle скрытого поддерева: эффекты скрытой части размонтируются, чтобы не оставлять активные подписки и таймеры, а render скрытого контента получает более низкий приоритет.

## Ключевая схема

| Состояние | Что происходит |
| --- | --- |
| `mode="visible"` | UI видим, эффекты активны, обновления обычного приоритета |
| `mode="hidden"` | UI скрыт, эффекты очищены, state сохраняется |
| снова `visible` | state восстановлен, эффекты созданы заново |
| conditional render | обычно размонтирует и теряет локальное состояние |

```text
visible
-> пользователь вводит данные
-> hidden: UI скрыт, effects cleanup, state сохранён
-> visible: UI возвращается с прежним state
```

## Развернутый ответ

`<Activity>` закрывает промежуток между двумя крайностями: полностью размонтировать поддерево или просто спрятать его CSS-ом. При размонтировании React теряет локальный state поддерева. При CSS-only скрытии эффекты продолжают жить: подписки, observers, timers и сетевые процессы могут работать как у видимого UI. Activity сохраняет state, но очищает эффекты hidden-части и снижает приоритет её обновлений.

Это полезно для интерфейсов с возвратом к уже подготовленному состоянию: tabs с формами, drawer, панели настроек, master-detail, предварительно подготовленный следующий экран. Пользователь получает быстрый возврат, а приложение не держит активными эффекты скрытого дерева.

Activity не заменяет архитектуру состояния. Если данные критичны для продукта, их хранят в state/store/query cache/form state, а не только в скрытом component state. Activity решает lifecycle и приоритеты UI-поддерева, но не является persistence-механизмом.

Нужно помнить, что hidden mode может повлиять на эффекты. Если компонент держит WebSocket, subscription или observer, при hidden он должен корректно cleanup-иться, а при visible - создаваться заново. Это ожидаемая семантика, а не баг.

## Пример

```tsx
import { Activity, useState } from "react";

function SettingsLayout() {
  const [tab, setTab] = useState<"profile" | "security">("profile");

  return (
    <>
      <button onClick={() => setTab("profile")}>Профиль</button>
      <button onClick={() => setTab("security")}>Безопасность</button>

      <Activity mode={tab === "profile" ? "visible" : "hidden"}>
        <ProfileForm />
      </Activity>

      <Activity mode={tab === "security" ? "visible" : "hidden"}>
        <SecurityForm />
      </Activity>
    </>
  );
}
```

Если пользователь ввёл данные в `ProfileForm`, переключился на другую вкладку и вернулся, локальный state формы сохранится.

## Ключевые уточнения

- `<Activity>` относится к React 19.2 и не входит в API React 18.
- Hidden-поддерево сохраняет state, но его Effects проходят cleanup и не продолжают работать как у видимого UI.
- Activity управляет lifecycle и приоритетом поддерева, поэтому не равен CSS-only скрытию.
- Критичное бизнес-состояние не должно зависеть только от времени жизни скрытого component state.
- Если сохранение state и предварительная подготовка не нужны, условный render остаётся проще.

## Связанные темы

- [React 18 и 19](<./React 18 и 19.md>)
- [Состояние в React](<./Состояние в React.md>)
- [Lifecycle](<./Lifecycle.md>)
- [useEffect vs useLayoutEffect](<./useEffect vs useLayoutEffect.md>)
- [Мемоизация](<./Мемоизация.md>)

## Источники

- [React docs: Activity](https://react.dev/reference/react/Activity)
- [React 19.2: Activity](https://react.dev/blog/2025/10/01/react-19-2)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← useEffectEvent](<./useEffectEvent.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Правила хуков →](<./Правила хуков.md>)
<!-- NOTE-NAV-BOTTOM:END -->
