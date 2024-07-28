# routing.py
from django.urls import path
from .consumers import WebRTCConsumer

websocket_urlpatterns = [
    path('ws/webrtc/<str:sender_username>/<str:recipient_username>/', WebRTCConsumer.as_asgi()),
]

