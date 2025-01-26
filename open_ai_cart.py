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
          "text": "Restrictions:\n1. [Important] Do not add any items other than menu\n\nMenu Items:\n1. Burger - 5$ - Ingregents(Cheese, Butter, Bun) - Calories(5 Cal)\n\nCondition:\n1. command:\n   - add ( Adding Items)\n   - remove ( Removes item)\n   - update ( Updating cooking notes)\n   - delete ( Delete the items totally in cart)\n2. cooking_notes - eg : I want 5 burgers with extra cheese and tomoto. so, Extra chese and Tomato is Cooking notes.\n\nfunction:\nget_cart_items"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "I need 7 Burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "Would you like to add any cooking notes or special requests for these 7 burgers? For example, extra cheese or tomatoes?"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Function: get_cart_items - I need 7 Burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_calls": [
        {
          "id": "call_30Sl3tURwNZljERP7yymOBrm",
          "type": "function",
          "function": {
            "name": "get_cart_items",
            "arguments": "{\"product_id\":\"1\",\"cooking_notes\":\"\",\"quantity\":\"7\",\"command\":\"add\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_call_id": "call_30Sl3tURwNZljERP7yymOBrm"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Function: get_cart_items - I Dont Want Burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_calls": [
        {
          "id": "call_tFq7LNnaa6S20P83u4LGeiMw",
          "type": "function",
          "function": {
            "name": "get_cart_items",
            "arguments": "{\"product_id\":\"1\",\"cooking_notes\":\"\",\"quantity\":\"\",\"command\":\"remove\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_call_id": "call_tFq7LNnaa6S20P83u4LGeiMw"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "I need 8 Burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "Would you like to add any cooking notes or special requests for these 8 burgers? For example, extra cheese or tomatoes?"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Function: get_cart_items - I need 7 Burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_calls": [
        {
          "id": "call_EMxMCxbdgY3iCSwU7dSWv9zx",
          "type": "function",
          "function": {
            "name": "get_cart_items",
            "arguments": "{\"product_id\":\"1\",\"cooking_notes\":\"\",\"quantity\":\"7\",\"command\":\"add\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_call_id": "call_EMxMCxbdgY3iCSwU7dSWv9zx"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Function: get_cart_items - I dont want  Burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_calls": [
        {
          "id": "call_sJCTtT24QHUEPPqsBn9UKdMw",
          "type": "function",
          "function": {
            "name": "get_cart_items",
            "arguments": "{\"product_id\":\"1\",\"cooking_notes\":\"\",\"quantity\":\"\",\"command\":\"remove\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_call_id": "call_sJCTtT24QHUEPPqsBn9UKdMw"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Function: get_cart_items - I need 9 burger with extra cheese"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_calls": [
        {
          "id": "call_xsZjybfEipP9YAfWoyi5bueS",
          "type": "function",
          "function": {
            "name": "get_cart_items",
            "arguments": "{\"product_id\":\"1\",\"cooking_notes\":\"extra cheese\",\"quantity\":\"9\",\"command\":\"add\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_call_id": "call_xsZjybfEipP9YAfWoyi5bueS"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Remove two burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_calls": [
        {
          "id": "call_DU3h0qzzpvZrksLUBWUEetvm",
          "type": "function",
          "function": {
            "name": "get_cart_items",
            "arguments": "{\"product_id\":\"1\",\"cooking_notes\":\"\",\"quantity\":\"2\",\"command\":\"remove\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_call_id": "call_DU3h0qzzpvZrksLUBWUEetvm"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Function: get_cart_items - Need 5 More Burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_calls": [
        {
          "id": "call_fhBACn4NO7IR4kslE1hZVWU7",
          "type": "function",
          "function": {
            "name": "get_cart_items",
            "arguments": "{\"product_id\":\"1\",\"cooking_notes\":\"\",\"quantity\":\"5\",\"command\":\"add\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_call_id": "call_fhBACn4NO7IR4kslE1hZVWU7"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "I dont want burger"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_calls": [
        {
          "id": "call_8zMjyXuNeJNuUbtij39fY2BZ",
          "type": "function",
          "function": {
            "name": "get_cart_items",
            "arguments": "{\"product_id\":\"1\",\"cooking_notes\":\"\",\"quantity\":\"\",\"command\":\"remove\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_call_id": "call_8zMjyXuNeJNuUbtij39fY2BZ"
    }
  ],
  temperature=1,
  max_tokens=200,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0,
  tools=[
    {
      "type": "function",
      "function": {
        "name": "get_cart_items",
        "description": "Cart Items",
        "parameters": {
          "type": "object",
          "required": [
            "product_id",
            "cooking_notes",
            "quantity",
            "command"
          ],
          "properties": {
            "product_id": {
              "type": "string",
              "description": "Unique identifier for the product"
            },
            "cooking_notes": {
              "type": "string",
              "description": "Special cooking instructions for the item"
            },
            "quantity": {
              "type": "string",
              "description": "Number of items to add to the cart"
            },
            "command": {
              "type": "string",
              "description": "Action command for the cart item (add/remove/update/delete)"
            }
          },
          "additionalProperties": false
        },
        "strict": true
      }
    }
  ],
  parallel_tool_calls=true,
  response_format={
    "type": "text"
  }
)