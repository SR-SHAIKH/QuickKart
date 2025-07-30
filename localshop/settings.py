import os
from pathlib import Path
from decouple import config  # use python-decouple for clean env management

BASE_DIR = Path(__file__).resolve().parent.parent

# Load secret values from .env
SECRET_KEY = config("SECRET_KEY", default="fallback-secret-key")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
RENDER_EXTERNAL_HOSTNAME = config("RENDER_EXTERNAL_HOSTNAME", default=None)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(str(RENDER_EXTERNAL_HOSTNAME))

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
    "django.contrib.sites",  # recommended if using email-related features
    "shop",
    "users",
    'widget_tweaks',
]

SITE_ID = 1

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

# PostgreSQL database with decouple
#for only render hosting
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            "sslmode": "require",
        },
    }
}

# #for local hosting server
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": config("DB_NAME"),
#         "USER": config("DB_USER"),
#         "PASSWORD": config("DB_PASSWORD"),
#         "HOST": config("DB_HOST"),
#         "PORT": config("DB_PORT", default="5432"),
#     }
# }

# # Only add SSL for production (Render)
# if os.environ.get("RENDER", None) == "true":
#     DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

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
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

# Custom authentication backend
AUTHENTICATION_BACKENDS = [
    'shop.auth_backends.EmailOrPhoneBackend',     # custom phone/email backend
    'django.contrib.auth.backends.ModelBackend',  # fallback username/password
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

# Cashfree settings using python-decouple config (reads from .env)
CASHFREE_APP_ID = config("CASHFREE_APP_ID", default="").strip()
CASHFREE_SECRET_KEY = config("CASHFREE_SECRET_KEY", default="").strip()
CASHFREE_ENV = config("CASHFREE_ENV", default="TEST").strip()
CASHFREE_PAYOUT_CLIENT_ID = config("CASHFREE_PAYOUT_CLIENT_ID", default="").strip()
CASHFREE_PAYOUT_CLIENT_SECRET = config("CASHFREE_PAYOUT_CLIENT_SECRET", default="").strip()
print("CASHFREE_PAYOUT_CLIENT_ID:", repr(CASHFREE_PAYOUT_CLIENT_ID))
print("CASHFREE_PAYOUT_CLIENT_SECRET:", repr(CASHFREE_PAYOUT_CLIENT_SECRET))
print("CASHFREE_APP_ID:", repr(CASHFREE_APP_ID))
print("CASHFREE_SECRET_KEY:", repr(CASHFREE_SECRET_KEY))
print("CASHFREE_ENV:", repr(CASHFREE_ENV))