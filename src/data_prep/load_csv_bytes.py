import pandas as pd
import streamlit as st
from . import normalize_df


@st.cache_data(show_spinner=False)
def load_csv_bytes(bytes_data: bytes) -> pd.DataFrame:
    """Load CSV from uploaded bytes (cache OK for uploads)."""
    df = pd.read_csv(
        pd.io.common.BytesIO(bytes_data),
        engine="python",
        on_bad_lines="skip",
        encoding="utf-8",
    )
    return normalize_df(df)
