from app.models.preference import UserPreference
from app.agents.connectors import JobSource

class WorkAtAStartupConnector(JobSource):
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        # Skeleton for YC WaaS
        return []
