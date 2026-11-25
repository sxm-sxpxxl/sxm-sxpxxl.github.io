# persona — план 1: основа

> **Для исполнителей-агентов:** ОБЯЗАТЕЛЬНЫЙ ПОД-НАВЫК: superpowers:subagent-driven-development (рекомендуется) или
> superpowers:executing-plans — задачу за задачей. Шаги отмечаются чекбоксами (`- [ ]`).

**Цель:** сайт из пяти вкладок со всеми текстами и раскладками на всех экранах, который переключает вкладки без
перезагрузки и собирается и тестируется в CI — пока без звука, без живых эффектов, без отправки формы и без публикации.

**Архитектура:** Zola собирает пять страниц из `content/` и шаблонов `templates/`, данные берёт из файлов в `data/`,
стили — Sass в `sass/`. Скрипты — ES-модули в `static/js/`: `app.js` поднимает роутер, роутер подменяет `#page`
и вызывает `mount` / `unmount` модуля вкладки. Логика без DOM — в чистых функциях с тестами `node --test`,
вёрстка проверяется тестами по собранным страницам.

**Стек:** Zola 0.23.6 (Tera, встроенный Sass), ES-модули без сборщика, Node 24 (`node --test`), GitHub Actions, ffmpeg 9.1.

**Спека:** `docs/superpowers/specs/2026-11-25-persona-final-design.md`. Образец — `docs/prototype/index.html`: в задачах
на него ссылаются по меткам разделов, которые находятся поиском (`// ---------- contact form`,
`/* ---------- phone stage`, `<!-- SXM TOOLS -->` и т. п.). Переносить из образца только выбранные варианты —
атрибуты выбора перечислены в спеке, раздел «Переносится из прототипа».

## Глобальные ограничения

- Тексты сайта — дословно из спеки, английские, американское написание; типографские знаки как в спеке
  («Salva’s», «can’t», «Kevin MacLeod’s», “Tower of Hanoi”).
- Адреса: `/`, `/about/`, `/etudes/`, `/metta-corpse/`, `/contact/`, `/contact/?product=ui-line-chart` (`ui-factory`),
  якоря `#ki-<id>-<slug>` и `#faq-<id>-<slug>`.
- Шапка: `ABOUT · SXM TOOLS · ÉTUDES · METTA CORPSE · CONTACT`; подписи разделов `NN / раздел`: 01 About,
  02 SXM Tools, 03 Études, 04 Metta Corpse, 05 Contact.
- Цвета: фон `#131417`, текст `#EEF0F5`, приглушённый `#969BA8`, линии `#25272e`, бирюзовый `#28D5E4`, оранжевый
  `#FB7D22`, «готово» `#66D87F`.
- Шрифты: Geologica и JetBrains Mono (оболочка); Poiret One + Port Lligat Sans (SXM Tools); Reenie Beanie + Shantell
  Sans (Études); Long Cang + Lacquer (Metta Corpse). Файлы на самом сайте, рядом их `OFL.txt`, без своей обрезки.
- Без JS сайт читается: вкладки — обычные ссылки `<a href>`, первый продукт раскрыт в разметке, все записи Known
  issues и FAQ есть в HTML.
- Модули без общих глобальных имён: ни одной переменной на `window`.
- Никаких npm-зависимостей; `package.json` только для скриптов тестов.
- «Уменьшить движение»: всё, что в этом плане движется (смена страницы, полоса меню телефона, курсор шапки,
  свёртка в авторах), при `prefers-reduced-motion: reduce` переключается сразу; остаются только переходы прозрачности.
- Выделение: интерфейс не выделяется, содержание выделяется (списки — спека, «Выделение текста»); картинки не
  перетаскиваются.
- Ссылка или кнопка с пустым адресом в данных не выводится вовсе.
- CI только собирает и тестирует, публикации нет.
- Коммиты: `тип: строчное предложение о получившемся состоянии`, без тела, с трейлером
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Предварительно (делает или разрешает автор)

- Zola 0.23.6 и ffmpeg 9.1 уже стоят (winget).
- Разрешить скачивание: в задаче 2 — файлы шрифтов с fonts.googleapis.com / fonts.gstatic.com и `OFL.txt` с
  github.com/google/fonts; в задаче 7 — шесть гифок Études с user-images.githubusercontent.com.
- Дать адреса: Docs UI Line Chart; GitHub и OpenUPM UI Factory; LinkedIn; профиль GitHub; репозитории шести этюдов.
  Пока адреса нет, в данных пустая строка, и ссылка не выводится.
- Разрешить пуш ветки, чтобы прогнать CI (задача 1).

## На что смотреть при проверке

1. Быстрые клики по вкладкам, пока страница ещё грузится: побеждает последний клик, на экране не остаётся смеси
   двух страниц и двух смонтированных модулей. Тест — задача 4 («последний переход побеждает»).
2. «Назад» и «вперёд» после нескольких переходов: содержимое, активная вкладка, заголовок окна и смонтированный
   модуль совпадают с адресом. Тест — задача 4 (`go(..., { push: false })`) и проверка в браузере.
3. Прямой заход на `/contact/?product=ui-factory#ki-3-no-support-for-unity-2021`: выбран UI Factory, запись раскрыта
   и прокручена в вид, в том числе после перехода роутером с другой вкладки. Тест — задача 11 (`parseDeepLink`,
   `productFromQuery`).
4. `?product=foo` и якорь на несуществующую запись: открывается UI Line Chart, ничего не раскрыто, ошибок нет.
   Тесты — задачи 10 и 11.
5. Файл больше 5 МиБ или не png/jpg/txt, пустое сообщение: инлайн-ошибка, отправки нет; после исправления ошибка
   уходит. Тест — задача 10 (`validateFile`, `canSend`).

## Структура файлов

```
config.toml                       адрес, заголовок, Sass, состояния проектов в шапке (extra.projects)
content/_index.md                 SXM Tools на «/»
content/{about,etudes,metta-corpse,contact}.md
data/products.toml                продукты: тексты, плашки, ссылки, кадры (план 5 заполняет версии, цену, стор)
data/etudes.toml                  этюды: текущий и законченные
data/credits.toml                 авторы для блока «01 / credits»
data/known-issues.json            записи Known issues (план 5 производит этот файл)
data/faq.json                     записи FAQ (план 5 производит этот файл)
templates/base.html               оболочка: head, шапка, #page, скрипты
templates/macros.html             label(), badge(), linkOrNothing()
templates/{sxm,about,etudes,metta,contact}.html
templates/partials/{product,credits,contact-form,known-issues,faq}.html
sass/main.scss + _tokens _fonts _shell _phone _sxm _etudes _metta _about _contact
static/fonts/<family>/*.woff2 + OFL.txt
static/img/{sxm,metta,about}/…  static/video/etudes/…
static/js/app.js router.js pages.js behaviour.js copy.js phone-menu.js carousel.js
static/js/pages/{sxm,about,etudes,metta,contact}.js
static/js/contact/{form-state,issues,send}.js
tools/fetch-fonts.mjs tools/make-etude-videos.mjs
tests/helpers/site.mjs tests/*.test.mjs
package.json .github/workflows/ci.yml .gitignore
```

---

### Задача 1: каркас Zola, тестовый стенд и CI

**Файлы:**
- Создать: `config.toml`, `content/_index.md`, `content/about.md`, `content/etudes.md`, `content/metta-corpse.md`,
  `content/contact.md`, `templates/base.html`, `templates/{sxm,about,etudes,metta,contact}.html`, `package.json`,
  `tests/helpers/site.mjs`, `tests/pages.test.mjs`, `.github/workflows/ci.yml`
- Изменить: `.gitignore` (добавить `public/`, `.test-public/`, `tools/src/`)

