import pygmc
import pandas as pd


def get_history_df():
    gc = pygmc.GMCSE(port="COM3")

    gc.get_version()
    gc.get_serial()

    history = gc.get_history_data()

    df = pd.DataFrame(history[1:], columns=history[0])

    return df


if __name__ == "__main__":
    df = get_history_df()
    print(df.head(10))
