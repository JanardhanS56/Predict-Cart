import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

payload_path = os.path.join("data", "processed", "kumo_payload.json")
with open(payload_path, "r") as f:
    payload = json.load(f)

api_key = os.getenv("NVIDIA_API_KEY")
if not api_key:
    raise RuntimeError("Set the NVIDIA_API_KEY environment variable in .env before running this script.")

# Basic check if it's the placeholder
if api_key == "nvapi-...actual-key-here...":
    raise RuntimeError("You are using the placeholder API key. Please update .env with your real NVIDIA API Key.")

print("Sending request to NVIDIA Kumo Relational endpoint...")

r = requests.post(
    "https://ai.api.nvidia.com/v1/structured-data/nvidia/kumo-relational/predictions",
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    },
    json=payload,
)
try:
    r.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(f"API Error: {e}")
    print(r.text)
    raise
resp_json = r.json()

out_path = os.path.join("data", "processed", "prediction_response.json")
with open(out_path, "w") as f:
    json.dump(resp_json, f, indent=2)

print(f"\nResponse saved to {out_path}")
print("\n--- Response Shape ---")
print(f"Top-level keys: {list(resp_json.keys())}")
for k, v in resp_json.items():
    if isinstance(v, list) and len(v) > 0:
        print(f"\nSample of list '{k}':")
        print(json.dumps(v[:2], indent=2))
    elif isinstance(v, dict) and len(v) > 0:
        print(f"\nSample of dict '{k}':")
        # Just show keys or a small slice
        print(json.dumps(dict(list(v.items())[:2]), indent=2))