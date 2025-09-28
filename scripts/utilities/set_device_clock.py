import pygmc


def set_device_clock():
    gc = pygmc.GMCSE(port="COM3")

    gc.get_version()
    gc.get_serial()

    gc.set_datetime()


if __name__ == "__main__":
    set_device_clock()
