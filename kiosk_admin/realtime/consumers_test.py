import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import vosk
import base64
import boto3
import json
from website.models import CommonUtils
from realtime.stt import *
from base.models import *
from asgiref.sync import sync_to_async, async_to_sync

try:
    common_utils = CommonUtils.objects.all()[0]
    result_dict = {}
    exec(common_utils.content, {}, result_dict)
    print("Author : "+result_dict.get("author"))

except Exception as e:
    print(f"Error getting common utils: {str(e)}")


class RealtimeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.available_languages                    = ['en-Us','es-Es']
        self.selected_language                      = 'en-Us'
        self.room_name                              = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name                        = f"realtime_{self.room_name}"
        self.chat_history                           = []
        self.llm_model_name,self.llm_model,         = result_dict['llm_model']
        self.cart_model_name,self.cart_model        = result_dict['cart_model']
        self.stt = result_dict['AssemblyAIWebSocket']("f88a356529c44ad8acfd4a458d3f2e12",on_final_transcript=self.send_final_transcript,on_partial_transcript=self.stop_audio)
        await self.stt.connect()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()        
        if "genai" not in self.llm_model.lower():
            self.chat_history({
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": self.instructions
                    }
                ]
            })



    async def disconnect(self, close_code): 
        self.stt.close()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, bytes_data=None, text_data=None):
        if bytes_data:
            await self.stt.send_audio_byte(bytes_data)
            
        if text_data:
            text_data_json = json.loads(text_data)
            command = text_data_json.get("command")
            if command == "text_input":
                await self.send_final_transcript(text_data_json.get("text"))

            if command == "get_cart":
                await self.handle_get_cart()
            else:
                await self.send(text_data=json.dumps({"error": "Unknown command"}))

    async def send_final_transcript(self, transcript_text):
        pass
    
    async def stop_audio(self):
        await self.send(text_data=json.dumps({"command": "stop_audio"}))
    
    async def text_to_speech(self):
        pass

    async def update_cart(self):
        pass
    
                
            
            

        
            