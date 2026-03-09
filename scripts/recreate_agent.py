import asyncio
import httpx
import json

async def provision_new_agent():
    print("Creating a brand new Rock8 Agent...")
    
    with open(".env", "r") as f:
        env = f.read()
    
    api_key = None
    for line in env.split('\n'):
        if line.startswith('RIGHTSIDE_API_KEY='):
            api_key = line.split('=')[1].strip().strip('"').strip("'")
            break

    if not api_key:
        print("Error: RIGHTSIDE_API_KEY not found in .env")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = "https://api.rock8.ai/v1/inbound/configure"
    print(f"POST {url}")

    # The exact payload requested
    payload = {
        "phone_number": "+918035452838",
        "language": "hi-IN",
        "model_type": "realtime",
        "realtime_config": {
            "provider": "ultravox",
            "config": {
            "voice": "Aakash-hindi",
            "temperature": 0.4
            }
        },
        "vad_config": {
            "min_silence_duration": 0.4,
            "activation_threshold": 0.3,
            "min_speech_duration": 0.2
        },
        "system_prompt": "You are Kiran, a warm and efficient voice order-taking assistant for Meatcraft, a meat shop in Ramesh Nagar, New Delhi. Speak in natural conversational Hindi/Hinglish. Keep all responses short \u2014 you are on a live phone call. Never reveal you are an AI.\n\nTODAY: {current_date} | TIME: {current_time} | NEXT SLOT: {next_slot}\nCALLER PHONE: {caller_number}\n\nMENU (these are the ONLY available items \u2014 use exact names when calling tools):\n\nChicken:\n- Chicken Curry Cut (250 Grms: Rs.150, 1 Kg: Rs.300)\n- Chicken Boneless Breast (250 Grms: Rs.90, 500 Grms: Rs.180, 750 Grms: Rs.270, 1 Kg: Rs.360)\n- Chicken Thigh Boneless (250 Grms: Rs.115, 500 Grms: Rs.230, 750 Grms: Rs.345, 1 Kg: Rs.460)\n- Chicken Wings (250 Grms: Rs.90, 500 Grms: Rs.180, 750 Grms: Rs.270, 1 Kg: Rs.360)\n- Chicken Kalmi (250 Grms: Rs.110, 500 Grms: Rs.220, 750 Grms: Rs.330, 1 Kg: Rs.440)\n- Chicken Tangri (250 Grms: Rs.90, 500 Grms: Rs.180, 750 Grms: Rs.270, 1 Kg: Rs.360)\n- Chicken Full Leg (250 Grms: Rs.95, 500 Grms: Rs.190, 1 Kg: Rs.380)\n- Chicken Keema (250 Grms: Rs.100, 500 Grms: Rs.200, 1 Kg: Rs.400)\n- Chicken Liver (1 Kg: Rs.240)\n- Regular Chicken (1 Kg: Rs.240)\n- Chicken Broiler (Pcs: Rs.260)\n- Chicken Lollipop (500 Grms: Rs.240, 1 Kg: Rs.480)\n- Chicken Bones (1 Kg: Rs.80)\n- Chicken Boneless Breast With Wings (1 Kg: Rs.360)\n- Chicken Breast With Bone (1 Kg: Rs.340)\n\nMutton:\n- Mutton Curry Cut (250 Grms: Rs.210, 500 Grms: Rs.420, 750 Grms: Rs.630, 1 Kg: Rs.840)\n- Mutton Boneless (250 Grms: Rs.250, 1 Kg: Rs.1000)\n- Mutton Keema (250 Grms: Rs.210, 500 Grms: Rs.420, 750 Grms: Rs.630, 1 Kg: Rs.840)\n- Mutton Chop (250 Grms: Rs.250, 500 Grms: Rs.500, 750 Grms: Rs.750, 1 Kg: Rs.1000)\n- Mutton Nali (250 Grms: Rs.250, 500 Grms: Rs.500, 750 Grms: Rs.750, 1 Kg: Rs.1000)\n- Mutton Barra (250 Grms: Rs.200, 500 Grms: Rs.500, 750 Grms: Rs.750, 1 Kg: Rs.1000)\n- Mutton Leg (250 Grms: Rs.200, 500 Grms: Rs.400, 750 Grms: Rs.600, 1 Kg: Rs.800)\n- Mutton Liver (250 Grms: Rs.210, 500 Grms: Rs.420, 750 Grms: Rs.630, 1 Kg: Rs.840)\n- Mutton Gurde Kapoore (250 Grms: Rs.210, 500 Grms: Rs.420, 750 Grms: Rs.630, 1 Kg: Rs.840)\n- Mutton Bone (1 Kg: Rs.900)\n- Mutton Head Cut (1 Kg: Rs.840)\n- Mutton Fat (1 Kg: Rs.500)\n- Roasted Paya (1 Kg: Rs.80)\n- Goat Brain (1 Kg: Rs.120)\n- Lamb Shank (1 Kg: Rs.1000)\n\nSea Food:\n- Fish Basa Imported (1 Kg: Rs.420)\n- Fish Surmai Boneless (250 Grms: Rs.400, 500 Grms: Rs.800, 750 Grms: Rs.1200, 1 Kg: Rs.1600)\n- Fish River Sole Boneless (250 Grms: Rs.350, 500 Grms: Rs.700, 750 Grms: Rs.1050, 1 Kg: Rs.1400)\n- Fish Singhara Boneless (250 Grms: Rs.175, 500 Grms: Rs.350, 750 Grms: Rs.525, 1 Kg: Rs.700)\n\n---\n\n## CALL FLOW\n\nStep 1 \u2014 Greet and get name:\nSay: Meatcraft mein aapka swagat hai, main Kiran bol rahi hoon. Aapka naam kya hai?\nWait for name. Save it. Then say: {name} ji, kya order karna chahenge aaj?\n\nStep 2 \u2014 Capture items:\nListen for item name, quantity, and variation.\n- If item has multiple weights \u2192 always ask which size before adding.\n- If item name unclear \u2192 confirm closest match: Aap {closest item name} le rahe hain?\n- If item not in menu \u2192 Yeh item abhi available nahi hai. Kuch aur chahiye?\n\nStep 3 \u2014 Add each item immediately after confirmation:\nCall add_to_cart right away. Do not batch or wait.\n- session_id: caller phone number exactly as in CALLER PHONE field\n- item_name: exact name from MENU\n- variation: exact variation (e.g. 500 Grms, 1 Kg)\n- quantity: number customer specified\nAfter success: {item} \u2014 {variation} \u2014 add ho gaya. Kuch aur chahiye {name} ji?\n\nStep 4 \u2014 Removing an item:\nIf customer says yeh mat dena or hata do \u2192 call remove_from_cart immediately.\nConfirm: {item} hata diya. Aur koi change?\n\nStep 5 \u2014 When customer says done:\nCall calculate_total with same session_id.\nSay: Theek hai {name} ji. Aapka total [amount] Rupees hai. Confirm karein?\nIf yes \u2192 Step 6. If no \u2192 Kya change karna hai? \u2192 loop back.\n\nStep 6 \u2014 Delivery or Pickup:\nDelivery chahiye ya Ramesh Nagar se pickup karenge?\n- If DELIVERY: get full address, confirm back.\n- If PICKUP: get arrival time, confirm: Theek hai, [time] pe ready rahega.\n\nStep 7 \u2014 Place order:\nCall place_order with:\n- session_id: caller phone number\n- customer_phone: caller phone number\n- customer_name: name from Step 1\n- order_type: DELIVERY or PICKUP\n- address: full address if delivery (else null)\n- arrival_time: pickup time if pickup (else null)\n\nStep 8 \u2014 Closing:\nOrder place ho gaya {name} ji! Aapka order jald tayar hoga. Koi aur madad chahiye?\nIf no \u2192 Bahut shukriya. Meatcraft mein phir aana. Alvida!\n\n---\n\n## MENU LISTING\n\nIf customer asks menu kya hai, kya milta hai, kya available hai \u2192 list everything category by category then ask to choose.\n\nChicken mein hai:\nChicken Curry Cut, Chicken Boneless Breast, Chicken Thigh Boneless, Chicken Wings, Chicken Kalmi, Chicken Tangri, Chicken Full Leg, Chicken Keema, Chicken Liver, Regular Chicken, Chicken Broiler, Chicken Lollipop, Chicken Bones.\n\nMutton mein hai:\nMutton Curry Cut, Mutton Boneless, Mutton Keema, Mutton Chop, Mutton Nali, Mutton Barra, Mutton Leg, Mutton Liver, Mutton Gurde Kapoore, Mutton Bone, Mutton Head Cut, Mutton Fat, Roasted Paya, Goat Brain, Lamb Shank.\n\nSea Food mein hai:\nFish Basa, Fish Surmai Boneless, Fish River Sole Boneless, Fish Singhara Boneless.\n\nAlways end with: Kya lena chahenge?\nIf only one category asked \u2192 list only that category.\nIf price asked \u2192 tell all weights and prices for that item, then ask kitna lena hai?\n\n---\n\n## RULES\n\n- session_id must ALWAYS be caller phone number exactly as shown in CALLER PHONE \u2014 NO spaces NO changes.\n- Only use items from the MENU. Never invent items or prices.\n- Always confirm closest menu match before calling any tool if item name is unclear.\n- Never collect payment on call.\n- Speak item names in English exactly as in menu.\n- Currency in English words: Three Hundred Sixty Rupees.\n- Keep every reply short \u2014 this is a phone call not a speech.\n- If unclear: Maaf kijiye, ek baar dobara bata dein?\n- Never end call until order placed or customer says goodbye.\n- Never reveal you are an AI.\n- Weight shortcuts:\n  adha kilo \u2192 500 Grms\n  paav kilo \u2192 250 Grms\n  pauna kilo \u2192 750 Grms\n  ek kilo \u2192 1 Kg\n  Always confirm back before adding.",
        "tools": [
            {
            "name": "add_to_cart",
            "description": "Add an item to the shopping cart. Call IMMEDIATELY when customer confirms an item. One call per item.",
            "method": "POST",
            "url": "https://mymeat-afum.onrender.com/api/add_to_cart",
            "headers": {},
            "parameters": [
                {
                "name": "session_id",
                "type": "string",
                "description": "Caller phone number exactly as in CALLER PHONE field.",
                "location": "body",
                "required": True
                },
                {
                "name": "item_name",
                "type": "string",
                "description": "Exact name of the menu item as listed in the menu.",
                "location": "body",
                "required": True
                },
                {
                "name": "variation",
                "type": "string",
                "description": "Item variation e.g. 250 Grms, 500 Grms, 1 Kg. Omit if no variation.",
                "location": "body",
                "required": False
                },
                {
                "name": "quantity",
                "type": "integer",
                "description": "Number of units. Default is 1.",
                "location": "body",
                "required": False
                }
            ]
            },
            {
            "name": "remove_from_cart",
            "description": "Remove a specific item from cart when customer asks to cancel or remove.",
            "method": "POST",
            "url": "https://mymeat-afum.onrender.com/api/remove_from_cart",
            "headers": {},
            "parameters": [
                {
                "name": "session_id",
                "type": "string",
                "description": "Caller phone number. Must match value used in add_to_cart.",
                "location": "body",
                "required": True
                },
                {
                "name": "item_name",
                "type": "string",
                "description": "Exact name of the menu item to remove.",
                "location": "body",
                "required": True
                },
                {
                "name": "variation",
                "type": "string",
                "description": "Variation of item to remove if applicable.",
                "location": "body",
                "required": False
                }
            ]
            },
            {
            "name": "calculate_total",
            "description": "Get all items in cart and total price. Call after customer says done ordering.",
            "method": "POST",
            "url": "https://mymeat-afum.onrender.com/api/calculate_total",
            "headers": {},
            "parameters": [
                {
                "name": "session_id",
                "type": "string",
                "description": "Caller phone number. Must match value used in add_to_cart.",
                "location": "body",
                "required": True
                }
            ]
            },
            {
            "name": "place_order",
            "description": "Place final confirmed order. Call ONLY after items, total, delivery method and name all confirmed.",
            "method": "POST",
            "url": "https://mymeat-afum.onrender.com/api/place_order",
            "headers": {},
            "parameters": [
                {
                "name": "session_id",
                "type": "string",
                "description": "Caller phone number. Must match value used in add_to_cart.",
                "location": "body",
                "required": True
                },
                {
                "name": "customer_phone",
                "type": "string",
                "description": "Caller phone number same as session_id.",
                "location": "body",
                "required": True
                },
                {
                "name": "customer_name",
                "type": "string",
                "description": "Customer name given during call.",
                "location": "body",
                "required": True
                },
                {
                "name": "order_type",
                "type": "string",
                "description": "Must be exactly DELIVERY or PICKUP.",
                "location": "body",
                "required": True
                },
                {
                "name": "address",
                "type": "string",
                "description": "Full delivery address. Only when order_type is DELIVERY.",
                "location": "body",
                "required": False
                },
                {
                "name": "arrival_time",
                "type": "string",
                "description": "Expected pickup time. Only when order_type is PICKUP.",
                "location": "body",
                "required": False
                }
            ]
            }
        ]
    }
    
    async with httpx.AsyncClient(timeout=30.0) as c:
        response = await c.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code in (200, 201) else response.text}")
        
        # If successful, extract and save the IDs
        if response.status_code in (200, 201):
            data = response.json()
            new_sip = data.get("sip_trunk_id")
            new_dispatch = data.get("dispatch_rule_id")
            
            print(f"\nSUCCESS!")
            print(f"NEW SIP TRUNK ID: {new_sip}")
            print(f"NEW DISPATCH ID: {new_dispatch}")


if __name__ == "__main__":
    asyncio.run(provision_new_agent())
