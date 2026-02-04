# core/celery.py
import os
from celery import Celery

# 1. Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelliresearchhub.settings')

# 2. Create the app instance
app = Celery('intelliresearchhub')

# 3. Load config from Django settings (using the namespace 'CELERY')
# This means variables in settings.py must start with CELERY_ (e.g., CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. Auto-discover tasks in all installed apps (looks for tasks.py)
app.autodiscover_tasks()