import os
import time
# # from anthropic import Anthropic
# # ANTHROPIC_API_KEY = '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'
XAI_API_KEY = "xai-XEjY420OFdQAfeTumOYUkceVft9IEcFhODTva3lG78t6dqnHOTJb9cv4Sm452Z2aqFHDiSwL8zAIDbdi"


# # from elevenlabs import ElevenLabs, VoiceSettings

# # client = ElevenLabs(
# #     api_key="YOUR_API_KEY",
# # )
# # client.text_to_speech.convert_as_stream(
# #     voice_id="pMsXgVXv3BLzUgSXRplE",
# #     optimize_streaming_latency="0",
# #     output_format="mp3_22050_32",
# #     text="It sure does, Jackie… My mama always said: “In Carolina, the air's so thick you can wear it!”",
# #     voice_settings=VoiceSettings(
# #         stability=0.1,
# #         similarity_boost=0.3,
# #         style=0.2,
# #     ),
# # )


from groq import Groq
start_time = time.time()
client = Groq(api_key="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")
completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "AI Assistant for Restaurant Orders\n\n- Role: You are an AI assistant for a restaurant, responsible for taking customer orders.\n- Speech Response Language: $language\n- Cart Management: Until 'End Session,' do not clear the cart.\n- If user asked items ingredients only tell the given ingredients in other_info\n- if user asks item not in menu. tell item not available now\n- Clarification: Ask for clarification if the customer's order is unclear.\n- Order Confirmation: Confirm the order details before finalizing.\n- Cost: Provide the total cost of the order.\n- Menu Information: The menu items and prices are as follows: [{\"id\":1,\"name\":\"burger\",\"price\":5.00},{\"id\":1,\"name\":\"sprite\",\"price\":2.00}].\n- Questions: Be prepared to answer questions about the menu items, ingredients, or any special requests.\n- Unavailable Items: If a customer asks for something not on the menu, politely inform them it's not available.\n- Drinks Inquiry: Ask if they would like any drinks with their meal.\n- Updated Order Confirmation: Confirm the updated order with the customer after each addition.\n\nResponse Format\n- [Important] Always return the output in the following JSON structure and an audio stream:\n  [{\n      \"speech_response\": \"<Speak to the customer in a friendly manner max 200 characters>\",\n    },\n    {\n      \"cart_items\": [\n        {\n          \"id\": \"<id>\",\n          \"instruction\": \"<e.g., 'Extra Cheese with Tomato' or empty>\",\n          \"quantity\": <Quantity>,\n          \"price\": <Price>\n        }\n      ],\n      \"total_cost\": <Total cost of the order>\n    }\n  ]\n\n- Cart Field: An array of all items currently in the cart, each with their name, quantity, and price.\n- Total Cost: The total cost of the items in the cart.\n- Command: Indicate whether the customer is adding, removing, or updating an item in the cart.\n\n- Unavailable Items: If the customer requests an item that is not on the menu, politely inform them and ensure it is not added to the cart.\n\nPersonality Traits\n- Be upbeat and welcoming.\n- Speak clearly and concisely.\n- Respond in a natural and customer-friendly manner."
        },
        {
            "role": "user",
            "content": "I want one sprite"
        }
    ],
    temperature=1,
    max_tokens=200,
    top_p=1,
    stream=False,
    stop=None,
)

print(completion.choices[0].message.content)


elapsed_time = time.time() - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")



# print("xai")
# import os
# import time
# from openai import OpenAI

# client = OpenAI(
#     api_key=XAI_API_KEY,
#     base_url="https://api.x.ai/v1",
# )