**Интерфейсы:**
- Производит: в шапке каждой страницы `[extra] tab = "sxm" | "about" | "etudes" | "metta" | "contact"` и `nn = "02"`
  (номер раздела); `templates/base.html` с переменной `doc` (страница или раздел), блоком `content` и
  `<body data-tab="…">`; сборка для тестов в
  `.test-public/` (`npm run pretest`); `tests/helpers/site.mjs`:
  `readPage(path: string): string` (путь вида `/` или `/about/`), `readOut(rel: string): string` (любой файл сборки),
  `textOf(html: string): string` (каждый тег заменяется пробелом, сущности раскрыты — `&amp; &lt; &gt; &quot; &#x27;`
  и числовые, пробелы схлопнуты),
  `buildWith(patch: Record<string, string>): string` (копия сайта во временной папке с подменой файлов, сборка,
  возвращает папку вывода).

- [ ] **Шаг 1: тест страниц**

```js
// tests/pages.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readPage } from './helpers/site.mjs';

const PAGES = {
  '/': ['sxm', 'SXM Tools'], '/about/': ['about', 'About'], '/etudes/': ['etudes', 'Études'],
  '/metta-corpse/': ['metta', 'Metta Corpse'], '/contact/': ['contact', 'Contact'],
};
for (const [path, [tab, title]] of Object.entries(PAGES)) {
  test(`${path} is the ${tab} tab`, () => {
    const html = readPage(path);
    assert.match(html, new RegExp(`<body[^>]*data-tab="${tab}"`));
    assert.match(html, new RegExp(`<title>persona=sxm-sxpxxl / ${title.toLowerCase()}</title>`));
  });
}
```

- [ ] **Шаг 2: запустить и убедиться, что падает**

`package.json`: `{ "private": true, "type": "module", "scripts": { "pretest": "zola build --output-dir .test-public --force", "test": "node --test \"tests/**/*.test.mjs\"" } }`.
Run: `npm test` → Expected: FAIL (`pretest`: нет `config.toml`).

- [ ] **Шаг 3: каркас**

`config.toml`: `base_url = "https://sxm-sxpxxl.github.io"`, `title = "sxm-sxpxxl"`, `compile_sass = true`,
`build_search_index = false`, `default_language = "en"`. Страницы: `content/_index.md` (`template = "sxm.html"`,
`title = "SXM Tools"`), остальные — `content/<slug>.md` с `template = "<tab>.html"`. В `base.html` в начале
`{% if page is defined %}{% set doc = page %}{% else %}{% set doc = section %}{% endif %}`: у главной есть только
`section`, у остальных страниц только `page` (`default(value=section.title)` не годится — на страницах переменной
`section` нет, и сборка падает; проверено на Zola 0.23.6). Заголовок окна —
`<title>persona=sxm-sxpxxl / {{ doc.title | lower }}</title>` (выходит `… / sxm tools`, `… / études`), у тела —
`<body data-tab="{{ doc.extra.tab }}">`. `readPage` читает `.test-public/<path>/index.html`; `buildWith` копирует `config.toml content data templates sass static` во
временную папку, пишет поверх файлы из `patch`, вызывает `zola build --output-dir <tmp>/out --force`
(бинарник — `process.env.ZOLA ?? 'zola'`).

- [ ] **Шаг 4: тесты проходят**

Run: `npm test` → Expected: PASS, 5 тестов.

- [ ] **Шаг 5: CI без публикации**

`.github/workflows/ci.yml` — на `push` и `pull_request`, `ubuntu-latest`: `actions/checkout@v4`; установка Zola
`curl -sL https://github.com/getzola/zola/releases/download/v0.23.6/zola-v0.23.6-x86_64-unknown-linux-gnu.tar.gz | sudo tar xz -C /usr/local/bin`;
`actions/setup-node@v4` с `node-version: 24`; `zola --version` (ожидается `zola 0.23.6`); `zola check`; `npm test`.
Шагов публикации нет.

- [ ] **Шаг 6: коммит и прогон CI**

```bash
git add config.toml content templates package.json tests .github .gitignore
git commit -m "feat: the site is a zola project of five tabs that builds and tests in ci"
```
Спросить автора разрешения на пуш; после пуша в Actions зелёный прогон `ci`.

---

### Задача 2: шрифты и цветовые токены

**Файлы:**
- Создать: `tools/fetch-fonts.mjs`, `static/fonts/<family>/*.woff2`, `static/fonts/<family>/OFL.txt`,
  `sass/main.scss`, `sass/_tokens.scss`, `sass/_fonts.scss`, `tests/fonts.test.mjs`
- Изменить: `templates/base.html` (подключить `main.css`)

**Интерфейсы:**
- Производит: CSS-переменные на `:root` — `--ground --ink --mute --line --cy --or --ok` (значения из «Глобальных
  ограничений»), `--f-shell: Geologica, system-ui, sans-serif`, `--f-mono: "JetBrains Mono", monospace`,
  `--f-sxm-d: "Poiret One"`, `--f-sxm-t: "Port Lligat Sans"`, `--f-et-d: "Reenie Beanie"`, `--f-et-t: "Shantell Sans"`,
  `--f-mc-d: "Long Cang"`, `--f-mc-t: "Lacquer"`; коэффициенты размеров пар на корне страницы вкладки — `--dk`, `--tk`
  (`body[data-tab="sxm"]` и т. д.).

- [ ] **Шаг 1: тест**

```js
// tests/fonts.test.mjs — для каждой из восьми семей
const FAMILIES = ['Geologica', 'JetBrains Mono', 'Poiret One', 'Port Lligat Sans', 'Reenie Beanie', 'Shantell Sans', 'Long Cang', 'Lacquer'];
test('every family is self-hosted with its licence', () => {
  const css = readOut('main.css');
  for (const f of FAMILIES) {
    const slug = f.toLowerCase().replace(/ /g, '-');
    assert.ok(existsSync(`static/fonts/${slug}/OFL.txt`), `${f}: OFL.txt`);
    assert.ok(readdirSync(`static/fonts/${slug}`).some(n => n.endsWith('.woff2')), `${f}: woff2`);
    assert.match(css, new RegExp(`@font-face\\{[^}]*font-family:\\s*"?${f}"?`), `${f}: @font-face`);
  }
  for (const c of ['#131417', '#eef0f5', '#969ba8', '#25272e', '#28d5e4', '#fb7d22', '#66d87f']) assert.ok(css.toLowerCase().includes(c), c);
});
```

- [ ] **Шаг 2: убедиться, что падает** — Run: `npm test` → FAIL (`main.css` нет).

- [ ] **Шаг 3: скачать шрифты (с разрешения автора)**

`tools/fetch-fonts.mjs`: запрашивает CSS у `https://fonts.googleapis.com/css2?family=…&display=swap` с заголовком
`User-Agent` современного Chrome (иначе отдаёт TTF), оставляет только `@font-face` с подмножествами `latin` и
`latin-ext` (по комментариям `/* latin */`, `/* latin-ext */`), скачивает их `woff2` как есть в
`static/fonts/<slug>/`, пишет `sass/_fonts.scss` с локальными `url()`. Веса — как запрашивает образец: Geologica
`wght@300;400;500;600;700;800;900`, JetBrains Mono `wght@400;500;700;800` (ссылка в начале `docs/prototype/index.html`),
у пар — по `fam()` и `STRONG` в разделе `// ---------- v81: set pickers`. `OFL.txt` — из
`https://raw.githubusercontent.com/google/fonts/main/ofl/<familyname>/OFL.txt`.

- [ ] **Шаг 4: токены и коэффициенты**

`_tokens.scss` — переменные из «Интерфейсов». `--dk` и `--tk` для SXM Tools, Études и Metta Corpse снять с образца:
открыть `docs/prototype/index.html` через `python -m http.server`, дождаться шрифтов и прочитать
`getComputedStyle(document.getElementById('p-<tab>')).getPropertyValue('--dk' | '--tk')` (их задаёт
`page.style.setProperty` в разделе `// ---------- v81: set pickers`); записать числа как есть.

- [ ] **Шаг 5: тесты проходят** — Run: `npm test` → PASS.

