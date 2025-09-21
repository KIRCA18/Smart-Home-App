import os
from datetime import timedelta

from celery import Celery

from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarthomeapp.settings')

app = Celery('smarthomeapp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'evaluate-scheduled-rules-every-minute': {
        'task': 'base.tasks.evaluate_scheduled_rules',
        'schedule': crontab(minute='*'),  # every minute
        # 'schedule': timedelta(seconds=15)
    },
    'find_offline_devices': {
        'task': 'base.tasks.find_offline_devices',
        'schedule': crontab(minute='*/2')
    },
    'heart_beat': {
        'task': 'base.tasks.heart_beat',
        'schedule': crontab(minute='*')
    }
}
