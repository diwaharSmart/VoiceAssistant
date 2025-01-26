import asyncio
import json
import base64
import contextlib
from websockets import connect
from channels.generic.websocket import AsyncWebsocketConsumer

class GeminiLiveAudioConsumer(AsyncWebsocketConsumer):
    gemini_ws_url = (
        "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"
    )
    model = "models/gemini-2.0-flash-exp"
    api_key = "AIzaSyAVep7d9vRn1MbkAN8c-RwKjC-ISZqMjWs"  # Replace with your actual API key

    async def connect(self):
        """
        Handle client connection.
        """
        self.gemini_ws = None
        self.audio_queue = asyncio.Queue()
        await self.accept()
        print("[INFO] Client connected to Django WebSocket.")
        await self.send(text_data=json.dumps({"message": "Connected to Gemini audio streaming WebSocket"}))

        # Start the Gemini WebSocket connection
        

    async def disconnect(self, close_code):
        """
        Handle client disconnection and cleanup.
        """
        print("[INFO] Client disconnected from Django WebSocket.")
        if self.gemini_ws:
            await self.gemini_ws.close()
            print("[INFO] Gemini WebSocket closed.")

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handle audio or text input from the client.
        """
        if text_data:
            system_message = json.loads(text_data).get("system_message", "")
            if system_message:
                print(f"[DEBUG] Received system message from client: {system_message}")
                asyncio.create_task(self.connect_to_gemini_ws(system_message))
            else:
                user_message = json.loads(text_data).get("text", "")
                print(f"[DEBUG] Received text data from client: {user_message}")
                await self.send_to_gemini(self.encode_text_input(user_message))
        elif bytes_data:
            print("[DEBUG] Received audio data from client.")
            await self.audio_queue.put(bytes_data)

    async def send_to_gemini(self, message):
        """
        Send a message to the Gemini WebSocket.
        """
        if self.gemini_ws:
            print(f"[DEBUG] Sending message to Gemini: {message}")
            await self.gemini_ws.send(json.dumps(message))

    async def connect_to_gemini_ws(self,system_message):
        """
        Connect to the Gemini Live API WebSocket and handle messages.
        """
        try:
            print("[INFO] Connecting to Gemini WebSocket...")
            self.gemini_ws = await connect(f"{self.gemini_ws_url}?key={self.api_key}")
            print("[INFO] Connected to Gemini WebSocket.")
            config_message = {
                "model": self.model,
                "generation_config": {
                    "speech_config": {
                        "voice_config": {
                            "prebuilt_voice_config": {
                                "voice_name": "Aoede"  # Predefined voice
                            }
                        }
                    }
                },
                "tools": []  # If you need to specify any tools, add them here
            }

            # Send the setup message for the Gemini model
            setup_message = {"setup": config_message}
            print(f"[DEBUG] Sending setup message: {setup_message}")
            await self.gemini_ws.send(json.dumps(setup_message))

            print("[INFO] Connected to Gemini WebSocket.")
            
           
            # Send an initial text message to Gemini
            initial_message = f"You are an AI Assistant, You need to help me to gain some knowledege and understanding of below content with a QA conversation {system_message}"
            print(f"[DEBUG] Sending initial text message: {initial_message}")
            await self.send_to_gemini(self.encode_text_input(initial_message))

            # Start processing the audio input queue
            asyncio.create_task(self.process_audio_queue())

            async for msg in self.gemini_ws:
                print(f"[DEBUG] Message received from Gemini: {msg}")
                message = json.loads(msg)
                if audio_output := self.decode_audio_output(message):
                    print("[INFO] Decoded audio output received from Gemini.")
                    await self.send(bytes_data=audio_output)
                elif "turnComplete" in message.get("serverContent", {}):
                    print("[INFO] Turn complete message received from Gemini.")
                    await self.send(text_data=json.dumps({"event": "turnComplete"}))
                elif message.get("serverContent") != {}:
                    print("[DEBUG] Other server content received from Gemini.")
                    await self.send(text_data=json.dumps(message))
        except Exception as e:
            print(f"[ERROR] Gemini connection error: {e}")
            await self.send(text_data=json.dumps({"error": f"Gemini connection error: {str(e)}"}))


    async def process_audio_queue(self):
        """
        Continuously send audio from the queue to Gemini WebSocket.
        """
        while True:
            data = await self.audio_queue.get()
            print("[DEBUG] Processing audio queue data.")
            if self.gemini_ws:
                await self.gemini_ws.send(json.dumps(self.encode_audio_input(data)))

    def encode_audio_input(self, data):
        """
        Build a JSPB message with audio bytes.
        """
        sample_rate = 16000  # Change based on your requirements
        encoded_message = {
            "realtimeInput": {
                "mediaChunks": [
                    {
                        "mimeType": f"audio/pcm;rate={sample_rate}",
                        "data": base64.b64encode(data).decode("UTF-8"),
                    }
                ]
            }
        }
        print(f"[DEBUG] Encoded audio input: {encoded_message}")
        return encoded_message

    def encode_text_input(self, text):
        """
        Build a JSPB message with text input.
        """
        encoded_message = {
            "clientContent": {
                "turns": [{"role": "USER", "parts": [{"text": text}]}],
                "turnComplete": True,
            }
        }
        print(f"[DEBUG] Encoded text input: {encoded_message}")
        return encoded_message
    
    def encode_system_input(self):
        """
        Build a JSPB message with text input.
        """
        encoded_message = {
            "clientContent": {
                "turns": [{"role": "SYSTEM", "parts": [{"text": "Your Name is Merzol"}]}],
                "turnComplete": False,
            }
        }
        print(f"[DEBUG] Encoded text input: {encoded_message}")
        return encoded_message

    def decode_audio_output(self, input):
        """
        Extract audio data from the Gemini response.
        """
        result = []
        content_input = input.get("serverContent", {})
        content = content_input.get("modelTurn", {})
        for part in content.get("parts", []):
            data = part.get("inlineData", {}).get("data", "")
            if data:
                result.append(base64.b64decode(data))
        decoded_audio = b"".join(result)
        print("[DEBUG] Decoded audio output.")
        return decoded_audio
