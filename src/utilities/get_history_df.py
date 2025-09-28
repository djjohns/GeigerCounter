import pygmc
import pandas as pd


def get_history_df() -> pd.DataFrame:
    """
    Fetches device's history as a list of tuples where the first row is column names and converts it to a pandas dataframe. Since the device's onboard ram is only 2MB with data logging size capped around 300KB before I started noticing issues with fetching the data from the device we can get away with just returning the pandas dataframe.

    Returns:
    df (DataFrame): Columns: "datetime", "count", "unit", "mode", "reference_datetime", "notes"
    """
    gc = pygmc.GMCSE(port="COM3")
    # gc = pygmc.connect()  # More generic, loses reference in IDE.

    gc.get_version()
    gc.get_serial()

    history = gc.get_history_data()

    df = pd.DataFrame(history[1:], columns=history[0])

    return df


if __name__ == "__main__":
    df = get_history_df()
    print(df.head(10))
