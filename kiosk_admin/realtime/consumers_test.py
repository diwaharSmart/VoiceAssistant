import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import vosk
import base64
import boto3
import json
from website.models import CommonUtils

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.utils import apply_realtime_delay

"""
Here's an example of a custom event handler you can extend to
process the returned transcription results as needed. This
handler will simply print the text out to your interpreter.
"""


SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2
CHANNEL_NUMS = 1

# An example file can be found at tests/integration/assets/test.wav
AUDIO_PATH = "tests/integration/assets/test.wav"
CHUNK_SIZE = 1024 * 8
REGION = "us-west-2"

import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.utils import apply_realtime_delay

REGION = "us-west-2"
SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2
CHANNEL_NUMS = 1

class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream, websocket_consumer):
        super().__init__(output_stream)
        self.websocket_consumer = websocket_consumer
        self.last_transcription = None

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                current_transcription = alt.transcript.strip()
                
                # Send only if this is a new transcription
                if current_transcription != self.last_transcription:
                    print(current_transcription)
try:
    common_utils = CommonUtils.objects.all()[0]
    exec_env = {}
    result_dict = exec(common_utils.content, {}, exec_env)
    print("Author : "+exec_env.get("author"))

except Exception as e:
    print(f"Error getting common utils: {str(e)}")


class RealtimeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.available_languages             = ['en-us','es-us']
        self.selected_language               = 'en-us'
        self.room_name                       = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name                 = f"realtime_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        self.vosk_model = vosk.Model("/home/anonymous/VoiceAssistant/kiosk_admin/models/vosk-model-small-en-us-0.15")
        self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
        self.audio_buffer = []

        # self.llm_name,   self.llm_model      = result_dict["get_llm_model"]()
        # self.tts_name,   self.stt_model      = result_dict["get_tts_model"]()
        # self.cart_model, self.llm_name       = result_dict["get_cart_model"](self.llm_name)
        # self.get_chat_sample                 = result_dict["get_chat_sample"]
        self.chat_history                    = []
        self.transcribe_client = TranscribeStreamingClient(region=REGION)
        self.transcription_stream = await self.transcribe_client.start_stream_transcription(
            language_code="en-US",
            media_sample_rate_hz=SAMPLE_RATE,
            media_encoding="pcm",
        )
        self.transcribe_handler = MyEventHandler(self.transcription_stream.output_stream, self)
        asyncio.create_task(self.transcribe_handler.handle_events())
        

    

    async def disconnect(self, close_code):
        await self.transcription_stream.input_stream.end_stream()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, bytes_data=None, text_data=None):
        self.audio_buffer.append(bytes_data)
        if bytes_data:
            
            await self.transcription_stream.input_stream.send_audio_event(audio_chunk=bytes_data)
                
            
            

    async def append_chat_history(self, model_name, role, data):
        chat_history = result_dict["append_chat_response"](model_name, role, data)
        self.chat_history.append(chat_history)

    async def generate_response(self, model):
        pass

        
            