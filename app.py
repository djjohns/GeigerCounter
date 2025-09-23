import os
import shutil
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
from typing import Optional, Tuple
from streamlit_autorefresh import st_autorefresh

DEFAULT_CONV = 0.0065  # µSv/hr per CPM (adjust if you've calibrated)
PAGE_BG = "#0f172a"

st.set_page_config(page_title="GQ GMC-SE Dashboard", layout="wide")


# --------------------------
# Helpers
# --------------------------
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


def copy_for_read(path: str) -> Optional[str]:
    """Workaround Windows locks: copy to temp file then read the copy."""
    try:
        base = os.path.basename(path)
        temp_dir = st.session_state.get("_temp_dir", os.path.dirname(path) or ".")
        os.makedirs(temp_dir, exist_ok=True)
        tmp_path = os.path.join(temp_dir, f"._reading_{base}.tmp")
        shutil.copyfile(path, tmp_path)
        return tmp_path
    except Exception:
        return None


def load_csv_path_live(path: str) -> Tuple[pd.DataFrame, str, Optional[float]]:
    """
    Live-mode read: no cache. Returns (df, info_message, mtime).
    We read fresh on every rerun; autorefresh triggers reruns.
    """
    try:
        mtime = os.path.getmtime(path)
    except FileNotFoundError:
        return pd.DataFrame(), f"File not found: {path}", None
    except Exception as e:
        return pd.DataFrame(), f"Could not stat file: {e}", None

    # Try direct read first
    try:
        df = pd.read_csv(path, engine="python", on_bad_lines="skip", encoding="utf-8")
        return normalize_df(df), "", mtime
    except Exception as e1:
        # If locked, try temp copy
        tmp = copy_for_read(path)
        if tmp:
            try:
                df = pd.read_csv(
                    tmp, engine="python", on_bad_lines="skip", encoding="utf-8"
                )
                return (
                    normalize_df(df),
                    "Read from temporary copy (source locked).",
                    mtime,
                )
            except Exception as e2:
                return pd.DataFrame(), f"Read failed (direct: {e1}) (temp: {e2})", mtime
            finally:
                try:
                    os.remove(tmp)
                except Exception:
                    pass
        else:
            return pd.DataFrame(), f"Read failed (direct): {e1}", mtime


def enrich(df: pd.DataFrame, conv_factor: float, roll_window: int) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    conv = conv_factor if (conv_factor and conv_factor > 0) else DEFAULT_CONV
    w = int(roll_window) if (roll_window and roll_window >= 1) else 15
    df["usv_hr"] = df["count"] * conv
    df["rolling_cpm"] = df["count"].rolling(window=w, min_periods=1).mean()
    df["rolling_usv"] = df["usv_hr"].rolling(window=w, min_periods=1).mean()
    return df


def filter_df(df: pd.DataFrame, date_range, notes_vals):
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


def kpis(df: pd.DataFrame):
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


def fig_time_series(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df["datetime"], y=df["count"], mode="lines+markers", name="CPM")
    )
    if "rolling_cpm" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"], y=df["rolling_cpm"], mode="lines", name="Rolling CPM"
            )
        )
    if "usv_hr" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["usv_hr"],
                mode="lines",
                name="µSv/hr",
                yaxis="y2",
            )
        )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PAGE_BG,
        plot_bgcolor=PAGE_BG,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title="Time"),
        yaxis=dict(title="CPM"),
        yaxis2=dict(title="µSv/hr", overlaying="y", side="right"),
    )
    return fig


def fig_hist(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(df, x="count", nbins=40)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PAGE_BG,
        plot_bgcolor=PAGE_BG,
        margin=dict(l=20, r=20, t=40, b=30),
        xaxis_title="CPM",
        yaxis_title="Frequency",
    )
    return fig


# --------------------------
# Sidebar: source + controls
# --------------------------
st.sidebar.title("Controls")

mode = st.sidebar.radio(
    "Data source", ["Upload CSV", "Read from file path (Live)"], index=0
)
conv_factor = st.sidebar.number_input(
    "CPM → µSv/hr factor", value=DEFAULT_CONV, step=0.0001, format="%.4f"
)
roll_window = st.sidebar.number_input(
    "Rolling window (minutes)", min_value=1, value=15, step=1
)

uploaded = None
file_path = None
follow_latest = False

