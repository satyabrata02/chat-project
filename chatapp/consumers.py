import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connecting...")
        user = self.scope["user"]
        other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f"chat_{min(user.id,int(other_user_id))}_{max(user.id,int(other_user_id))}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = self.scope["user"].id
        receiver_id = int(self.scope["url_route"]["kwargs"]["user_id"])

        msg_obj = await self.save_message(sender_id, receiver_id, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'timestamp': str(msg_obj.timestamp)
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        return Message.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=message
        )
