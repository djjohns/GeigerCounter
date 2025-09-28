import time
from schedule import every, repeat, run_pending
from utilities import (
    set_device_clock,
    erase_history,
    get_device_log,
    get_history_length,
)


@repeat(every().day.at("23:59"))
def daily_reset_device_log():

    get_device_log()
    set_device_clock()
    erase_history()
    if get_history_length() > 1:
        erase_history()


if __name__ == "__main__":
    while True:
        run_pending()
        time.sleep(1)
