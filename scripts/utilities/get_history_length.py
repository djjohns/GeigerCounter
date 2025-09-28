import pygmc


def get_history_length():
    gc = pygmc.GMCSE(port="COM3")
    # gc = pygmc.connect()  # More generic, loses reference in IDE.

    gc.get_version()
    gc.get_serial()

    history = gc.get_history_data()
    row_count = len(history)
    print(f"Current row count: {row_count}")
    return row_count


if __name__ == "__main__":
    get_history_length()
