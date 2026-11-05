from dotenv import load_dotenv
from langchain_ollama import ChatOllama
import os

# Load settings from .env
load_dotenv()

# Read Ollama configuration
model_name = os.getenv("OLLAMA_MODEL")
base_url = os.getenv("OLLAMA_BASE_URL")

# Connect to the local Llama model
llm = ChatOllama(
    model=model_name,
    base_url=base_url,
    temperature=0
)

# Send a test question
response = llm.invoke(
    "In two simple sentences, explain what a company research brief contains."
)

print("\nLlama 3 Response:\n")
print(response.content)