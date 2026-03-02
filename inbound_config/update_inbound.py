import requests
import json

# API Endpoint
url = "https://voice.rock8.ai/inbound/update"

HEADERS = {
    "Content-Type": "application/json"
}

# The identifiers of the configuration you want to update (returned from configure_inbound)
SIP_TRUNK_ID = "ST_266BKFBsyaTQ"
DISPATCH_RULE_ID = "SDR_i5rH5Z52yvKC"

with open("prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read().strip()
# Only include fields that you want to update. Excluded fields will remain unchanged.
# Note: Updating the dispatch rule will create a new dispatch_rule_id, which will be returned in the response.
payload = {
    "sip_trunk_id": SIP_TRUNK_ID,
    "dispatch_rule_id": DISPATCH_RULE_ID,
    
    # Feel free to comment out or remove fields you don't need to change
    # "phone_number": "+919004868097", 
    "system_prompt": system_prompt,
    # "voice": "female",
    # "language": "hi-IN",
    # "model_type": "standard",
    
    # "llm_config": {
    #     "provider": "openai",
    #     "config": {
    #         "model": "gpt-4o-mini"
    #     }
    # },
}

def update_inbound():
    print(f"Updating configuration for SIP Trunk: {SIP_TRUNK_ID}")
    try:
        response = requests.put(url, json=payload, headers=HEADERS)
        if not response.ok:
            print(f"Error {response.status_code}: {response.reason}")
            try:
                print("Server response:", json.dumps(response.json(), indent=2))
            except Exception:
                print("Raw response:", response.text)
        else:
            print("Agent Updated Successfully!")
            print(json.dumps(response.json(), indent=2))
            
            # NOTE: Be sure to update your saved dispatch_rule_id with the one returned here
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    update_inbound()
