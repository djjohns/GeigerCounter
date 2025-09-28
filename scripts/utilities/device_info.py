import pygmc
from typing import Any


def device_info() -> dict[str, dict[str, Any]]:
    """Returns a dictionary of device info."""
    gc = pygmc.GMCSE(port="COM3")
    # gc = pygmc.connect()  # More generic, loses reference in IDE.

    conn_details = gc.get_connection_details()

    device_info: dict[str, dict[str, Any]] = {
        "device_details": {
            "version": gc.get_version(),
            "serial_number": gc.get_serial(),
        },
        "com_port_details": {
            "port": conn_details["port"],
            "baudrate": conn_details["baudrate"],
            "timeout": conn_details["timeout"],
            "open": conn_details["is_open"],
            "in_waiting": conn_details["in_waiting"],
            "out_waiting": conn_details["out_waiting"],
        },
        "sensor_readings": {
            "voltage": gc.get_voltage(),
            "temp": gc.get_temp(),
            "gyroscope": gc.get_gyro(),
            "RTC": gc.get_datetime(),
            "CPM": gc.get_cpm(),
            "μSv_hr": gc.get_usv_h(),
        },
    }

    return device_info


if __name__ == "__main__":
    info = device_info()
    header = f"|-------------------GQ GMC GEIGER COUNTER----------------------|"

    footer = f"|-------------------GQ GMC GEIGER COUNTER----------------------|"

    sep = f"|--------------------------------------------------------------|"

    print(header)

    for group, group_dict in info.items():
        print(sep)
        print(f"|{group}")
        print(sep)
        for k, v in group_dict.items():
            print(f"|{k}: {v}")

    print(footer)
