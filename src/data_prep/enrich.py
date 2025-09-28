import pandas as pd


def enrich(
    df: pd.DataFrame,
    conv_factor: float,
    roll_window: int,
    default_conv_factor: float = None,
) -> pd.DataFrame:
    """
    Calculates µSv/hr based on CPM * conv_factor and adds it as a column to the returned dataframe. µSv/hr is estimated from CPM using a fixed factor and is most accurate for the calibration energy (e.g., Cs-137 gamma). Default conversion factor of 0.0065 is set at the app level.
    """

    if df.empty:
        return df

    df = df.copy()

    conv = conv_factor if (conv_factor and conv_factor > 0) else default_conv_factor

    w = int(roll_window) if (roll_window and roll_window >= 1) else 15

    df["usv_hr"] = df["count"] * conv

    df["rolling_cpm"] = df["count"].rolling(window=w, min_periods=1).mean()

    df["rolling_usv"] = df["usv_hr"].rolling(window=w, min_periods=1).mean()

    return df
