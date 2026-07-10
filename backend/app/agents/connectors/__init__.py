from abc import ABC, abstractmethod
from app.models.preference import UserPreference

class JobSource(ABC):
    @abstractmethod
    async def fetch_jobs(self, url: str, preferences: UserPreference) -> list[dict]:
        """
        Fetches jobs from the given URL and applies any local filtering based on preferences.
        Returns a list of dictionaries that map to the Job SQLAlchemy model.
        """
        pass
