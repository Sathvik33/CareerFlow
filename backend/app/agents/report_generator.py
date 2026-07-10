import asyncio
from app.agents.models import DailyReportModel, GapAnalysisModel, RecommendationModel
from app.agents.researcher import research_company

async def generate_daily_report(
    new_jobs_count: int,
    high_match_jobs_count: int,
    top_companies: list[str],
    gap_analysis_list: list[GapAnalysisModel],
    recommendation_list: list[RecommendationModel]
) -> DailyReportModel:
    strengths = set()
    weaknesses = set()

    for gap in gap_analysis_list:
        strengths.update(gap.strengths)
        weaknesses.update(gap.missing_skills)

    recommended_actions = []
    for rec in recommendation_list:
        if rec.action_items:
            recommended_actions.append(rec.action_items[0])

    recommended_action = recommended_actions[0] if recommended_actions else "Review more jobs to identify skill gaps."

    # Research the top companies in parallel
    company_insights = {}
    if top_companies:
        tasks = [research_company(company) for company in top_companies]
        insights = await asyncio.gather(*tasks, return_exceptions=True)
        for i, company in enumerate(top_companies):
            insight = insights[i]
            if isinstance(insight, Exception):
                company_insights[company] = f"Could not fetch insights: {str(insight)}"
            else:
                company_insights[company] = insight

    return DailyReportModel(
        new_jobs=new_jobs_count,
        high_match_jobs=high_match_jobs_count,
        top_companies=top_companies,
        strengths=list(strengths)[:5],
        weaknesses=list(weaknesses)[:5],
        recommended_action=recommended_action,
        company_insights=company_insights
    )
