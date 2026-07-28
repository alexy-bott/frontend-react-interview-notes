---
aliases:
  - структура URL
  - URL anatomy
  - absolute URL
  - relative URL
  - URLSearchParams
---

#### Быстрый ответ

URL — адрес ресурса и инструкция браузеру, как к нему обратиться. Он может содержать схему, хост, порт, путь, query string и fragment. Например, в `https://example.com:443/products?id=42#reviews` схема задаёт HTTPS, хост — сервер, путь — ресурс, query — параметры запроса, а fragment — позицию или состояние внутри документа.

Сервер получает путь и query, но не fragment после `#`. Origin страницы определяется схемой, хостом и эффективным портом; именно origin участвует в Same-Origin Policy и CORS. Относительный URL разрешается относительно base URL документа, поэтому строка `../avatar.png` не имеет полного смысла без контекста.

Во frontend URL собирают через `URL` и `URLSearchParams`, а не конкатенацией строк. Эти API корректно кодируют специальные символы и позволяют независимо менять path, query и fragment.

#### Части URL

```text
https://user@example.com:443/products/42?tab=reviews#latest
└scheme┘      └host────┘port└──path────┘└─query────┘└fragment
```

| Часть | Пример | Назначение |
| --- | --- | --- |
| Scheme | `https` | протокол или способ обработки адреса |
| Username/password | `user@` | устаревшие данные пользователя; для веб-авторизации не используют |
| Host | `example.com` | доменное имя или IP-адрес |
| Port | `443` | сетевой порт; часто выводится из scheme |
| Path | `/products/42` | иерархический путь к ресурсу |
| Query | `tab=reviews` | параметры после `?` |
| Fragment | `latest` | идентификатор после `#`, обрабатываемый клиентом |

Порт может отсутствовать в строке, но участвовать в адресе как порт по умолчанию: `80` для HTTP и `443` для HTTPS. URL API обычно нормализует такие детали, а также регистр доменного имени и некоторые последовательности в пути.

#### Origin и Same-Origin Policy

Origin, или источник, — сочетание scheme, host и эффективного port:

```text
https://example.com:443
```

| URL | Тот же origin, что `https://example.com` |
| --- | --- |
| `https://example.com/products` | да |
| `https://example.com:443/admin` | да, порт 443 подразумевается |
| `http://example.com` | нет, другая scheme |
| `https://api.example.com` | нет, другой host |
| `https://example.com:8443` | нет, другой port |

Path не входит в origin. Две страницы одного origin обычно могут взаимодействовать через DOM и хранилища согласно browser policy, даже если их пути различаются. Между разными origins браузер применяет границы Same-Origin Policy, а CORS может разрешить отдельные сетевые чтения, но не объединяет origins.

#### Query и fragment

Query string отправляется серверу как часть целевого URL:

```text
/products?category=books&sort=price
```

Порядок и повторение параметров могут иметь значение для API. `URLSearchParams` поддерживает несколько значений одного ключа через `append()` и `getAll()`.

Fragment не входит в HTTP-запрос. Для обычного документа браузер может прокрутить элемент с соответствующим `id`, а приложение может использовать fragment для клиентского состояния. Изменение только fragment является same-document navigation и не загружает новый HTML-документ.

Query и fragment видны в адресной строке и истории. Секреты, access tokens и персональные данные в URL могут попасть в логи, аналитику, скриншоты и referrer. Для чувствительных данных выбирают тело запроса или защищённое хранилище согласно протоколу приложения.

#### Абсолютные и относительные URL

Абсолютный URL содержит scheme и host:

```text
https://cdn.example.com/assets/logo.svg
```

Относительный URL разрешается относительно base URL:

```js
new URL("../avatar.png", "https://example.com/users/42/profile").href;
// https://example.com/users/avatar.png
```

Начальный `/` означает путь от корня origin, а `//cdn.example.com/file.js` наследует scheme текущего документа. Scheme-relative URL исторически использовали при миграции HTTP/HTTPS, но в современном приложении явный `https://` обычно понятнее и безопаснее.

Элемент `<base href="...">` меняет базу всех относительных ссылок документа. Он полезен редко и влияет сразу на ссылки, формы, scripts и styles, поэтому неожиданное значение `<base>` способно направить запросы не туда.

#### Кодирование

URL допускает ограниченный набор символов в каждой части. Пробелы, кириллица и служебные символы представляются через percent-encoding — последовательности вида `%20`.

```js
const url = new URL("https://example.com/search");

url.searchParams.set("query", "React hooks");
url.searchParams.set("redirect", "/profile?tab=security");

console.log(url.href);
// https://example.com/search?query=React+hooks&redirect=%2Fprofile%3Ftab%3Dsecurity
```

`encodeURIComponent()` кодирует отдельное значение компонента, а не полный URL. Применение его ко всей строке закодирует `:`, `/` и `?` и разрушит структуру. Повторное кодирование создаёт `%25` вместо уже существующего `%`.

Unicode-домены передаются в DNS в совместимом ASCII-представлении Punycode. Браузер может показывать пользователю Unicode-форму, но применяет защиту от доменов, визуально похожих на другой алфавит.

#### URL API во frontend

```js
function createProductsUrl(baseUrl, filters) {
  const url = new URL("/products", baseUrl);

  for (const [name, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") {
      url.searchParams.set(name, String(value));
    }
  }

  return url;
}

const url = createProductsUrl("https://api.example.com", {
  category: "books",
  page: 2,
});
```

Объект `URL` отдельно хранит `origin`, `pathname`, `searchParams` и `hash`, поэтому код не путает разделители и кодирование. Однако URL API не проверяет, разрешён ли адрес продуктом. Перед redirect по пользовательскому параметру нужно сверять допустимый origin или использовать список разрешённых путей, иначе возникает open redirect.

#### Ключевые уточнения

- Origin состоит из scheme, host и эффективного port; path не меняет origin.
- Query отправляется серверу, а fragment остаётся на стороне браузера и участвует в same-document navigation.
- Относительный URL получает смысл только после разрешения относительно base URL.
- `URLSearchParams` кодирует значения параметров, а `encodeURIComponent()` предназначен для отдельного компонента, не для полной URL-строки.
- Корректный синтаксис URL не делает redirect безопасным: пользовательский адрес всё равно проверяют по допустимым origins и путям.

#### Связанные темы

- [[Конспект для подготовки/Browser Internals/Что происходит после ввода URL]]
- [[Конспект для подготовки/Web Basics/HTTP запрос]]
- [[Конспект для подготовки/Web Basics/CORS]]
- [[Конспект для подготовки/Web Basics/HTTP vs HTTPS]]

#### Источники

- [URL Standard](https://url.spec.whatwg.org/)
- [MDN: What is a URL?](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_URL)
- [MDN: `URL`](https://developer.mozilla.org/en-US/docs/Web/API/URL)
- [MDN: `URLSearchParams`](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams)
