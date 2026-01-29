
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("Testing imports...")

try:
    print("Importing core...")
    import streamlit
    import pinecone
    import google.generativeai
    print("Core imports successful.")
    
    print("Importing src modules...")
    from src.config import Config
    from src.utils import setup_logger
    from src.auth import AuthManager
    from src.extractor import PrescriptionExtractor
    from src.vector_store import VectorStoreManager
    from src.otc_manager import OTCManager
    from src.reminder import ReminderManager
    from src.pharmacy_locator import PharmacyLocator
    from src.language import LanguageManager
    from src.voice_assistant import VoiceAssistant
    from src.graph import RAGGraph
    print("Src imports successful.")
    
    print("Environment OK.")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)
