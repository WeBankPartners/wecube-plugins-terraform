"""
Django settings for wecube_plugins_terraform project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

SECRET_KEY = 'y%nm(%vdc8w6o%lm0-=g$bxretg3(&%#ao8@dm!j#^-hl9u!+j'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_BASE_PATH = os.path.join(BASE_DIR, 'logs')
KEY_BASE_PATH = os.path.join(BASE_DIR, 'key')
YAML_TMP_PATH = os.path.join(LOG_BASE_PATH, "yamlfiles")
CAFILE_PATH = os.path.join(BASE_DIR, 'cafile')
TERRFORM_BIN_PATH = os.path.join(BASE_DIR, "bin/terraform")
TERRAFORM_BASE_PATH = os.path.join(BASE_DIR, "terraform")

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
]

MIDDLEWARE = [
    'wecube_plugins_terraform.logger_middleware.logger_middleware',
    'django.middleware.security.SecurityMiddleware'
]

from ._config import *

if not os.path.exists(TERRFORM_BIN_PATH):
    TERRFORM_BIN_PATH = "/usr/bin/terraform"

if not os.path.exists(TERRFORM_BIN_PATH):
    TERRFORM_BIN_PATH = "terraform"

ROOT_URLCONF = 'wecube_plugins_terraform.urls'
WSGI_APPLICATION = 'wecube_plugins_terraform.wsgi.application'
ALLOWED_HOSTS = ["*"]
DEFAULT_CHARSET = 'UTF-8'
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
STATIC_URL = '/static/'
USE_I18N = True
USE_L10N = True
USE_TZ = True
