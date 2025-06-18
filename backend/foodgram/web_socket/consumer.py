from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "global_chat"
        self.room_group_name = f"chat_{self.room_name}"
        self.user_name = "Аноним"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if 'set_name' in data:
            self.user_name = data['set_name']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": f"{self.user_name} теперь с нами",
                    "is_system": True
                }
            )
            return

        message = data["message"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user_name": self.user_name,
                "is_system": False
            }
        )

    async def chat_message(self, event):
        if event["is_system"]:
            await self.send(text_data=json.dumps({
                "message": event["message"],
                "is_system": True
            }))
        else:
            await self.send(text_data=json.dumps({
                "message": event["message"],
                "user_name": event["user_name"],
                "is_system": False
            }))


class NotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "notifications"
        self.room_group_name = f"notify_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": "Вы подписаны на уведомления"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data["message"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "notify_message",
                "message": message
            }
        )

    async def notify_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
