import pandas as pd


def filter_df(df: pd.DataFrame, date_range, notes_vals) -> pd.DataFrame:
    """
    Provides a filtered dataframe base on passed args.

    Args:
    df (dataframe): Pandas dataframe we want to apply filter to.

    date_range (list): List of days you want to filter by.

    notes_vals (str): Specific values in the notes column.
    """
    out = df

    if not out.empty and date_range and date_range[0]:
        out = out[out["datetime"] >= pd.to_datetime(date_range[0])]

    if not out.empty and date_range and len(date_range) > 1 and date_range[1]:
        # inclusive end-of-day
        out = out[
            out["datetime"] <= pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
        ]

    if not out.empty and notes_vals:
        out = out[out["notes"].isin(notes_vals)]

    return out
