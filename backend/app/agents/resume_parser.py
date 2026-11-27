from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.agents.llm import get_llm
from app.agents.models import ResumeModel

def parse_resume(raw_text: str) -> ResumeModel:
    llm = get_llm(max_tokens=500)
    parser = PydanticOutputParser(pydantic_object=ResumeModel)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract resume fields as valid JSON only.\n{format_instructions}"),
        ("user", "{raw_text}")
    ])

    chain = prompt | llm | parser

    return chain.invoke({
        "raw_text": (raw_text or "")[:6000],
        "format_instructions": parser.get_format_instructions()
    })
