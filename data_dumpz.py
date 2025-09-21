import pygmc
import pandas as pd


gc = pygmc.GMCSE(port="COM3")

conn_details = gc.get_connection_details()
version = gc.get_version()

device_info = f"""\
|------------------------GQ GMC GEIGER COUNTER---------------------------------|
|Device Details
|------------------------------------------------------------------------------|
|Version: {gc.get_version()}
|Serial Number: {gc.get_serial()}
|------------------------------------------------------------------------------|
|COM PORT DETAILS
|------------------------------------------------------------------------------|
|Port: {conn_details["port"]}
|Baudrate: {conn_details["baudrate"]}
|Timeout: {conn_details["timeout"]}
|Open: {conn_details["is_open"]}
|In Waiting: {conn_details["in_waiting"]}
|Out Waiting: {conn_details["out_waiting"]}
|------------------------------------------------------------------------------|
|Sensor Readings
|------------------------------------------------------------------------------|
|Current Voltage: {gc.get_voltage()}
|Current Temp: {gc.get_temp()}
|Gyroscope: {gc.get_gyro()}
|RTC: {gc.get_datetime()}
|CPM: {gc.get_cpm()}
|μSv/hr: {gc.get_usv_h()}
|------------------------GQ GMC GEIGER COUNTER---------------------------------|
"""

print(device_info)

# gc.heartbeat_live_print()

gc.save_history_csv("sample.csv")

# history = gc.get_history_data()
# print(len(history))
# history[0:3]

# df = pd.DataFrame(history[1:], columns=history[0])
# print(df.head(10))
