# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room, Message
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class WebRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.sender_username = self.scope['url_route']['kwargs']['sender_username']
            self.recipient_username = self.scope['url_route']['kwargs']['recipient_username']
            self.room_name = f'{self.sender_username}_{self.recipient_username}'
        except KeyError:
            await self.close(code=400, reason="Invalid username(s) provided")
            return

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON data'}))
            return

        # Save message to the database
        await self.save_message(data)

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'signal_message',
                'message': data,
                'sender': self.sender_username,
                'recipient': self.recipient_username
            }
        )

    async def signal_message(self, event):
        message = event['message']
        sender = event['sender']
        recipient = event['recipient']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'recipient': recipient
        }))

    async def save_message(self, data):
        sender = await self.get_user(self.sender_username)
        recipient = await self.get_user(self.recipient_username)
        room, _ = await Room.objects.get_or_create(name=self.room_name)

        if data.get('type') == 'offer' or data.get('type') == 'answer':
            video_message = data['data']
            ice_candidate = None
        elif data.get('type') == 'candidate':
            video_message = None
            ice_candidate = data['data']

        message = Message(
            room=room,
            sender=sender,
            recipient=recipient,
            video_message=video_message,
            ice_candidate=ice_candidate
        )
        await message.save()

    @database_sync_to_async
    def get_user(self, username):
        return CustomUser.objects.get(username=username)

    def validate_message_data(self, data):
        if not isinstance(data, dict) or 'type' not in data or 'data' not in data:
            return False

        if data['type'] not in ['candidate', 'offer', 'answer']:
            return False

        return True

