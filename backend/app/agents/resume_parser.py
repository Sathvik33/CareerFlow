from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.agents.llm import get_llm
from app.agents.models import ResumeModel

def parse_resume(raw_text: str) -> ResumeModel:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=ResumeModel)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert HR agent. Parse the following resume text and extract the required fields as structured JSON.\n{format_instructions}"),
        ("user", "{raw_text}")
    ])

    chain = prompt | llm | parser

    return chain.invoke({
        "raw_text": raw_text,
        "format_instructions": parser.get_format_instructions()
    })
