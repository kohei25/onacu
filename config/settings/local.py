from .common import *

DEBUG = True

ALLOWED_HOSTS = [
  '0.0.0.0',
  '127.0.0.1',
  'localhost',
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'postgres',
    'USER': 'postgres',
    'HOST': 'db',
    'PORT': 5432,
    'PASSWORD': 'somepassword',
  }
}

SASS_PROCESSOR_ROOT = os.path.join(BASE_DIR, 'staticfiles')
SASS_PROCESSOR_AUTO_INCLUDE = False
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]
SASS_PRECISION = 5
SASS_OUTPUT_STYLE = 'compressed'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Emailをコンソールに表示