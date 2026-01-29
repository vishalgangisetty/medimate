
import google.generativeai as genai
from src.config import Config

genai.configure(api_key=Config.GOOGLE_API_KEY)

print("Listing available models...")
for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(f"Name: {m.name}")
