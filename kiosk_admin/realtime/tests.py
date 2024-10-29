# import os
import time
# from anthropic import Anthropic
# ANTHROPIC_API_KEY = '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'
# XAI_API_KEY = "xai-XEjY420OFdQAfeTumOYUkceVft9IEcFhODTva3lG78t6dqnHOTJb9cv4Sm452Z2aqFHDiSwL8zAIDbdi"


# from elevenlabs import ElevenLabs, VoiceSettings

# client = ElevenLabs(
#     api_key="YOUR_API_KEY",
# )
# client.text_to_speech.convert_as_stream(
#     voice_id="pMsXgVXv3BLzUgSXRplE",
#     optimize_streaming_latency="0",
#     output_format="mp3_22050_32",
#     text="It sure does, Jackie… My mama always said: “In Carolina, the air's so thick you can wear it!”",
#     voice_settings=VoiceSettings(
#         stability=0.1,
#         similarity_boost=0.3,
#         style=0.2,
#     ),
# )


# client = Anthropic(
#     api_key=XAI_API_KEY,
#     base_url="https://api.x.ai",
# )

# # Start the timer
# start_time = time.time()

# # Make the API call
# message = client.messages.create(
#     model="grok-beta",
#     max_tokens=128,
#     system="""You are a Restaurant order booking Assistant
#     AI Assistant for Restaurant Orders. 
#     Personality : Kind
#     Response : Simple Response
#     Menu Items : {"name": "Burger", "description": "","id": "1"}
#     """,
#     messages=[
#         {
#             "role": "user",
#             "content": "Get weathe of dindigul",
#         },
#     ],
    
    
# )

# # Calculate elapsed time
# elapsed_time = time.time() - start_time
# print(f"Elapsed time: {elapsed_time:.2f} seconds")
# # Print the response and elapsed time
# print(message.content)



# import os
# import time
# from openai import OpenAI

# client = OpenAI(
#     api_key=XAI_API_KEY,
#     base_url="https://api.x.ai/v1",
# )

# start_time = time.time()
# completion = client.chat.completions.create(
#     model="grok-beta",
#     max_tokens = 200,
#     # stream= True,
#     messages=[
#         {"role": "system", 
#         "content": """You are a Restaurant order booking Assistant
#                       AI Assistant for Restaurant Orders.
#                       Personality: Kind
#                       Response: Simple Response
#                       Menu Items: {"name": "Burger", "description": "", "id": "1","price": "$8.99"}
#                       """
#         },
#         {"role": "user", 
#         "content": "I need one Burger"
#         },
#         {"role": "system", 
#         "content": "Sure adding to your cart. Anything else you'd like to order?"
#         }
#     ],
# )

# # Calculate elapsed time

# # Print the response and elapsed time
# # print(completion.choices[0].message)
# for chunk in completion:
#     print(chunk)
# elapsed_time = time.time() - start_time
# print(f"Elapsed time: {elapsed_time:.2f} seconds")


# import os
# import google.generativeai as genai

# genai.configure(api_key="AIzaSyBYXaUKjFNEwH7gAaAtTS_uvwqcXt1n31I")


    
# cart = {
#     'name': "cart_items",
#     'description': "Get Product item",
#     'parameters': {
#         "type": "object",
#         "properties": {
#             "command": {
#                 "type": "string",
#                 "description": "add/remove/update"
#             },
#             "id": {
#                 "type": "number",
#                 "description": "id of the product"
#             },
#             "instruction": {
#                 "type": "string",
#                 "description": "(eg : Extra Cheese and Tomato) or None"
#             },
#             "quantity": {
#                 "type": "number",
#                 "description": "Quantity of the product"
#             },
#         },
#         "required": [
#             "id",
#             "command",
#             "quantity",
#         ]
#     },
# }

# prompt = "I want one burger and two pizza"
# genai.configure(api_key="AIzaSyBYXaUKjFNEwH7gAaAtTS_uvwqcXt1n31I")
# generation_config = {
#             "temperature": float(0.5),
#             "top_p": float(0.95),
#             "top_k": int(40),
#             "max_output_tokens": int(1500),
            
#             }

# start_time = time.time()
# genai_model = genai.GenerativeModel(
#                             model_name="gemini-1.5-flash",
#                             generation_config=generation_config,
#                             system_instruction="""
#                             [{"id":"1","name":"burger","price":"$9.9"},{"id":"2","name":"pizza","price":"$9.5"},
#                             """,
#                             tools=[{
#                                 'function_declarations': [cart],
#                             }],
#                         )

