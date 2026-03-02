import requests
import json

# The identifiers of the configuration you want to delete
SIP_TRUNK_ID = "ST_xxxxxxxxxxxx"
DISPATCH_RULE_ID = "SDR_xxxxxxxxxxxx"

# API Endpoint
url = f"https://voice.rock8.ai/inbound/{SIP_TRUNK_ID}/{DISPATCH_RULE_ID}"

HEADERS = {
    "Content-Type": "application/json"
}

def delete_inbound():
    print(f"Deleting configuration for SIP Trunk: {SIP_TRUNK_ID} and Dispatch Rule: {DISPATCH_RULE_ID}")
    try:
        response = requests.delete(url, headers=HEADERS)
        if not response.ok:
            print(f"Error {response.status_code}: {response.reason}")
            try:
                print("Server response:", json.dumps(response.json(), indent=2))
            except Exception:
                print("Raw response:", response.text)
        else:
            print("Agent Deleted Successfully!")
            print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    delete_inbound()
