"""
Django settings for gather project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q*a@dd=d-d^2p#+$%an3q#d^ww0i3csc)-ev4%nd+4(b72i70x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

LOGIN_URL = '/accounts/login/'

ADMINS = (
    ('zhangbo', '413761980@qq.com'),
)
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
)

ROOT_URLCONF = 'gather.urls'

WSGI_APPLICATION = 'gather.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gather',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '115.29.76.132',
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Chongqing'

USE_I18N = True

USE_L10N = True

# USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
STATIC_ROOT = os.path.join(os.path.join(BASE_DIR, ".."), 'static')


STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, os.path.join(os.pardir, "media"))

MEDIA_URL = "/media/"

SERVER_EMAIL = 'gather_jacsice@163.com'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'gather_jacsice@163.com'
EMAIL_HOST_PASSWORD = 'gather_zhangbo'
# EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'gather_jacsice@163.com'

# logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        # 'special': {
        #     '()': 'project.logging.SpecialFilter',
        #     'foo': 'bar',
        # }
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false']
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/wei_debug.log'),
            'formatter': 'verbose',
        },
        'info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/wei_info.log'),
            'formatter': 'verbose',
        },
        'err': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/wei_err.log'),
            'formatter': 'verbose',
        },
        'statistics': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/statistics.log'),
            'formatter': 'verbose',
        },
        
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'gather': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            # 'filters': ['special']
        },
        'debug': {
            'handlers': ['debug'],
            'level': 'DEBUG',
        },
        'info': {
            'handlers': ['info'],
            'level': 'INFO',
        },
        'err': {
            'handlers': ['err'],
            'level': 'ERROR',
        },
        'statistics': {
            'handlers': ['statistics'],
            'level': 'INFO',
        },
        'allinpay': {
            'handlers': ['allinpay'],
            'level': 'INFO',
        },
        'api': {
            'handlers': ['api'],
            'level': 'DEBUG',
        },
    }
}
# admin页面时间格式
DATETIME_FORMAT = 'Y-m-d'

SESSION_COOKIE_AGE = 60 * 60 * 2
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# django-celery
# CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
# BROKER_URL = 'redis://localhost:6379/0'
# CELERY_DISABLE_RATE_LIMITS = True
