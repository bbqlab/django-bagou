# -*- coding: utf-8 -*-
import sys
import logging
from django.utils.importlib import import_module
from django.conf import settings as django_settings

from .exceptions import BagouException

if sys.version_info[0] == 3:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger('bagou.general')
logger.setLevel(logging.INFO)

if not hasattr(django_settings, 'BAGOU'):
    settings = {}
    setattr(django_settings, 'BAGOU', settings)
else:
    settings = django_settings.BAGOU

# Default events handler
settings.setdefault('DEFAULT_HANDLER_CLASS', 'bagou.handler.WebSocketHandler')

# Websocket
settings.setdefault('WEBSOCKET_URL', 'ws://localhost:9000/websocket')
__websocket_url = urlparse(settings.get('WEBSOCKET_URL'))
settings['WEBSOCKET_ADDR'] = __websocket_url.hostname
settings['WEBSOCKET_PORT'] = int(__websocket_url.port)
settings['WEBSOCKET_PATH'] = __websocket_url.path

# AMQP
settings.setdefault('AMQP_BROKER_URL', 'amqp://guest:guest@localhost:5672/')
settings.setdefault('QUEUE_NAME', 'websocket')
__amqp_url = urlparse(settings.get('AMQP_BROKER_URL'))
settings['AMQP_BROKER_USER'] = __amqp_url.username
settings['AMQP_BROKER_PASS'] = __amqp_url.password
settings['AMQP_BROKER_ADDR'] = __amqp_url.hostname
settings['AMQP_BROKER_PORT'] = int(__amqp_url.port)
settings['AMQP_BROKER_PATH'] = __amqp_url.path

# Authentication
settings.setdefault('AUTH', True)
if settings['AUTH'] and django_settings.SESSION_COOKIE_HTTPONLY:
    raise BagouException(
        'Bagou need SESSION_COOKIE_HTTPONLY = False to have authentification.')
if settings['AUTH']:
    logger.warning(
        'Please read '
        'https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SESSION_COOKIE_HTTPONLY'
        ' to known consequences.')


# Try and import an ``events`` module in each installed app,
# to ensure all event handlers are connected.
for app in django_settings.INSTALLED_APPS:
    try:
        import_module("%s.events" % app)
    except ImportError as err:
        logger.info('No events found in %s (%s)' % (app, err))
        pass
