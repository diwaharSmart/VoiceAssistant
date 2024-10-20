from django.urls import re_path

from realtime import consumers

websocket_urlpatterns = [
    re_path(r"ws/realtime/(?P<room_name>\w+)/$", consumers.RealtimeConsumer.as_asgi()),
]