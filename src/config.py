import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    PINECONE_INDEX_NAME = "prescription-index"
    PINECONE_ENV = "us-east-1"
    GEMINI_MODEL_NAME = "gemini-2.5-flash-lite"
    DATA_DIR = os.path.join(os.getcwd(), "data")
    INPUT_DIR = os.path.join(DATA_DIR, "input")
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

    @staticmethod
    def validate():
        """Validate that all necessary API keys are present."""
        if not Config.MONGO_URI:
            raise ValueError("MONGO_URI is missing in .env")
        if not Config.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is missing in .env")
        if not Config.GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY is missing. Ensure you have access.")

