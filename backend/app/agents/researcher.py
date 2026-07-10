from langgraph.prebuilt import create_react_agent
from app.agents.llm import get_llm
from app.agents.tools.scraper import scrape_website
from app.agents.tools.search import search_web

def get_research_agent():
    llm = get_llm()
    tools = [scrape_website, search_web]
    # create_react_agent creates a state graph that loops between the LLM and the tools
    # until the LLM decides it has finished the task.
    agent = create_react_agent(llm, tools=tools)
    return agent

async def research_company(company_name: str) -> str:
    """Uses the ReAct agent to research a company and return a summary."""
    agent = get_research_agent()
    prompt = f"Research the company '{company_name}'. Use the search tool to find their main products, recent news, and work culture. Return a concise 1-2 paragraph summary."
    
    result = await agent.ainvoke({"messages": [("user", prompt)]})
    # The last message in the state is the agent's final response
    return result["messages"][-1].content
