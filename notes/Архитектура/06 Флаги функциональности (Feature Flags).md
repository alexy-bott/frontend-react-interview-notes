# Флаги функциональности (Feature Flags)

<!-- NOTE-NAV-TOP:START -->
[← Обработка ошибок и наблюдаемость](<./05 Обработка ошибок и наблюдаемость.md>) · [↑ Архитектура](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Микрофронтенды →](<./07 Микрофронтенды.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Feature flag отделяет deployment кода от release поведения: один artifact содержит новую ветку, но flag service включает её для выбранного environment, сегмента или процента пользователей. Это позволяет постепенно проверить feature, быстро остановить проблемный путь и проводить controlled experiment без нового build.

Flag добавляет временную runtime-конфигурацию и две ветки поведения. Для него определяют owner, цель, evaluation boundary, безопасный default, метрики, test matrix и дату удаления. Клиентский flag управляет UI, но не даёт permission и не защищает API; backend независимо проверяет authorization.

## Ключевая схема

```text
flag definition + targeting rules
-> evaluation for context
-> stable variant
-> code path
-> exposure + product/technical metrics
-> full rollout or rollback
-> remove flag and dead branch
```

| Тип | Назначение | Обычный срок жизни |
| --- | --- | --- |
| Release flag | постепенный выпуск новой реализации | короткий |
| Experiment flag | сравнение вариантов с устойчивым распределением | до завершения анализа |
| Operational flag | kill switch дорогой/рискованной функции | может быть долгим |
| Configuration | параметр поведения без build | долгий, но с typed contract |
| Entitlement | вариант продукта по тарифу/аккаунту | долгий; не заменяет server permission |

## Базовая модель

Evaluation принимает flag key и context: environment, account, user, app version и другие разрешённые attributes. Результат должен оставаться стабильным для одного участника эксперимента, иначе пользователь переключается между вариантами и данные теряют смысл.

Server evaluation скрывает rules и позволяет до render выбрать HTML/API behavior. Client evaluation быстрее меняет интерактивный UI, но rules/value доступны browser и приходят не мгновенно. Часто server формирует initial snapshot, а frontend использует его как согласованную конфигурацию сессии.

Недоступность flag service является отдельным failure mode. Для checkout kill switch default может отключать рискованную интеграцию; для базовой навигации fail-closed способен сделать приложение недоступным. Default выбирают по impact конкретного флага, а не один раз для всей системы.

## Развернутый ответ

**Rollout.** Процент включения увеличивают по этапам и сравнивают error rate, latency, conversion и support signals между variants. Rollback flag возвращает старую ветку, только если она всё ещё совместима с текущими data/API migrations.

**Experiment.** Событие exposure отправляют в момент, когда пользователь действительно получил вариант, а не при каждом чтении flag. Assignment и analysis используют один stable identifier и исключают пересечение несовместимых experiments.

**SSR/hydration.** Server и первый client render используют один snapshot. Повторная evaluation с другим context создаёт hydration mismatch или flicker. Обновление flags после hydration имеет явную policy: применить сразу, со следующей navigation или с новой session.

**Security.** Bundle может содержать выключенную client feature, а значение flag можно подменить в DevTools. Sensitive data и операции защищаются backend authorization. Даже server-side entitlement не заменяет permission check конкретного request.

**Bundle.** Условный JSX со статическим import обычно оставляет обе реализации в bundle. Если новая тяжёлая feature должна загружаться только после включения, используют dynamic import и проектируют loading/error path.

**Flag debt.** После полного rollout удаляют definition, старую ветку, tests и telemetry. Забытый flag увеличивает число combinations и не позволяет понять, какой код реально достижим. Owner и expiry автоматизируют через dashboard/CI reminders, но удаление требует ручной проверки dependencies.

## Пример

```tsx
function CheckoutRoute() {
  const variant = useFeatureFlag("checkout-redesign");

  if (variant.status === "loading") {
    return <CheckoutSkeleton />;
  }

  if (variant.value === "new") {
    return <NewCheckout />;
  }

  return <LegacyCheckout />;
}
```

Для SSR `variant` гидратируется из server snapshot. После завершения rollout `LegacyCheckout`, условие и flag удаляются одной задачей; наличие fallback не является постоянным архитектурным требованием.

## Ключевые уточнения

- Deploy доставляет artifact, release включает поведение; feature flag связывает эти события, но не заменяет deployment rollback.
- Flag и permission отвечают на разные вопросы: «какой вариант показать?» и «разрешено ли действие?».
- Safe default зависит от impact и доступности fallback; универсального `false` для всех flags нет.
- Stable assignment и exposure event обязательны для корректного experiment, но лишни простому operational switch.
- Полный rollout не завершён, пока flag и мёртвая ветка не удалены.

## Связанные темы

- [Архитектура фронтенда](<./01 Архитектура фронтенда.md>)
- [Обработка ошибок и наблюдаемость](<./05 Обработка ошибок и наблюдаемость.md>)
- [Размер бандла и стратегия загрузки](<../Производительность/03 Размер бандла и стратегия загрузки.md>)
- [Стратегия тестирования фронтенда](<../Тестирование/02 Стратегия тестирования фронтенда.md>)
- [Гидратация (Hydration)](<../React/28 Гидратация (Hydration).md>)

## Источники

- [Martin Fowler: Feature Toggles](https://martinfowler.com/articles/feature-toggles.html)
- [OpenFeature: Concepts](https://openfeature.dev/docs/reference/concepts/)
- [LaunchDarkly: Feature flags](https://docs.launchdarkly.com/home/flags)

---

<!-- NOTE-NAV-BOTTOM:START -->
[← Обработка ошибок и наблюдаемость](<./05 Обработка ошибок и наблюдаемость.md>) · [↑ Архитектура](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Микрофронтенды →](<./07 Микрофронтенды.md>)
<!-- NOTE-NAV-BOTTOM:END -->