if mode == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload GMC-SE CSV", type=["csv"])
else:
    file_path = st.sidebar.text_input("CSV path", value="")
    follow_latest = st.sidebar.checkbox(
        "Follow latest (auto-extend end date)", value=True
    )
    refresh_secs = st.sidebar.number_input(
        "Auto-refresh seconds", min_value=2, value=10, step=1
    )
    # Trigger rerun on a timer (no-op if value is None)
    st_autorefresh(interval=int(refresh_secs * 1000), key="autorefresh_key")


# --------------------------
# Main
# --------------------------
st.title("GQ GMC-SE Radiation Dashboard")

df = pd.DataFrame()
info = None
mtime = None

try:
    if mode == "Upload CSV" and uploaded is not None:
        df = load_csv_bytes(uploaded.getvalue())
        info = "Loaded from upload."
    elif mode == "Read from file path (Live)" and file_path:
        df, info, mtime = load_csv_path_live(file_path)
except Exception as e:
    st.error(f"Failed to load CSV: {e}")

if info:
    st.caption(f"ℹ️ {info}")

if df.empty:
    st.info(
        "Upload a CSV or provide a valid file path to begin. Expected columns: "
        "`datetime, count, unit, mode, reference_datetime, notes`."
    )
    st.stop()

# --- Build safe date bounds
min_dt = pd.to_datetime(df["datetime"].min())
max_dt = pd.to_datetime(df["datetime"].max())

if pd.isna(min_dt) or pd.isna(max_dt):
    st.info("No valid datetimes found in the CSV.")
    st.stop()

min_date = min_dt.date()
max_date = max_dt.date()

# Initialize date_range in session_state so we can adjust it in live mode.
if "date_range" not in st.session_state:
    # Default to last 24h clamped within data
    default_start = max(min_date, (max_date - timedelta(days=1)))
    st.session_state.date_range = (default_start, max_date)

# In live mode with follow_latest ON:
# If new data arrived (max_date increased), slide the end date forward to keep showing the latest.
if mode == "Read from file path (Live)" and follow_latest:
    cur_start, cur_end = st.session_state.date_range
    # If the end equals previous max or is beyond it, bump end to new max_date.
    if cur_end >= max_date or cur_end == min_date:
        st.session_state.date_range = (cur_start, max_date)
    # Also clamp start within bounds
    st.session_state.date_range = (
        max(min_date, st.session_state.date_range[0]),
        min(max_date, st.session_state.date_range[1]),
    )
else:
    # Still ensure bounds stay valid if data range shrank
    st.session_state.date_range = (
        max(min_date, st.session_state.date_range[0]),
        min(max_date, st.session_state.date_range[1]),
    )

date_range = st.date_input(
    "Date range",
    value=st.session_state.date_range,
    min_value=min_date,
    max_value=max_date,
    key="date_range_picker",
)

# Keep session_state in sync with widget selection
if isinstance(date_range, tuple) and len(date_range) == 2:
    st.session_state.date_range = date_range

# Notes filter
note_options = sorted(df["notes"].dropna().unique()) if "notes" in df.columns else []
notes_vals = st.multiselect(
    "Filter by notes/location", options=note_options, default=[]
)

# Filter + enrich
df_sel = filter_df(df, st.session_state.date_range, notes_vals)
df_sel = enrich(df_sel, conv_factor, roll_window)

# KPIs
cpm_cur, usv_cur, avg_roll, max_cpm = kpis(df_sel)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Current CPM", cpm_cur)
c2.metric("Current µSv/hr", usv_cur)
c3.metric(f"{roll_window}-min Avg (CPM)", avg_roll)
c4.metric("Max CPM (range)", max_cpm)

# Charts
left, right = st.columns([2, 1])
with left:
    st.subheader("Time Series (CPM & µSv/hr)")
    st.plotly_chart(fig_time_series(df_sel), use_container_width=True)
with right:
    st.subheader("CPM Distribution")
    st.plotly_chart(fig_hist(df_sel), use_container_width=True)

# Data preview
st.subheader("Data Preview")
show_cols = [
    c
    for c in [
        "datetime",
        "count",
        "usv_hr",
        "unit",
        "mode",
        "reference_datetime",
        "notes",
    ]
    if c in df_sel.columns
]
df_display = df_sel[show_cols].copy()
if "usv_hr" in df_display.columns:
    df_display["usv_hr"] = df_display["usv_hr"].round(4)
st.dataframe(df_display, use_container_width=True, height=360)

# Download enriched CSV
csv_bytes = df_display.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download enriched CSV",
    data=csv_bytes,
    file_name="gmcse_enriched.csv",
    mime="text/csv",
)

st.caption(
    "Note: µSv/hr is estimated from CPM using a fixed factor and is most accurate for the calibration energy (e.g., Cs-137 gamma)."
)
