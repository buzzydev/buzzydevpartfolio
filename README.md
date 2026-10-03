# Portfolio Website (Django 6)

Professional developer portfolio: jamoat sayti + custom dashboard + rank tizimi + Railway deploy.

## Features
- Home, About, Projects (+ detail `/projects/<slug>/`), Contact, Login/Logout
- Skills, Services, Experience, Stats, Social links, Website settings — hammasi dashboard orqali boshqariladi
- Custom User (`role` = rank), custom dashboard `/dashboard/`, Django admin `/admin/` (faqat superuser)
- Contact form: honeypot + imzolangan vaqt tokeni + IP bo'yicha limit (soatiga 3 ta)
- Login brute-force himoyasi (5 ta xato → 15 daqiqa blok), Admin Action Log (kim, nima, qachon, IP)
- SEO: dynamic title/description, Open Graph, Twitter Card, sitemap.xml, robots.txt
- Rasmlar avtomatik kichraytirilib WEBP ga o'giriladi, lazy loading, WhiteNoise

## Technologies
Python 3.13 (kamida 3.12), Django 6, PostgreSQL (production) / SQLite (local), Gunicorn, WhiteNoise, Pillow, django-environ.

## Local installation (Windows)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
`.env` faylini oching va to'ldiring:
```
SECRET_KEY=(pastdagi command natijasi)
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
```
SECRET_KEY yaratish:
```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Keyin:
```
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```
`seed_demo` — ixtiyoriy, namuna ma'lumotlarni qo'shadi. Sayt: http://127.0.0.1:8000/ , dashboard: http://127.0.0.1:8000/dashboard/ , admin: http://127.0.0.1:8000/admin/

## Superuser
`python manage.py createsuperuser` — masalan username `buzzy`. Parol faqat terminalda kiritiladi, kodga yozilmaydi.
Superuser avtomatik **Super Administrator** (rank 5) bo'ladi.

## Admin rank system
| Rank | Nomi | Imkoniyatlar |
|---|---|---|
| 1 | Moderator | Messages: ko'rish, read/unread |
| 2 | Editor | + Messages delete, Projects/Skills/Services/Experience/Stats/Social CRUD |
| 3 | Manager | + Users ko'rish, oddiy userlarni faollashtirish/o'chirish |
| 4 | Administrator | + Admins ko'rish (o'zidan past rankdagilarni deaktivatsiya), Website settings, Action logs |
| 5 | Super Administrator | Hammasi: admin yaratish, rank berish/o'zgartirish. Faqat Django superuser |

Rank berish faqat Super Administrator uchun: Dashboard → Admins. Rank `users.User.role` maydonida saqlanadi,
ruxsatlar `dashboard/permissions.py` dagi `SECTION_RANK` lug'atida (bir joyda o'zgartiriladi).

## Media files
Railway diskida fayllar deploydan keyin o'chib ketadi. Yechimlar:
1. **Cloudinary** (tavsiya): `pip install cloudinary django-cloudinary-storage`, ularni `requirements.txt` ga qo'shing, Railway Variables ga `CLOUDINARY_URL` qo'shing. `settings.py` buni avtomatik yoqadi.
2. Railway Volume ulash (pullik reja) — lekin Django media'ni production'da o'zi bermaydi, shuning uchun Cloudinary osonroq.

## GitHub
```
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```
`.env` `.gitignore` da — GitHub'ga ketmaydi. Push qilishdan oldin `git status` bilan tekshiring.

## Railway deployment
1. GitHub'da repository yarating va kodni push qiling.
2. railway.com da akkaunt oching → **New Project** → **Deploy from GitHub repo** → repositoryni tanlang.
3. Project ichida **+ New** → **Database** → **PostgreSQL**.
4. Django servisi → **Variables**:
   - `SECRET_KEY` = yangi tasodifiy kalit
   - `DEBUG` = `False`
   - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}` (Postgres servis nomiga mos)
   - `ALLOWED_HOSTS` = Railway domeningiz (masalan `myapp.up.railway.app`)
   - `CSRF_TRUSTED_ORIGINS` = `https://myapp.up.railway.app`
5. Servis → **Settings** → **Networking** → **Generate Domain**. Shu domenni 4-qadamdagi ikki o'zgaruvchiga yozing.
   (Railway `RAILWAY_PUBLIC_DOMAIN` ni o'zi beradi va `settings.py` uni avtomatik qo'shadi, lekin o'z domeningiz bo'lsa qo'lda yozing.)
6. Start command `Procfile` da: `collectstatic` → `migrate` → `gunicorn config.wsgi:application`. Alohida sozlash shart emas.
7. Deploy tugagach superuser yarating (Railway CLI): `railway link`, keyin `railway run python manage.py createsuperuser`
   (yoki servis → **Shell**, agar mavjud bo'lsa). Lokal `DATABASE_URL` ni Railway public URL ga o'zgartirib ham yaratish mumkin.
8. Saytni oching, `/login/` orqali kirib, `/dashboard/` ni tekshiring.

`git push` qilinganda Railway avtomatik qayta deploy qiladi.

## Production settings
`DEBUG=False` bo'lganda avtomatik yoqiladi: HTTPS redirect, secure cookie, HSTS, nosniff, X-Frame-Options DENY. Tekshirish:
`python manage.py check --deploy`

## Troubleshooting
- **DisallowedHost** — `ALLOWED_HOSTS` da domen yo'q.
- **CSRF verification failed** (production) — `CSRF_TRUSTED_ORIGINS` da `https://` bilan domen yozilmagan.
- **Missing staticfiles manifest entry** — `python manage.py collectstatic --noinput` ishlamagan.
- **ImproperlyConfigured: SECRET_KEY** — `.env` yo'q yoki `SECRET_KEY` bo'sh.
- **Rasmlar deploydan keyin yo'qoladi** — Cloudinary ulang (yuqoriga qarang).
- **PowerShell "running scripts is disabled"** — `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- **Logout 405** — logout faqat POST (dashboard va saytdagi tugma shuni ishlatadi).
- Login bloklangan bo'lsa 15 daqiqa kuting yoki serverni qayta ishga tushiring (cache xotirada).