# start_time = time.time()
# elapsed_time = time.time() - start_time
# print(f"Elapsed time: {elapsed_time:.2f} seconds")
# completion = client.chat.completions.create(
#     model="grok-beta",
#     max_tokens = 200,
#     # stream= True,
#     messages=[
#         {"role": "system", 
#         "content": "AI Assistant for Restaurant Orders\n\n- Role: You are an AI assistant for a restaurant, responsible for taking customer orders.\n- Speech Response Language: $language\n- Cart Management: Until 'End Session,' do not clear the cart.\n- If user asked items ingredients only tell the given ingredients in other_info\n- if user asks item not in menu. tell item not available now\n- Clarification: Ask for clarification if the customer's order is unclear.\n- Order Confirmation: Confirm the order details before finalizing.\n- Cost: Provide the total cost of the order.\n- Menu Information: The menu items and prices are as follows: [{\"id\":1,\"name\":\"burger\",\"price\":5.00},{\"id\":1,\"name\":\"sprite\",\"price\":2.00}].\n- Questions: Be prepared to answer questions about the menu items, ingredients, or any special requests.\n- Unavailable Items: If a customer asks for something not on the menu, politely inform them it's not available.\n- Drinks Inquiry: Ask if they would like any drinks with their meal.\n- Updated Order Confirmation: Confirm the updated order with the customer after each addition.\n\nResponse Format\n- [Important] Always return the output in the following JSON structure and an audio stream:\n  [{\n      \"speech_response\": \"<Speak to the customer in a friendly manner max 200 characters>\",\n    },\n    {\n      \"cart_items\": [\n        {\n          \"id\": \"<id>\",\n          \"instruction\": \"<e.g., 'Extra Cheese with Tomato' or empty>\",\n          \"quantity\": <Quantity>,\n          \"price\": <Price>\n        }\n      ],\n      \"total_cost\": <Total cost of the order>\n    }\n  ]\n\n- Cart Field: An array of all items currently in the cart, each with their name, quantity, and price.\n- Total Cost: The total cost of the items in the cart.\n- Command: Indicate whether the customer is adding, removing, or updating an item in the cart.\n\n- Unavailable Items: If the customer requests an item that is not on the menu, politely inform them and ensure it is not added to the cart.\n\nPersonality Traits\n- Be upbeat and welcoming.\n- Speak clearly and concisely.\n- Respond in a natural and customer-friendly manner."
#         },
#         {"role": "user", 
#         "content": "I need one Burger"
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


# # import os
# # import google.generativeai as genai

# # genai.configure(api_key="AIzaSyBYXaUKjFNEwH7gAaAtTS_uvwqcXt1n31I")


    
# # cart = {
# #     'name': "cart_items",
# #     'description': "Get Product item",
# #     'parameters': {
# #         "type": "object",
# #         "properties": {
# #             "command": {
# #                 "type": "string",
# #                 "description": "add/remove/update"
# #             },
# #             "id": {
# #                 "type": "number",
# #                 "description": "id of the product"
# #             },
# #             "instruction": {
# #                 "type": "string",
# #                 "description": "(eg : Extra Cheese and Tomato) or None"
# #             },
# #             "quantity": {
# #                 "type": "number",
# #                 "description": "Quantity of the product"
# #             },
# #         },
# #         "required": [
# #             "id",
# #             "command",
# #             "quantity",
# #         ]
# #     },
# # }

# # prompt = "I want one burger and two pizza"
# # genai.configure(api_key="AIzaSyBYXaUKjFNEwH7gAaAtTS_uvwqcXt1n31I")
# # generation_config = {
# #             "temperature": float(0.5),
# #             "top_p": float(0.95),
# #             "top_k": int(40),
# #             "max_output_tokens": int(1500),
            
# #             }

# # start_time = time.time()
# # genai_model = genai.GenerativeModel(
# #                             model_name="gemini-1.5-flash",
# #                             generation_config=generation_config,
# #                             system_instruction="""
# #                             [{"id":"1","name":"burger","price":"$9.9"},{"id":"2","name":"pizza","price":"$9.5"},
# #                             """,
# #                             tools=[{
# #                                 'function_declarations': [cart],
# #                             }],
# #                         )

# # response = genai_model.start_chat(history=[{
# #                         "role": "user",
# #                         "parts": "I need one Pizza",
# #                         },
# #                         {
# #                         "role": "model",
# #                         "parts": "I pizza Added to you order. Anything else you want",
# #                         },
# #                         ]).send_message("I need 2 burgers instead of 3 Burger")

# # elapsed_time = time.time() - start_time
                   

