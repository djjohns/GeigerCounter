import pandas as pd
from typing import Optional, Tuple
from sqlalchemy import text
from sqlalchemy.engine import Engine
from . import quote_table


def db_min_max(
    engine: Engine, table: str
) -> Tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    full = quote_table(table)
    q = text(f'SELECT MIN("datetime") AS min_dt, MAX("datetime") AS max_dt FROM {full}')
    with engine.begin() as conn:
        row = conn.execute(q).mappings().first()
    if not row:
        return None, None
    return pd.to_datetime(row["min_dt"]), pd.to_datetime(row["max_dt"])
