import pandas as pd
import streamlit as st
from datetime import timedelta
from streamlit_autorefresh import st_autorefresh
from src import (
    load_csv_bytes,
    load_csv_path_live,
    enrich,
    filter_df,
    kpis,
    fig_time_series,
    fig_cpm_distribution,
)

DEFAULT_CONV = 0.0065  # µSv/hr per CPM (adjust if you've calibrated)
PAGE_BG = "#0f172a"

st.set_page_config(page_title="GQ GMC-SE Dashboard", page_icon="☢️", layout="wide")


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
st.title("☢️GQ GMC-SE Radiation Dashboard☢️")

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

df_sel = enrich(df_sel, conv_factor, roll_window, default_conv_factor=DEFAULT_CONV)

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
    st.plotly_chart(fig_time_series(df_sel, PAGE_BG), use_container_width=True)
with right:
    st.subheader("CPM Distribution")
    st.plotly_chart(fig_cpm_distribution(df_sel, PAGE_BG), use_container_width=True)

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