# response = genai_model.start_chat(history=[{
#                         "role": "user",
#                         "parts": "I need one Pizza",
#                         },
#                         {
#                         "role": "model",
#                         "parts": "I pizza Added to you order. Anything else you want",
#                         },
#                         ]).send_message("I need 2 burgers instead of 3 Burger")

# elapsed_time = time.time() - start_time
                   

# print(response)
# print(f"Elapsed time: {elapsed_time:.2f} seconds")     
# function_call = response.candidates[0].content.parts[0].function_call
# args = function_call.args
# function_name = function_call.name

# if function_name == 'score_checker':
#     result = score_checker(args['score'])


# response = model.generate_content(
#     "Based on this information `" + result + "` respond to the student in a friendly manner.",
# )
# print(response.text)

# import base64
# from openai import OpenAI

# client = OpenAI(
#     api_key = "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"
# )

# from pathlib import Path
# from openai import OpenAI

# speech_file_path = Path(__file__).parent / "s1.mp3"
# response = client.audio.speech.create(
#   model="tts-1",
#   voice="nova",
#   input="Hola! Mi nombre es Penelope. Puedo leer cualquier texto que introduzcas aquí."
# )

# response.stream_to_file(speech_file_path)


# import pyaudio
# import requests
# import datetime
# from botocore.auth import SigV4Auth
# from botocore.awsrequest import AWSRequest
# from botocore.credentials import Credentials

# # AWS credentials and settings
# access_key = 'AKIAZQ3DUFIK26LNH35Z'
# secret_key = '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'
# region = 'us-west-2'
# service = 'transcribe'

# # URL for Amazon Transcribe
# url = f"https://transcribestreaming.{region}.amazonaws.com/stream-transcription"

# # Audio configuration
# sample_rate = 16000  # Set according to the chosen sample rate
# chunk_size = 1024  # Size of audio chunks sent

# # Headers
# headers = {
#     'Content-Type': 'application/vnd.amazon.eventstream',
#     'X-Amz-Target': 'com.amazonaws.transcribe.Transcribe.StartStreamTranscription',
#     'X-Amz-Content-Sha256': 'STREAMING-AWS4-HMAC-SHA256-EVENTS',
#     'X-Amz-Date': datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'),
#     'x-amzn-transcribe-media-encoding': 'flac',
#     'x-amzn-transcribe-sample-rate': str(sample_rate),
#     'x-amzn-transcribe-identify-language': 'true',
#     'x-amzn-transcribe-language-options': 'en-US,de-DE',
#     'x-amzn-transcribe-preferred-language': 'en-US',
#     'Transfer-Encoding': 'chunked',
# }

# # Request signing
# req = AWSRequest(method="POST", url=url, headers=headers)
# req.context['timestamp'] = headers['X-Amz-Date']
# credentials = Credentials(access_key, secret_key)
# SigV4Auth(credentials, service, region).add_auth(req)

# # Initialize PyAudio to capture audio data from the microphone
# audio = pyaudio.PyAudio()
# stream = audio.open(format=pyaudio.paInt16,
#                     channels=1,
#                     rate=sample_rate,
#                     input=True,
#                     frames_per_buffer=chunk_size)

# def stream_audio():
#     """Generator function to stream audio chunks."""
#     try:
#         while True:
#             data = stream.read(chunk_size)
#             yield data
#     except Exception as e:
#         print("Audio streaming stopped:", e)
#         stream.stop_stream()
#         stream.close()
#         audio.terminate()

# # Send audio to Amazon Transcribe and receive transcription results
# try:
#     with requests.post(url, headers=dict(req.headers), data=stream_audio(), stream=True) as response:
#         if response.status_code == 200:
#             for chunk in response.iter_content(chunk_size=1024):
#                 print(chunk.decode())  # Process transcription in real-time
#         else:
#             print("Failed to start transcription:", response.text)
# finally:
#     stream.stop_stream()
#     stream.close()
#     audio.terminate()

# import asyncio
# import boto3
# import websockets
# import json
# import pyaudio
# import base64
# import hmac
# import hashlib
# import time
# from urllib.parse import urlencode

# # Initialize PyAudio
# p = pyaudio.PyAudio()

# # Audio stream settings
# stream = p.open(format=pyaudio.paInt16,
#                 channels=1,
#                 rate=16000,
#                 input=True,
#                 frames_per_buffer=1024)