- [ ] **Шаг 6: коммит**

```bash
git add tools/fetch-fonts.mjs static/fonts sass templates/base.html tests/fonts.test.mjs
git commit -m "feat: the site carries its own eight ofl fonts and colour tokens"
```

---

### Задача 3: оболочка — шапка, подписи, кнопки, общие правила

**Файлы:**
- Создать: `templates/macros.html`, `sass/_shell.scss`, `static/js/behaviour.js`, `static/js/app.js`, `tests/shell.test.mjs`,
  `tests/behaviour.test.mjs`
- Изменить: `templates/base.html`, `config.toml` (`[extra] projects`)

**Интерфейсы:**
- Производит: `macros::label(nn, name)` → `<div class="lbl"><b>{{ nn }}</b> / {{ name }}</div>`;
  `macros::badge(k, v, accent=false)`; `macros::link_or_nothing(url, text, class)` — пустой `url` ничего не выводит;
  разметка шапки (ниже); `behaviour.js`: `export function installDragGuard(doc: Document): () => void` (возвращает
  отписку); `app.js` — точка входа `<script type="module" src="/js/app.js">`.
- Разметка шапки (классы — как в образце, раздел `/* ---------- boot sequence` и выше, чтобы стили переносились
  без переименований): `<header class="bar">` → `<span class="mark"><span class="mk-code"><span class="a">persona</span><span class="b">=</span><span>sxm-sxpxxl</span><span class="k"></span></span></span>`
  и `<nav class="tabs">` с `<a class="tab" data-p="about" href="/about/">About</a>`, `<span class="tproj">` с тремя
  вкладками проектов вида `<a class="tab" data-p="sxm" href="/" data-st="done">` (атрибуты в этом порядке — на него
  рассчитан тест; `data-st` из `config.extra.projects`: `done | wip | seed`), `<a class="tab" data-p="contact" …>`,
  `<button class="snd" id="snd" type="button">sound=<b>on</b></button>` (оживёт в плане 2). У вкладки текущей
  страницы класс `on`.

- [ ] **Шаг 1: тесты**

```js
// tests/shell.test.mjs
const ORDER = [['about', '/about/', 'About'], ['sxm', '/', 'SXM Tools'], ['etudes', '/etudes/', 'Études'], ['metta', '/metta-corpse/', 'Metta Corpse'], ['contact', '/contact/', 'Contact']];
for (const [tab, path] of ORDER) test(`header on ${path}`, () => {
  const html = readPage(path);
  const tabs = [...html.matchAll(/<a class="tab[^"]*" data-p="(\w+)" href="([^"]+)"/g)].map(m => [m[1], m[2]]);
  assert.deepEqual(tabs, ORDER.map(([t, p]) => [t, p]));
  assert.equal([...html.matchAll(/class="tab on"/g)].length, 1);
  assert.match(html, new RegExp(`class="tab on" data-p="${tab}"`));
  assert.match(textOf(html), /persona=sxm-sxpxxl/);
  assert.match(html, /data-p="sxm"[^>]*data-st="done"|data-st="done"[^>]*data-p="sxm"/);
  assert.match(html, /id="snd"[^>]*>sound=<b>on<\/b>/);
});
// tests/behaviour.test.mjs
test('a picture is never dragged, a link is', () => {
  const listeners = {}; const doc = { addEventListener: (t, f) => (listeners[t] = f), removeEventListener() {} };
  installDragGuard(doc);
  const ev = (tag) => ({ target: { nodeType: 1, closest: (s) => (s.includes('img') && tag === 'IMG' ? {} : null) }, prevented: false, preventDefault() { this.prevented = true; } });
  const img = ev('IMG'), a = ev('A'); listeners.dragstart(img); listeners.dragstart(a);
  assert.equal(img.prevented, true); assert.equal(a.prevented, false);
});
```

- [ ] **Шаг 2: убедиться, что падают** — Run: `npm test` → FAIL.

- [ ] **Шаг 3: шапка и стили оболочки**

Перенести в `_shell.scss` правила `.px`, `.bar`, `.mark`, `.mk-code`, `.tabs`, `.tab`, `.tproj` (линия метро:
точки `done/wip/seed`, связки 26 px — сплошная от готового, пунктир от того, что в работе), `.snd` (место под три
знака), `.row.sec`, `.lbl`, `.neon`, `.lnk` из образца; цвета вкладок проектов в покое и активные — как в спеке,
«Вкладки проектов в шапке» (без анимаций: вздрагивание, кипение, пепел, приманка — план 3). Курсор `.mk-code .k`
мигает (`blink 1.1s steps(1) infinite`), при «уменьшить движение» стоит. Выделение: `.bar, .mnu-ov, .lbl, .neon,
.lnk { user-select: none }`. Картинки: `.px img { -webkit-user-drag: none }` и `installDragGuard(document)` в `app.js`
(отмена `dragstart`, если цель — картинка внутри `#px`).

- [ ] **Шаг 4: тесты проходят** — Run: `npm test` → PASS.

- [ ] **Шаг 5: коммит**

```bash
git add templates config.toml sass static/js tests
git commit -m "feat: every page has the shell header with its metro line and section labels"
```

---

### Задача 4: роутер и жизненный цикл страниц

**Файлы:**
- Создать: `static/js/router.js`, `static/js/pages.js`, `static/js/pages/{sxm,about,etudes,metta,contact}.js`
  (заглушки), `tests/router.test.mjs`
- Изменить: `static/js/app.js`, `sass/_shell.scss` (проявление страницы)

**Интерфейсы:**
- Производит (все последующие планы опираются на это):
  - `router.js`: `export const TABS = ['about', 'sxm', 'etudes', 'metta', 'contact']`;
    `export const TAB_PATH = { about: '/about/', sxm: '/', etudes: '/etudes/', metta: '/metta-corpse/', contact: '/contact/' }`;
    `export function routeOf(href: string, origin: string): { tab: string, path: string, search: string, hash: string } | null`;
    `export function createRouter({ origin, fetchPage, render }): { go(href: string, opts?: { push?: boolean }): Promise<boolean> }`,
    где `fetchPage(path: string, signal: AbortSignal): Promise<{ tab: string, title: string, html: string }>`,
    `render(page, route, { push }): void`; `go` отменяет незавершённый переход и возвращает `true`, если отрисовал,
    `false`, если его обогнал другой переход.
  - `pages.js`: `export const PAGE_MODULES: Record<string, () => Promise<{ mount(root: HTMLElement, ctx: PageContext): void, unmount(): void }>>`;
    `export function makeContext(win: Window, route): PageContext`, где
    `PageContext = { reducedMotion: boolean, audio: null, now: () => number, params: URLSearchParams, hash: string }`
    (`audio` заполнит план 2).

- [ ] **Шаг 1: тесты**

```js
// tests/router.test.mjs
const O = 'https://sxm-sxpxxl.github.io';
test('routeOf maps addresses to tabs', () => {
  assert.deepEqual(routeOf('/', O), { tab: 'sxm', path: '/', search: '', hash: '' });
  assert.equal(routeOf('/about', O).path, '/about/');
  assert.equal(routeOf('/metta-corpse/', O).tab, 'metta');
  assert.deepEqual(routeOf('/contact/?product=ui-factory#ki-3-x', O), { tab: 'contact', path: '/contact/', search: '?product=ui-factory', hash: '#ki-3-x' });
  assert.equal(routeOf('https://github.com/x', O), null);
  assert.equal(routeOf('/fonts/geologica/OFL.txt', O), null);
});
test('the last navigation wins', async () => {
  const rendered = [];
  const fetchPage = (path, signal) => new Promise((res, rej) => {
    const t = setTimeout(() => res({ tab: routeOf(path, O).tab, title: path, html: path }), path === '/about/' ? 50 : 5);
    signal.addEventListener('abort', () => { clearTimeout(t); rej(new DOMException('aborted', 'AbortError')); });
  });
  const r = createRouter({ origin: O, fetchPage, render: (p) => rendered.push(p.title) });
  const a = r.go(O + '/about/'), b = r.go(O + '/etudes/');
  assert.deepEqual(await Promise.all([a, b]), [false, true]);
  assert.deepEqual(rendered, ['/etudes/']);
});
test('back and forward render without a new history entry', async () => {
  const calls = [];
  const r = createRouter({ origin: O, fetchPage: async (path) => ({ tab: routeOf(path, O).tab, title: path, html: '' }),
    render: (page, route, opts) => calls.push([route.tab, opts.push]) });
  await r.go(O + '/contact/?product=ui-factory#ki-3-x'); await r.go(O + '/', { push: false });
  assert.deepEqual(calls, [['contact', true], ['sxm', false]]);
});
```

