import os
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq

load_dotenv(find_dotenv(usecwd=True))


def _build_chat_groq(api_key: str | None, max_tokens: int, reasoning_effort: str | None, max_retries: int) -> ChatGroq:
    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    effort = reasoning_effort if reasoning_effort is not None else os.getenv("GROQ_REASONING_EFFORT", "none")

    kwargs = {
        "model": model,
        "temperature": 0,
        "max_tokens": max_tokens,
        "max_retries": max_retries,
        "groq_api_key": api_key,
    }
    if effort:
        kwargs["reasoning_effort"] = effort

    return ChatGroq(**kwargs)


def get_llm(max_tokens: int = 512, reasoning_effort: str | None = None):
    primary_key = (os.getenv("GROQ_API_KEY") or "").strip() or None
    secondary_key = (os.getenv("GROQ_API_KEY_2") or "").strip() or None

    if primary_key and secondary_key:
        primary = _build_chat_groq(primary_key, max_tokens, reasoning_effort, max_retries=1)
        secondary = _build_chat_groq(secondary_key, max_tokens, reasoning_effort, max_retries=2)
        return primary.with_fallbacks([secondary])

    return _build_chat_groq(primary_key or secondary_key, max_tokens, reasoning_effort, max_retries=3)
