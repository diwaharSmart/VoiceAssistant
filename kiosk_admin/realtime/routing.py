from django.urls import re_path

from realtime import consumers_live


websocket_urlpatterns = [
    re_path(r"ws/realtime/(?P<room_name>\w+)/$", consumers_live.GeminiLiveAudioConsumer.as_asgi()),
]