- [ ] **Шаг 2: убедиться, что падают** — Run: `npm test` → FAIL.

- [ ] **Шаг 3: роутер и подключение**

`app.js`: при загрузке монтирует модуль текущей вкладки; перехватывает клики по `a[href]`, для которых `routeOf`
не `null`, кроме кликов с модификаторами, средней кнопкой, `target="_blank"` и `download`; `popstate` →
`go(location.href, { push: false })`. `fetchPage` — `fetch(path)` → `DOMParser` → `#page` (innerHTML), `title`,
`body[data-tab]`. `render`: `unmount()` старого модуля, замена `#page`, `document.title`, `body.dataset.tab`,
класс `on` у вкладки, `history.pushState` (если `push`), класс `enter` на `#page` (CSS `fade .25s ease-out`, только
`opacity`), фокус на `#page` (`tabindex="-1"`), прокрутка к `hash` или наверх, `mount()` нового модуля. Модули
вкладок пока пустые (`mount() {}`, `unmount() {}`).

- [ ] **Шаг 4: тесты проходят и проверка в браузере**

Run: `npm test` → PASS. Затем `zola serve` и в браузере: переходы по вкладкам без перезагрузки (в консоли
`performance.getEntriesByType('navigation').length` остаётся `1`), «назад» и «вперёд» возвращают нужную вкладку и
заголовок окна, при отключённом JS ссылки работают как обычные.

- [ ] **Шаг 5: коммит**

```bash
git add static/js sass tests
git commit -m "feat: tabs switch without a reload and each tab mounts its own module"
```

---

### Задача 5: телефон и узкие экраны

**Файлы:**
- Создать: `sass/_phone.scss`, `static/js/phone-menu.js`, `tests/phone-menu.test.mjs`
- Изменить: `static/js/app.js`

**Интерфейсы:**
- Производит: `export function neighbours(order: string[], cur: string): { prev: string, cur: string, next: string }`;
  `export function stripLayout(w: { prev: number, cur: number, next: number }, strip: number): { prevX: number, curX: number, nextX: number }`;
  `export function installPhoneMenu(nav: HTMLElement, opts: { tab: string, reducedMotion: boolean }): { update(tab: string): void, destroy(): void }`.

- [ ] **Шаг 1: тесты**

```js
test('three around: the circle closes at both ends', () => {
  assert.deepEqual(neighbours(TABS, 'about'), { prev: 'contact', cur: 'about', next: 'sxm' });
  assert.deepEqual(neighbours(TABS, 'contact'), { prev: 'metta', cur: 'contact', next: 'about' });
});
test('the current tab sits between its neighbours with equal gaps', () => {
  const w = { prev: 60, cur: 90, next: 70 }, x = stripLayout(w, 340);
  assert.equal(x.prevX, 0); assert.equal(x.nextX, 340 - 70);
  assert.equal(x.curX - (x.prevX + w.prev), x.nextX - (x.curX + w.cur));
});
```

- [ ] **Шаг 2: убедиться, что падают** — Run: `npm test` → FAIL.

- [ ] **Шаг 3: раскладки и меню**

Перенести раскладки из раздела образца `/* ---------- phone stage` с контейнерных запросов на медиазапросы:
`max-width: 700px` — телефон (шапка в две строки, меню 12,5 px, всё в одну колонку, подписи над разделами, у
продуктов скрыты миниатюра и `details`, у Known issues — колонка Version); `701–880px` — шапка в одну строку 62 px
с меню из трёх вкладок посередине; `max-height: 500px` — низкий экран. `installPhoneMenu` — перенос `placeTabs` из
`// ---------- phone: stage switcher`: остальные вкладки ждут за краями, переход «прокручивает» полосу за 0,4 с
(`transform`), при «уменьшить движение» — сразу; связки метро тянутся до соседа и сжимаются с прокруткой.

- [ ] **Шаг 4: тесты проходят и проверка в браузере** — Run: `npm test` → PASS; `zola serve`, ширина 375, 800 и
  1100 px: снимки шапки и каждой вкладки, ничего не вылезает по горизонтали, меню по кругу работает.

- [ ] **Шаг 5: коммит**

```bash
git add sass static/js tests
git commit -m "feat: phones and narrow screens get the three-tab circle menu and one-column pages"
```

---

### Задача 6: SXM Tools

**Файлы:**
- Создать: `data/products.toml`, `static/img/sxm/*` (из `docs/prototype/files/`: `sxm-logo.png`, `chart-card.png`,
  `factory-card.png`, семь `chart-*.png`, четыре `factory-*.png`), `templates/partials/product.html`, `sass/_sxm.scss`,
  `static/js/carousel.js`, `tests/sxm.test.mjs`, `tests/carousel.test.mjs`
- Изменить: `templates/sxm.html`, `static/js/pages/sxm.js`

**Интерфейсы:**
- Потребляет: `macros::label`, `macros::badge`, `macros::link_or_nothing` (задача 3); `mount/unmount` (задача 4).
- Производит: схема `data/products.toml` (план 5 заполняет `version`, `versions`, `unity`, `price`, `asset_store_url`):

```toml
[[product]]
key = "ui-line-chart"              # стабильный ключ: адреса, якоря, ?product=
name = "UI Line Chart"
line = "Line chart control for UI Toolkit in Unity."
description = "One control, set up in UI Builder with a live preview, or driven from code."
version = "0.9.14"                 # последний тег
versions = ["0.9.14", "0.9.13", "0.9.12", "0.9.11", "0.9.10"]   # новые первыми — список формы бага
unity = "6.0+"
price = "$19.99"
license = ""                       # пусто — плашки нет
store = true                       # продаётся в Asset Store: кнопки «Asset Store →» + «Docs ↗»
asset_store_url = ""               # пусто — состояние «до стора»
docs_url = ""                      # адрес даёт автор
github_url = ""
openupm_url = ""
thumb = "chart-card.png"
frames = ["chart-hero.png", "chart-builder.png", "chart-datasets.png", "chart-playback.png", "chart-textstyles.png", "chart-tool.png", "chart-documentation.png"]
```

UI Factory: `line = "Builds meshes for custom UI Toolkit controls."`, описание из спеки, `version = "7.0.2"`,
`unity = "2022.3+"`, `price = "free"`, `license = "MIT"`, `store = false` (кнопки «GitHub →» по `github_url` +
«OpenUPM ↗» по `openupm_url`), кадры `factory-shapes/caching/chart/usage.png`.
- `carousel.js`: `export function wrapIndex(i: number, n: number): number`;
  `export function sideOf(from: number, to: number, arrow?: -1 | 1): -1 | 1` (у стрелки — её сторона, в том числе
  при переходе по кругу; у точки — знак `to − from`).

- [ ] **Шаг 1: тесты**

