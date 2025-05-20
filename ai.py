from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

api_key: str = os.environ.get("OPENAI_API_KEY")

client: OpenAI = OpenAI(api_key=api_key)

def get_embedding(text: str):
    """Given a text returns its embedding"""
    
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding
