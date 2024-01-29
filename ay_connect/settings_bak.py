"""
Django settings for ay_connect project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from sqlalchemy import create_engine

import pandas as pd




LOCAL_DEV_XXERP = create_engine("""""")
    

LOCAL_DEV_XXERP = create_engine("""""")



LOCAL_DEV_XXERP_ORA = str(LOCAL_DEV_XXERP.url).split("oracle+cx_oracle://")[1].replace(':','/')
#print(LOCAL_DEV_XXERP_ORA)
CURRENT_DB_ENGINE=LOCAL_DEV_XXERP #TEST_APPS
ENGINE = LOCAL_DEV_XXERP
DEV_BOOLINF= LOCAL_DEV_XXERP





from pathlib import Path
import os
import environ
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-f8k)eq6szikr6@(-$=$o0&dtfgp)ycvogbjq$gbs)4eo8f1st7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'leads',
    'quotation',
    'core',
    'simple_history',
    'customer',
    'product',
    'invoice',
    'saleswores',
    'sales',
    'accountant_dash',
    'adv_tax_invoice',
    'inventory_transfers',
    'rest_framework_datatables',
    'accounts',
    'crequest'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'crequest.middleware.CrequestMiddleware'
]
X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'ay_connect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'ay_connect.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env('DATABASE_ENGINE'),
        'NAME':  'ayconnect2',  #env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST':  '192.168.16.129', #env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT')
    }
}
# DATABASES = {    'default': {        'ENGINE': 'django.db.backends.mysql',        'NAME': 'ay_connect',        'USER': 'root',        'PASSWORD': '',        'HOST': 'localhost',        'PORT': '3306'    }}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

#STATIC_ROOT = os.path.join(BASE_DIR,'static')

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), BASE_DIR / "static",
]
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LDAP_URL='ldap://AYDXBDC03.alyousuf.net'
AUTH_LDAP_START_TLS = False
AUTH_LDAP_ALWAYS_UPDATE_USER = False
AUTH_LDAP_SERVER_URI = LDAP_URL
AUTH_LDAP_BIND_DN = ''
AUTH_LDAP_BIND_PASSWORD = ''
AUTH_LDAP_USER_SEARCH = LDAPSearch("DC=alyousuf,DC=net",
                                   ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0,
}

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "photo": "thumbnailPhoto",
    "emp_id": "employeeID"
}

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    'core.auth_backend.ForceAuth'
)
LOGIN_URL = '/'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 50,
}
