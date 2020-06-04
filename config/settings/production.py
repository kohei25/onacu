from .common import *

DEBUG = False

ALLOWED_HOSTS = [
  'onacuproduction-env.eba-izd3p7h2.ap-northeast-1.elasticbeanstalk.com',
  'onacu.org',
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

# S3
AWS_ACCESS_KEY_ID = os.environ["ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["BUCKET_NAME"]
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # 1日はそのキャッシュを使う
}

# AWS_LOCATION = 'static'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'

# Email
EMAIL_BACKEND = 'django_ses.SESBackend'
# us-east-1 以外のAWSリージョンを使用する場合はこれも必要↓
# AWS_SES_REGION_NAME = 'us-west-2'
# AWS_SES_REGION_ENDPOINT = 'email.us-west-2.amazonaws.com'

# DEFAULT_FROM_EMAIL: サイト管理者からの自動送信メールに使用するデフォルトの Email アドレス
# SERVER_EMAIL: ADMINS や MANAGERS に送信されるエラーメッセージの送信元 Email アドレス
DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'no-reply <noreply@onacu.org>'