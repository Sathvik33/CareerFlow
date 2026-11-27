from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.agents.llm import get_llm
from app.agents.models import ResumeModel, JDModel, GapAnalysisModel

async def analyze_gap(resume: ResumeModel, jd: JDModel, semantic_score: float, bm25_score: float) -> GapAnalysisModel:
    llm = get_llm(max_tokens=350)
    parser = PydanticOutputParser(pydantic_object=GapAnalysisModel)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Compare resume vs JD (semantic={semantic_score}/100, BM25={bm25_score}/100). Return concise strengths and missing skills as JSON only.\n{format_instructions}"),
        ("user", "Resume: {resume}\nJD: {jd}")
    ])

    chain = prompt | llm | parser

    return await chain.ainvoke({
        "semantic_score": semantic_score,
        "bm25_score": bm25_score,
        "resume": resume.model_dump_json(),
        "jd": jd.model_dump_json(),
        "format_instructions": parser.get_format_instructions()
    })
