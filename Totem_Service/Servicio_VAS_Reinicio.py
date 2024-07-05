import os
import socket
import threading
import traceback
import logging
import pandas as pd
import pyaudio
import servicemanager
import win32serviceutil
import win32service
import win32event
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

class AudioServerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AudioServerService"
    _svc_display_name_ = "Audio Server Service"
    _svc_description_ = "Servicio que gestiona el servidor de audio."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.server_active = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.server_active = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))
        self.main()

    def main(self):
        HOST = '172.21.0.133'
        PORT = 65335
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024

        def handle_client(conn, addr):
            call_logger.info('Conexión establecida desde: %s - %s', addr, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            audio = pyaudio.PyAudio()

            def send_audio_to_client():
                stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
                while self.server_active:
                    data = stream.read(CHUNK)
                    conn.sendall(data)

            def receive_audio_from_client():
                stream_output = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
                while self.server_active:
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
                while self.server_active:
                    conn, addr = server_socket.accept()
                    threading.Thread(target=handle_client, args=(conn, addr)).start()
            except Exception as e:
                error_logger.error('Error en el servidor: %s', e)
                error_logger.error('Traceback: %s', traceback.format_exc())

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AudioServerService)
