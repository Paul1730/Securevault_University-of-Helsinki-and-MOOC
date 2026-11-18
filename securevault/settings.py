"""SecureVault settings - Created by Pablo Landos (Cyber Security Base, Course Project I)."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-course-project-only-do-not-use-in-production"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "vault",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "securevault.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "securevault.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# FLAW 4 (A07:2021 Identification and Authentication Failures): all password validators are
# disabled, so 1-character passwords such as "a" are accepted.
AUTH_PASSWORD_VALIDATORS = []  # [vulnerable]

# FIX FOR FLAW 4: re-enable the four validators (delete the empty list above, uncomment this).
# AUTH_PASSWORD_VALIDATORS = [
#     {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

# FLAW 5 (A09:2021 Security Logging and Monitoring Failures): no LOGGING configuration exists,
# so nothing is written to a security audit log.

# FIX FOR FLAW 5: uncomment to write security events to security.log and the console.
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "audit": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
#     },
#     "handlers": {
#         "file": {
#             "class": "logging.FileHandler",
#             "filename": BASE_DIR / "security.log",
#             "formatter": "audit",
#         },
#         "console": {"class": "logging.StreamHandler", "formatter": "audit"},
#     },
#     "loggers": {
#         "security": {"handlers": ["file", "console"], "level": "INFO", "propagate": False},
#     },
# }
