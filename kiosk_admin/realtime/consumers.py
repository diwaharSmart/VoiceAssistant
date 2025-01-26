import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from io import BytesIO
import numpy as np
import base64  # For converting bytes to a text format
# import soundfile as sf  # For saving OGG files
import os
import google.generativeai as genai
import time
from base.models import *
from asgiref.sync import sync_to_async, async_to_sync
import boto3
from realtime.serializer import *
import io
from realtime.stt import *
import noisereduce as nr
from elevenlabs import ElevenLabs, VoiceSettings
from openai import OpenAI
import time
from website.models import CommonUtils

from django.db.models.functions import Cast
from django.db.models import F, FloatField
matches = Match.objects.all().filter(is_active=True, sport=sport).annotate(start_at_float=Cast('start_at', FloatField())).order_by('start_at_float')


try:
    common_utils = CommonUtils.objects.all()[0]
    result_dict = {}
    exec(common_utils.content, {}, result_dict)
    print("Author : "+result_dict.get("author"))

except Exception as e:
    print(f"Error getting common utils: {str(e)}")

session = boto3.Session(
    aws_access_key_id='AKIAZQ3DUFIK26LNH35Z',
    aws_secret_access_key='Q/D+obwgwG2ProirfC5QAMBr7OZ5pmR8etMM8JuD',
    region_name='us-east-1'  # or your preferred region
)
elevenlab_client = ElevenLabs(
            api_key="sk_42e4ac29610e59db0b3dfedc81e4b91d26815b592483d068",
        )

open_ai_client = OpenAI(
    api_key = "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"
)
polly_client = session.client('polly')
genai.configure(api_key="AIzaSyAVep7d9vRn1MbkAN8c-RwKjC-ISZqMjWs")


class RealtimeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("connected "+self.scope["url_route"]["kwargs"]["room_name"])
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"realtime_{self.room_name}"
        self.audio_buffer = []
        self.chat_history = []
        self.gemini_audio_history = []
        self.audio_counter = 0
        self.available_languages = ["en-us","es-us"]
        self.language = "en-us"
        self.set_language = False
        self.session, self.cart = await self.get_or_create_session_and_cart()
        self.configuration = await self.get_model_configuration("GenAI")
        system_instructions = self.configuration.system_instruction.replace("$product_info",str(self.load_product_data()))
        system_instructions = system_instructions.replace("$language",self.language)
        self.instructions = system_instructions
        self.welcome_text = self.configuration.welcome_text
        self.post_welcome_text = self.configuration.post_welcome_text
        self.language_voice_map = {"en-us": "Joanna", "es-us": "Mia"}
        self.aii = result_dict['AssemblyAIWebSocket']("63a9fd56f22647fa9de59fe4b4023e97",on_final_transcript=self.send_final_transcript,on_partial_transcript=self.stop_audio)
        await self.aii.connect()



        self.generation_config = {
            "temperature": float(self.configuration.temperature),
            "top_p": float(self.configuration.top_p),
            "top_k": int(self.configuration.top_k),
            "max_output_tokens": int(self.configuration.max_output_tokens),
            "response_mime_type": self.configuration.response_mime_type
            }

        self.genai_model = genai.GenerativeModel(
                            model_name="gemini-1.5-flash",
                            generation_config=self.generation_config,
                            system_instruction=self.instructions,
                        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()


        self.chat_history.append({
                        "role": "model",
                        "parts": [
                            self.welcome_text,
                        ],
        })
        # self.welcome_text ="""The following code examples show you how to perform actions and implement common scenarios by using the AWS SDK for Python (Boto3) with Amazon Polly. Actions are code excerpts from larger programs and must be run in context. While actions show you how to call individual service functions, you can see actions in context in their related scenarios."""
        # await self.openai_text_to_speech(self.welcome_text)
        await self.convert_text_to_speech(self.welcome_text)
        
        



    async def audio_data(self):
        while True:
            bytes_data = await self.receive()
            yield bytes_data

    async def disconnect(self, close_code):
        # await self.update_session_end()
        self.aii.close()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def get_model_configuration(self, name):
        """
        Retrieve the model configuration based on the name.
        """
        try:
            # Await the query and convert to a list
            config_list = await sync_to_async(list)(ModelConfigurations.objects.filter(name=name))
            return config_list[0] if config_list else None
        except Exception as e:
            print(f"Error retrieving model configuration: {str(e)}")
            return None

    def get_cart(self, cart_id):
        """
        This is a synchronous method that retrieves the cart from the database.
        It is wrapped with sync_to_async when called asynchronously.
        """
        try:
            return Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return None

    async def send_cart_data(self):
        try:
            # Retrieve the cart asynchronously
            cart_id = self.cart.id
            cart = await sync_to_async(self.get_cart)(cart_id)  # Fetch the cart asynchronously

            if cart:
                # Fetch cart items and their products asynchronously
                cart_items = await sync_to_async(list)(cart.items.select_related('product').all())  # Select related product to minimize queries
                
                # Manually prepare the serialized data
                cart_data = {
                    "id": cart.id,
                    "total": str(cart.total),
                    "items": []
                }

                # Manually construct each cart item and its associated product
                for item in cart_items:
                    product = item.product  # Already fetched with select_related
                    product_data = {
                        "id": product.id,
                        "thumbnail": product.thumbnail.url if product.thumbnail else None,
                        "name": product.name,
                        "price": str(product.price),
                        "audio_key": product.audio_key
                    }
                    cart_item_data = {
                        "id": item.id,
                        "quantity": item.quantity,
                        "instructions": item.instructions,
                        "line_total": str(item.line_total),
                        "product": product_data
                    }
                    cart_data["items"].append(cart_item_data)
                # Send the manually constructed serialized data
                await self.send(text_data=json.dumps({"command": "cart_data", "cart": cart_data}))
                
            else:
                await self.send(text_data=json.dumps({"error": "Cart not found"}))

        except Exception as e:
            print(f"Error sending cart data: {str(e)}")
            await self.send(text_data=json.dumps({"error": "Failed to retrieve cart data"}))
    

    async def send_final_transcript(self, transcript_text):
        if "english" in transcript_text.lower():
            self.language = "en-us"
        if "spanish" in transcript_text.lower():
            self.language = "es-us"
            transcript_text =  "Spanish(Mexican)"
        print(transcript_text)
        start_time = time.time()
        elapsed_time = time.time() - start_time
        print(f"Proccess Starts: {elapsed_time:.2f} seconds")
        transcript = transcript_text
        # print(transcript)
        if transcript:
            user_input = {
                "role": "user",
                "parts": transcript,
                }
            response = self.genai_model.start_chat(history=self.chat_history).send_message(user_input)
            print(response.text)
            self.chat_history.append(user_input)

            self.chat_history.append({
                "role": "model",
                "parts": [
                    response.text,
                ],
                })
            

            elapsed_time = time.time() - start_time
            print(f"Cart Starts: {elapsed_time:.2f} seconds")
            try:
                #thread
                await self.update_cart(json.loads(response.text)[1]["cart_items"])
                
            except:
                pass
            elapsed_time = time.time() - start_time
            print(f"Cart Ends: {elapsed_time:.2f} seconds")
            
            elapsed_time = time.time() - start_time
            print(f"Speech Starts: {elapsed_time:.2f} seconds")
            try:
                speech_audio = await self.convert_text_to_speech(json.loads(response.text)[0]["speech_response"])
                
            except:
                pass
            elapsed_time = time.time() - start_time
            print(f"Speech Ends: {elapsed_time:.2f} seconds")

    async def stop_audio(self):
        await self.send(text_data=json.dumps({"command": "stop_audio"}))
    
    async def receive(self, bytes_data=None, text_data=None):    
        if bytes_data:    
            # print(bytes_data)
            audio_array = np.frombuffer(bytes_data, dtype=np.int16)
            # Perform noise reduction on the audio array
            audio_chunk = nr.reduce_noise(y=audio_array, sr=16000)
            # Convert the processed audio back to bytes to send
            audio_chunk_bytes = audio_chunk.astype(np.int16).tobytes()
            # Send the processed audio to AssemblyAI
            await self.aii.send_audio_byte_to_assembly_ai(audio_chunk_bytes)
            
        if text_data:

            text_data_json = json.loads(text_data)
            command = text_data_json.get("command")

            if command == "text_input":
                await self.send_final_transcript(text_data_json.get("text"))
            if command == "get_cart":
                await self.handle_get_cart()
            elif command == "save":
                await self.save_audio_buffer(text_data_json)  # Save audio buffer as OGG and return as base64
            


    async def update_cart(self, new_items):
        """
        Clear the existing cart items and add new items received from the client.
        """
        # Clear existing items
        await sync_to_async(self.cart.items.all().delete)()  # Delete all existing cart items

        # Add new items
        for item in new_items:
            product_id = item.get('id')
            quantity = item.get('quantity')
            instruction = item.get('instruction')
            # Retrieve the product (make sure to handle cases where product might not exist)
            product = await sync_to_async(Product.objects.get)(id=product_id)
            # Create a new CartItem
            cart_item = CartItem(cart=self.cart, product=product, quantity=quantity,instructions=instruction)
            await sync_to_async(cart_item.save)()  # Save the new cart item
            
        await self.send_cart_data()


        # Update the cart total after modifying items

    async def elevenlabs_text_to_speech(self, text):
        await self.send(text_data=json.dumps({"command": "stop_audio"}))
        start_time = time.time()

        audio_stream = elevenlab_client.text_to_speech.convert_as_stream(
            voice_id="pMsXgVXv3BLzUgSXRplE",
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            voice_settings=VoiceSettings(
                stability=0.1,
                similarity_boost=0.1,
                style=0.1,
            ),
        )
        elapsed_time = time.time() - start_time
        print(f"Audio Stream Gen: {elapsed_time:.2f} seconds")

        # Iterate synchronously over the generator
        for audio_chunk in audio_stream:
            # Encode the audio chunk in base64
            
            audio_base64 = base64.b64encode(audio_chunk).decode('utf-8')

            # print(audio_base64)
            # print("\n\n\n")
            # print(audio_base64)
            # Send audio bytes to client asynchronously
            await self.send(text_data=json.dumps({
                "command": "play_audio",
                "audio_bytes": audio_base64
            }))
            elapsed_time = time.time() - start_time
            print(f"Eleven Labs Elapsed time: {elapsed_time:.2f} seconds")

        
        
        # Notify the client when audio has finished playing
        
    # async def openai_text_to_speech(self, text):
    #     # Notify the client that the audio has finished
    #     await self.send(text_data=json.dumps({"command": "stop_audio"}))
    #     # Initialize the streaming request
    #     start_time = time.time()
    #     response = open_ai_client.audio.speech.create(
    #         model="tts-1",
    #         voice="nova",
    #         input=text,
    #     )
    #     elapsed_time = time.time() - start_time
    #     print(f"Audio Stream Gen: {elapsed_time:.2f} seconds")
    #     audio_stream = await response.aiter_bytes()

    #     # Now you can async iterate over the audio chunks
    #     async for audio_chunk in audio_stream:
    #         # Convert the audio chunk to base64
    #         audio_base64 = base64.b64encode(audio_chunk).decode("utf-8")
    #         # print(audio_base64)
    #         # print("\n\n\n")

    #         # Send the encoded audio chunk to the WebSocket client
    #         await self.send(text_data=json.dumps({
    #             "command": "play_audio",
    #             "audio_bytes": audio_base64
    #         }))
    #         elapsed_time = time.time() - start_time
    #         print(f"Open ai Elapsed time: {elapsed_time:.2f} seconds")
        
        
    



    async def convert_text_to_speech(self, text):
        """Convert text to speech using Amazon Polly."""
        try:
            start_time = time.time()
            response = polly_client.synthesize_speech(
                Text=f"<speak><prosody rate='100%'>{text}</prosody></speak>",  # Adjust rate as needed
                OutputFormat='mp3',
                VoiceId=self.language_voice_map[self.language],
                Engine='standard',
                TextType='ssml'
            )
            elapsed_time = time.time() - start_time
            print(f"Audio Stream Gen: {elapsed_time:.2f} seconds")
            audio_stream = response.get('AudioStream')
            # while True:
            #     audio_chunk = audio_stream.read(1024)  # Read in small chunks
            #     if not audio_chunk:
            #         break  # Exit loop if no more audio chunks

            #     # Convert to base64
            #     audio_base64 = base64.b64encode(audio_chunk).decode("utf-8")
            #     # print(audio_base64)
            #     # print("\n\n\n")

            #     # Send the audio chunk to the client
            #     await self.send(text_data=json.dumps({
            #         "command": "play_audio",
            #         "audio_bytes": audio_base64
            #     }))
                
            if audio_stream:
                audio_bytes = audio_stream.read()
                await self.send(text_data=json.dumps({"command": "stop_audio"}))
                await self.send(text_data=json.dumps({"command": "play_audio", "audio_bytes": base64.b64encode(audio_bytes).decode('utf-8')}))
                elapsed_time = time.time() - start_time
                print(f"Amazon Polly Elapsed time: {elapsed_time:.2f} seconds")
                response =self.genai_model.start_chat(history=self.chat_history).send_message("I Need 5 Burger and 1 Pizza with sprite")
                print(response)
                elapsed_time = time.time() - start_time
                print(f"Gemini Elapsed time: {elapsed_time:.2f} seconds")

                
        except Exception as e:
            print(f"Error converting text to speech: {str(e)}")
            return None

    async def get_or_create_session_and_cart(self):
        """
        Retrieve or create a session and a cart based on the room name.
        """
        session_id = self.room_name
        
        # Use sync_to_async to get or create session and cart
        session, created = await sync_to_async(Session.objects.get_or_create)(session_id=session_id)
        cart, cart_created = await sync_to_async(Cart.objects.get_or_create)(session=session)
        
        return session, cart

    async def upload_to_gemini(self,path, mime_type=None):
        """Uploads the given file to Gemini.

        See https://ai.google.dev/gemini-api/docs/prompting_with_media
        """
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    

    async def handle_get_cart(self):
        await self.send_cart_data()

    def load_product_data(self):
        """
        Load product data from product.json file.
        """
        json_file_path = os.path.join("media", "product.json")  # Adjust path as necessary
        try:
            with open(json_file_path, 'r') as json_file:
                product_data = json.load(json_file)
                return product_data

        except FileNotFoundError:
            print("Product JSON file not found.")
            return []
            
        except json.JSONDecodeError:
            print("Error decoding JSON from the product file.")
            return []


