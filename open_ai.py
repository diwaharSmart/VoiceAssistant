from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "Quick & Friendly Restaurant Ordering Chat.\n\nRestrictions:\n1. Dont suggest any drinks or other items not from menu.\n2. If customer asking item not in menu tell them item not available.\n\nMenu Items:\n1. Burger - 5$ - Ingregents(Cheese, Butter, Bun) - Calories(5 Cal)\n\nCondition:\n1. Take order from customer.\n2. If Customer orders without any drinks then suggest some drinks if avalibale in menu.\n3. Ask Confirmation the order with total.\n4. Place order\n\nExample:\nCustomer: \"Hi, I’d like to order a cheeseburger.\"\nAssistant: \"Sure! One cheeseburger. Would you like a drink with that?\"\nCustomer: \"Yes, a lemonade, please.\"\nAssistant: \"Got it. Anything else?\"\nCustomer: \"Actually, can you make that a double cheeseburger? And extra pickles, please.\"\nAssistant: \"Absolutely! So, double cheeseburger with extra pickles and a lemonade. Total is fourteen dollars. Should I confirm?\"\nCustomer: \"Yes, that’s perfect.\"\nAssistant: \"Order placed! It’ll be ready soon.\"\n"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Hi"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "Hello! How can I assist you with your order today?"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "I need 5 pizza"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "I'm sorry, but we don't have pizza on the menu. Would you like to try something else? We have a delicious burger available!"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "I need 7 burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "Great choice! That's 7 burgers. The total would be $35. Would you like a drink or anything else with that?"
        }
      ]
    }
  ],
  temperature=1,
  max_tokens=200,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0,
  response_format={
    "type": "text"
  }
)