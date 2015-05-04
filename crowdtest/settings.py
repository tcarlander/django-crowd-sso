"""
Django settings for crowdtest project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y4ul1)#cgvl^-6#hri@ifxzp+gk80*$(tzy5r=u11zytto8gb0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


CROWD_PROD = { 
    'url': 'http://login.q.wfp.org/crowd/rest',         # your CROWD rest API url
    'app_name': 'mdca-test',                            # appname, registered with CROWD
    'password': 'mdca-test',                            # correct password for provided appname
    'superuser': True,                                  # if set makes CROWD-authorized users superusers;
    'staffuser': True,                                  # BE CAREFUL WITH THIS PARAMETER!
    'group-import':False,
    'validation':'10.11.40.34',
}

CROWD_DEV = {
    'url': 'http://login.dev.wfptha.org/crowd/rest',    # your CROWD rest API url
    'app_name': 'toby-test',                            # appname, registered with CROWD
    'password': 'toby-test',                            # correct password for provided appname
    'superuser': True,                                  # if set makes CROWD-authorized users superusers;
    'staffuser': True,                                  # BE CAREFUL WITH THIS PARAMETER!
    'group-import':False,
    'validation':'127.0.0.1',
}
#CROWD = CROWD_DEV
CROWD = CROWD_PROD

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'hello_crowd',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django-crowd.crowd.middleware.CookieMiddleware',
)
AUTHENTICATION_BACKENDS = (
    # ...
    'django-crowd.crowd.backends.CrowdBackend',
    'django.contrib.auth.backends.ModelBackend',
)
ROOT_URLCONF = 'crowdtest.urls'

WSGI_APPLICATION = 'crowdtest.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'mysite.log',
            'formatter': 'verbose'
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django-crowd': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}