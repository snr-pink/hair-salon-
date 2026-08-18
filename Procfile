release: python manage.py migrate --noinput
web: gunicorn hair_studio_scheduler.wsgi --bind 0.0.0.0:$PORT
