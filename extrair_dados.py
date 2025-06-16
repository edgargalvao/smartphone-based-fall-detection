import websocket
import json
import csv
import time
import datetime
import os
import math
import threading
import sys
from pynput import keyboard  # pip install pynput

SENSOR_TYPES = [
    "android.sensor.accelerometer",
    "android.sensor.gyroscope",
    "android.sensor.magnetic_field",
    "android.sensor.gravity",
    "android.sensor.linear_acceleration",
    "android.sensor.rotation_vector",
]
SENSOR_VALUE_COUNTS = {
    "android.sensor.accelerometer": 3,
    "android.sensor.gyroscope": 3,
    "android.sensor.magnetic_field": 3,
    "android.sensor.gravity": 3,
    "android.sensor.linear_acceleration": 3,
    "android.sensor.rotation_vector": 5,  # Only 4 values (x, y, z, cos)
}

csv_exists = os.path.isfile('sensor_data.csv')
csv_file = open('sensor_data.csv', mode='a', newline='')
csv_writer = None

space_pressed = False

def on_press(key):
    global space_pressed
    if key == keyboard.Key.space:
        space_pressed = True

def on_release(key):
    global space_pressed
    if key == keyboard.Key.space:
        space_pressed = False

# Inicie o listener do teclado em uma thread separada
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.daemon = True
listener.start()

def get_headers():
    headers = ['timestamp']
    for sensor in SENSOR_TYPES:
        for i in range(SENSOR_VALUE_COUNTS[sensor]):
            headers.append(f"{sensor}_value_{i}")
    headers.append('norm')
    headers.append('falling')
    return headers

# Buffer for sensor values per window
sensor_buffer = {}
window_timestamp = None
WINDOW_SIZE = 0.1  # seconds

def on_message(ws, message):
    global csv_writer, sensor_buffer, window_timestamp, csv_exists, space_pressed
    data = json.loads(message)
    values = data['values']
    sensor_type = data['type']
    timestamp = datetime.datetime.now().isoformat()
    print("timestamp = ", timestamp)

    # Determine window
    if window_timestamp is None or (isinstance(window_timestamp, float) and time.time() - window_timestamp > WINDOW_SIZE):
        window_timestamp = time.time()
        sensor_buffer = {}

    sensor_buffer[sensor_type] = values

    # Write only when all sensors are present
    if all(s in sensor_buffer for s in SENSOR_TYPES):
        if csv_writer is None:
            headers = get_headers()
            csv_writer = csv.writer(csv_file)
            # Write header only if file is empty
            if not csv_exists or os.stat('sensor_data.csv').st_size == 0:
                csv_writer.writerow(headers)
                csv_exists = True
        row = [datetime.datetime.now().isoformat()]
        all_values = []
        for s in SENSOR_TYPES:
            row.extend(sensor_buffer[s])
            all_values.extend(sensor_buffer[s])
        # Calcule a norma Euclidiana
        norm = math.sqrt(sum(float(v)**2 for v in all_values))
        row.append(norm)
        row.append(int(space_pressed))  # 1 se pressionado, 0 caso contrário
        csv_writer.writerow(row)
        csv_file.flush()
        # Prepare for next window
        window_timestamp = None
        sensor_buffer = {}

def on_error(ws, error):
    print("error occurred")
    print(error)

def on_close(ws, close_code, reason):
    print("connection close")
    print("close code : ", close_code)
    print("reason : ", reason  )

def on_open(ws):
    print("connected")
    

def connect(url):
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
 

connect('ws://wfu30-235.rc.unesp.br:8080/sensors/connect?types=["android.sensor.accelerometer","android.sensor.gyroscope","android.sensor.magnetic_field","android.sensor.gravity","android.sensor.linear_acceleration","android.sensor.rotation_vector"]')
