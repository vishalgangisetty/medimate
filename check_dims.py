
import os
import google.generativeai as genai
from src.config import Config

genai.configure(api_key=Config.GOOGLE_API_KEY)

models_to_test = [
    "models/text-embedding-004",
    "models/gemini-embedding-001",
    "models/embedding-001"
]

print(f"Checking dimensions for models (Target Index Dimension: 768)...")

for model_name in models_to_test:
    try:
        result = genai.embed_content(
            model=model_name,
            content="Hello world",
            task_type="retrieval_document"
        )
        # result['embedding'] is the list
        dims = len(result['embedding'])
        print(f"Model: {model_name} -> Dimensions: {dims}")
    except Exception as e:
        print(f"Model: {model_name} -> Error: {e}")
