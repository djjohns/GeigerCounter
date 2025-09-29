import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from typing import Optional, Sequence
from . import quote_table, normalize_df


def db_fetch_slice(
    engine: Engine,
    table: str,
    start_date,
    end_date,
    notes_vals: Optional[Sequence[str]],
) -> pd.DataFrame:
    """
    Fetch filtered rows from DB. We apply end-date as exclusive (end + 1 day).
    Uses array ANY() for notes if provided.
    """
    full = quote_table(table)

    base = f"""
        SELECT 
          "datetime"
          ,"count"
          ,"unit"
          ,"mode"
          ,"reference_datetime"
          ,"notes"
        FROM {full}
        WHERE "datetime" >= :start
          AND "datetime" < :end_excl
    """

    params = {
        "start": pd.to_datetime(start_date),
        "end_excl": pd.to_datetime(end_date) + pd.Timedelta(days=1),
    }

    if notes_vals:
        base += ' AND "notes" = ANY(:notes)'
        params["notes"] = list(notes_vals)

    query = text(base + ' ORDER BY "datetime" ASC')

    with engine.begin() as conn:
        df = pd.read_sql_query(query, conn, params=params)

    return normalize_df(df)
