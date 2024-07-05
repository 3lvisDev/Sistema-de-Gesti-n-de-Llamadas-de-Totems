import os
import socket
import threading
import traceback
import logging
import pandas as pd
import pyaudio
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO)
error_logger = logging.getLogger("error")
call_logger = logging.getLogger("call")
event_logger = logging.getLogger("event")

# Crear archivos de log si no existen
log_files = ['errores.log', 'llamadas.log', 'eventos.log']
for file_name in log_files:
    if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            pass

# Función principal
def main():
    HOST = '172.21.0.133'
    PORT = 5001
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    server_active = True

    def handle_client(conn, addr):
        call_logger.info('Conexión establecida desde: %s - %s', addr, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        audio = pyaudio.PyAudio()

        def send_audio_to_client():
            stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            while server_active:
                data = stream.read(CHUNK)
                conn.sendall(data)

        def receive_audio_from_client():
            stream_output = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
            while server_active:
                try:
                    data = conn.recv(CHUNK)
                    if not data:
                        break
                    stream_output.write(data)
                except Exception as e:
                    error_logger.error('Error al recibir audio: %s', e)
                    error_logger.error('Traceback: %s', traceback.format_exc())

        send_thread = threading.Thread(target=send_audio_to_client)
        recv_thread = threading.Thread(target=receive_audio_from_client)
        send_thread.start()
        recv_thread.start()
        send_thread.join()
        recv_thread.join()
        conn.close()
        audio.terminate()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            event_logger.info("Servidor escuchando en %s:%s", HOST, PORT)
            while server_active:
                conn, addr = server_socket.accept()
                threading.Thread(target=handle_client, args=(conn, addr)).start()
        except Exception as e:
            error_logger.error('Error en el servidor: %s', e)
            error_logger.error('Traceback: %s', traceback.format_exc())

if __name__ == '__main__':
    main()

# Crear y mostrar DataFrames de logs
if os.path.exists('errores.log'):
    error_df = pd.read_csv('errores.log', sep=' - ', names=['Timestamp', 'Nombre', 'Nivel', 'Mensaje'], engine='python')
    print("Registros de errores:")
    print(error_df)

if os.path.exists('llamadas.log'):
    call_df = pd.read_csv('llamadas.log', sep=' - ', names=['Timestamp', 'Mensaje'], engine='python')
    print("\nRegistros de llamadas:")
    print(call_df)

if os.path.exists('eventos.log'):
    event_df = pd.read_csv('eventos.log', sep=' - ', names=['Timestamp', 'Mensaje'], engine='python')
    print("\nRegistros de eventos:")
    print(event_df)
else:
    print("No se encontró el archivo eventos.log")
