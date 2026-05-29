import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from urllib.parse import unquote, urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------
# ðŸ” SECRET & DEBUG
# -----------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    os.getenv("RENDER_EXTERNAL_HOSTNAME", ""),
    "localhost",
    "127.0.0.1",
]

# -----------------------------------------
# ðŸ“¦ STATIC & MEDIA (Render)
# -----------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Whitenoise (obrigatÃ³rio no Render)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # âœ” serve static no Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -----------------------------------------
# ðŸ—„ï¸ DATABASE â€“ AUTO pelo RENDER / fallback
# -----------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    parsed_db_url = urlparse(DATABASE_URL)
    if parsed_db_url.scheme not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured("MySQL foi removido do sistema. Configure DATABASE_URL com PostgreSQL.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": parsed_db_url.hostname or "",
            "PORT": str(parsed_db_url.port or "5432"),
            "NAME": (parsed_db_url.path or "/").lstrip("/"),
            "USER": unquote(parsed_db_url.username or ""),
            "PASSWORD": unquote(parsed_db_url.password or ""),
            "OPTIONS": {"sslmode": "require"},
            "CONN_MAX_AGE": 600,
        }
    }
else:
    # fallback local
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "dpg-d8c7mmgjo6nc73ekgodg-a.oregon-postgres.render.com",
            "PORT": "5432",
            "NAME": "gcondid_db_fbeg",
            "USER": "gcondid_db_fbeg_user",
            "PASSWORD": "FjI4HL6dWzR1D7P775FTwavPDCDYLwV4",
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    }
# -----------------------------------------
# ðŸ“© EMAIL (SMTP)
# -----------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# -----------------------------------------
# ðŸ’¬ WHATSAPP META API
# -----------------------------------------

WHATSAPP_PROVIDER = os.getenv("WHATSAPP_PROVIDER", "meta")
WHATSAPP_META_API = os.getenv("WHATSAPP_META_API", "")
WHATSAPP_META_TOKEN = os.getenv("WHATSAPP_META_ACCESS_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
WHATSAPP_WEBHOOK_URL = os.getenv("WHATSAPP_WEBHOOK_URL", "")

WHATSAPP_SEND_URL = (
    f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
    if WHATSAPP_PHONE_ID else ""
)

# -----------------------------------------
# ðŸ” PASSWORD VALIDATION
# -----------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------
# ðŸŒŽ CONFIGURAÃ‡Ã•ES GERAIS
# -----------------------------------------

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = 'users.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


# -----------------------------------------
# ðŸ“ APPS & TEMPLATES
# -----------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    'users',
    'estoque',
    'chamados',
    'dashboard',
    'relatorios',
]

ROOT_URLCONF = "gcondid.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gcondid.wsgi.application"