# # print(response)
# # print(f"Elapsed time: {elapsed_time:.2f} seconds")     
# # function_call = response.candidates[0].content.parts[0].function_call
# # args = function_call.args
# # function_name = function_call.name

# # if function_name == 'score_checker':
# #     result = score_checker(args['score'])


# # response = model.generate_content(
# #     "Based on this information `" + result + "` respond to the student in a friendly manner.",
# # )
# # print(response.text)

# import base64
# from openai import OpenAI

# open_ai_client = OpenAI(
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

# import asyncio
# import boto3
# import websockets
# import json
# import base64
# import wave
# from botocore.auth import SigV4Auth
# from botocore.awsrequest import AWSRequest
# from botocore.credentials import Credentials
# from urllib.parse import urlencode

# # Audio settings
# RATE = 16000
# CHUNK = 1024
# LANGUAGE_CODE = "en-US"
# MEDIA_ENCODING = "pcm"
# REGION = "us-west-2"
# AUDIO_FILE_PATH = "output.wav"  # Replace with your audio file path

# # AWS credentials
# session = boto3.Session()
# credentials = session.get_credentials().get_frozen_credentials()
# access_key = credentials.access_key
# secret_key = credentials.secret_key

# # Helper to create a signed WebSocket URL for AWS Transcribe
# def create_websocket_url():
#     endpoint = f"wss://transcribestreaming.{REGION}.amazonaws.com:8443/stream-transcription-websocket"
#     params = {
#         "language-code": LANGUAGE_CODE,
#         "media-encoding": MEDIA_ENCODING,
#         "sample-rate": str(RATE),
#     }
#     query_string = urlencode(params)
#     request_url = f"{endpoint}?{query_string}"

#     # Create a SigV4-signed request for WebSocket URL
#     headers = {"host": f"transcribestreaming.{REGION}.amazonaws.com"}
#     request = AWSRequest(method="GET", url=request_url, headers=headers)
#     SigV4Auth(Credentials(access_key, secret_key), "transcribe", REGION).add_auth(request)

#     # Use only the signed query parameters and add them to the WebSocket URL
#     signed_params = urlencode(request.headers)
#     signed_url = f"{endpoint}?{query_string}&{signed_params}"
#     return signed_url

# async def send_audio_file(ws, audio_file_path):
#     """Stream audio from a file to the WebSocket in real-time."""
#     print("Starting to send audio file...")
#     try:
#         with wave.open(audio_file_path, "rb") as wf:
#             while True:
#                 audio_chunk = wf.readframes(CHUNK)
#                 if not audio_chunk:
#                     break
#                 payload = {
#                     "AudioEvent": {
#                         "AudioChunk": base64.b64encode(audio_chunk).decode("utf-8")
#                     }
#                 }
#                 await ws.send(json.dumps(payload))
#         print("Audio file streaming complete.")
#     except Exception as e:
#         print("Error sending audio file:", e)

# async def receive_transcription(ws):
#     """Receive transcriptions from AWS Transcribe WebSocket in real-time."""
#     print("Receiving transcriptions...")
#     try:
#         async for message in ws:
#             try:
#                 result = json.loads(message)
#                 if "Transcript" in result:
#                     transcript = result["Transcript"]["Results"][0]["Alternatives"][0]["Transcript"]
#                     print("Transcript:", transcript)
#             except json.JSONDecodeError as e:
#                 print("Error decoding JSON:", e)
#     except websockets.exceptions.ConnectionClosed as e:
#         print("WebSocket connection closed:", e)
#     except Exception as e:
#         print("Error receiving transcription:", e)


# async def main():
#     uri = create_websocket_url()
#     async with websockets.connect(uri) as ws:
#         await asyncio.gather(send_audio_file(ws, AUDIO_FILE_PATH), receive_transcription(ws))

# # Run the main function
# asyncio.run(main())


# import asyncio
# import boto3
# import websockets
# import json
# import base64
# import wave
# from botocore.auth import SigV4Auth
# from botocore.awsrequest import AWSRequest
# from botocore.credentials import Credentials
# from datetime import datetime
# from urllib.parse import urlencode

