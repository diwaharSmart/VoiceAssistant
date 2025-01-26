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
  "max_output_tokens": 1500,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="Restrictions:\n1. [Important] Do not add any items other than menu\n\nMenu Items:\n1. Burger - 5$ - Ingregents(Cheese, Butter, Bun) - Calories(5 Cal)\n\nCondition:\n1. command - add/remove/update/delete\n2. cooking_notes - eg : I want 5 burgers with extra cheese and tomoto. so, Extra chese and Tomato is Cooking notes.\n",
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
        "Hi\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "What can I do for you today? \nI can help you add, update, or remove items from your cart.\nYou can also check what's in your cart.\nWhat would you like to do? \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I need 5 Burgers",
      ],
    },
    {
      "role": "model",
      "parts": [
        "\n```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"command\": \"add\",\n    \"quantity\": \"5\",\n    \"product_id\": \"Burger\"\n  }\n}\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I need 5 Burgers with 6 Pizza",
      ],
    },
    {
      "role": "model",
      "parts": [
        "\n```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"product_id\": \"Burger\",\n    \"cooking_notes\": \"\",\n    \"quantity\": \"5\",\n    \"command\": \"add\"\n  }\n}\n```\n\n```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"product_id\": \"Pizza\",\n    \"command\": \"add\",\n    \"cooking_notes\": \"\",\n    \"quantity\": \"6\"\n  }\n}\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I need 5 Burgers and 6 Pizza\n\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "\n```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"5\",\n    \"command\": \"add\"\n  }\n}\n```\n\n```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Pizza\",\n    \"quantity\": \"6\",\n    \"command\": \"add\"\n  }\n}\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "i want 5 Burger and 7 Pizza\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"5\",\n    \"command\": \"add\"\n  }\n}\n```\n\n```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Pizza\",\n    \"quantity\": \"7\",\n    \"command\": \"add\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "No I want Burger only\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"1\",\n    \"command\": \"add\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Hi\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "What can I do for you today? \nI can help you add, update, or remove items from your cart.\nYou can also check what's in your cart.\nWhat would you like to do? \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I need 5 Burder and 7 pizza",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burder\",\n    \"quantity\": \"5\",\n    \"command\": \"add\"\n  }\n}\n```\n\n```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Pizza\",\n    \"quantity\": \"7\",\n    \"command\": \"add\"\n  }\n}\n```\n\nBurder is not in the menu, would you like to add 5 Burgers and 7 Pizza to your cart? \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "what are my menu items\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "We have the following items on the menu:\n\n1. Burger - 5$ - Ingregents(Cheese, Butter, Bun) - Calories(5 Cal) \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "what are my cart items?\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Your cart currently has: 1 Burger. \nWould you like to add anything else? \n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I need 7 pizza and 5 Burger",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Pizza\",\n    \"quantity\": \"7\",\n    \"command\": \"add\"\n  }\n}\n```\n\n```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"5\",\n    \"command\": \"add\"\n  }\n}\n```\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Need Extra cheese in burger\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"Extra cheese\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"5\",\n    \"command\": \"update\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Extra CHeese and Tomato",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"Extra CHeese and Tomato\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"5\",\n    \"command\": \"update\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Remove 3 burger\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"3\",\n    \"command\": \"remove\"\n  }\n}\n```\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Remove Burger",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"1\",\n    \"command\": \"remove\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Remove all burger\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"1\",\n    \"command\": \"remove\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I need 4 more burgers",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"4\",\n    \"command\": \"add\"\n  }\n}\n```\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Need extra cheese and tomoto with burger\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"extra cheese and tomoto\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"4\",\n    \"command\": \"update\"\n  }\n}\n```\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "I dont want burger",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_cart_items\",\n  \"args\": {\n    \"cooking_notes\": \"\",\n    \"product_id\": \"Burger\",\n    \"quantity\": \"4\",\n    \"command\": \"remove\"\n  }\n}\n```\n\nOK. I have removed all burgers from your cart. \n\n\n",
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