# # Get AWS credentials from your environment or configure manually
# client = boto3.client('transcribe')
# access_key = boto3.Session().get_credentials().access_key
# secret_key = boto3.Session().get_credentials().secret_key
# region = "us-west-2"  # Replace with your region
# session = boto3.Session()
# credentials = session.get_credentials().get_frozen_credentials()
# access_key = credentials.access_key
# secret_key = credentials.secret_key
# from botocore.auth import SigV4Auth
# from botocore.awsrequest import AWSRequest
# # Helper to create a signed WebSocket URL

# def create_websocket_url():
#     endpoint = f"wss://transcribestreaming.{region}.amazonaws.com:8443/stream-transcription-websocket"
#     params = {
#         "media_encoding": "pcm",
#         "language_code": "en-US",
#         "sample_rate": "16000"
#     }
#     url = f"{endpoint}?{urlencode(params)}"
#     return url

# async def send_audio(uri):
#     async with websockets.connect(uri) as ws:
#         print("Connected to AWS Transcribe WebSocket")

#         # Stream audio in real-time
#         while True:
#             # Read a chunk of audio and send it as base64-encoded PCM
#             audio_chunk = stream.read(1024)
#             payload = {
#                 "AudioEvent": {
#                     "AudioChunk": base64.b64encode(audio_chunk).decode("utf-8")
#                 }
#             }
#             await ws.send(json.dumps(payload))

# async def receive_transcription(uri):
#     async with websockets.connect(uri) as ws:
#         async for message in ws:
#             result = json.loads(message)
#             if "Transcript" in result:
#                 transcript = result["Transcript"]["Results"][0]["Alternatives"][0]["Transcript"]
#                 print("Transcript:", transcript)

# # Run send and receive as concurrent tasks
# async def main():
#     uri = create_websocket_url()
#     await asyncio.gather(send_audio(uri), receive_transcription(uri))

# asyncio.run(main())

import asyncio
import boto3
import websockets
import json
import base64
import wave
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from urllib.parse import urlencode

# Audio settings
RATE = 16000
CHUNK = 1024
LANGUAGE_CODE = "en-US"
MEDIA_ENCODING = "pcm"
REGION = "us-west-2"
AUDIO_FILE_PATH = "output.wav"  # Replace with your audio file path

# AWS credentials
session = boto3.Session()
credentials = session.get_credentials().get_frozen_credentials()
access_key = credentials.access_key
secret_key = credentials.secret_key

# Helper to create a signed WebSocket URL for AWS Transcribe
def create_websocket_url():
    endpoint = f"wss://transcribestreaming.{REGION}.amazonaws.com:8443/stream-transcription-websocket"
    params = {
        "language-code": LANGUAGE_CODE,
        "media-encoding": MEDIA_ENCODING,
        "sample-rate": str(RATE),
    }
    query_string = urlencode(params)
    request_url = f"{endpoint}?{query_string}"

    # Create a SigV4-signed request for WebSocket URL
    headers = {"host": f"transcribestreaming.{REGION}.amazonaws.com"}
    request = AWSRequest(method="GET", url=request_url, headers=headers)
    SigV4Auth(Credentials(access_key, secret_key), "transcribe", REGION).add_auth(request)

    # Use only the signed query parameters and add them to the WebSocket URL
    signed_params = urlencode(request.headers)
    signed_url = f"{endpoint}?{query_string}&{signed_params}"
    return signed_url

async def send_audio_file(ws, audio_file_path):
    """Stream audio from a file to the WebSocket in real-time."""
    print("Starting to send audio file...")
    try:
        with wave.open(audio_file_path, "rb") as wf:
            while True:
                audio_chunk = wf.readframes(CHUNK)
                if not audio_chunk:
                    break
                payload = {
                    "AudioEvent": {
                        "AudioChunk": base64.b64encode(audio_chunk).decode("utf-8")
                    }
                }
                await ws.send(json.dumps(payload))
        print("Audio file streaming complete.")
    except Exception as e:
        print("Error sending audio file:", e)

async def receive_transcription(ws):
    """Receive transcriptions from AWS Transcribe WebSocket in real-time."""
    print("Receiving transcriptions...")
    try:
        async for message in ws:
            try:
                result = json.loads(message)
                if "Transcript" in result:
                    transcript = result["Transcript"]["Results"][0]["Alternatives"][0]["Transcript"]
                    print("Transcript:", transcript)
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
    except websockets.exceptions.ConnectionClosed as e:
        print("WebSocket connection closed:", e)
    except Exception as e:
        print("Error receiving transcription:", e)


async def main():
    uri = create_websocket_url()
    async with websockets.connect(uri) as ws:
        await asyncio.gather(send_audio_file(ws, AUDIO_FILE_PATH), receive_transcription(ws))

# Run the main function
asyncio.run(main())
