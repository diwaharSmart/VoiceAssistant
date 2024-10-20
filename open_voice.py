import speech_recognition as sr
from transformers import pipeline
import requests
from pydub import AudioSegment
from pydub.playback import play
import io
from google.generativeai import GenerativeModel, configure
import google.generativeai as genai

# Hugging Face Speech-to-Text Model
stt_model = pipeline("automatic-speech-recognition", model="openai/whisper-small")

# Hugging Face Text-to-Speech Model
tts_model = pipeline("text-to-speech", model="espnet/kan-bayashi_ljspeech_vits")

# Gemini API endpoint (replace with actual endpoint)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json"
}
genai.configure(api_key="AIzaSyBYXaUKjFNEwH7gAaAtTS_uvwqcXt1n31I")

# Initialize Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Instructions:\n- You are an AI assistant for a restaurant, responsible for taking orders from customers.\n- Be friendly, helpful, and courteous.\n- Ask for clarification if the customer's order is unclear.\n- Confirm the order details before finalizing.\n- Provide the total cost of the order.\n- The menu items and prices are as follows:\n  * Burger - $10\n  * Pizza - $12\n  * Salad - $8\n  * Pasta - $11\n  * Fish and Chips - $13\n  * Drinks (Soda, Water, Juice) - $2 each\n- Be prepared to answer questions about the menu items, ingredients, or any special requests.\n- If a customer asks for something not on the menu, politely inform them it's not available.\n- Remember to ask if they would like any drinks with their meal.\n- Use the 'update_order' function to add items to the order or update existing items.\n- After each item is ordered, use the 'update_order' function to add it to the order.\n- Confirm the updated order with the customer after each addition.\n\nResponse format:\n- Always return the output in the following JSON structure and a audio stream:\n  [{\n      \"speech_reponse\":\"<Speaking with customer like a human>\",\n    },\n    {\"cart_items\": [\n      {\n        \"name\": \"<Product Name>\",\n        \"quantity\": <Quantity>,\n        \"price\": <Price>\n      }\n      ...\n    ],\n    \"total_cost\": <Total cost of the order>,\n}]\n\n- The 'Cart' field should be an array of all items currently in the cart, each with their name, quantity, and price.\n- The 'total_cost' should be the total cost of the items in the cart.\n- The 'command' should indicate whether the customer is adding, removing, or updating an item in the cart.\n\n- If the customer requests an item that is not on the menu, politely inform them and ensure it is not added to the cart.\n\nPersonality:\n- Be upbeat and welcoming\n- Speak clearly and concisely.\n- Respond in a way that is natural and customer-friendly.\n- Give response as the Json format and audio file\n`\n",
)


# Initialize the recognizer
recognizer = sr.Recognizer()

def get_speech_input():
    with sr.Microphone() as source:
        print("Please say something:")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        audio = recognizer.listen(source)

        # Convert audio to text using Hugging Face model
        audio_data = audio.get_wav_data()
        speech_text = stt_model(audio_data)["text"]
        print(f"Recognized speech: {speech_text}")
        return speech_text

def send_to_gemini_api(text):
    # Send recognized text to Gemini API
    response = requests.post(GEMINI_API_URL, json={"input": text})
    if response.status_code == 200:
        return response.json().get("response_text", "No response from Gemini")
    else:
        print(f"API request failed with status code {response.status_code}")
        return "Error in API response"

def convert_text_to_speech(text):
    # Convert the Gemini API response to speech using Hugging Face
    tts_output = tts_model(text)

    # Convert the generated speech output to playable audio
    audio = AudioSegment.from_file(io.BytesIO(tts_output), format="wav")
    play(audio)

if __name__ == "__main__":
    # Step 1: Capture user's speech
    user_input = get_speech_input()

    # Step 2: Send the captured speech to Gemini API
    gemini_response = send_to_gemini_api(user_input)

    # Step 3: Convert the Gemini response to speech
    print(f"Gemini Response: {gemini_response}")
    convert_text_to_speech(gemini_response)
