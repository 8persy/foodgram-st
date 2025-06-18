from django.urls import re_path
from .consumer import ChatConsumer, NotifyConsumer


urlpatterns = [
    re_path("web_socket/chat/$", ChatConsumer.as_asgi()),
    re_path("web_socket/notify/$", NotifyConsumer.as_asgi()),
]
