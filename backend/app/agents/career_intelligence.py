from collections import Counter
from app.agents.models import JDModel, CareerTrendModel

def analyze_career_trends(jds: list[JDModel]) -> CareerTrendModel:
    all_skills = []
    for jd in jds:
        all_skills.extend(jd.skills)

    skill_counts = Counter(all_skills)
    total_jds = len(jds)

    skill_frequency = {skill: count / total_jds for skill, count in skill_counts.items()} if total_jds > 0 else {}
    top_missing_skill = skill_counts.most_common(1)[0][0] if skill_counts else "Unknown"

    return CareerTrendModel(
        top_missing_skill=top_missing_skill,
        skill_frequency=skill_frequency,
        most_valuable_project=f"Build a project using {top_missing_skill}",
        potential_match_increase_pct=15.0  # Placeholder heuristic
    )