```js
// tests/sxm.test.mjs
test('SXM Tools copy and products', () => {
  const html = readPage('/'), t = textOf(html);
  for (const s of ['I make tools for Unity developers.', 'In each one, I try to follow three principles:',
    'Easy to understand, with nothing on screen that does nothing.', 'It talks to you through hints, notices and clear errors.',
    'It respects your time and your hardware: no waiting, no wasted work.', 'Questions, ideas or a problem?',
    'Let me know, and I\'ll try to help. Known bugs are listed there too.']) assert.ok(t.includes(s), s);
  assert.match(html, /alt="SXM Tools — Intuitive\. Attentive\. Fast\."/);
  assert.match(html, /<div class="prod open"[^>]*data-key="ui-line-chart"/);
  assert.match(html, /<div class="prod"[^>]*data-key="ui-factory"/);
  assert.ok(t.includes('license MIT') && t.includes('price free') && t.includes('unity 2022.3+'));
  assert.ok(t.includes('02 / tools') && t.includes('02 / contact'));
});
const withDocs = () => readFileSync('data/products.toml', 'utf8').replace('docs_url = ""', 'docs_url = "https://example.com/docs"');
test('UI Line Chart before the store: Docs → and «store | coming soon»', () => {
  const out = buildWith({ 'data/products.toml': withDocs() });
  const card = readFileSync(`${out}/index.html`, 'utf8').split('data-key="ui-line-chart"')[1].split('class="prod')[0];
  assert.match(card, /Docs →/); assert.match(textOf(card), /store coming soon/);
  assert.doesNotMatch(card, /Asset Store →/); assert.doesNotMatch(card, /\$19\.99/);
});
test('UI Line Chart in the store: Asset Store → with the price and Docs ↗', () => {
  const toml = withDocs().replace('asset_store_url = ""', 'asset_store_url = "https://assetstore.unity.com/x"');
  const out = buildWith({ 'data/products.toml': toml });
  const card = readFileSync(`${out}/index.html`, 'utf8').split('data-key="ui-line-chart"')[1].split('class="prod')[0];
  assert.match(card, /href="https:\/\/assetstore\.unity\.com\/x"[^>]*>Asset Store →/); assert.match(card, /\$19\.99/);
  assert.match(card, /href="https:\/\/example\.com\/docs"[^>]*>Docs ↗/);
});
// tests/carousel.test.mjs
test('carousel sides', () => {
  assert.equal(wrapIndex(-1, 7), 6); assert.equal(wrapIndex(7, 7), 0);
  assert.equal(sideOf(6, 0, 1), 1); assert.equal(sideOf(0, 6, -1), -1); assert.equal(sideOf(1, 5), 1); assert.equal(sideOf(5, 2), -1);
});
```

- [ ] **Шаг 2: убедиться, что падают** — Run: `npm test` → FAIL.

- [ ] **Шаг 3: страница**

`templates/sxm.html` по разделу образца `<!-- SXM TOOLS -->`: скрытый `<h1 class="sr">SXM Tools</h1>`, логотип, лид,
принципы, `label("02", "tools")`, продукты через `partials/product.html` (первый с классом `open`), `label("02",
"contact")` с текстом и `Write to me →` (`<a class="neon" href="/contact/">`). Кнопки: у продукта стора —
неоновая `Asset Store →` (`asset_store_url`) и `.lnk` `Docs ↗` (`docs_url`); у остальных — `GitHub →` и `OpenUPM ↗`;
пустой адрес — ничего. «До стора»: `store && asset_store_url == ""` → неоновая `Docs →` (`docs_url`), плашка
`badge("store", "coming soon")` вместо цены, второй ссылки нет. `_sxm.scss` —
перенос правил `.prod`, `.ph`, `.pb`, `.badges`/`.b-chips` (вид «щит»), `.gal`, `.shot`, `.arr`, `.dots`, `.lb`, роли
бирюзового и оранжевого. Закрытый заголовок продукта не выделяется, открытый — выделяется (`cursor: auto`);
карусель и картинки не выделяются. `pages/sxm.js`: клик по закрытому продукту открывает его и закрывает прежний
(без анимации, она — в плане 3); карусель — стрелки, точки, свайп (> 40 px) по `wrapIndex`, смена `src` без
анимации; клик по кадру — полноэкранный просмотр, клик по нему закрывает. `mount/unmount` снимают свои слушатели.

- [ ] **Шаг 4: тесты проходят и проверка в браузере** — Run: `npm test` → PASS; в браузере продукты открываются,
  карусель листает по кругу, полноэкранный кадр открывается и закрывается.

- [ ] **Шаг 5: коммит**

```bash
git add data/products.toml static/img/sxm templates sass static/js tests
git commit -m "feat: sxm tools shows its logo, principles and products with a working carousel"
```

---

### Задача 7: Études

**Файлы:**
- Создать: `data/etudes.toml`, `tools/make-etude-videos.mjs`, `static/video/etudes/<slug>.mp4` и `<slug>.jpg`,
  `sass/_etudes.scss`, `tests/etudes.test.mjs`
- Изменить: `templates/etudes.html`, `static/js/pages/etudes.js`

**Интерфейсы:**
- Производит: схема `data/etudes.toml`:

```toml
[now]
title = "Hanoi Tower"
state = "in progress"
description = "An experimental environment for proving a popular mathematical statement in the context of the “Tower of Hanoi” game."
later = "It will be playable on itch.io, with the source on GitHub, once it is ready."

[[earlier]]
slug = "procedural-mesh-generator"
title = "Procedural Mesh Generator"
year = 2022
description = "A Unity editor tool that generates primitive meshes, bends them with modifiers on the Job System and Burst, and exports them to OBJ."
repo = ""          # адрес даёт автор
angle = 0.8        # наклон отпечатка, градусы
```

остальные пять этюдов — по таблице спеки (раздел «Études»), углы из образца: −1, 1.1, −0.7, 1, −0.9.

- [ ] **Шаг 1: тест**

```js
test('Études: lead, Hanoi Tower and six earlier études with videos', () => {
  const html = readPage('/etudes/'), t = textOf(html);
  assert.ok(t.includes('Prototypes and sketches of ideas. Something bigger may grow from them.'));
  assert.ok(t.includes('It will be playable on itch.io, with the source on GitHub, once it is ready.'));
  assert.ok(t.includes('n discs: left → right') && t.includes('T(n) = 2·T(n−1) + 1'));
  const videos = [...html.matchAll(/<video([^>]*)>/g)].map(m => m[1]);
  assert.equal(videos.length, 6);
  for (const v of videos) { assert.match(v, /\bmuted\b/); assert.match(v, /\bloop\b/); assert.match(v, /\bplaysinline\b/); assert.doesNotMatch(v, /\bautoplay\b/); assert.match(v, /poster="\/video\/etudes\/[\w-]+\.jpg"/); }
  for (const y of ['done · 2022', 'done · 2021', 'done · 2020']) assert.ok(t.includes(y), y);
  for (const f of readdirSync('static/video/etudes')) assert.ok(statSync(`static/video/etudes/${f}`).size > 0);
});
```

- [ ] **Шаг 2: убедиться, что падает** — Run: `npm test` → FAIL.

- [ ] **Шаг 3: видео (с разрешения автора на скачивание гифок)**

Скачать шесть гифок по адресам из раздела `<!-- ETUDES -->` образца в `tools/src/etudes/<slug>.gif` (папка не
коммитится). `tools/make-etude-videos.mjs` вызывает ffmpeg (`process.env.FFMPEG ?? 'ffmpeg'`):
`-i <gif> -an -c:v libx264 -crf 23 -pix_fmt yuv420p -movflags +faststart -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" <slug>.mp4`,
для `zrlc-meter` перед масштабом `crop=531:332:792:37` (область 792…1323 × 37…369 из спеки); обложка —
`-i <slug>.mp4 -frames:v 1 -q:v 3 <slug>.jpg`.

- [ ] **Шаг 4: страница**

