from typing import Sequence
from sqlalchemy import text
from sqlalchemy.engine import Engine
from . import quote_table


def db_distinct_notes(engine: Engine, table: str) -> Sequence[str]:

    full = quote_table(table)

    query = text(
        f"""\
        SELECT DISTINCT "notes"
        FROM {full}
        WHERE "notes" IS NOT NULL
        ORDER BY "notes"
        """
    )

    with engine.begin() as conn:
        rows = conn.execute(query).fetchall()

    return [r[0] for r in rows if r[0] is not None]
