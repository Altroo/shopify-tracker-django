from pathlib import Path
from os import path


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-9#=a^-4sb&7zd*e4@0t8#_%*daz8tco6^6d2+0pdfqe%y5ezq#'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# SSL secure proxy config
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https"
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'daphne',
    'django.contrib.staticfiles',
    # 'django.contrib.sites',
    'django.contrib.postgres',
    'corsheaders',
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'shops.apps.ShopsConfig',
    'products.apps.ProductsConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
)

ROOT_URLCONF = 'shopify_tracker_backend.urls'
ASGI_APPLICATION = 'shopify_tracker_backend.asgi.application'
WSGI_APPLICATION = 'shopify_tracker_backend.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'shopify_tracker_db',
        'USER': 'vd5obg3d9i5k',
        'PASSWORD': '5Ybd1sZh43wjl',
        'HOST': 'localhost',
        'PORT': '',
    },
}

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
# STATIC_ROOT = path.join(BASE_DIR, "static")
# Static & media files config
STATIC_PATH = path.join(BASE_DIR, "static")
STATICFILES_DIRS = (
    path.join(BASE_DIR, "static"),
)
MEDIA_ROOT = path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

# Rest framework config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_PERMISSION_CLASSES': ("rest_framework.permissions.IsAuthenticated",),
    'DEFAULT_PAGINATION_CLASS': "rest_framework.pagination.PageNumberPagination",
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': ("rest_framework.renderers.JSONRenderer",),
    'DEFAULT_SCHEMA_CLASS': "rest_framework.schemas.coreapi.AutoSchema",
    'DEFAULT_FILTER_BACKENDS': "django_filters.rest_framework.DjangoFilterBackend",
    'TOKEN_MODEL': None,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': 60,
    'REFRESH_TOKEN_LIFETIME': 365,
    'BLACKLIST_AFTER_ROTATION': False,
    'ROTATE_REFRESH_TOKENS': False,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis config
REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': "channels_redis.core.RedisChannelLayer",
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}
# Celery
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
