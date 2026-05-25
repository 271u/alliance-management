from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

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

    "core",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Require login by default
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    # Required by django-allauth
    "allauth.account.middleware.AccountMiddleware",
]

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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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

# Do not require email confirmation for this app
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"

# Important with recent allauth versions:
# avoid requiring local signup-form fields like username/password
ACCOUNT_SIGNUP_FIELDS = ["email"]

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


OIDC_GROUPS_CLAIM = "groups"

OIDC_USER_GROUPS = env_set("OIDC_USER_GROUP", "271u-management")
OIDC_SUPERUSER_GROUPS = env_set("OIDC_ADMIN_GROUP", "271u-superuser")

SOCIALACCOUNT_ADAPTER = "core.adapters.OIDCGroupSocialAccountAdapter"
