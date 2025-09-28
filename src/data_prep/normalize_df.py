import pandas as pd


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize columns and types for the GMC-SE CSV format."""

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    df.columns = [c.strip().lower() for c in df.columns]

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    if "reference_datetime" in df.columns:
        df["reference_datetime"] = pd.to_datetime(
            df["reference_datetime"], errors="coerce"
        )

    if "count" in df.columns:
        df["count"] = pd.to_numeric(df["count"], errors="coerce")

    if "notes" in df.columns:
        df["notes"] = df["notes"].astype(str)

    # Drop rows missing core fields
    core = [c for c in ["datetime", "count"] if c in df.columns]
    if core:
        df = df.dropna(subset=core)

    if "datetime" in df.columns:
        df = df.sort_values("datetime")

    return df.reset_index(drop=True)
