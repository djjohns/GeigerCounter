def quote_table(table: str) -> str:
    """
    Quote an identifier like schema.table or table.
    """

    if "." in table:
        schema, tbl = table.split(".", 1)
        return f'"{schema}"."{tbl}"'
    return f'"{table}"'
