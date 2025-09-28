import pygmc
from datetime import datetime


def get_device_log():
    gc = pygmc.GMCSE(port="COM3")

    gc.get_version()
    gc.get_serial()

    # Pull log from GMC-SE
    base_filename = "GMC-SE"
    # ds = datetime.now().strftime("_%Y%m%d_%H%M%S")
    ds = datetime.now().strftime("_%Y%m%d")
    filename = f"{base_filename}{ds}.csv"
    filepath = "./data/"
    file = f"{filepath}{filename}"
    gc.save_history_csv(file)
    print(f"{file} has been written!")

    # gc.heartbeat_live_print()


if __name__ == "__main__":
    get_device_log()
