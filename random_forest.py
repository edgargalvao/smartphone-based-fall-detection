import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import websocket
import json
import threading
import time
import numpy as np
import os

# Twilio Call integration
from twilio.rest import Client

# Credenciais do Twilio (preencher para uso real)
account_sid = "<your_account_sid>"
auth_token = "<your_auth_token>"
twilio_client = Client(account_sid, auth_token)
TO_PHONE = "<>your_phone_number>"
FROM_PHONE = "<twilio_phone_number>"

# Variáveis de controle de tempo e alerta
start_time = time.time()
fall_alert_sent = False

# Carrega os dados do CSV
df = pd.read_csv('sensor_data.csv')

# Balanceamento dos dados: seleciona todos os exemplos de queda e não-queda
falling_1 = df[df['falling'] == 1]
falling_0 = df[df['falling'] == 0].sample(n=len(falling_1), random_state=42, replace=False)
df_balanced = pd.concat([falling_1, falling_0]).sample(frac=1, random_state=42)

# Seleciona as colunas de features (exclui timestamp, falling, norm)
feature_cols = [col for col in df_balanced.columns if col not in ['timestamp', 'falling', 'norm']]
X = df_balanced[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
y = df_balanced['falling'].astype(int)

# Divide em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Treina o Random Forest
clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
clf.fit(X_train, y_train)

# Avalia o modelo
y_pred = clf.predict(X_test)
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# Lista de sensores e quantidade de valores por sensor
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
    "android.sensor.rotation_vector": 5,
}

# Novamente, seleciona as colunas de features
feature_cols = [col for col in df_balanced.columns if col not in ['timestamp', 'falling', 'norm']]

# Buffer para armazenar os dados dos sensores em tempo real
sensor_buffer = {}
window_timestamp = None
WINDOW_SIZE = 0.1  # segundos

# Função para realizar chamada de alerta via Twilio
def make_call_alert():
    global fall_alert_sent
    try:
        call = twilio_client.calls.create(
            #url="http://demo.twilio.com/docs/voice.xml",
            twiml='<Response><Say voice="alice" language="pt-BR" >Alerta de queda detectada! Alerta de queda! A vovó caiu!</Say></Response>',
            to=TO_PHONE,
            from_=FROM_PHONE,
        )
        print(f"Ligação realizada! SID: {call.sid}")
        fall_alert_sent = True
    except Exception as e:
        print(f"[DEBUG] Falha ao realizar ligação Twilio: {e}")

# Função para classificar uma janela de dados e emitir alerta se necessário
def classify_and_alert(row):
    global fall_alert_sent
    os.system('clear' if os.name == 'posix' else 'cls')  # Limpa o console
    X_live = pd.DataFrame([row], columns=feature_cols)
    X_live = X_live.apply(pd.to_numeric, errors='coerce').fillna(0)
    pred = clf.predict(X_live)[0]
    now = time.time()
    if pred == 1:
        print("ALERTA: Queda detectada!")
        # Só faz a chamada uma vez, e só se já passaram 5 segundos do início da execução
        if not fall_alert_sent and (now - start_time > 5):
            print("Fazendo chamada de alerta...")
            print("Fazendo chamada de alerta...")
            print("Fazendo chamada de alerta...")
            print("Fazendo chamada de alerta...")
            print("Fazendo chamada de alerta...")
            make_call_alert()
    else:
        print("Nenhuma queda detectada.")

# Função chamada ao receber mensagem do WebSocket (dados do sensor)
def on_message(ws, message):
    global sensor_buffer, window_timestamp
    data = json.loads(message)
    values = data['values']
    sensor_type = data['type']
    timestamp = time.time()

    # Determina a janela de tempo
    if window_timestamp is None or timestamp - window_timestamp > WINDOW_SIZE:
        window_timestamp = timestamp
        sensor_buffer = {}

    sensor_buffer[sensor_type] = values

    # Quando todos os sensores estiverem presentes, classifica
    if all(s in sensor_buffer for s in SENSOR_TYPES):
        row = []
        for s in SENSOR_TYPES:
            row.extend(sensor_buffer[s])
        classify_and_alert(row)
        # Prepara para próxima janela
        window_timestamp = None
        sensor_buffer = {}

# Função chamada em caso de erro no WebSocket
def on_error(ws, error):
    print("WebSocket error:", error)

# Função chamada ao fechar o WebSocket
def on_close(ws, close_code, reason):
    print("WebSocket closed:", close_code, reason)

# Função chamada ao abrir o WebSocket
def on_open(ws):
    print("WebSocket connected.")

# Função para iniciar o WebSocket e receber dados em tempo real
def start_websocket():
    ws_url = 'ws://192.168.1.2:8080/sensors/connect?types=["android.sensor.accelerometer","android.sensor.gyroscope","android.sensor.magnetic_field","android.sensor.gravity","android.sensor.linear_acceleration","android.sensor.rotation_vector"]'
    try:
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever()
    except Exception as e:
        print(f"[DEBUG] Falha ao conectar ao servidor WebSocket: {e}")

# Ponto de entrada principal
if __name__ == "__main__":
    print("Iniciando classificação em tempo real...")
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()
    while True:
        time.sleep(1)