`templates/etudes.html` по разделу `<!-- ETUDES -->`: большое «Études» (пока статичным текстом, перо — план 4),
`label("03", "études")`, лид, `label("03", "now")` с листом блокнота (перенос `<div class="et-sheet">` целиком, SVG
и записка), `label("03", "earlier")` с сеткой карточек: `<video muted loop playsinline preload="metadata" poster>`
в рамке-отпечатке с наклоном `--r: <angle>deg`, `done · <year>`, название, описание, `GitHub ↗` (если есть адрес).
`_etudes.scss` — перенос `.et-*`. `pages/etudes.js`: обычный режим — видео играет, когда видно
(`IntersectionObserver`), и встаёт, когда ушло; «уменьшить движение» — обложка с меткой `▶ gif`, видео играет,
пока мышь на нём, касание включает и выключает. Записка на листке и статусы не выделяются.

- [ ] **Шаг 5: тесты проходят и проверка в браузере** — Run: `npm test` → PASS; в браузере видео идут, у zRLC Meter
  виден мастер калибровки без пустого графика; при «уменьшить движение» (эмуляция в DevTools) стоят обложки.

- [ ] **Шаг 6: коммит**

```bash
git add data/etudes.toml tools/make-etude-videos.mjs static/video sass templates static/js tests .gitignore
git commit -m "feat: études lists hanoi tower and six earlier études with their own videos"
```

---

### Задача 8: Metta Corpse

**Файлы:**
- Создать: `static/img/metta/mc-logo-h.png` (из `docs/prototype/files/`), `sass/_metta.scss`, `tests/metta.test.mjs`
- Изменить: `templates/metta.html`, `static/js/pages/metta.js`

**Интерфейсы:**
- Производит: `pages/metta.js` экспортирует кроме `mount/unmount` функцию `placeLetters(root: HTMLElement): void`
  (план 4 вызывает её после пересборки пепла).

- [ ] **Шаг 1: тест**

```js
test('Metta Corpse copy, games and letters', () => {
  const html = readPage('/metta-corpse/'), t = textOf(html);
  for (const s of ['The games I am working toward. Two so far, both still more of a dream than a game.',
    'Both games are at the very start, so what you read here may still change as the work goes on.',
    'Light of Salva’s Tower', 'Auspicious Birthplace', 'then ↓']) assert.ok(t.includes(s), s);
  const lines = [...html.matchAll(/<span class="ln">([^<]+)<\/span>/g)].map(m => m[1]);
  assert.deepEqual(lines, ['You run, and it follows.', 'It wears a new face every time,', 'but you always know who it is.',
    'You are held so close you can’t breathe,', 'and still you are afraid of being let go.']);
  assert.match(html, /data-ab="LoST"/); assert.match(html, /data-ab="AB"/);
  assert.equal([...html.matchAll(/class="mc-meta">concept</g)].length, 2);
  assert.match(html, /<h1[^>]*class="[^"]*big[^"]*"[^>]*>Metta/);
});
```

- [ ] **Шаг 2: убедиться, что падает** — Run: `npm test` → FAIL.

- [ ] **Шаг 3: страница**

`templates/metta.html` по разделу `<!-- METTA CORPSE -->`: скрытое большое «Metta Corpse», логотип (`.mc-mark`,
`.mc-smoke`, `.mc-pic` с `alt="Metta Corpse"`), `label("04", "metta corpse")`, лид, записка, `label("04", "now")`,
две записи `.mc-entry` с `data-ab`, `then ↓`. `_metta.scss` — перенос правил `#p-metta` выбранных вариантов
(`grey=ash`: лид `#D6D1C8`, строки `#ADA79D`, мелкий текст `#908A81`; `logo=left` на компьютере и по центру при
`max-width: 700px` и `max-height: 500px`; коэффициенты `--mk-w: 2.07680; --mk-top: .28610; --mk-left: 1.03110;
--mk-h: .49919; --mk-sm: .88210`; буквы LoST и AB через `::before` в Long Cang). `placeLetters` — перенос раздела
`// ---------- Metta Corpse: placing by measured glyphs`: начало букв по чернилам названия, низ — на линии названия,
`then ↓` посередине (по 32 px); вызывается при `mount`, после загрузки шрифтов и при изменении ширины.

- [ ] **Шаг 4: тесты проходят и проверка в браузере** — Run: `npm test` → PASS; в браузере на 375, 800 и 1100 px L над L
  из «Light», A над A из «Auspicious», `then ↓` посередине.

- [ ] **Шаг 5: коммит**

```bash
git add static/img/metta sass templates static/js tests
git commit -m "feat: metta corpse shows its logo and two games with the lost and ab letters"
```

---

### Задача 9: About и авторы

**Файлы:**
- Создать: `data/credits.toml`, `static/img/about/portrait.jpg`, `templates/partials/credits.html`, `sass/_about.scss`,
  `tests/about.test.mjs`
- Изменить: `templates/about.html`, `static/js/pages/about.js`

**Интерфейсы:**
- Производит: схема `data/credits.toml`:

```toml
lead = "Almost everything you hear on this site was made by these people and shared for anyone to use. Thank you all."
[[group]]
key = "music"
title = "music"
[[group]]
key = "mix"
title = "the Metta Corpse theme"
note = "My own mix of Kevin MacLeod’s “Ossuary 6 - Air” and eleven recordings from freesound.org by Jovica, Badgie42, Nosebleed Cinema, bassimat (MANTICE), Sadiquecat, DeVern, steaq, BrainClaim and 3bagbrew. Those under CC BY 4.0 are edited."
[[group]]
key = "sounds"
title = "sounds"
[[person]]
who = "Kevin MacLeod"
site = "incompetech.com"
group = "music"
work = [
  { t = "Limit 70", url = "https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1900042", use = "the SXM Tools theme", lic = "by", change = "looped" },
]
```

остальные — по таблице спеки (раздел «`01 / credits` — авторы», 16 человек, 20 работ). Лицензии: `by` →
`https://creativecommons.org/licenses/by/4.0/` («CC BY 4.0»), `cc0` → `https://creativecommons.org/publicdomain/zero/1.0/` («CC0»).

- [ ] **Шаг 1: тест**

```js
test('About text, portrait and buttons', () => {
  const html = readPage('/about/'), t = textOf(html);
  for (const s of ['I\'m Alexey Pestov, a game developer who makes tools for Unity.', 'They\'ve pulled at me since I was a kid.',
    'That\'s why I started SXM Tools.', 'That\'s why I started Études.', 'That\'s why I started Metta Corpse.']) assert.ok(t.includes(s), s);
  assert.match(html, /<a[^>]*href="\/"[^>]*>SXM Tools<\/a>/); assert.match(html, /<a[^>]*href="\/etudes\/"[^>]*>Études<\/a>/);
  assert.match(html, /<img[^>]*src="\/img\/about\/portrait\.jpg"[^>]*alt="Alexey Pestov"/);
  assert.match(html, /<a class="neon"[^>]*href="\/contact\/"[^>]*>Write to me →/);
});
test('credits: everyone named, the long group folded', () => {
  const html = readPage('/about/'), t = textOf(html);
  for (const who of ['Kevin MacLeod', 'Memoraphile', 'Jovica', 'Badgie42', 'Nosebleed Cinema', 'bassimat (MANTICE)', 'Sadiquecat', 'DeVern', 'steaq', 'BrainClaim', '3bagbrew', 'heyheytheree', 'KorgMS2000B', 'TRP', 'samwd', 'oscaraudiogeek']) assert.ok(t.includes(who), who);
  assert.equal([...html.matchAll(/class="cr-p"/g)].length, 16);
  assert.equal([...html.matchAll(/href="https:\/\/(incompetech\.com|opengameart\.org|freesound\.org)[^"]+"/g)].length, 20);
  assert.equal([...html.matchAll(/<details class="cr-more"/g)].length, 1);
  assert.match(html, /<details class="cr-more"[\s\S]*Jovica[\s\S]*<\/details>/);
  assert.ok(t.includes('+ show the recordings') && t.includes('− hide'));
  assert.ok(t.includes('Those under CC BY 4.0 are edited.'));
});
```

- [ ] **Шаг 2: убедиться, что падают** — Run: `npm test` → FAIL.

- [ ] **Шаг 3: страница**

