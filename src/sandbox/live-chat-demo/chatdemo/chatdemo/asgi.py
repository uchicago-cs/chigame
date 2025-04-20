"""
ASGI config for chatdemo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatdemo.settings')
application = ProtocolTypeRouter({
    "http": django_asgi_app,
})

ASGI_APPLICATION = "chatdemo.asgi.application"

application = get_asgi_application()
