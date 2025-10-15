import os
from pathlib import Path

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'messaging_app'),
        'USER': os.getenv('DB_USER', 'app_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'app_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}