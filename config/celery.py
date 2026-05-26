"""Celery application configuration."""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("codecompare")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["codecompare.tasks"])
