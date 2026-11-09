
import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

load_dotenv()


def summarize_company(company_name: str, search_results: list):

    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "groq":
        llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0,
            max_tokens=800,
            api_key=os.getenv("GROQ_API_KEY")
        )
    else:
        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0,
            num_predict=220
        )

    research_text = ""

    for result in search_results[:3]:
        research_text += (
            f"\nSource title: {result.get('title', '')}\n"
            f"Source information: {result.get('content', '')[:350]}\n"
            f"Source URL: {result.get('url', '')}\n"
        )

    prompt = f"""
Create a short factual research brief about {company_name}.
Use only the facts in these sources.
Do not invent facts or guess.

Use these four headings:
Company Overview
Products and Services
Industry and Customers
Key Insights

Write one or two short sentences under each heading.
If a fact is missing, write "Information not available."

SOURCES:
{research_text}
"""

    response = llm.invoke(prompt)

    if not response.content:
        raise ValueError("AI returned an empty summary.")

    summary = response.content.strip()

    summary = summary.replace(
        f"Here is a short factual research brief about {company_name}:",
        ""
    ).strip()

    summary = summary.replace("(Information not available)", "").strip()

    if not summary:
        raise ValueError("AI summary is empty after cleaning.")

    return summary
