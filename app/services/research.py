
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()


def search_company(company_name: str):
    company_name = company_name.strip()

    if not company_name:
        raise ValueError("Please enter a company name.")

    # Search the web for this company's information.
    search = TavilySearch(max_results=8)

    query = (
        f"{company_name} company official website "
        "overview products services industry customers"
    )

    response = search.invoke({"query": query})

    # Extract search results from Tavily's response.
    if isinstance(response, dict):
        results = response.get("results", [])
    elif isinstance(response, list):
        results = response
    else:
        results = []

    # Keep valid search results.
    relevant_results = []

    for result in results:
        if not isinstance(result, dict):
            continue

        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = result.get("content", "")

        if not content and not title:
            continue

        relevant_results.append({
            "title": title,
            "url": url,
            "content": content
        })

    if not relevant_results:
        raise ValueError(
            f"No web search results found for {company_name}. "
            "Please try again."
        )

    return relevant_results[:5]
