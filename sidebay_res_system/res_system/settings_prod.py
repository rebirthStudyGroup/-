from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'res_system',
        'USER': 'root',
        'PASSWORD': 'gf!$eeP58/_UQv%bgxSiRq,C',
        'HOST': 'yoyakukun_db',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

STATIC_URL = '/yoyaku-kun/static/'