Портрет: из `D:\media-pool\affinity-projects\sxm-about\sxm-portrait.JPG` уменьшить до 1000 px по длинной стороне,
JPEG качества 85 (Pillow). `templates/about.html` по разделу `<!-- ABOUT -->`: `label("01", "about")`, ABOUT, лид,
абзацы (названия проектов — ссылки на вкладки), портрет 3:4 с уголками видоискателя, ряд `Write to me →`,
`LinkedIn ↗`, `GitHub ↗` (пустой адрес — нет ссылки), `label("01", "credits")` и `partials/credits.html`: группа
длиннее шести человек — в `<details class="cr-more">` с `<summary>` `+ show the recordings` / `− hide` и `note` над
ней; у работы название-ссылка (`target="_blank" rel="noopener"`), где звучит и `looped` / `edited`, строка
`сайт · лицензия`. `_about.scss` — перенос `#p-about`, `.portrait` (уголки 18 px в 9 px от краёв, `#6a6f7a`),
`.acts-me`, `.cr-*`, `.cr-more` (раскрытие 0,4 с через `interpolate-size`, при «уменьшить движение» сразу).
`pages/about.js` пока пустой (лампа и лупа — план 4).

- [ ] **Шаг 4: тесты проходят** — Run: `npm test` → PASS.

- [ ] **Шаг 5: коммит**

```bash
git add data/credits.toml static/img/about templates sass static/js tests
git commit -m "feat: about tells the story with the portrait and thanks every author by name"
```

---

### Задача 10: Contact — форма

**Файлы:**
- Создать: `templates/partials/contact-form.html`, `sass/_contact.scss`, `static/js/contact/form-state.js`,
  `static/js/contact/send.js`, `static/js/copy.js`, `tests/contact-form.test.mjs`, `tests/copy.test.mjs`,
  `tests/contact.test.mjs`
- Изменить: `templates/contact.html`, `static/js/pages/contact.js`

**Интерфейсы:**
- Потребляет: `data/products.toml` (`key`, `name`, `versions`).
- Производит:
  - `form-state.js`: `export function formState(type: 'bug' | 'question' | 'suggestion'): { label, placeholder, hint, note, bugFields: boolean }`;
    `export function validateFile(f: { name: string, size: number }): { ok: true, size: string } | { ok: false, error: string }`;
    `export function canSend(s: { message: string }): boolean`;
    `export function productFromQuery(search: string, keys: string[]): string` (по умолчанию первый ключ);
    `export function doneLine(s: { type, product, version, attached: boolean }): string`.
  - `send.js`: `export async function sendReport(payload): Promise<void>` — заглушка, отвечает через 300 мс; план 6
    заменяет её отправкой в Worker.
  - `copy.js`: `export async function copyText(text: string, env = { clipboard: navigator.clipboard, legacy: execCopy }): Promise<boolean>`;
    `export function copySay(el: HTMLElement, ok: boolean, text: string, rest: string, ms = 1500): void`.

- [ ] **Шаг 1: тесты**

```js
// tests/contact-form.test.mjs
test('form copy follows the type', () => {
  assert.deepEqual(formState('bug'), { label: 'what happened and how to reproduce it',
    placeholder: 'The tooltip disappears when I hover the last point.\n\n1. Add a LineChart in UI Builder\n2. Hover the last point…',
    hint: 'Before reporting a bug, check the known issues ↓ — it may already have a workaround.',
    note: "Without an email I can't ask you for details.", bugFields: true });
  assert.equal(formState('question').placeholder, 'Can I update the chart from my own script while the game runs?');
  assert.equal(formState('question').hint, 'It may already be answered — check the FAQ ↓.');
  assert.equal(formState('suggestion').placeholder, 'It would be great if the chart could…');
  assert.equal(formState('suggestion').hint, ''); assert.equal(formState('suggestion').bugFields, false);
  assert.equal(formState('suggestion').note, "Without an email you'll only see it in the changelog.");
});
test('attachments: png, jpg, txt up to 5 MB, and Unity logs quietly too', () => {
  assert.deepEqual(validateFile({ name: 'shot.PNG', size: 50_000 }), { ok: true, size: '< 0.1 MB' });
  assert.deepEqual(validateFile({ name: 'log.txt', size: 2.5 * 1048576 }), { ok: true, size: '2.5 MB' });
  assert.deepEqual(validateFile({ name: 'Editor.log', size: 1.5 * 1048576 }), { ok: true, size: '1.5 MB' });
  assert.deepEqual(validateFile({ name: 'a.gif', size: 10 }), { ok: false, error: 'a.gif — only png, jpg or txt, please.' });
  assert.deepEqual(validateFile({ name: 'big.png', size: 6.2 * 1048576 }), { ok: false, error: 'big.png is 6.2 MB — the limit is 5 MB. Try a cropped screenshot or a shorter log.' });
});
test('sending needs words; the product falls back to the first', () => {
  assert.equal(canSend({ message: '  ' }), false); assert.equal(canSend({ message: 'x' }), true);
  assert.equal(productFromQuery('?product=ui-factory', ['ui-line-chart', 'ui-factory']), 'ui-factory');
  assert.equal(productFromQuery('?product=foo', ['ui-line-chart', 'ui-factory']), 'ui-line-chart');
  assert.equal(doneLine({ type: 'bug', product: 'ui-line-chart', version: '0.9.14', attached: true }), '> send bug · ui-line-chart@0.9.14 + 1 file ok');
  assert.equal(doneLine({ type: 'question', product: 'ui-factory', version: '7.0.2', attached: false }), '> send question · ui-factory ok');
});
// tests/copy.test.mjs
test('copy: clipboard first, then the old command, else false', async () => {
  assert.equal(await copyText('a', { clipboard: { writeText: async () => {} }, legacy: () => false }), true);
  assert.equal(await copyText('a', { clipboard: { writeText: async () => { throw new Error('denied'); } }, legacy: () => true }), true);
  assert.equal(await copyText('a', { clipboard: undefined, legacy: () => false }), false);
});
// tests/contact.test.mjs
test('Contact page: lead, switch, form and the email', () => {
  const html = readPage('/contact/'), t = textOf(html);
  assert.ok(t.includes('Found a bug, have a question or an idea? Write to me — one form for all of it.'));
  assert.ok(t.includes('or skip the form and email me at sxm.sxpxxl.dev@gmail.com'));
  assert.match(html, /href="mailto:sxm\.sxpxxl\.dev@gmail\.com"/);
  assert.match(html, /<select[^>]*id="cfPkg"[\s\S]*0\.9\.14[\s\S]*latest/);
  assert.match(html, /placeholder="e\.g\. 6000\.0\.84f1"/); assert.match(html, /placeholder="you@example\.com"/);
  assert.ok(t.includes('png, jpg, txt · up to 5 MB'));
});
```

- [ ] **Шаг 2: убедиться, что падают** — Run: `npm test` → FAIL.

- [ ] **Шаг 3: форма**

