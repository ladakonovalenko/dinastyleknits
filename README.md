# DinaStyleKnits — сайт для Digital-товарів

Багатосторінковий сайт-каталог в'язальних PDF-патернів з адмінкою для
самостійного керування товарами. Бекенд — FastAPI + SQLAlchemy + Postgres,
фронтенд — чистий HTML/CSS/JS (без фреймворків).

**Живий сайт:** https://dinastyleknits.vercel.app
**Бекенд/API:** https://dinastyleknits-api.onrender.com (Swagger: `/docs`)

## Структура проєкту

```
dinastyleknits/
├── backend/                 # FastAPI застосунок
│   ├── app/
│   │   ├── main.py           # точка входу, підключення роутерів
│   │   ├── config.py         # налаштування з .env
│   │   ├── database.py       # SQLAlchemy engine/session
│   │   ├── models.py         # Pattern, Subscriber, AdminUser, Post (заготовка)
│   │   ├── schemas.py        # Pydantic-схеми
│   │   ├── auth.py           # JWT-авторизація адмінки
│   │   ├── migrations.py     # легкі авто-міграції (як у StoryLore)
│   │   ├── seed_data.py      # наповнення/оновлення БД реальними даними з Etsy
│   │   └── routers/          # patterns.py, subscribers.py, auth_router.py
│   ├── static/images/        # фото 13 базових патернів (нові товари з адмінки
│   │                         # зберігаються як бінарні дані прямо в БД — Render
│   │                         # не має постійного диска на безкоштовному плані)
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 # статичний сайт
    ├── index.html             # Home (об'єднано з колишньою Patterns) + каталог
    ├── pattern-detail.html    # повна сторінка товару — наразі ніде не залінкована
    ├── new.html               # New releases (тільки is_new патерни)
    ├── blog.html              # відео-тьюторіали з YouTube-каналу
    ├── about.html             # про магазин (текст з Etsy, каруусель фото)
    ├── admin.html             # адмінка: CRUD патернів + перегляд підписників
    ├── 404.html               # кастомна сторінка "не знайдено" (підхоплює Vercel)
    ├── css/
    │   ├── style.css          # спільна дизайн-система (кольори/типографіка/адаптив)
    │   ├── about.css           # стилі каруселі й розкладки About
    │   ├── blog.css            # стилі сітки відео
    │   └── admin.css           # стилі адмін-панелі
    ├── js/
    │   ├── config.js           # API_BASE_URL
    │   ├── api.js               # усі виклики до бекенду в одному місці
    │   ├── layout.js             # спільна шапка/футер, соцмережі
    │   ├── pattern-card.js       # рендер картки товару (Home, New)
    │   ├── pattern-detail.js     # рендер сторінки товару
    │   ├── home.js / new.js      # завантаження й рендер сітки патернів
    │   ├── subscribe.js          # форма підписки
    │   ├── about.js              # каруусель фото на About
    │   ├── blog.js                # список відео (масив у коді, редагується вручну)
    │   └── admin.js                # логіка адмінки (логін, CRUD, підписники)
    └── static/images/           # емблема, іконки соцмереж, фото About, hero-ілюстрація
                                  # (фото самих 13 товарів — у backend/static/images)
```

## Запуск бекенду (локально)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # опційно, але рекомендовано
pip install -r requirements.txt

cp .env.example .env
# відкрити .env і задати ADMIN_EMAIL / ADMIN_PASSWORD / JWT_SECRET

python3 -m app.seed_data      # створює БД, наповнює 13 патернами + адмін-акаунт
python3 -m uvicorn app.main:app --reload --port 8000
```

Після старту:
- API: http://127.0.0.1:8000
- Swagger: **http://127.0.0.1:8000/docs**

## Запуск фронтенду (локально)

```bash
cd frontend
python3 -m http.server 3000
```

Відкрити http://127.0.0.1:3000/index.html

⚠️ Для локального тестування тимчасово змінити `API_BASE_URL` у
`frontend/js/config.js` на `http://127.0.0.1:8000`, а перед комітом
**обов'язково повернути** на продакшн-URL Render — легко забути й
закомітити локальну адресу за замовчуванням.

## Адмінка

- URL: `/admin.html` (не в публічній навігації — посилання дається лише замовниці)
- Email/пароль — ті, що задані в Environment Variables на Render
  (`ADMIN_EMAIL` / `ADMIN_PASSWORD`)
- Вкладка **Patterns** — додати/редагувати/видалити товар (назва, ціна,
  посилання на Etsy, опис, фото, перемикач "New")
- Вкладка **Subscribers** — список email з форми підписки + кнопка експорту в CSV
- Фото нових товарів зберігаються прямо в Postgres (не на диску) — див.
  коментар у `models.py` (`Pattern.image_url`) щодо причини цього рішення

## Деплой

- **Фронтенд:** Vercel, Root Directory = `frontend`, автодеплой при push у `main`
- **Бекенд:** Render Web Service, Root Directory = `backend`,
  Start Command = `python -m app.seed_data && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  (seed запускається на кожному старті, ідемпотентно — оновлює лише
  ціну/назву/посилання існуючих патернів, не чіпає фото/опис/is_new)
- **БД:** спільна Postgres-інстанція з проєктом StoryLore (той самий Render-акаунт)

## Що вже реалізовано

- ✅ Повна модель даних: Pattern (з фото як BLOB для нових товарів), Subscriber,
  AdminUser, Post (заготовка під текстовий блог)
- ✅ JWT-авторизація єдиного адмін-акаунта
- ✅ Повний CRUD патернів + завантаження фото, і публічні read-ендпоінти
- ✅ Адмінка з UI (не тільки Swagger) — патерни й підписники
- ✅ 7 сторінок фронтенду: Home (з каталогом), New, Blog (реальні відео),
  About (реальний текст+фото), Admin, 404, орфанна pattern-detail
- ✅ Мобільно-дружня верстка, перевірена на ширинах 320–640px без горизонтального скролу
- ✅ Open Graph теги на публічних сторінках (превʼю при поширенні в соцмережах)
- ✅ Реальні 13 патернів з Etsy (ціни й фото звірені й виправлені після плутанини)

## Що ще в розробці / чекає на замовницю

- 🔲 Домен/хостинг (чекаємо інформацію від розробника основного сайту)
- 🔲 3 фото-аватарки на About (сама Діна + команда) — замовниця надішле пізніше
- 🔲 Повний список відео для Blog — зараз лише 4, знайдені вручну через пошук
  (YouTube блокує автоматичний перегляд повного списку каналу)
- 🔲 Інтеграція розсилки з реальним email-сервісом (поки просто збір бази)
- 🔲 Описи товарів (`description` поки порожнє в більшості патернів)
- 🔲 Текстовий блог (модель `Post` готова, фронтенду немає — зараз тільки відео)
