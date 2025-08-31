"""
Django settings for ward_system project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# Security
# -------------------------
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY and DEBUG is False:
    raise RuntimeError("SECRET_KEY must be set in production")
if not SECRET_KEY:
    SECRET_KEY = 'dev-insecure-secret'
_allowed = [h for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h]
_render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if _render_host:
    _allowed.append(_render_host)
ALLOWED_HOSTS = _allowed or (['*'] if DEBUG else [])

# -------------------------
# Database
# -------------------------
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

# -------------------------
# Applications
# -------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'accounts',
    'residents',
    'letters',
    'communications',
    'visitors',
    'utils',
    'whitenoise.runserver_nostatic',  # Added for WhiteNoise
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Inserted WhiteNoise middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ward_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ward_system.wsgi.application'

# -------------------------
# Security headers / CSRF / Proxy
# -------------------------
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
CSRF_TRUSTED_ORIGINS = [
    'https://' + h for h in ALLOWED_HOSTS if h and not h.startswith('*')
] + ['https://*.onrender.com']

# -------------------------
# Password validation
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------
# Internationalization
# -------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------
# Static and Media Files
# -------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Use hashed & compressed static files in production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------------
# Crispy Forms
# -------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# -------------------------
# Authentication
# -------------------------
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'accounts.User'

# -------------------------
# Default primary key field type
# -------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
