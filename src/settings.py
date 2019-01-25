import os
import logging

BASE_DIR = os.path.dirname(__file__)

APP_HOST = os.environ.get('HOST', '0.0.0.0')
APP_PORT = os.environ.get('PORT', 80)

# logging
logger = logging.getLogger('duckchat')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)

DEBUG = True

# Database url
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Static files
STATIC_URL = '/static/'
STATIC_DIR = os.path.join(BASE_DIR, 'static')


# Redis settings
REDIS = '127.0.0.1', 6379


# Template dir path
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
