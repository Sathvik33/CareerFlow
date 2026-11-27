import re
from langchain_core.prompts import ChatPromptTemplate
from app.agents.llm import get_llm
from app.agents.tools.search import search_web


def _clean_plain_text(text: str) -> str:
    """Strip markdown formatting and extra whitespace for clean UI display."""
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"^\s*[-*•]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


async def research_company(company_name: str) -> str:
    """Fetches web context once and generates a concise plain-text company summary."""
    search_context = ""
    try:
        raw_results = await search_web.ainvoke(f"{company_name} company products recent news culture")
        search_context = str(raw_results)[:1200]
    except Exception:
        search_context = ""

    llm = get_llm(max_tokens=160)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Summarize the company in 2-3 concise plain-text sentences covering main products, "
            "recent news, and work culture. Output ONLY plain text: no markdown, no headings (#), "
            "no bold (**), no bullet points, and no commentary about search tools."
        ),
        (
            "user",
            "Company: {company_name}\nContext: {context}"
        ),
    ])

    chain = prompt | llm
    response = await chain.ainvoke({
        "company_name": company_name,
        "context": search_context or "No external search results available; use known facts concisely.",
    })
    return _clean_plain_text(response.content)
