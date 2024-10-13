import asyncio
import websockets
import os
import json
import base64
import threading
import webrtcvad
import struct
import json
import numpy as np
import time
from pydub import AudioSegment
from pydub.utils import which
from constants import *

TOKEN_USAGE_FILE = "token_usage.json"
# Ensure pydub knows where to find ffmpeg
AudioSegment.converter = which("ffmpeg")

def update_cart(new_items):
    # Load the current cart from the JSON file
    if os.path.exists(CART_FILE):
        with open(CART_FILE, "r") as file:
            current_cart = json.load(file)
    else:
        current_cart = {"items": []}

    # Iterate over new items and update or add them to the current cart
    for new_item in new_items:
        found = False
        for item in current_cart["items"]:
            if item["name"] == new_item["name"]:
                # Update the quantity and total cost if item already exists
                item["quantity"] = new_item["quantity"]
                item["total_cost"] = new_item["total_cost"]
                found = True
                break
        if not found:
            # Add new item to the cart
            current_cart["items"].append(new_item)

    # Save the updated cart back to the JSON file
    with open(CART_FILE, "w") as file:
        json.dump(current_cart, file, indent=2)

class OpenAIRealtimeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        self.client_url = "ws://192.168.1.9:8765"
        self.ws = None
        self.audio_queue = asyncio.Queue()
        self.should_stop = False
        self.session_id = None  # Store the session ID
        self.vad = webrtcvad.Vad()  # Initialize VAD
        self.vad.set_mode(1)  # Reduce aggressiveness mode from 2 to 1 (less aggressive to avoid false positives)
        self.response_in_progress = False  # Track if a response is in progress

        # Persistent buffers for audio data and state tracking
        self.audio_buffer = []  # Buffer to store the audio frames
        self.is_speech_detected = False  # Track if speech is currently being detected
        self.silence_counter = 0  # Count consecutive silent frames
        self.relay_server = None
        self.speech_start_time = None  # Track the start time of speech
        self.ensure_token_usage_file()

    async def connect(self):
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "OpenAI-Beta": "realtime=v1",
        }
        self.ws = await websockets.connect(self.url, extra_headers=headers)
        print("Connected to OpenAI Realtime API.")
        event = await self.ws.recv()
        event_data = json.loads(event)
        
        # Extract and store the session ID
        if event_data["type"] == "session.created":
            self.session_id = event_data.get("session", {}).get("id")
            print(f"Session initialized with ID: {self.session_id}")

        await self.ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "turn_detection": {
                    "type": "server_vad"
                },
                "tools":function_tools,
                "instructions": instructions
            }
        }))

        send_task = asyncio.create_task(self.send_audio())
        receive_task = asyncio.create_task(self.receive_events())

        await asyncio.gather(send_task, receive_task)

    async def send_audio(self):
        while not self.should_stop:
            audio_unit8list = await self.audio_queue.get()
            if audio_unit8list is None:
                continue

            audio_bytes = bytes(audio_unit8list)
            frame_duration_ms = 30
            sample_rate = 16000
            frame_size = int(sample_rate * frame_duration_ms / 1000) * 2  # 16-bit samples, so multiply by 2

            for i in range(0, len(audio_bytes), frame_size):
                frame = audio_bytes[i:i + frame_size]
                if len(frame) != frame_size:
                    continue
                audio_array = np.frombuffer(frame, dtype=np.int16)

                if audio_array.size == 0:
                    continue

                rms = np.sqrt(np.mean(np.square(audio_array.astype(np.float32))))
                volume_threshold = 800

                if rms < volume_threshold:
                    self.silence_counter += 1
                    if self.is_speech_detected and self.silence_counter >= 10:
                        # Speech has ended, send the collected audio
                        speech_end_time = time.time()
                        elapsed_time = speech_end_time - self.speech_start_time
                        print(f"Speech ended. Elapsed time: {elapsed_time:.2f} seconds")

                        if len(self.audio_buffer) < 20:
                            print("Audio buffer is empty. No frames were collected.")
                            self.audio_buffer.clear()
                        else:
                            print(f"Number of frames in audio buffer: {len(self.audio_buffer)}")

                            # Concatenate all frames in the buffer
                            complete_audio = b''.join(self.audio_buffer)

                            # Convert the complete audio to base64 for transmission
                            base64_audio_data = base64.b64encode(complete_audio).decode('ascii')

                            # Create the event for conversation.item.create
                            event = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "message",
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "input_audio",
                                            "audio": base64_audio_data
                                        }
                                    ]
                                }
                            }

                            # Send the message event
                            await self.ws.send(json.dumps(event))

                            # Request a response from OpenAI
                            await self.ws.send(json.dumps({"type": "response.create"}))

                        # Reset the speech detection flag and silence counter
                        self.is_speech_detected = False
                        self.silence_counter = 0

                        # Clear the audio buffer after sending
                        self.audio_buffer.clear()
                    continue

                # Reset the silence counter if voice is detected
                self.silence_counter = 0

                # Check if voice is detected using VAD
                if self.vad.is_speech(frame, sample_rate):
                    if not self.is_speech_detected:
                        print("Speech started")
                        self.is_speech_detected = True
                        # Record the start time of speech
                        self.speech_start_time = time.time()

                    # Append frame to the buffer
                    self.audio_buffer.append(frame)


    def ensure_token_usage_file(self):
        """Ensure the token usage file exists and initialize it if necessary."""
        if not os.path.exists(TOKEN_USAGE_FILE):
            initial_data = {
                "total_tokens": 0,
                "text_tokens": 0,
                "audio_tokens": 0
            }
            with open(TOKEN_USAGE_FILE, "w") as file:
                json.dump(initial_data, file)

    def update_token_usage(self, token_data):
        """Update the token usage in the JSON file."""
        # Load the current token data
        with open(TOKEN_USAGE_FILE, "r") as file:
            current_data = json.load(file)

        # Update the token counts
        current_data["total_tokens"] += token_data["total_tokens"]
        current_data["text_tokens"] += token_data["text_tokens"]
        current_data["audio_tokens"] += token_data["audio_tokens"]

        # Save the updated token data
        with open(TOKEN_USAGE_FILE, "w") as file:
            json.dump(current_data, file)

    async def handle_get_cart_items(self):

        # Prepare the response
        response = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": f"get_cart_items"
                    }
                ]
            }
        }

        # Send the response back to the OpenAI API
        await self.ws.send(json.dumps(response))

    async def receive_events(self):
        try:
            while True:
                response = await self.ws.recv()
                event = json.loads(response)
                print("Received event from OpenAI:", event)

                # Flow handling based on event type

                if event["type"] == 'response.output_item.done':
                    print(event)

                try:
                    if event['type'] == 'response.output_item.done' and event['item']['name'] == 'get_cart_items':
                    # Extract the cart items from the function call response
                        arguments = json.loads(event['item']['arguments'])  # Get the items argument

                        # Here i need to send message to the websocket sonnection from relay server from where i am getting audio. Help
                        if self.relay_server:
                            await self.relay_server.send_message_to_client(json.dumps({'command': 'update_cart', 'cart_items': arguments}))
                            print("--------------------CART-----------------------------------")
                        self.save_to_file(json.dumps(arguments, indent=2), "cart_items.json")

                        # Send the cart data to the relay server
                        # await self.send_to_relay_server(arguments)

                except:
                    pass

                if event['type'] == 'conversation.item.created':
                    if event['item']['type'] == 'message' and event['item']['role'] == 'assistant':
                        for content in event['item']['content']:
                            if content['type'] == 'text':
                                print('Assistant:', content['text'])
                                self.save_to_file(content['text'], "assistant_response.txt")
                            elif content['type'] == 'audio':
                                await self.handle_audio_response(content['audio'])
                    elif event['item']['type'] == 'function_call':
                        # print(event)
                        await self.handle_get_cart_items()
                        # await self.handle_function_call(self.ws, event['item']['function_call'])
                elif event['type'] == 'response.audio.delta':
                     # Here i need to send message to the websocket sonnection from relay server from where i am getting audio. Help
                    if self.relay_server:
                        await self.relay_server.send_message_to_client(json.dumps({'command': 'audio_stream', 'stream': event['delta']}))
                        print("--------------------STREAM-----------------------------------")

                elif event['type'] == 'error':
                    # print('Error:', event['error'])
                    self.save_to_file(json.dumps(event['error']), "error_log.json")
                elif event['type'] == 'input_audio_buffer.speech_started':
                    print('Speech started')
                elif event['type'] == 'input_audio_buffer.speech_stopped':
                    print('Speech stopped')
                elif event['type'] == 'input_audio_buffer.committed':
                    print('Audio buffer committed')
                elif event['type'] == 'response.done':
                    # Extract token usage details
                    token_usage = event.get('response', {}).get('usage', {})
                    if token_usage:
                        total_tokens = token_usage.get('total_tokens', 0)
                        text_tokens = token_usage.get('output_token_details', {}).get('text_tokens', 0)
                        audio_tokens = token_usage.get('output_token_details', {}).get('audio_tokens', 0)

                        token_data = {
                            "total_tokens": total_tokens,
                            "text_tokens": text_tokens,
                            "audio_tokens": audio_tokens
                        }
                        # Update token usage in the JSON file
                        self.update_token_usage(token_data)

        except websockets.exceptions.ConnectionClosed:
            print("Connection to OpenAI Realtime API closed.")
        except Exception as e:
            print(f"Error receiving events: {str(e)}")

    @staticmethod
    def save_to_file(content, file_name):
        with open(file_name, "a") as file:
            file.write(content + "\n")

    async def close(self):
        self.should_stop = True
        if self.ws:
            await self.ws.close()



    

