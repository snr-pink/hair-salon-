# Bella's Hair Studio &mdash; Scheduling App

A Django web app for booking hair salon appointments. Customers can sign up, browse
services and stylists, book appointments, and cancel them. Staff manage stylists,
services, and bookings through the Django admin panel. The booking form blocks
double-booking automatically by checking stylist availability.

## Tech stack
- Python 3.12, Django 6.1
- SQLite for local development, PostgreSQL-ready for production (via `dj-database-url`)
- `whitenoise` for serving static files in production
- `gunicorn` as the production WSGI server

## Project structure
```
hair_studio_scheduler/
├── hair_studio_scheduler/   # project settings, urls, wsgi
├── scheduler/                # app: models, views, forms, admin, urls
├── templates/                 # base.html, scheduler/, registration/
├── static/css/style.css       # theme
├── requirements.txt
├── Procfile                   # for Render/Railway/Heroku-style platforms
├── runtime.txt
└── manage.py
```

## Run it locally

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. (Optional) load sample services/stylists:
   ```bash
   python manage.py shell < seed_data.py
   ```
5. Create an admin account:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the dev server:
   ```bash
   python manage.py runserver
   ```
   Visit http://127.0.0.1:8000/ — admin panel is at http://127.0.0.1:8000/admin/

## Deploying to Render (free tier) — step by step

Render is the easiest free option for a Django app like this one. This app is already
configured for it (`Procfile`, `whitenoise`, `dj-database-url`, env-based settings).

1. **Put the code on GitHub.**
   - Go to https://github.com/new, create a new repository (e.g. `hair-studio-scheduler`).
   - In the project folder, run:
     ```bash
     git init
     git add .
     git commit -m "Initial commit"
     git branch -M main
     git remote add origin https://github.com/<your-username>/hair-studio-scheduler.git
     git push -u origin main
     ```

2. **Create a Render account.** Go to https://render.com and sign up (free, can use your GitHub account).

3. **Create a PostgreSQL database.**
   - In the Render dashboard: **New +** → **PostgreSQL**.
   - Give it a name (e.g. `hair-studio-db`), pick the free plan, click **Create Database**.
   - Once created, copy the **Internal Database URL** shown on its page — you'll need it in step 5.

4. **Create a Web Service.**
   - **New +** → **Web Service** → connect your GitHub account → select the repo you pushed.
   - Render should detect Python automatically. Set:
     - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
     - **Start Command:** `gunicorn hair_studio_scheduler.wsgi --bind 0.0.0.0:$PORT`
   - Choose the **Free** instance type.

5. **Add environment variables** (in the Web Service's **Environment** tab):
   | Key | Value |
   |---|---|
   | `SECRET_KEY` | any long random string (e.g. generate one at https://djecrety.ir) |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `<your-app-name>.onrender.com` (Render also shows you this) |
   | `DATABASE_URL` | paste the Internal Database URL from step 3 |

6. **Deploy.** Click **Create Web Service**. Render will build and deploy automatically.
   Migrations run on release via the `Procfile`'s `release:` line.

7. **Create your admin user on the live site.** In the Render dashboard, open your
   Web Service → **Shell** tab, and run:
   ```bash
   python manage.py createsuperuser
   ```

8. **Visit your live URL** — it'll be `https://<your-app-name>.onrender.com`.

That's it — from here on, every `git push` to `main` auto-deploys the latest version.

### Notes
- Render's free web service spins down after inactivity and takes ~30–60s to wake back
  up on the next request — normal for the free tier, not a bug.
- Free Postgres databases on Render expire after 90 days; upgrade or recreate as needed
  for anything beyond a demo/school project.
