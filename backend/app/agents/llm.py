import os
# from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

def get_llm():
    # return ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    return ChatOllama(model="qwen2.5:7b", temperature=0)
