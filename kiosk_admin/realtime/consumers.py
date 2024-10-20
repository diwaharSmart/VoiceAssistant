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
        self.audio_buffer = []
        self.chat_history = []
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
            self.audio_buffer.append(bytes_data)  

            
            if self.recognizer.AcceptWaveform(bytes_data):
                result = self.recognizer.Result()
                result_json = json.loads(result)
                transcript = result_json.get('text', '')
                if transcript in [None, '']:
                    self.audio_buffer = []
                if transcript not in [None, '']:
                    
                    print(f"Audio buffer")
                    audio_data = b"".join(self.audio_buffer)
                    self.audio_buffer = []
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    if len(audio_array.shape) == 1:
                        audio_array = np.reshape(audio_array, (-1, 1)) 
                    ogg_file_path = "media/ogg/audio.ogg"
                    sf.write(ogg_file_path, audio_array, 16000, format='OGG')
                    file = await self.upload_to_gemini(ogg_file_path, mime_type="audio/ogg")
                    response = self.genai_model.start_chat(history=self.chat_history).send_message(file)
                    print(response.text)
                    self.chat_history.append({
                        "role": "user",
                        "parts": [
                            file,
                        ],
                        })

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
                        await self.send(text_data=json.dumps({"command":"cart_items","cart_items":{"items":json.loads(response.text)[1]["cart_items"]}}))
                    except Exception as e:
                        print(f"Error sending response to client: {str(e)}")
                    

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

    async def save_audio_buffer(self, text_data_json):
        # Save audio buffer as an OGG file
        ogg_file_path = "audio.ogg"
        self.audio_buffer.seek(0)  # Rewind the buffer to the start
        audio_data = np.frombuffer(self.audio_buffer.read(), dtype=np.int16)  # Convert buffer to numpy array
        sf.write(ogg_file_path, audio_data, 16000, format="OGG")  # Save as OGG

        # Save the JSON data as a JSON file
        json_file_path = "command_data.json"
        with open(json_file_path, "w") as json_file:
            json.dump(text_data_json, json_file)

        # Clear the buffer for next use
        self.audio_buffer = BytesIO()

        # Return the base64-encoded OGG file
        with open(ogg_file_path, "rb") as f:
            ogg_bytes = f.read()
            ogg_base64 = base64.b64encode(ogg_bytes).decode("utf-8")

        await self.send(text_data=json.dumps({"status": "saved", "ogg_base64": ogg_base64}))
