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

# Lista dos tipos de sensores a serem coletados
SENSOR_TYPES = [
    "android.sensor.accelerometer",
    "android.sensor.gyroscope",
    "android.sensor.magnetic_field",
    "android.sensor.gravity",
    "android.sensor.linear_acceleration",
    "android.sensor.rotation_vector",
]
# Quantidade de valores para cada tipo de sensor
SENSOR_VALUE_COUNTS = {
    "android.sensor.accelerometer": 3,
    "android.sensor.gyroscope": 3,
    "android.sensor.magnetic_field": 3,
    "android.sensor.gravity": 3,
    "android.sensor.linear_acceleration": 3,
    "android.sensor.rotation_vector": 5,  # Apenas 4 valores relevantes normalmente
}

# Verifica se o arquivo CSV já existe
csv_exists = os.path.isfile('sensor_data.csv')
# Abre o arquivo CSV para escrita (append)
csv_file = open('sensor_data.csv', mode='a', newline='')
csv_writer = None

# Variável para indicar se a barra de espaço está pressionada
space_pressed = False

# Função chamada ao pressionar uma tecla
def on_press(key):
    global space_pressed
    if key == keyboard.Key.space:
        space_pressed = True

# Função chamada ao soltar uma tecla
def on_release(key):
    global space_pressed
    if key == keyboard.Key.space:
        space_pressed = False

# Inicia o listener do teclado em uma thread separada
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.daemon = True
listener.start()

# Função para gerar o cabeçalho do CSV
def get_headers():
    headers = ['timestamp']
    for sensor in SENSOR_TYPES:
        for i in range(SENSOR_VALUE_COUNTS[sensor]):
            headers.append(f"{sensor}_value_{i}")
    headers.append('norm')
    headers.append('falling')
    return headers

# Buffer para armazenar os valores dos sensores por janela
sensor_buffer = {}
window_timestamp = None
WINDOW_SIZE = 0.1  # segundos

# Função chamada ao receber mensagem do WebSocket (dados do sensor)
def on_message(ws, message):
    global csv_writer, sensor_buffer, window_timestamp, csv_exists, space_pressed
    data = json.loads(message)
    values = data['values']
    sensor_type = data['type']
    timestamp = datetime.datetime.now().isoformat()
    print("timestamp = ", timestamp)

    # Determina a janela de tempo
    if window_timestamp is None or (isinstance(window_timestamp, float) and time.time() - window_timestamp > WINDOW_SIZE):
        window_timestamp = time.time()
        sensor_buffer = {}

    sensor_buffer[sensor_type] = values

    # Escreve no CSV apenas quando todos os sensores estiverem presentes
    if all(s in sensor_buffer for s in SENSOR_TYPES):
        if csv_writer is None:
            headers = get_headers()
            csv_writer = csv.writer(csv_file)
            # Escreve o cabeçalho apenas se o arquivo estiver vazio
            if not csv_exists or os.stat('sensor_data.csv').st_size == 0:
                csv_writer.writerow(headers)
                csv_exists = True
        row = [datetime.datetime.now().isoformat()]
        all_values = []
        for s in SENSOR_TYPES:
            row.extend(sensor_buffer[s])
            all_values.extend(sensor_buffer[s])
        # Calcula a norma Euclidiana dos valores dos sensores
        norm = math.sqrt(sum(float(v)**2 for v in all_values))
        row.append(norm)
        row.append(int(space_pressed))  # 1 se pressionado, 0 caso contrário
        csv_writer.writerow(row)
        csv_file.flush()
        # Prepara para próxima janela
        window_timestamp = None
        sensor_buffer = {}

# Função chamada em caso de erro no WebSocket
def on_error(ws, error):
    print("error occurred")
    print(error)

# Função chamada ao fechar a conexão WebSocket
def on_close(ws, close_code, reason):
    print("connection close")
    print("close code : ", close_code)
    print("reason : ", reason  )

# Função chamada ao abrir a conexão WebSocket
def on_open(ws):
    print("connected")
    
# Função para conectar ao WebSocket e iniciar a coleta de dados
def connect(url):
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
 
# Inicia a conexão com o servidor WebSocket
connect('ws://wfu30-235.rc.unesp.br:8080/sensors/connect?types=["android.sensor.accelerometer","android.sensor.gyroscope","android.sensor.magnetic_field","android.sensor.gravity","android.sensor.linear_acceleration","android.sensor.rotation_vector"]')
