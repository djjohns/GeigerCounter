import pygmc
from time import sleep
from . import get_history_length


def erase_history() -> None:
    """
    Simulates user key stroke sequence to navigate the device's menu to select erase history. This is a bit clunky and you'll need to check the row count of the device log afterwards and repeat if necessary, as we have no method to capture the boolean (yes, no) of the erase history function on the device. In other words we don't know if when selecting the erase history function will default to yes or no without looking at the device's display.

    Suggested Implementation:
    ```python
    from utilities import get_history_length, erase_history

    erase_history()

    if get_history_length() > 1:
        erase_history()
    ```
    """
    gc = pygmc.GMCSE(port="COM3")
    # gc = pygmc.connect()  # More generic, loses reference in IDE.

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

    if get_history_length() > 1:
        erase_history()
