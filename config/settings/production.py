from .common import *

DEBUG = False

ALLOWED_HOSTS = [
  'onacustaging-env.eba-m5p325p4.ap-northeast-1.elasticbeanstalk.com',
  'onacu-staging.com',
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

STATIC_ROOT = os.path.join(BASE_DIR, 'www', 'static')

