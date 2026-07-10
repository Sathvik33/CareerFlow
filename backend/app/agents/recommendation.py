from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.agents.llm import get_llm
from app.agents.models import GapAnalysisModel, RecommendationModel

async def generate_recommendations(gap_analysis: GapAnalysisModel) -> RecommendationModel:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=RecommendationModel)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Based on the provided gap analysis between a resume and a job description, generate actionable recommendations and a projected improvement percentage (0-100) if these actions are taken.\n{format_instructions}"),
        ("user", "Gap Analysis: {gap_analysis}")
    ])

    chain = prompt | llm | parser

    return await chain.ainvoke({
        "gap_analysis": gap_analysis.model_dump_json(),
        "format_instructions": parser.get_format_instructions()
    })
