from .common import *

DEBUG = False

ALLOWED_HOSTS = [
  'onacu-staging.ap-northeast-1.elasticbeanstalk.com',
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
    }
}

# STATICFILES_STORAGE = 'sass_processor.storage.SassS3Boto3Storage'
STATIC_ROOT = os.path.join(BASE_DIR, 'www', 'static')
# STATIC_URL = '/static/'
# STATICFILES_FINDERS = [
#     'django.contrib.staticfiles.finders.FileSystemFinder',
#     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#     'sass_processor.finders.CssFinder',
# ]
# SASS_PRECISION = 5
# SASS_OUTPUT_STYLE = 'compressed'
