import os
from typing import Optional


def get_db_url() -> Optional[str]:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    else:
        raise EnvironmentError("No url found for backend!")
