from dotenv import load_dotenv
from langchain_tavily import TavilySearch
import os

# Load API key from .env
load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise ValueError("Tavily API key is missing from .env")

# Initialize web search
search = TavilySearch(max_results=3)

# Search for company information
response = search.invoke({
    "query": "Microsoft company overview products and services"
})

# Extract search results from the response
results = response.get("results", []) if isinstance(response, dict) else response

print("\nTavily Search Results:\n")

for result in results:
    if isinstance(result, dict):
        print("Title:", result.get("title", "Not available"))
        print("URL:", result.get("url", "Not available"))
        print("Content:", result.get("content", "")[:300])
        print("-" * 50)
    else:
        print(result)