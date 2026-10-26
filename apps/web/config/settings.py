"""Environment-driven Django settings for the GrowthTwin web application."""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def required_setting(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise ImproperlyConfigured(f"Set the {name} environment variable.")
    return value


SECRET_KEY = required_setting("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "growthtwin.apps.GrowthTwinConfig",
    "growthtwin.modules.assets.apps.AssetsConfig",
    "growthtwin.modules.approvals.apps.ApprovalsConfig",
    "growthtwin.modules.workspaces.apps.WorkspacesConfig",
    "growthtwin.modules.campaigns.apps.CampaignsConfig",
    "growthtwin.modules.connections.apps.ConnectionsConfig",
    "growthtwin.site.apps.SiteConfig",
    "growthtwin.demo.apps.DemoConfig",
]

MIDDLEWARE = [
    "growthtwin.modules.connections.middleware.LocalOAuthHeadersMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "growthtwin.modules.assets.middleware.ClosedSyntheticMaterialIntakeMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": required_setting("POSTGRES_DB"),
            "USER": required_setting("POSTGRES_USER"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "tr-tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "false").lower() in {
    "1",
    "true",
    "yes",
}
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0"))
secure_cookies = os.environ.get("DJANGO_SECURE_COOKIES", "false").lower() in {
    "1",
    "true",
    "yes",
}
SESSION_COOKIE_SECURE = secure_cookies
CSRF_COOKIE_SECURE = secure_cookies
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
X_FRAME_OPTIONS = "DENY"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "demo:profile-edit"
LOGOUT_REDIRECT_URL = "login"

GOOGLE_ADS_LOCAL_OAUTH_ENABLED = (
    os.environ.get("GOOGLE_ADS_LOCAL_OAUTH_ENABLED") == "true"
)
GOOGLE_ADS_LOCAL_OWNER_ID = os.environ.get("GOOGLE_ADS_LOCAL_OWNER_ID", "")
GOOGLE_ADS_LOCAL_WORKSPACE_ID = os.environ.get("GOOGLE_ADS_LOCAL_WORKSPACE_ID", "")
GOOGLE_ADS_LOCAL_TEST_CUSTOMER_ID = os.environ.get(
    "GOOGLE_ADS_LOCAL_TEST_CUSTOMER_ID", ""
)
GOOGLE_ADS_LOCAL_TEST_MANAGER_ID = os.environ.get(
    "GOOGLE_ADS_LOCAL_TEST_MANAGER_ID", ""
)

GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED = (
    os.environ.get("GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED") == "true"
)

# Fixed-fixture owner journey only; unrelated to Google authorization/execution.
SYNTHETIC_CLOSURE_UI_ENABLED = os.environ.get("SYNTHETIC_CLOSURE_UI_ENABLED") == "true"

# Callback URLs may contain one-time codes. Apply before handler formatting;
# reverse-proxy access logs still require separate controls before deployment.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "oauth_callback": {
            "()": "growthtwin.modules.connections.logging.OAuthCallbackFilter"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["oauth_callback"],
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# Internal rehearsal only; enable explicitly with isolated test settings.
SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED = False
SYNTHETIC_CONNECTOR_UI_ENABLED = False

# Closed scoped candidate flow; never adopt an existing grant implicitly.
GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED = False
GOOGLE_ADS_SCOPED_ENDPOINTS_ENABLED = False
GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED = False
GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED = False
GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED = False

# No routes or customer bytes; generated-image rehearsal only.
SYNTHETIC_MATERIAL_BINARY_REHEARSAL_ENABLED = False
SYNTHETIC_MATERIAL_PERSISTENCE_ENABLED = False
SYNTHETIC_CAMPAIGN_DESIGN_ENABLED = False
SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED = False
SYNTHETIC_BRAND_COPY_APPLY_ENABLED = False

# One explicitly admitted local workspace; fixed fictional text, never free input.
LOCAL_HOSTED_TEXT_TRIAL_ENABLED = False
LOCAL_HOSTED_TEXT_TRIAL_WORKSPACE_ID = None
LOCAL_HOSTED_IMAGE_TRIAL_ENABLED = False
LOCAL_HOSTED_AD_DRAFT_ENABLED = False
LOCAL_HOSTED_AD_CAMPAIGN_ENABLED = False
LOCAL_BRAND_PRODUCTION_BRIEF_ENABLED = False
LOCAL_BRAND_AI_ENABLED = False
LOCAL_BRAND_AI_APPROVED_REQUESTS = {}
LOCAL_BRAND_AD_ENABLED = False
