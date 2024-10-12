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

# Ensure pydub knows where to find ffmpeg
AudioSegment.converter = which("ffmpeg")
class OpenAIRealtimeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
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
        self.speech_start_time = None  # Track the start time of speech

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
                "instructions": "Please respond in a friendly and helpful manner."
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

            # Convert audio_unit8list to bytes
            audio_bytes = bytes(audio_unit8list)

            # Split audio into 30ms frames
            frame_duration_ms = 30
            sample_rate = 16000
            frame_size = int(sample_rate * frame_duration_ms / 1000) * 2  # 16-bit samples, so multiply by 2

            for i in range(0, len(audio_bytes), frame_size):
                frame = audio_bytes[i:i + frame_size]

                # Check if the frame length matches the requirement
                if len(frame) != frame_size:
                    continue

                # Convert the frame to an array of 16-bit signed integers
                audio_array = np.frombuffer(frame, dtype=np.int16)

                # Skip processing if the frame is empty
                if audio_array.size == 0:
                    continue

                # Calculate the root mean square (RMS) volume of the frame
                rms = np.sqrt(np.mean(np.square(audio_array.astype(np.float32))))

                # Set a volume threshold, e.g., 500 (adjust as necessary)
                volume_threshold = 500

                # Skip processing if the RMS volume is below the threshold (likely just noise)
                if rms < volume_threshold:
                    self.silence_counter += 1
                    # If we've had 10 consecutive silent frames (approximately 300ms), end the speech
                    if self.is_speech_detected and self.silence_counter >= 10:
                        # Mark the end of speech and calculate elapsed time
                        speech_end_time = time.time()
                        elapsed_time = speech_end_time - self.speech_start_time
                        print(f"Speech ended. Elapsed time: {elapsed_time:.2f} seconds")

                        # Check if audio buffer has frames
                        if len(self.audio_buffer) == 0:
                            print("Audio buffer is empty. No frames were collected.")
                        else:
                            print(f"Number of frames in audio buffer: {len(self.audio_buffer)}")

                            # Save the audio buffer to an MP3 file
                            self.save_audio_to_mp3(self.audio_buffer, sample_rate)

                        # Reset speech detection flag and silence counter
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

    def save_audio_to_mp3(self, audio_frames, sample_rate):
        # Concatenate the audio frames
        complete_audio = b''.join(audio_frames)

        # Check if complete_audio is empty
        if len(complete_audio) == 0:
            print("Error: complete_audio is empty. No audio to save.")
            return

        # Create an AudioSegment from the raw audio data
        audio_segment = AudioSegment(
            data=complete_audio,
            sample_width=2,  # 16-bit audio
            frame_rate=sample_rate,
            channels=1
        )

        # Create a file name with the current timestamp
        file_name = f"speech_{int(time.time())}.mp3"

        # Export the audio as MP3
        audio_segment.export(file_name, format="mp3")
        print(f"Audio saved to file: {file_name}")

    async def receive_events(self):
        try:
            while True:
                response = await self.ws.recv()
                event = json.loads(response)
                print("Received event from OpenAI:", event)

                # Flow handling based on event type
                if event['type'] == 'conversation.item.created':
                    if event['item']['type'] == 'message' and event['item']['role'] == 'assistant':
                        for content in event['item']['content']:
                            if content['type'] == 'text':
                                print('Assistant:', content['text'])
                                self.save_to_file(content['text'], "assistant_response.txt")
                            elif content['type'] == 'audio':
                                await self.handle_audio_response(content['audio'])
                    elif event['item']['type'] == 'function_call':
                        await self.handle_function_call(self.ws, event['item']['function_call'])
                elif event['type'] == 'error':
                    print('Error:', event['error'])
                    self.save_to_file(json.dumps(event['error']), "error_log.json")
                elif event['type'] == 'input_audio_buffer.speech_started':
                    print('Speech started')
                elif event['type'] == 'input_audio_buffer.speech_stopped':
                    print('Speech stopped')
                elif event['type'] == 'input_audio_buffer.committed':
                    print('Audio buffer committed')
                elif event.get('type') == 'response.completed':
                    self.response_in_progress = False

        except websockets.exceptions.ConnectionClosed:
            print("Connection to OpenAI Realtime API closed.")
        except Exception as e:
            print(f"Error receiving events: {str(e)}")

    @staticmethod
    def convert_uint8_to_base64(uint8_list):
        chunk_size = 0x8000  # 32KB chunk size
        binary_string = ""

        for i in range(0, len(uint8_list), chunk_size):
            chunk = uint8_list[i:i + chunk_size]
            binary_string += ''.join(chr(b) for b in chunk)

        # Convert binary string to base64
        base64_string = base64.b64encode(binary_string.encode('latin1')).decode('ascii')
        return base64_string

    @staticmethod
    def save_to_file(content, file_name):
        with open(file_name, "a") as file:
            file.write(content + "\n")

    async def handle_audio_response(self, audio_content):
        # Placeholder for handling audio content
        print("Handling audio response")
        # You can save the audio content or play it back

    async def handle_function_call(self, websocket, function_call):
        # Placeholder for handling function calls
        print("Handling function call:", function_call)
        # Implement function call handling logic here

    async def close(self):
        self.should_stop = True
        if self.ws:
            await self.ws.close()




class AudioRelayServer:
    def __init__(self, host, port, openai_client):
        self.host = host
        self.port = port
        self.openai_client = openai_client

    async def handler(self, websocket, path):
        print("Client connected to audio relay server.")
        try:
            async for message in websocket:
                audio_chunk = message 
                await self.openai_client.audio_queue.put(audio_chunk)
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected from audio relay server.")

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

