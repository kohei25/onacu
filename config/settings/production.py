from .common import *

DEBUG = False

ALLOWED_HOSTS = [
  'onacuproduction-env.eba-izd3p7h2.ap-northeast-1.elasticbeanstalk.com',
  'onacu.org',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

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

STATIC_ROOT = os.path.join(BASE_DIR, 'www', 'static')

# S3
AWS_ACCESS_KEY_ID = os.environ["ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["BUCKET_NAME"]
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # 1日はそのキャッシュを使う
}

AWS_LOCATION = 'static'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

SASS_PROCESSOR_ROOT = os.path.join(BASE_DIR, 'staticfiles')
SASS_PROCESSOR_AUTO_INCLUDE = False
STATICFILES_DIR = (
  os.path.join(BASE_DIR, 'static')
)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]
SASS_PRECISION = 5
SASS_OUTPUT_STYLE = 'compressed'

# Email
EMAIL_BACKEND = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'no-reply <noreply@onacu.org>'

DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'
AWS_DEFAULT_ACL = None
