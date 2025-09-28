import pygmc
from time import sleep
from get_history_length import get_history_length


def erase_history():
    gc = pygmc.GMCSE(port="COM3")

    gc.get_version()
    gc.get_serial()

    # Get to erase history menu item enter and wait 10s.
    key_sequence = [3, 2, 2, 3, 2, 2, 2, 2, 3]
    for i in key_sequence:
        print(i)
        gc.send_key(i)
        sleep(0.5)
    sleep(10.0)

    # Exit menu
    key_sequence = [2, 3, 2, 2, 2, 2, 2, 3]
    for i in key_sequence:
        print(i)
        gc.send_key(i)
        sleep(0.5)

    print(f"History should be deleted!")


if __name__ == "__main__":
    erase_history()

    if get_history_length() > 0:
        erase_history()
