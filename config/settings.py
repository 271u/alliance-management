from pathlib import Path

import sentry_sdk
import logging

from helpers.env import env_bool, env_list
import os


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-secret-key")
DEBUG = env_bool("DJANGO_DEBUG", False)

logging_time_format = "" if env_bool("RUNNING_IN_CONTAINER", False) else "%(asctime)s "

if DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format=logging_time_format + "[%(levelname)s] (%(filename)s:%(lineno)d in %(funcName)s) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
else:
    logging.basicConfig(
    level=logging.INFO,
    format=logging_time_format + "[%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_LOGGING = env_bool("SENTRY_LOGGING", False)
ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)

CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Optional but useful for admin/site-aware setups
    "django.contrib.sites",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.openid_connect",

    "core.apps.CoreConfig",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    
    # Serve collected static files in production
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.audit_context.AuditContextMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Require login by default
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    # Required by django-allauth
    "allauth.account.middleware.AccountMiddleware",
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",  # required by allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.player_sync_status", # Player Sync Status
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("SQLITE_PATH", BASE_DIR / "data" / "db.sqlite3"),
    }
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Fine for local demo. Tighten this later.
ACCOUNT_EMAIL_VERIFICATION = "none"

SESSION_COOKIE_AGE = 60 * 60 * 8  # 8 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

OIDC_PROVIDER_ID = "oidc"
OIDC_PROVIDER_NAME = os.getenv("OIDC_PROVIDER_NAME", "OIDC Login")

SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "OAUTH_PKCE_ENABLED": True,
        "APPS": [
            {
                "provider_id": OIDC_PROVIDER_ID,
                "name": OIDC_PROVIDER_NAME,
                "client_id": os.getenv("OIDC_CLIENT_ID", ""),
                "secret": os.getenv("OIDC_CLIENT_SECRET", ""),
                "settings": {
                    "server_url": os.getenv("OIDC_SERVER_URL", ""),
                    "fetch_userinfo": True,
                    "oauth_pkce_enabled": True,
                    "scope": ["openid", "profile", "email", "groups"],
                    "token_auth_method": os.getenv(
                        "OIDC_TOKEN_AUTH_METHOD",
                        "client_secret_basic",
                    ),
                    "uid_field": "sub",
                },
            }
        ],
    }
}

# Only use OIDC/social login, no local username/password signup flow
SOCIALACCOUNT_ONLY = True

# Try to create users automatically from OIDC claims
SOCIALACCOUNT_AUTO_SIGNUP = True

ACCOUNT_LOGIN_METHODS = {"email"}

# Do not require email confirmation for this app
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"

# Important with recent allauth versions:
# avoid requiring local signup-form fields like username/password
ACCOUNT_SIGNUP_FIELDS = ["email*"]

# Optional, but useful if your OIDC provider is trusted and may return
# an email that already exists on a local Django user.
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

def env_set(name: str, default: str = "") -> set[str]:
    return {
        item.strip()
        for item in os.getenv(name, default).split(",")
        if item.strip()
    }


if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment="production" if DEBUG else "development",
        auto_session_tracking=False,  # GlitchTip does not support sessions
        enable_logs=SENTRY_LOGGING,
    )

OIDC_GROUPS_CLAIM = "groups"

OIDC_USER_GROUPS = env_set("OIDC_USER_GROUP", "server-management")
OIDC_SUPERUSER_GROUPS = env_set("OIDC_ADMIN_GROUP", "server-superuser")

SOCIALACCOUNT_ADAPTER = "core.adapters.OIDCGroupSocialAccountAdapter"
