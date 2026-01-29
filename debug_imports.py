
try:
    print("Importing googletrans...")
    from googletrans import Translator
    t = Translator()
    print("googletrans imported.")
except Exception as e:
    print(f"googletrans failed: {e}")

try:
    print("Importing langchain_google_genai...")
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("langchain_google_genai imported.")
except Exception as e:
    print(f"langchain_google_genai failed: {e}")
