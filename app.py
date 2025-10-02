import os
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
    get_engine,
    safe_ident,
    db_min_max,
    db_distinct_notes,
    db_fetch_slice,
)

DEFAULT_CONV = 0.0065  # µSv/hr per CPM (adjust if you've calibrated)
PAGE_BG = "#0f172a"

st.set_page_config(page_title="GQ GMC-SE Dashboard", page_icon="☢️", layout="wide")


# MARK: Sidebar

st.sidebar.title("Controls")

# Default source = Postgres
source_mode = st.sidebar.radio(
    "Data source",
    ["Postgres (Live)", "Upload CSV", "Read from file path (Live)"],
    index=0,
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
refresh_secs = 10

db_table = os.getenv("GMC_TABLE", "public.gmc_readings")  # schema-qualified default

# MARK: Upload controls
if source_mode == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload GMC-SE CSV", type=["csv"])

elif source_mode == "Read from file path (Live)":
    file_path = st.sidebar.text_input(
        "CSV path (inside container or host if running locally)", value=""
    )

    follow_latest = st.sidebar.checkbox(
        "Follow latest (auto-extend end date)", value=True
    )

    refresh_secs = st.sidebar.number_input(
        "Auto-refresh seconds", min_value=2, value=10, step=1
    )

    st_autorefresh(interval=int(refresh_secs * 1000), key="autorefresh_file")

else:
    # MARK: Postgres controls
    st.sidebar.text_input(
        "DB URL (optional; else uses env)",
        value="DATABASE_URL",
        key="dburl_display",
    )

    db_table = st.sidebar.text_input(
        "Table (schema.table)", value=db_table, key="db_table"
    )

    follow_latest = st.sidebar.checkbox(
        "Follow latest (auto-extend end date)", value=True
    )

    refresh_secs = st.sidebar.number_input(
        "Auto-refresh seconds", min_value=2, value=10, step=1
    )

    st_autorefresh(interval=int(refresh_secs * 1000), key="autorefresh_db")


# MARK: Main

st.title("☢️GQ GMC-SE Radiation Dashboard☢️")

df = pd.DataFrame()
info_msg = None

try:
    if source_mode == "Upload CSV" and uploaded is not None:
        df = load_csv_bytes(uploaded.getvalue())
        info_msg = "Loaded from upload."

    elif source_mode == "Read from file path (Live)" and file_path:
        df, info_msg = load_csv_path_live(file_path)

    else:
        # MARK: Postgres
        if not safe_ident(db_table.replace(".", "")) and "." not in db_table:
            st.error("Invalid table name.")
            st.stop()

        engine = get_engine()

        if engine is None:
            st.error("No DATABASE_URL / PG* env provided.")
            st.stop()

        # Compute min/max and notes from DB for controls
        min_dt, max_dt = db_min_max(engine, db_table)
        if min_dt is None or max_dt is None:
            st.info(f"No data found in table {db_table}.")
            st.stop()

        note_options = db_distinct_notes(engine, db_table)

        # Initialize / update date_range in session state
        min_date = pd.to_datetime(min_dt).date()
        max_date = pd.to_datetime(max_dt).date()

        if "date_range" not in st.session_state:
            default_start = max(min_date, max_date - timedelta(days=1))
            st.session_state.date_range = (default_start, max_date)

        if follow_latest:
            cur_start, cur_end = st.session_state.date_range
            st.session_state.date_range = (
                max(min_date, cur_start),
                max_date,  # always extend to latest
            )

        else:
            st.session_state.date_range = (
                max(min_date, st.session_state.date_range[0]),
                min(max_date, st.session_state.date_range[1]),
            )

        # Render controls now that we have bounds
        date_range = st.date_input(
            "Date range",
            value=st.session_state.date_range,
            min_value=min_date,
            max_value=max_date,
            key="date_range_picker",
        )

        # Keep session_state in sync
        if isinstance(date_range, tuple) and len(date_range) == 2:
            st.session_state.date_range = date_range

        notes_vals = st.multiselect(
            "Filter by notes/location", options=note_options, default=[]
        )

        # Fetch only the slice we need from DB
        df = db_fetch_slice(
            engine,
            db_table,
            st.session_state.date_range[0],
            st.session_state.date_range[1],
            notes_vals,
        )

        info_msg = f"Loaded from Postgres table {db_table}."

except Exception as e:
    st.error(f"Failed to load data: {e}")

if info_msg:
    st.caption(f"ℹ️ {info_msg}")

# MARK: Date Bounds
# If not using Postgres, we still need to build date bounds & controls
if source_mode != "Postgres (Live)":
    if df.empty:
        st.info(
            "Upload a CSV or provide a valid file path to begin. Expected columns: "
            "`datetime, count, unit, mode, reference_datetime, notes`."
        )
        st.stop()

    min_dt = pd.to_datetime(df["datetime"].min())

    max_dt = pd.to_datetime(df["datetime"].max())

    if pd.isna(min_dt) or pd.isna(max_dt):
        st.info("No valid datetimes found in the data.")
        st.stop()

    min_date = min_dt.date()

    max_date = max_dt.date()

    if "date_range" not in st.session_state:
        default_start = max(min_date, (max_date - timedelta(days=1)))
        st.session_state.date_range = (default_start, max_date)

    if follow_latest:
        cur_start, cur_end = st.session_state.date_range
        st.session_state.date_range = (max(min_date, cur_start), max_date)

    else:
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

    if isinstance(date_range, tuple) and len(date_range) == 2:
        st.session_state.date_range = date_range

    # MARK: Notes filter
    note_options = (
        sorted(df["notes"].dropna().unique()) if "notes" in df.columns else []
    )

    notes_vals = st.multiselect(
        "Filter by notes/location", options=note_options, default=[]
    )

    # Filter in-memory
    df = filter_df(df, st.session_state.date_range, notes_vals)

# MARK: Enrich & KPIs
df = enrich(df, conv_factor, roll_window)

cpm_cur, usv_cur, avg_roll, max_cpm = kpis(df)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Current CPM", cpm_cur)

c2.metric("Current µSv/hr", usv_cur)

c3.metric(f"{roll_window}-min Avg (CPM)", avg_roll)

c4.metric("Max CPM (range)", max_cpm)

# MARK: Plots
left, right = st.columns([2, 1])

with left:
    st.subheader("Time Series (CPM & µSv/hr)")
    st.plotly_chart(fig_time_series(df, PAGE_BG), use_container_width=True)

with right:
    st.subheader("CPM Distribution")
    st.plotly_chart(fig_cpm_distribution(df, PAGE_BG), use_container_width=True)

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
    if c in df.columns
]

df_display = df[show_cols].copy()

if "usv_hr" in df_display.columns:
    df_display["usv_hr"] = df_display["usv_hr"].round(4)

st.dataframe(df_display, use_container_width=True, height=360)

csv_bytes = df_display.to_csv(index=False).encode("utf-8")

# MARK: DL Button
st.download_button(
    "Download enriched CSV",
    data=csv_bytes,
    file_name="gmcse_enriched.csv",
    mime="text/csv",
)

# MARK: Footer
st.caption(
    "Note: µSv/hr is estimated from CPM using a fixed factor and is most accurate for the calibration energy (e.g., Cs-137 gamma)."
)
