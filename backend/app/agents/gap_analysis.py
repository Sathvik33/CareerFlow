from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.agents.llm import get_llm
from app.agents.models import ResumeModel, JDModel, GapAnalysisModel

async def analyze_gap(resume: ResumeModel, jd: JDModel, semantic_score: float, bm25_score: float) -> GapAnalysisModel:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=GapAnalysisModel)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert career counselor. Compare the resume to the job description and identify missing skills and strengths. The semantic match score is {semantic_score}/100 and BM25 score is {bm25_score}/100.\n{format_instructions}"),
        ("user", "Resume: {resume}\n\nJob Description: {jd}")
    ])

    chain = prompt | llm | parser

    return await chain.ainvoke({
        "semantic_score": semantic_score,
        "bm25_score": bm25_score,
        "resume": resume.model_dump_json(),
        "jd": jd.model_dump_json(),
        "format_instructions": parser.get_format_instructions()
    })
