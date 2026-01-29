
from pinecone import Pinecone
from src.config import Config
from src.utils import setup_logger

logger = setup_logger(__name__)

def reset_index():
    try:
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        index_name = Config.PINECONE_INDEX_NAME
        
        if index_name in pc.list_indexes().names():
            print(f"Deleting index: {index_name}...")
            pc.delete_index(index_name)
            print("Index deleted.")
        else:
            print(f"Index {index_name} does not exist.")
            
    except Exception as e:
        print(f"Error resetting index: {e}")

if __name__ == "__main__":
    reset_index()
