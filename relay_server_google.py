import asyncio
import websockets
import os
import json
import base64
import webrtcvad
import struct
import numpy as np
import time
# import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
from google.generativeai import GenerativeModel, configure
import google.generativeai as genai
import requests
import torch
from transformers import Speech2TextProcessor, Speech2TextForConditionalGeneration
from scipy.io.wavfile import write
# import whisper
import soundfile as sf
import vosk
# Load the Whisper model
# au_model = whisper.load_model("medium.en")

au_model=""

# Example usage:
# audio_data should be a NumPy array and sampling_rate should be an integer
# text = transcribe_audio(audio_data, sampling_rate)


# Ensure pydub knows where to find ffmpeg
AudioSegment.converter = which("ffmpeg")



# genai.configure
# Define the model generation configuration for Gemini
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json"
}

genai.configure(api_key="AIzaSyBYXaUKjFNEwH7gAaAtTS_uvwqcXt1n31I")

# Initialize Gemini Model
self.genai_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Instructions:\n- You are an AI assistant for a restaurant, responsible for taking orders from customers.\n- Be friendly, helpful, and courteous.\n- Ask for clarification if the customer's order is unclear.\n- Confirm the order details before finalizing.\n- Provide the total cost of the order.\n- The menu items and prices are as follows:\n  * Burger - $10\n  * Pizza - $12\n  * Salad - $8\n  * Pasta - $11\n  * Fish and Chips - $13\n  * Drinks (Soda, Water, Juice) - $2 each\n- Be prepared to answer questions about the menu items, ingredients, or any special requests.\n- If a customer asks for something not on the menu, politely inform them it's not available.\n- Remember to ask if they would like any drinks with their meal.\n- Use the 'update_order' function to add items to the order or update existing items.\n- After each item is ordered, use the 'update_order' function to add it to the order.\n- Confirm the updated order with the customer after each addition.\n\nResponse format:\n- Always return the output in the following JSON structure and a audio stream:\n  [{\n      \"speech_reponse\":\"<Speaking with customer like a human>\",\n    },\n    {\"cart_items\": [\n      {\n        \"name\": \"<Product Name>\",\n        \"quantity\": <Quantity>,\n        \"price\": <Price>\n      }\n      ...\n    ],\n    \"total_cost\": <Total cost of the order>,\n}]\n\n- The 'Cart' field should be an array of all items currently in the cart, each with their name, quantity, and price.\n- The 'total_cost' should be the total cost of the items in the cart.\n- The 'command' should indicate whether the customer is adding, removing, or updating an item in the cart.\n\n- If the customer requests an item that is not on the menu, politely inform them and ensure it is not added to the cart.\n\nPersonality:\n- Be upbeat and welcoming\n- Speak clearly and concisely.\n- Respond in a way that is natural and customer-friendly.\n- Give response as the Json format and audio file\n`\n",
)

# Initialize the speech recognizer
# recognizer = sr.Recognizer()


# Ensure pydub knows where to find ffmpeg
AudioSegment.converter = which("ffmpeg")

# Initialize the speech recognizer
# recognizer = sr.Recognizer()
ELEVEN_LABS_API_KEY="sk_3369e1e39d3ac63cb612eb272443967986091bf0b3df47fe"
ELEVEN_LABS_VOICE_ID="9BWtsMINqrJLrRacOk9x"


class GoogleGeminiClient:
    def __init__(self, volume_threshold=800):
        self.is_speech_detected = False
        self.speech_start_time = None
        self.audio_buffer = []
        self.chat_history = []
        self.silence_counter = 0
        self.should_stop = False
        self.audio_queue = asyncio.Queue()
        self.vad = webrtcvad.Vad()  # Voice Activity Detector
        self.vad.set_mode(1)  # Less aggressive, mode 1
        self.volume_threshold = volume_threshold  # Volume threshold for RMS

    
    
    def calculate_rms(self, audio_frame):
        """Calculate the RMS (Root Mean Square) value for the audio frame."""
        audio_data = np.frombuffer(audio_frame, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_data ** 2))
        return rms

    async def transcribe_audio(self,audio_data):
        # audio_segment = AudioSegment(
        # data=audio_data,
        # sample_width=2,  # 16-bit audio
        # frame_rate=16000,
        # channels=1  # Mono audio
        # )

        # Save the converted audio to a temporary WAV file
        temp_audio_file = "temp_audio.wav"
        audio_data = np.frombuffer(audio_data, dtype=np.int16)
        # audio_segment.export(temp_audio_file, format="wav")
        write(temp_audio_file, 16000, audio_data)

        audio = whisper.load_audio("temp_audio.wav")
        audio = whisper.pad_or_trim(audio)

        # # make log-Mel spectrogram and move to the same device as the model
        # mel = whisper.log_mel_spectrogram(audio).to(au_model.device)

        # # detect the spoken language
        # _, probs = au_model.detect_language(mel)
        # print(f"Detected language: {max(probs, key=probs.get)}")

        # # decode the audio
        # options = whisper.DecodingOptions()
        # result = whisper.decode(model, mel, options)

        # # print the recognized text
        # print(result.text)
        # Save the audio data to a temporary file
        result = au_model.transcribe("temp_audio.wav")
        text = result["text"]
        # text = result.text
        print(f"Recognized Speech: {text}")
        await self.generate_response(text)

    async def process_audio_stream(self):
        """Process the audio stream and detect speech using VAD and RMS threshold."""
        while not self.should_stop:
            audio_unit8list = await self.audio_queue.get()
            if audio_unit8list is None:
                continue

            audio_bytes = bytes(audio_unit8list)
            frame_duration_ms = 30
            sample_rate = 16000
            frame_size = int(sample_rate * frame_duration_ms / 1000) * 2  # 16-bit samples

            for i in range(0, len(audio_bytes), frame_size):
                frame = audio_bytes[i:i + frame_size]
                if len(frame) != frame_size:
                    continue
                audio_array = np.frombuffer(frame, dtype=np.int16)

                if audio_array.size == 0:
                    continue

                rms = np.sqrt(np.mean(np.square(audio_array.astype(np.float32))))

                if rms < self.volume_threshold:
                    self.silence_counter += 1
                    if self.is_speech_detected and self.silence_counter >= 15:
                        # Speech has ended, send the collected audio
                        speech_end_time = time.time()
                        elapsed_time = speech_end_time - self.speech_start_time
                        print(f"Speech ended. Elapsed time: {elapsed_time:.2f} seconds")

                        if len(self.audio_buffer) < 10:
                            print("Audio buffer is empty. No frames were collected.")
                            self.audio_buffer.clear()
                        else:
                            print(f"Number of frames in audio buffer: {len(self.audio_buffer)}")

                            # Concatenate all frames in the buffer
                            complete_audio = b''.join(self.audio_buffer)

                            # Process the buffered audio using SpeechRecognition
                            await self.transcribe_audio(complete_audio)

                        # Reset the speech detection flag and silence counter
                        self.is_speech_detected = False
                        self.silence_counter = 0

                        # Clear the audio buffer after processing
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

    
    async def process_collected_audio(self, audio_data):
       
        # Convert raw audio data to a valid WAV format using pydub
        audio_segment = AudioSegment(
            data=audio_data,
            sample_width=2,  # 16-bit audio, so 2 bytes per sample
            frame_rate=16000,
            channels=1  # mono audio
        )

        # Save the converted audio to a temporary WAV file
        temp_audio_file = "temp_audio.wav"
        audio_segment.export(temp_audio_file, format="wav")

        # Convert the audio to text using SpeechRecognition
        try:
            with sr.AudioFile(temp_audio_file) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                print(f"Recognized Speech: {text}")
                # Now that we have the transcribed text, we can generate a response
                await self.generate_response(text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        

    # async def process_collected_audio(self, audio_data):
    #     """Process the collected audio buffer and convert it to text using Wav2Vec2."""
    #     # Convert raw audio data to a numpy array
    #     audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        
    #     # Normalize audio
    #     audio_array = audio_array / 32768.0  # Normalizing the audio

    #     # Use librosa to resample the audio to 16000 Hz (if necessary)
    #     audio_array = librosa.resample(audio_array, orig_sr=16000, target_sr=16000)

    #     # Convert to a tensor for Wav2Vec2
    #     inputs = processor(audio_array, return_tensors="pt", sampling_rate=16000)
        
    #     # Perform inference with the Wav2Vec2 model
    #     with torch.no_grad():
    #         logits = model(**inputs).logits  # This is the correct way to call the model

    #     # Get the predicted ids from the logits
    #     predicted_ids = torch.argmax(logits, dim=-1)
    #     transcription = processor.batch_decode(predicted_ids)[0]

    #     print(f"Recognized Speech: {transcription}")
    #     await self.generate_response(transcription)


    async def generate_response(self, text):
        """Generate a response based on the transcribed text and send it to the client."""
        print(f"Processing the transcribed text: {text}")
        response = model.start_chat(history=self.chat_history).send_message(text)
        print(response.text)
        
        self.chat_history.append({
        "role": "user",
        "parts": [
            text,
        ],
        })

        self.chat_history.append({
        "role": "model",
        "parts": [
            response.text,
        ],
        })
        try:
            if self.relay_server and self.relay_server.client_websocket:
                await self.relay_server.send_message_to_client(json.dumps({"command":"speech_response","text":json.loads(response.text)[0]["speech_response"]}))
        except:
            pass
        try:
            if self.relay_server and self.relay_server.client_websocket:
                await self.relay_server.send_message_to_client(json.dumps({"command":"cart_items","cart_items":{"items":json.loads(response.text)[1]["cart_items"]}}))
        except Exception as e:
            print(f"Error sending response to client: {str(e)}")
        """Response Recieved as [{"speech_response": "Good morning! Welcome to our restaurant. What can I get for you today?"}, {"cart_items": [], "total_cost": 0}]"""
        # Simulate sending a response back to the client
        # if self.relay_server:
        #     await self.relay_server.send_message_to_client(f"Processed speech: {text}")
vmodel = vosk.Model("vosk-model-small-en-us-0.15")
class AudioRelayServer:
    def __init__(self, host, port, gemini_client):
        self.host = host
        self.port = port
        self.gemini_client = gemini_client
        self.client_websocket = None
        self.gemini_client.relay_server = self
        self.recognizer = vosk.KaldiRecognizer(vmodel, 16000)
    async def handler(self, websocket, path):
        """Handle incoming WebSocket connections and forward audio data to Google Gemini."""
        print("Client connected to audio relay server.")
        self.client_websocket = websocket
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    audio_data = message  # Convert the incoming byte stream to numpy array (int16)

                    # Pass the audio data to the recognizer
                    if self.recognizer.AcceptWaveform(audio_data):
                        result = self.recognizer.Result()
                        result_json = json.loads(result)
                        transcript = result_json.get('text', '')
                        print(f"Transcription: {transcript}")
                        if transcript not in ['huh',None,""]:
                            await self.gemini_client.generate_response(transcript)
                    # Place the audio bytes into the queue for processing
                    # await self.gemini_client.audio_queue.put(message)
                    
                else:
                    await websocket.send(f"Received: {message}")

        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected from audio relay server.")
            self.client_websocket = None

    async def send_message_to_client(self, message):
        """Send a message back to the client."""
        if self.client_websocket:
            try:
                await self.client_websocket.send(message)
                print("Message sent to client.")
            except websockets.exceptions.ConnectionClosed:
                print("Failed to send message, client disconnected.")

    async def start_server(self):
        """Start the WebSocket server."""
        server = await websockets.serve(self.handler, self.host, self.port)
        print(f"Audio relay server started at ws://{self.host}:{self.port}")
        await server.wait_closed()

async def main():
    gemini_client = GoogleGeminiClient(volume_threshold=900)  # Set volume threshold here
    relay_server = AudioRelayServer('192.168.1.9', 8765, gemini_client)
    # Start processing the audio stream in parallel
    audio_task = asyncio.create_task(gemini_client.process_audio_stream())
    server_task = asyncio.create_task(relay_server.start_server())
    await asyncio.gather(audio_task, server_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted.")
