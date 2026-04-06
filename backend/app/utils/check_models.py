import os
import requests
from dotenv import load_dotenv

# Load your API key from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Hit the ListModels endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

print("--- AVAILABLE GOOGLE MODELS ---")
for model in response.json().get('models', []):
    # We only care about models that can generate text/content
    if 'generateContent' in model.get('supportedGenerationMethods', []):
        print(model['name'])
