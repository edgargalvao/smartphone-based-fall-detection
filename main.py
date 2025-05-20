import websocket
import json

def read_config_and_get_address(config_file_path):
    """
    Reads a JSON configuration file, parses its arguments, and extracts the address.

    Args:
        config_file_path (str): The path to the JSON configuration file.

    Returns:
        str: The address extracted from the configuration, or None if not found.
    """
    try:
        with open(config_file_path, 'r') as f:
            config = json.load(f)
            return config.get('address')
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {config_file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def on_message(ws, message):
    try:
        data = json.loads(message)
        if 'values' in data:
            values = data['values']
            if len(values) == 3:
                x, y, z = values
                print(f"x = {x}, y = {y}, z = {z}")
            else:
                print(f"Warning: Received message with {len(values)} values, expecting 3.")
        else:
            print("Warning: Received message without 'values' field.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON message: {message}")
    except Exception as e:
        print(f"An error occurred processing the message: {e}")

def on_error(ws, error):
    print("Error occurred:", error)

def on_close(ws, close_code, reason):
    print("Connection closed:", reason)

def on_open(ws):
    print("Connected to WebSocket server.")

def connect_to_websocket(address):
    """
    Connects to a WebSocket server at the given address for accelerometer data.

    Args:
        address (str): The WebSocket URL to connect to.
    """
    websocket_url = f"{address}/sensor/connect?type=android.sensor.accelerometer"
    ws = websocket.WebSocketApp(websocket_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

if __name__ == "__main__":
    config_file = 'config.json'  # You can change the filename here
    server_address = read_config_and_get_address(config_file)

    if server_address:
        print(f"Connecting to WebSocket server at: {server_address}")
        connect_to_websocket(f"ws://{server_address}:8080")
    else:
        print("Server address not found in configuration. Exiting.")