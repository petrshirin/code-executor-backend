import os

# Run settings
HOST = os.environ.get('HOST', 'localhost')
PORT = 5000

SITE_URL = f'{HOST}:{PORT}'


# Auth settings
AUTH_KEY = os.environ.get('AUTH_KEY', 'secret')


# Docker settings
DOCKER_HOST = os.environ.get('DOCKER_HOST') or 'tcp://localhost:2375'
DEFAULT_IMAGE = 'vi-creator/code_executor:latest'


# Redis settings
REDIS_URL = 'redis://executor-redis:6379/1'

# Celery settings
CELERY_BROKER_URL = 'redis://executor-redis:6379/5'
CELERY_RESULT_BACKEND = 'redis://executor-redis:6379/5'


try:
    from local import *
except ImportError:
    pass
