import pygmc


def device_info():
    gc = pygmc.GMCSE(port="COM3")

    conn_details = gc.get_connection_details()

    device_info = f"""\
    |------------------------GQ GMC GEIGER COUNTER-----------------------------|
    |Device Details
    |--------------------------------------------------------------------------|
    |Version: {gc.get_version()}
    |Serial Number: {gc.get_serial()}
    |---------------------------------------------------------------------------|
    |COM PORT DETAILS
    |--------------------------------------------------------------------------|
    |Port: {conn_details["port"]}
    |Baudrate: {conn_details["baudrate"]}
    |Timeout: {conn_details["timeout"]}
    |Open: {conn_details["is_open"]}
    |In Waiting: {conn_details["in_waiting"]}
    |Out Waiting: {conn_details["out_waiting"]}
    |---------------------------------------------------------------------------|
    |Sensor Readings
    |--------------------------------------------------------------------------|
    |Current Voltage: {gc.get_voltage()}
    |Current Temp: {gc.get_temp()}
    |Gyroscope: {gc.get_gyro()}
    |RTC: {gc.get_datetime()}
    |CPM: {gc.get_cpm()}
    |μSv/hr: {gc.get_usv_h()}
    |------------------------GQ GMC GEIGER COUNTER-----------------------------|
    """

    return device_info


if __name__ == "__main__":
    print(device_info())
