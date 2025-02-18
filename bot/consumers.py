import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "global_chat"
        self.room_group_name = f"chat_{self.room_name}"

        # Join the chat group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({"message": "Connected to WebSocket"}))

    async def disconnect(self, close_code):
        print("Disconnected:", close_code)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        print("""Receive message from WebSocket and send it to the group""")
        data = json.loads(text_data)
        message = data["message"]

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event):
        print("""Receive message from the group and send it to WebSocket""")
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
