from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.agents.llm import get_llm
from app.agents.models import JDModel

async def parse_jd(raw_description: str) -> JDModel:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=JDModel)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert HR agent. Parse the following job description and extract the required fields as structured JSON. Be highly thorough when extracting the required technical and soft skills, as they will be used for semantic matching against candidates. If a salary or compensation range is mentioned, extract it into the salary field.\n{format_instructions}"),
        ("user", "{raw_description}")
    ])

    chain = prompt | llm | parser

    return await chain.ainvoke({
        "raw_description": raw_description,
        "format_instructions": parser.get_format_instructions()
    })
