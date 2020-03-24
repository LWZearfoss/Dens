from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from .consumers import DenConsumer, IndexConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            url(r'^ws/index/$', IndexConsumer),
            url(r'^ws/den/(?P<den_slug>[^/]+)/$', DenConsumer),
        ])
    ),
})