Тексты — дословно как в тестах; принимаются расширения `png jpg jpeg txt log` (`.log` — логи Unity, в подписи и
ошибке не назван; `accept=".png,.jpg,.jpeg,.txt,.log"`), предел
`5 * 1048576` байт. `templates/contact.html` по разделу `<!-- CONTACT -->`: `label("05", "contact")`, CONTACT, лид,
переключатель продукта (`<span data-p="<key>">`), форма из `partials/contact-form.html` (подписи `> поле`,
`optional`; пунктир у пустых необязательных, сплошная рамка у остальных и у заполненных), `Send →`, почта —
`<a class="lnk mail" href="mailto:…">` и `<span class="cf-copy" role="button" tabindex="0">copy</span>`. Версии и
продукты для скрипта — `<script type="application/json" id="contact-data">` из `products.toml`. `_contact.scss` —
перенос `/* ---------- contact form` с выпадающим списком «терминал» (`appearance: base-select`, пункты моно, у
выбранного `>`, открытие под полем с отступом 6 px, проявление 0,14 с). `pages/contact.js`: продукт из
`?product=` (`productFromQuery`), смена продукта меняет `?product=` через `history.replaceState` и список версий;
тип меняет подпись, пример, подсказку (ссылка `↓` плавно прокручивает к разделу), примечание к почте, поля бага;
вложение кликом и перетаскиванием с `validateFile` (ошибка инлайн, `remove`); `Send →` — `canSend`, иначе ошибка
«Write a few words here — I can't help without them.» и фокус; при успехе `sendReport` → форма заменяется строкой
`doneLine(...)` и «Thanks — I'll do my best to look into it. If you left an email, I'll reply there.»; `copy` у почты —
`copyText` → `copySay(el, true, 'copied ✓', 'copy')`, иначе выделить адрес и `copySay(el, false, 'press Ctrl+C' |
'press ⌘C' | 'selected', 'copy')` (Mac — по `navigator.platform`, телефон — по `(hover: none) and (pointer: coarse)`).
«Скопировано»: моно 500 12,5 px, `#66D87F`, ✓, 1,5 с.

- [ ] **Шаг 4: тесты проходят и проверка в браузере** — Run: `npm test` → PASS; в браузере все три типа,
  вложение (большое и неподходящее), отправка с пустым и с непустым сообщением, `copy` у почты.

- [ ] **Шаг 5: коммит**

```bash
git add templates sass static/js tests
git commit -m "feat: contact has the one form for bugs, questions and ideas with the email copy"
```

---

### Задача 11: Contact — Known issues и FAQ

**Файлы:**
- Создать: `data/known-issues.json`, `data/faq.json`, `templates/partials/known-issues.html`,
  `templates/partials/faq.html`, `static/js/contact/issues.js`, `tests/issues.test.mjs`
- Изменить: `templates/contact.html`, `static/js/pages/contact.js`, `sass/_contact.scss`, `tests/contact.test.mjs`

**Интерфейсы:**
- Потребляет: `copyText`, `copySay` (задача 10); `productFromQuery` (задача 10).
- Производит: схема файлов (план 5 производит их из Notion и тегов; поля для показа уже посчитаны):

```json
{ "items": [ { "id": 1, "slug": "tooltip-flickers-at-the-chart-edge", "product": "ui-line-chart",
  "title": "Tooltip flickers at the chart edge", "line": "Workaround: set the tooltip offset to 4 px or more.",
  "status": "investigating", "version": "0.9.14", "affects": "0.9.12 – 0.9.14", "reported": "2026-10-12", "fix": "—",
  "body_html": "<p>When the pointer is within …</p><h4>Workaround</h4><ol><li>…</li></ol>" } ] }
```

`status` ∈ `investigating | planned | fixed | wontfix`; `faq.json`: `{ "items": [ { "id", "slug", "product",
"question", "answer_html" } ] }`. Образцы — четыре записи Known issues и четыре FAQ из раздела `<!-- CONTACT -->`
образца (номера 1…4, `slug` из заголовка; у «No support for Unity 2021» — `id: 3`, `product: "ui-factory"`).
- `issues.js`: `export function anchorOf(kind: 'ki' | 'faq', id: number, slug: string): string`;
  `export function parseDeepLink(hash: string): { kind: 'ki' | 'faq', id: number } | null`;
  `export function countsFor(items, product: string): { open: number, fixed: number }`.

- [ ] **Шаг 1: тесты**

```js
// tests/issues.test.mjs
test('anchors survive a title change', () => {
  assert.equal(anchorOf('ki', 12, 'chart-flickers-on-resize'), 'ki-12-chart-flickers-on-resize');
  assert.deepEqual(parseDeepLink('#ki-12-anything-else'), { kind: 'ki', id: 12 });
  assert.deepEqual(parseDeepLink('#faq-7'), { kind: 'faq', id: 7 });
  assert.equal(parseDeepLink('#ki-x'), null); assert.equal(parseDeepLink(''), null);
});
test('counts per product', () => {
  const items = [{ product: 'a', status: 'planned' }, { product: 'a', status: 'fixed' }, { product: 'b', status: 'wontfix' }];
  assert.deepEqual(countsFor(items, 'a'), { open: 1, fixed: 1 }); assert.deepEqual(countsFor(items, 'b'), { open: 1, fixed: 0 });
});
// tests/contact.test.mjs (добавить)
test('known issues and FAQ are all in the page, with anchors and statuses', () => {
  const html = readPage('/contact/'), t = textOf(html);
  assert.match(html, /id="ki-1-tooltip-flickers-at-the-chart-edge"/); assert.match(html, /id="faq-1-/);
  assert.ok(t.includes('Check here first — your problem may already have a workaround. Click an issue for details.'));
  assert.ok(t.includes('Click one for the answer.'));
  assert.match(html, /class="st investigating">Investigating/); assert.match(html, /class="st wontfix">Won't fix/);
  assert.ok(t.includes('affects') && t.includes('0.9.12 – 0.9.14') && t.includes('planned for 0.9.15'));
  assert.ok(t.includes('Nothing here for this product.') && t.includes('No questions for this product yet.'));
});
```

- [ ] **Шаг 2: убедиться, что падают** — Run: `npm test` → FAIL.

- [ ] **Шаг 3: разделы**

`label("05", "known issues")` и `label("05", "faq")`, лиды с названием продукта `<b>` («Known issues in <b>UI Line
Chart</b>. …», «Questions people ask most about <b>UI Line Chart</b>. …»), `<details>` `not fixed (n)` (открыт) и
`fixed (n)`, таблицы Issue / Version / Status одинаковых колонок, строка `.ki-r` с `id` по `anchorOf`, `data-prod`,
статус — `<span class="st <status>">Investigating | Planned | Fixed | Won't fix</span>`, под строкой `.ki-d` с телом
и сведениями `affects · reported · fix` (на телефоне столбиком); пустые состояния; FAQ —
Question и ответ. Без JS видны все записи. `pages/contact.js`: показ только выбранного продукта и счётчики
(`countsFor`, `fixed` скрыт при нуле, «Nothing here…» при пустом `not fixed`), строка — кнопка (рука, не
выделяется, клик открывает и закрывает), `#` после названия (виден при наведении и у открытой) — `copyText(<адрес с
?product и якорем>)` → `copySay(a, ok, ok ? '# link copied ✓' : "# couldn't copy", '#')`; прямой заход и переход
роутером с якорем — `parseDeepLink` → нужный продукт, раскрыть, прокрутить в вид; несуществующая запись — ничего.

- [ ] **Шаг 4: тесты проходят и проверка в браузере** — Run: `npm test` → PASS; в браузере
  `/contact/?product=ui-factory#ki-3-no-support-for-unity-2021` открывает нужную запись, `?product=foo` — UI Line Chart.

- [ ] **Шаг 5: коммит**

```bash
git add data templates sass static/js tests
git commit -m "feat: contact lists known issues and faq per product with shareable anchors"
```

---

### Задача 12: проверка целиком

**Файлы:** без новых.

- [ ] **Шаг 1:** Run: `zola check` → Expected: `Done` без ошибок; `npm test` → все тесты PASS.
- [ ] **Шаг 2:** `zola serve`, браузер, ширина 375, 800 и 1100 px, обычный режим и эмуляция «уменьшить движение»:
  пройти все вкладки по шапке и по внутренним ссылкам, «назад» и «вперёд», выделение (интерфейс не выделяется,
  содержание выделяется), перетаскивание картинок, прямые адреса из «Адресов» спеки. Снимки приложить к отчёту.
- [ ] **Шаг 3:** сверить каждую английскую строку спеки из разделов вкладок с собранными страницами (скрипт поиска
  цитат `«…»` из спеки по `.test-public`); расхождения исправить.
- [ ] **Шаг 4:** коммит исправлений, если были: `git commit -m "fix: …"`; отчёт автору — что готово, что ждёт
  адресов и разрешений, что уходит в планы 2–7.
