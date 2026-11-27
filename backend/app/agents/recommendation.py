from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.agents.llm import get_llm
from app.agents.models import GapAnalysisModel, RecommendationModel

async def generate_recommendations(gap_analysis: GapAnalysisModel) -> RecommendationModel:
    llm = get_llm(max_tokens=300)
    parser = PydanticOutputParser(pydantic_object=RecommendationModel)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Given this gap analysis, return 2-3 concise action items and projected improvement percentage (0-100) as JSON only.\n{format_instructions}"),
        ("user", "{gap_analysis}")
    ])

    chain = prompt | llm | parser

    return await chain.ainvoke({
        "gap_analysis": gap_analysis.model_dump_json(),
        "format_instructions": parser.get_format_instructions()
    })
