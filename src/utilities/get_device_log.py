import pygmc
from datetime import datetime


def get_device_log(base_filename="GMC-SE", data_dir="./data/") -> None:
    """
    Pulls device's log and writes it to GMC-SE_YYYYMMDD.csv in the repo's data dir.

    #### KWARGS:
    base_filename (str): Optional, base filename. Default: ``GMC-SE``.

    data_dir (str): Optional, path to where we write the file. Default: ``./data/``
    """
    gc = pygmc.GMCSE(port="COM3")
    # gc = pygmc.connect()  # More generic, loses reference in IDE.

    gc.get_version()
    gc.get_serial()

    # Pull log from GMC-SE
    # ds = datetime.now().strftime("_%Y%m%d_%H%M%S") # Suffix _YYYYMMDD_HHMMSS
    ds = datetime.now().strftime("_%Y%m%d")  # Suffix _YYYYMMDD
    filename = f"{base_filename}{ds}.csv"
    file = f"{data_dir}{filename}"
    gc.save_history_csv(file)
    print(f"{file} has been written!")

    # gc.heartbeat_live_print()


if __name__ == "__main__":
    get_device_log()
