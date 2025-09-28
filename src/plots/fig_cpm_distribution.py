import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def fig_cpm_distribution(df: pd.DataFrame, bgcolor: str) -> go.Figure:
    """
    Generates a plotly graph object figure to visualize the CPM Distribution of a passed dataframe. In layman's terms the frequency of which a specific CPM number appears in the passed dataframe. EG: 5 counts of 15CPM, 2 counts of 20CPM, etc...
    """

    fig = px.histogram(df, x="count", nbins=40)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=bgcolor,
        plot_bgcolor=bgcolor,
        margin=dict(l=20, r=20, t=40, b=30),
        xaxis_title="CPM",
        yaxis_title="Frequency",
    )
    return fig
