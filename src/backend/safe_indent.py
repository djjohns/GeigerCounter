import re


def safe_ident(name: str) -> bool:
    """
    Allow only letters, numbers, underscore; optionally schema.table with dot."""
    return bool(
        re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?", name)
    )
