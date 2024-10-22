import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import vosk
import webrtcvad
from io import BytesIO
import numpy as np
import base64  # For converting bytes to a text format
import soundfile as sf  # For saving OGG files
import os
import google.generativeai as genai
import time
from base.models import *
from asgiref.sync import sync_to_async, async_to_sync
import boto3
from realtime.serializer import *

session = boto3.Session(
    aws_access_key_id='AKIAZQ3DUFIK26LNH35Z',
    aws_secret_access_key='Q/D+obwgwG2ProirfC5QAMBr7OZ5pmR8etMM8JuD',
    region_name='us-east-1'  # or your preferred region
)

polly_client = session.client('polly')
genai.configure(api_key="AIzaSyBYXaUKjFNEwH7gAaAtTS_uvwqcXt1n31I")


class RealtimeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"realtime_{self.room_name}"
        self.vosk_model = vosk.Model("/home/anonymous/VoiceAssistant/vosk-model-en-us-daanzu-20200905")
        self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
        self.audio_buffer = []
        self.chat_history = []
        self.gemini_audio_history = []
        self.audio_counter = 0
        self.available_languages = ["en","es"]
        self.language = "english"
        self.session, self.cart = await self.get_or_create_session_and_cart()
        self.configuration = await self.get_model_configuration("GenAI")
        system_instructions = self.configuration.system_instruction.replace("$product_info",str(self.load_product_data()))
        system_instructions = system_instructions.replace("$language",self.language)
        self.instructions = system_instructions
        # print(self.instructions)
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

    async def disconnect(self, close_code):
        # await self.update_session_end()
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

        

    async def receive(self, bytes_data=None, text_data=None):
        if bytes_data:
            # print(bytes_data)
            
            if self.recognizer.AcceptWaveform(bytes_data):
                result = self.recognizer.Result()
                result_json = json.loads(result)
                transcript = result_json.get('text', '')
                print("Audio to Text :", transcript)
                if transcript not in [None, '','huh',"oh"]:
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
                    try:
                        await self.send(text_data=json.dumps({"command":"speech_response","text":json.loads(response.text)[0]["speech_response"]}))
                        
                    except:
                        pass
                    try:
                        await self.update_cart(json.loads(response.text)[1]["cart_items"])
                    except:
                        pass
                   
                    try:
                        speech_audio = await self.convert_text_to_speech(json.loads(response.text)[0]["speech_response"])
                        await self.send(text_data=json.dumps({"command":"audio_data","bytes":speech_audio}))
                    except:
                        pass
            else:
                partial_result = self.recognizer.PartialResult()
                    
        elif text_data:
            text_data_json = json.loads(text_data)
            command = text_data_json.get("command")
            if command == "get_cart":
                await self.handle_get_cart()
            elif command == "save":
                await self.save_audio_buffer(text_data_json)  # Save audio buffer as OGG and return as base64
            else:
                await self.send(text_data=json.dumps({"error": "Unknown command"}))

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
        


    async def convert_text_to_speech(self, text):
        """Convert text to speech using Amazon Polly."""
        try:
            response = polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Joanna',
                Engine='neural'
            )
            audio_stream = response.get('AudioStream')
            if audio_stream:
                audio_bytes = audio_stream.read()
                return audio_bytes
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