import requests
import json

# API Endpoint
url = "https://voice.rock8.ai/inbound/configure"

HEADERS = {
    "Content-Type": "application/json"
}

# The System Prompt
system_prompt = """
Persona: Priya, Female, Order-taking agent for MEAT CRAFT.
Tone: Efficient, clear, helpful, direct. Hindi/Hinglish focused.

Core Rules:
1. Primary language: Hindi/Hinglish. Item names in English.
2. Currency: Verbalized in English (e.g., "one hundred and forty Rupees").
3. Weight Terms: "adha kilo" -> 500g, "dhai sau gram" -> 250g. Prompt for standard weights if unclear.
4. NEVER collect payment or addresses over the phone (use WhatsApp handoff).
5. Call Persistence: Do not end until order is placed or user cancels.
6. Cart Management: 'koala_add_to_cart' overwrites the cart. Always send the full list of items.

Call Flow:
- Intro: "MEAT CRAFT mein call karne ke liye dhanyavaad..."
- Category/Item Selection: List categories/items from menu.
- Confirmation: Verify full order items and quantities.
- Fulfillment: Ask "Delivery" or "Pickup from Ramesh Nagar". 
- Handoff: Trigger 'koala_place_order' then inform user about WhatsApp message.
"""

# IMPORTANT: Ensure the phone number does not conflict with existing inbound SIP Trunks
payload = {
    "phone_number": "+919004868097", # Replace with your target inbound number
    "system_prompt": system_prompt,
    "tools": [
        {
            "name": "koala_add_to_cart",
            "description": "Updates the shopping cart. Overwrites previous cart state.",
            "method": "POST",
            "url": "https://your-api-endpoint.com/cart/add",
            "headers": {
                "Content-Type": "application/json"
            },
            "parameters": [
                {
                    "name": "cart_id",
                    "description": "The unique ID for the session cart",
                    "type": "string",
                    "location": "body"
                },
                {
                    "name": "items",
                    "description": "List of objects containing item_name and quantity",
                    "type": "array",
                    "location": "body"
                }
            ]
        }
    ],
    "voice": "female",
    "language": "hi-IN",
    "model_type": "standard",
    "stt_config": {
        "provider": "deepgram",
        "config": {
            "model": "nova-2",
            "language": "hi"
        }
    },
    "llm_config": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o"
        }
    },
    "tts_config": {
        "provider": "cartesia",
        "config": {
            "model": "sonic-english",
            "voice_id": "your-voice-id"
        }
    },
    "vad_config": {
        "min_silence_duration": 0.6,
        "activation_threshold": 0.4,
        "min_speech_duration": 0.3
    }
}

def configure_inbound():
    print(f"Configuring inbound number: {payload.get('phone_number')}")
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        if not response.ok:
            print(f"Error {response.status_code}: {response.reason}")
            try:
                print("Server response:", json.dumps(response.json(), indent=2))
            except Exception:
                print("Raw response:", response.text)
        else:
            print("Agent Configured Successfully!")
            print(json.dumps(response.json(), indent=2))
            
            # NOTE: Remember to save the sip_trunk_id and dispatch_rule_id from the response
            # You will need them for updating or deleting the configuration later.
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    configure_inbound()
