import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ats_scanner.settings')

app = Celery('ats_scanner')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
