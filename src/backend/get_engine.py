from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from . import get_db_url


def get_engine() -> Optional[Engine]:
    url = get_db_url()
    if not url:
        return None
    return create_engine(url, pool_pre_ping=True)
