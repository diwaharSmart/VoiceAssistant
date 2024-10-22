import json
import torch
import soundfile as sf
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
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
from concurrent.futures import ThreadPoolExecutor


generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json"
}

genai.configure(api_key="AIzaSyBYXaUKjFNEwH7gAaAtTS_uvwqcXt1n31I")


class RealtimeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"realtime_{self.room_name}"
        self.vosk_model = vosk.Model("/home/anonymous/VoiceAssistant/vosk-model-small-en-us-0.15")
        self.recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
        # self.audio_buffer = []
        self.chat_history = []
        self.gemini_audio_history = []
        self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
        self.wav_vec_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
        self.audio_buffer = BytesIO()  # Use this to accumulate raw audio data
        self.sample_rate = 16000
        self.audio_counter = 0
        self.genai_model = genai.GenerativeModel(
                            model_name="gemini-1.5-flash",
                            generation_config=generation_config,
                            system_instruction="Instructions:\n- You are an AI assistant for a restaurant, responsible for taking orders from customers.\n -Unitil 'End Session' Dont Clear Cart\n- Be friendly, helpful, and courteous.\n- Ask for clarification if the customer's order is unclear.\n- Confirm the order details before finalizing.\n- Provide the total cost of the order.\n- The menu items and prices are as follows:\n  * Burger - $10\n  * Pizza - $12\n  * Salad - $8\n  * Pasta - $11\n  * Fish and Chips - $13\n  * Drinks (Soda, Water, Juice) - $2 each\n- Be prepared to answer questions about the menu items, ingredients, or any special requests.\n- If a customer asks for something not on the menu, politely inform them it's not available.\n- Remember to ask if they would like any drinks with their meal.\n- Use the 'update_order' function to add items to the order or update existing items.\n- After each item is ordered, use the 'update_order' function to add it to the order.\n- Confirm the updated order with the customer after each addition.\n\nResponse format:\n- Always return the output in the following JSON structure and a audio stream:\n  [{\n      \"speech_reponse\":\"<Speaking with customer like a human>\",\n    },\n    {\"cart_items\": [\n      {\n        \"name\": \"<Product Name>\",\n        \"quantity\": <Quantity>,\n        \"price\": <Price>\n      }\n      ...\n    ],\n    \"total_cost\": <Total cost of the order>,\n}]\n\n- The 'Cart' field should be an array of all items currently in the cart, each with their name, quantity, and price.\n- The 'total_cost' should be the total cost of the items in the cart.\n- The 'command' should indicate whether the customer is adding, removing, or updating an item in the cart.\n\n- If the customer requests an item that is not on the menu, politely inform them and ensure it is not added to the cart.\n\nPersonality:\n- Be upbeat and welcoming\n- Speak clearly and concisely.\n- Respond in a way that is natural and customer-friendly.\n- Give response as the Json format and audio file\n`\n",
                        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, bytes_data=None, text_data=None):
        if bytes_data:
            # Accumulate audio data in the buffer
            self.audio_buffer.write(bytes_data)

            # Once enough audio is accumulated, process the buffer
            if self.audio_buffer.tell() > self.sample_rate * 2:  # Process 2 seconds of audio
                # Reset buffer for the next chunk of audio
                self.audio_buffer.seek(0)
                audio_data, _ = sf.read(self.audio_buffer, dtype="float32")
                
                # Clear the buffer after reading
                self.audio_buffer = BytesIO()
                
                # Process the audio data using Wav2Vec2
                inputs = self.processor(audio_data, sampling_rate=self.sample_rate, return_tensors="pt", padding=True)
                with torch.no_grad():
                    logits = self.wav_vec_model(inputs.input_values).logits
                
                # Get predicted IDs and decode transcription
                predicted_ids = torch.argmax(logits, dim=-1)
                transcription = self.processor.batch_decode(predicted_ids)[0]
                print(transcription)

                if transcription not in [None, '', 'huh']:
                    # Pass transcription to the AI model
                    response = self.genai_model.start_chat(history=self.chat_history).send_message(transcription)
                    print(response.text)

                    self.chat_history.append({
                        "role": "user",
                        "parts": transcription,
                    })

                    self.chat_history.append({
                        "role": "model",
                        "parts": [response.text],
                    })

                    # Send the response back to the client
                    try:
                        await self.send(text_data=json.dumps({
                            "command": "speech_response",
                            "text": json.loads(response.text)[0]["speech_response"]
                        }))
                    except Exception as e:
                        print(f"Error sending response: {str(e)}")

                    try:
                        await self.send(text_data=json.dumps({
                            "command": "cart_items",
                            "cart_items": {"items": json.loads(response.text)[1]["cart_items"]}
                        }))
                    except Exception as e:
                        print(f"Error sending cart items: {str(e)}")
                    
        elif text_data:
            text_data_json = json.loads(text_data)
            command = text_data_json.get("command")
            if command == "get_cart":
                await self.handle_get_cart(text_data_json)
            elif command == "save":
                await self.save_audio_buffer(text_data_json)  # Save audio buffer as OGG and return as base64
            else:
                await self.send(text_data=json.dumps({"error": "Unknown command"}))


    async def upload_to_gemini(self,path, mime_type=None):
        """Uploads the given file to Gemini.

        See https://ai.google.dev/gemini-api/docs/prompting_with_media
        """
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    

    async def handle_get_cart(self, data):
        cart = {
            "items": [
                {"product": "Burger", "quantity": 2, "price": 10.00},
                {"product": "Pizza", "quantity": 1, "price": 12.00},
            ],
            "total": 32.00,
        }
        await self.send(text_data=json.dumps({"command": "get_cart", "cart": cart}))