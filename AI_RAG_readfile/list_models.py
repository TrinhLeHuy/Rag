import os
import requests
from core.config import settings

def list_groq_models():
    api_key = settings.GROQ_API_KEY
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
    if response.status_code == 200:
        models = response.json().get("data", [])
        for m in models:
            if "vision" in m.get("id", "").lower():
                print("VISION MODEL:", m.get("id"))
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    list_groq_models()
