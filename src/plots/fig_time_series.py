import pandas as pd
import plotly.graph_objects as go


def fig_time_series(df: pd.DataFrame, bgcolor: str) -> go.Figure:
    """
    Generates a plotly graph object figure to visualize a time series of
    CPM, µSv/hr, and the rolling CPM over the length of time present in the passed dataframe.
    """
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
        paper_bgcolor=bgcolor,
        plot_bgcolor=bgcolor,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title="Time"),
        yaxis=dict(title="CPM"),
        yaxis2=dict(title="µSv/hr", overlaying="y", side="right"),
    )

    return fig
