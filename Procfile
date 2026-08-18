release: python manage.py migrate --noinput && python manage.py
create_default_superuser
web: gunicorn hair_studio_scheduler.wsgi --bind 0.0.0.0:$PORT

