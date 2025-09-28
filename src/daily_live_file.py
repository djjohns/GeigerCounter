import time
from schedule import every, repeat, run_pending
from utilities import get_device_log


@repeat(every(1).minutes)
def daily_live_file():
    get_device_log()


if __name__ == "__main__":
    while True:
        run_pending()
        time.sleep(1)
