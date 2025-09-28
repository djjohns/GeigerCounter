import pandas as pd


def kpis(df: pd.DataFrame) -> tuple[str, str, str, str]:
    """
    Calculates and returns the following based on the passed dataframe:
    cur_cpm (str): Current CPM in passed dataframe.

    cur_usv (str): Current µSv/hr in passed dataframe.

    avg_roll (str): Rolling CPM or average CPM of passed dataframe.

    max_cpm (str): Maximum CPM in passed dataframe.
    """

    if df.empty:
        return "-", "-", "-", "-"

    last = df.iloc[-1]

    cur_cpm = f"{last['count']:.0f}" if pd.notna(last.get("count")) else "-"

    cur_usv = (
        f"{last['usv_hr']:.3f}"
        if "usv_hr" in df.columns and pd.notna(last.get("usv_hr"))
        else "-"
    )

    avg_roll = (
        f"{last['rolling_cpm']:.1f}"
        if "rolling_cpm" in df.columns and pd.notna(last.get("rolling_cpm"))
        else "-"
    )

    max_cpm = (
        f"{df['count'].max():.0f}"
        if "count" in df.columns and not df["count"].empty
        else "-"
    )

    return cur_cpm, cur_usv, avg_roll, max_cpm
