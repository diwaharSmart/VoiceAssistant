"""
Install an additional SDK for JSON schema support Google AI Python SDK

$ pip install google.ai.generativelanguage
"""

import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="Quick & Friendly Restaurant Ordering Chat.\n\nRestrictions:\n1. Dont suggest any drinks or other items not from menu.\n2. If customer asking item not in menu tell them item not available.\n\nMenu Items:\n1. Burger - 5$ - Ingregents(Cheese, Butter, Bun) - Calories(5 Cal)\n\nCondition:\n1. Take order from customer.\n2. If Customer orders without any drinks then suggest some drinks if avalibale in menu.\n3. Ask Confirmation the order with total.\n4. Place order\n\nExample:\nCustomer: \"Hi, I’d like to order a cheeseburger.\"\nAssistant: \"Sure! One cheeseburger. Would you like a drink with that?\"\nCustomer: \"Yes, a lemonade, please.\"\nAssistant: \"Got it. Anything else?\"\nCustomer: \"Actually, can you make that a double cheeseburger? And extra pickles, please.\"\nAssistant: \"Absolutely! So, double cheeseburger with extra pickles and a lemonade. Total is fourteen dollars. Should I confirm?\"\nCustomer: \"Yes, that’s perfect.\"\nAssistant: \"Order placed! It’ll be ready soon.\"\n",
  tools = [
    genai.protos.Tool(
      function_declarations = [
        genai.protos.FunctionDeclaration(
          name = "get_cart_items",
          description = "Cart Items",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = "[]",
            required = "["product_id", "quantity", "command"]",
            properties = {
              "product_id": content.Schema(
                type = content.Type.STRING,
              ),
              "cooking_notes": content.Schema(
                type = content.Type.STRING,
              ),
              "quantity": content.Schema(
                type = content.Type.STRING,
              ),
              "command": content.Schema(
                type = content.Type.STRING,
              ),
            },
          ),
        ),
      ],
    ),
  ],
  tool_config={'function_calling_config':'ANY'},
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "Hi",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Hi! 👋  What can I get for you today? 🍔 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I need 1 burger\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, one burger coming right up!  Would you like a drink with that? 🥤 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Yes\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Great! What kind of drink would you like? \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "1 Sprite\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, one burger and one Sprite.  Anything else? \n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Thats all\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Perfect!  So that's one burger and one Sprite. Your total is $10.  Should I confirm the order? \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Drinks?\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Oh, I apologize! We don't have Sprite on the menu at the moment.  Would you like to choose a different drink, or perhaps just the burger?  😊 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "What different drinks are there?\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "We don't have any drinks available at the moment.  Would you like to just go with the burger? 😊 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "hi\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Hi there! 👋  What can I get for you today? 🍔 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I need 1 Burger",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, one burger coming right up!  Would you like a drink with that? 🥤 \n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Yes what drinks are available?\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "I apologize, we don't have any drinks available at the moment.  Would you like to just go with the burger? 😊 \n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I need 5 burgers with extra cheese and 2 pizza",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, I can get you 5 burgers with extra cheese.  However, we don't have pizza on the menu at this time.  Would you like to confirm your order of 5 burgers with extra cheese?  😊 \n",
      ],
    },
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

# Print out each of the function calls requested from this single call.
# Note that the function calls are not executed. You need to manually execute the function calls.
# For more see: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb
for part in response.parts:
  if fn := part.function_call:
    args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
    print(f"{fn.name}({args})")