# # Audio settings
# RATE = 16000
# CHUNK = 1024
# LANGUAGE_CODE = "en-US"
# MEDIA_ENCODING = "pcm"
# REGION = "us-west-2"
# AUDIO_FILE_PATH = "output.wav"  # Replace with your audio file path
# VOCABULARY_NAME = None  # Optional: Add your vocabulary name if available

# # AWS credentials
# session = boto3.Session()
# credentials = session.get_credentials().get_frozen_credentials()
# access_key = credentials.access_key
# secret_key = credentials.secret_key
# session_token = credentials.token  # Temporary credentials support

# # Helper to create a pre-signed WebSocket URL for AWS Transcribe
# def create_websocket_url():
#     endpoint = f"https://transcribestreaming.{REGION}.amazonaws.com:8443/stream-transcription-websocket"
#     params = {
#         "language-code": LANGUAGE_CODE,
#         "media-encoding": MEDIA_ENCODING,
#         "sample-rate": str(RATE),
#     }
#     if VOCABULARY_NAME:
#         params["vocabulary-name"] = VOCABULARY_NAME

#     query_string = urlencode(params)
#     url = f"{endpoint}?{query_string}"

#     # Prepare request for SigV4 signing
#     request = AWSRequest(method="GET", url=url)
#     request.context["timestamp"] = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
#     SigV4Auth(credentials, "transcribe", REGION).add_auth(request)

#     # Create the signed URL by adding signature and headers
#     signed_url = f"{url}&{urlencode(request.headers)}"
#     return signed_url.replace("https://", "wss://")  # Switch to WebSocket Secure

# async def send_audio_file(ws, audio_file_path):
#     """Stream audio from a file to the WebSocket in real-time."""
#     print("Starting to send audio file...")
#     try:
#         with wave.open(audio_file_path, "rb") as wf:
#             while True:
#                 audio_chunk = wf.readframes(CHUNK)
#                 if not audio_chunk:
#                     break
#                 payload = {
#                     "AudioEvent": {
#                         "AudioChunk": base64.b64encode(audio_chunk).decode("utf-8")
#                     }
#                 }
#                 await ws.send(json.dumps(payload))
#         # Signal end of the audio stream
#         await ws.send(json.dumps({"AudioEvent": {}}))
#         print("Audio file streaming complete.")
#     except Exception as e:
#         print("Error sending audio file:", e)

# async def receive_transcription(ws):
#     """Receive transcriptions from AWS Transcribe WebSocket in real-time."""
#     print("Receiving transcriptions...")
#     try:
#         async for message in ws:
#             print(message)
#             try:
#                 result = json.loads(message)
#                 if "Transcript" in result and result["Transcript"]["Results"]:
#                     transcript = result["Transcript"]["Results"][0]["Alternatives"][0]["Transcript"]
#                     print("Transcript:", transcript)
#             except json.JSONDecodeError as e:
#                 print("Error decoding JSON:", e)
#                 print("Received message:", message)  # Log message for debugging
#     except websockets.exceptions.ConnectionClosedError as e:
#         print("WebSocket connection closed unexpectedly:", e)
#     except Exception as e:
#         print("Error receiving transcription:", e)

# async def main():
#     uri = create_websocket_url()
#     async with websockets.connect(uri) as ws:
#         await asyncio.gather(send_audio_file(ws, AUDIO_FILE_PATH), receive_transcription(ws))

# # Run the main function
# asyncio.run(main())

# import jwt
# import time

# # Replace with your actual secret key and other details
# secret_key = 'your_secret_key'
# app_id = 'your_app_id'  # Optional, depending on your Jitsi configuration
# room_name = 'testroom'  # The room you want to join

# # Create the payload
# payload = {
#     "context": {
#         "user": {
#             "name": "Username",
#             "email": "user@example.com"
#         }
#     },
#     "sub": "meet.jit.si",  # Jitsi server domain
#     "room": room_name,
#     "exp": int(time.time()) + 3600  # Token expiry time (1 hour from now)
# }

# # Generate the token
# token = jwt.encode(payload, secret_key, algorithm="HS256")

# # If using PyJWT 2.x, it returns bytes; decode to string if needed
# token = token if isinstance(token, str) else token.decode("utf-8")

# print("Generated JWT token:", token)