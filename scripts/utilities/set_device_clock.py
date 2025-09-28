import pygmc


def set_device_clock() -> None:
    """
    Resets the device's internal RTC. So far I am not convinced.
    """
    gc = pygmc.GMCSE(port="COM3")
    # gc = pygmc.connect()  # More generic, loses reference in IDE.

    gc.get_version()
    gc.get_serial()

    gc.set_datetime()


if __name__ == "__main__":
    set_device_clock()
