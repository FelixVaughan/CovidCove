python3 manage.py collectstatic
python3 crontab add
gunicorn --workers 3 -b 0.0.0.0:8000 CovidCove.wsgi:application
