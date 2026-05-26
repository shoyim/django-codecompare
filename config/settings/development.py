"""Development settings."""
from config.settings.base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "dev-insecure-key-change-before-production"

CORS_ALLOW_ALL_ORIGINS = True

