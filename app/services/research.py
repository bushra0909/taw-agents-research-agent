import re

from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()


def normalize_text(text: str) -> str:
    """Make text easier to compare."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def search_company(company_name: str):
    company_name = company_name.strip()

    if not company_name:
        raise ValueError("Please enter a company name.")

    # Ask Tavily for information about this specific company.
    search = TavilySearch(max_results=8)

    query = (
        f'"{company_name}" company official website '
        "company overview products services industry customers"
    )

    response = search.invoke({"query": query})

    # Tavily can return a dictionary containing results or a list.
    if isinstance(response, dict):
        results = response.get("results", [])
    elif isinstance(response, list):
        results = response
    else:
        results = []

    # Keep only results that mention the requested company.
    target = normalize_text(company_name)
    relevant_results = []

    for result in results:
        if not isinstance(result, dict):
            continue

        title = result.get("title", "")
        content = result.get("content", "")
        url = result.get("url", "")

        searchable_text = normalize_text(
            f"{title} {content} {url}"
        )

        if target in searchable_text:
            relevant_results.append({
                "title": title or "Untitled",
                "url": url,
                "content": content
            })

    if not relevant_results:
        raise ValueError(
            f"No sufficiently relevant results found for {company_name}. "
            "Try entering the full company name."
        )

    return relevant_results[:5]