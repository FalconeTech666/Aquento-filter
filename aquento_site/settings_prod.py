from .settings_base import *

DEBUG = False

ALLOWED_HOSTS = ["aquento.com", "www.aquento.com"]  # потом добавишь IP/домен

# ОБЯЗАТЕЛЬНО: нормальный секретный ключ из env
import os
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_SSL_REDIRECT = True
