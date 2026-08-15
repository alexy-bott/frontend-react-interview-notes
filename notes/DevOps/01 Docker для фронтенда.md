# Docker для фронтенда

<!-- NOTE-NAV-TOP:START -->
[↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Многоэтапная сборка Dockerfile →](<./02 Многоэтапная сборка Dockerfile.md>)
<!-- NOTE-NAV-TOP:END -->

## Быстрый ответ

Docker упаковывает приложение и его runtime в image, из которого запускаются изолированные processes - containers. Dockerfile описывает сборку, registry хранит images, layers позволяют переиспользовать части сборки, а volumes и networks подключают внешние данные и другие services.

Для статической SPA Node.js обычно нужен только на build stage: результат `dist` отдаёт Nginx, CDN или static hosting. SSR-приложение выполняет server code на каждый request и требует Node.js либо другого поддерживаемого runtime. Docker делает среду воспроизводимее только при фиксированных dependencies, base images и одном проверенном artifact; сам контейнер не устраняет различия configuration.

## Ключевая схема

```text
source + Dockerfile + build context
-> docker build
-> immutable image layers
-> registry repository:tag / digest
-> docker run
-> container process + writable layer
```

| Сущность | Роль | Важная граница |
| --- | --- | --- |
| Image | шаблон filesystem/config | не является запущенным process |
| Container | экземпляр image | его writable layer временный |
| Tag | удобное изменяемое имя image | может указывать на другой digest |
| Digest | content-addressed identity | точно определяет image content |
| Build context | доступные build files | лишнее увеличивает transfer и риск утечки |
| Volume | данные вне writable layer | lifecycle отделён от container |
| Network | связь containers/services | published host port настраивается отдельно |

## Базовая модель

Image состоит из read-only layers и metadata, включая default command. При запуске Docker создаёт container с отдельным writable layer и process namespace. Удаление container удаляет его локальные изменения, если данные не вынесены во volume или внешний service.

Registry хранит image manifests/layers. Tag вроде `frontend:production` можно переназначить, поэтому для диагностики и rollback release связывают с immutable commit tag и digest. `latest` не означает «самая новая безопасная версия» и не является стратегией versioning.

Build context отправляется builder до выполнения `COPY`. `.dockerignore` исключает `node_modules`, `.git`, build output, coverage и локальные env files. Исключение уменьшает контекст, но уже попавший в layer секрет нельзя надёжно «удалить» следующей инструкцией: предыдущий layer сохраняется.

## Развернутый ответ

**SPA.** Build stage устанавливает dependencies и создаёт hashed HTML/CSS/JS/assets. Runtime image содержит только эти files и static server. Альтернатива Docker - загрузка тех же immutable assets в object storage/CDN; container не обязателен для статического frontend.

**SSR.** Runtime запускает server entry, читает server-only environment и обрабатывает requests. Nginx может завершать TLS и работать reverse proxy, но HTML rendering выполняет application runtime. Static export Next.js снова относится к SPA/static model.

**Configuration.** Один image можно запускать с разными runtime variables, если application действительно читает их во время runtime. Готовая SPA не начинает читать `docker run -e` автоматически: её JavaScript уже собран, поэтому нужен публичный config endpoint/file либо отдельный build.

**Ports.** `EXPOSE` документирует ожидаемый port image. Доступ с host создаётся параметром `-p host:container` или orchestration service. Container-to-container traffic использует network и service name, а не автоматически `localhost` host machine.

**Supply chain.** Base image выбирают по поддерживаемой runtime-версии, регулярно обновляют и сканируют. Pin по digest усиливает воспроизводимость, но требует процесса обновления security fixes; floating tag обновляется незаметно. Команда выбирает policy и фиксирует обновления dependency bot/review.

## Пример

```bash
docker build -t registry.example.com/frontend:abc123 .
docker run --rm -p 8080:80 registry.example.com/frontend:abc123
docker push registry.example.com/frontend:abc123
docker image inspect registry.example.com/frontend:abc123 --format "{{.Id}}"
```

```dockerignore
node_modules
dist
coverage
.git
.env
.env.*
!.env.example
```

Commit tag связывает image с source revision. Для production deployment registry/orchestrator дополнительно фиксирует digest, полученный после push.

## Ключевые уточнения

- Image описывает filesystem и запуск, container является process instance с отдельным временным writable layer.
- Tag можно переназначить, digest неизменно идентифицирует content; release metadata хранит оба.
- Docker обеспечивает одинаковый artifact, но runtime configuration и внешняя инфраструктура всё равно могут различаться.
- Static SPA и SSR требуют разных runtime: Nginx не исполняет server rendering приложения.
- Секрет исключают до попадания в build context/layer; удаление файла поздней инструкцией не очищает историю image.

## Связанные темы

- [Многоэтапная сборка Dockerfile](<./02 Многоэтапная сборка Dockerfile.md>)
- [Nginx и раздача статических файлов](<./03 Nginx и раздача статических файлов.md>)
- [Переменные окружения и секреты](<./04 Переменные окружения и секреты.md>)
- [CI-CD-пайплайн фронтенда](<./07 CI-CD-пайплайн фронтенда.md>)
- [Деплой, переменные окружения и Docker](<../Next.js/07 Деплой, переменные окружения и Docker.md>)

## Источники

- [Docker: Docker overview](https://docs.docker.com/get-started/docker-overview/)
- [Docker: Images](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)
- [Docker: Build context](https://docs.docker.com/build/concepts/context/)

---

<!-- NOTE-NAV-BOTTOM:START -->
[↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [Многоэтапная сборка Dockerfile →](<./02 Многоэтапная сборка Dockerfile.md>)
<!-- NOTE-NAV-BOTTOM:END -->
