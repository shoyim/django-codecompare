"""Development settings."""
from config.settings.base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "dev-insecure-key-change-before-production"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}  # noqa: F405

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
