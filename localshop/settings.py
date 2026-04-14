import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Detect if running on Render
IS_RENDER = os.environ.get("RENDER") is not None

# Load .env strictly if we are NOT on Render (i.e. local) and file exists
if not IS_RENDER:
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(env_path)


# Load secret values from .env
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if IS_RENDER:
    DEBUG = True
    ALLOWED_HOSTS = [os.environ.get("RENDER_EXTERNAL_HOSTNAME")]
else:
    DEBUG = os.getenv("DEBUG", "True") == "True"
    ALLOWED_HOSTS = ["*"]  # Allow all locally


_csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "https://*.onrender.com")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(",") if o.strip()]



# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Installed apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop",
    "users",
    'widget_tweaks',
]



# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "localshop.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, 'shop/templates')],
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

WSGI_APPLICATION = "localshop.wsgi.application"

# Database Configuration
# Use DATABASE_URL for production (Render), fallback to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Production (Render)
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL)
    }
else:
    # Local fallback
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")


# Custom authentication backend
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Redirect if login required
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/shop/'  # Default redirect for shop owners

# Logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "error.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cashfree Settings
CASHFREE_APP_ID = os.getenv("CASHFREE_APP_ID", "").strip()
CASHFREE_SECRET_KEY = os.getenv("CASHFREE_SECRET_KEY", "").strip()
CASHFREE_ENV = os.getenv("CASHFREE_ENV", "TEST").strip()
CASHFREE_PAYOUT_CLIENT_ID = os.getenv("CASHFREE_PAYOUT_CLIENT_ID", "").strip()
CASHFREE_PAYOUT_CLIENT_SECRET = os.getenv("CASHFREE_PAYOUT_CLIENT_SECRET", "").strip()