class AudioRelayServer:
    def __init__(self, host, port, openai_client):
        self.host = host
        self.port = port
        self.openai_client = openai_client
        self.client_websocket = None
        openai_client.relay_server = self

    async def handler(self, websocket, path):
        print("Client connected to audio relay server.")
        self.client_websocket = websocket
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    await self.openai_client.audio_queue.put(message)
                else:
                    await websocket.send(f"Received: {message}")

        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected from audio relay server.")
            self.client_websocket = None

    async def send_message_to_client(self, message):
        if self.client_websocket:
            try:
                await self.client_websocket.send(message)
                print("Message sent to client.")
            except websockets.exceptions.ConnectionClosed:
                print("Failed to send message, client disconnected.")

    async def start_server(self):
        server = await websockets.serve(self.handler, self.host, self.port)
        print(f"Audio relay server started at ws://{self.host}:{self.port}")
        await server.wait_closed()

        

async def main():
    api_key = "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"
    openai_client = OpenAIRealtimeClient(api_key)
    openai_task = asyncio.create_task(openai_client.connect())
    relay_server = AudioRelayServer('192.168.1.9', 8765, openai_client)
    server_task = asyncio.create_task(relay_server.start_server())
    await asyncio.gather(openai_task, server_task)
    await openai_client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted.")

