import socket
import threading
import logging
import pyaudio

# Clase para manejar la comunicación de audio entre los tótems
class AudioCommunicator:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.FRAGMENTO = 1024
        self.FORMATO = pyaudio.paInt16
        self.CANALES = 1
        self.TASA = 44100
        self.sessions = {}

    # Iniciar una llamada con el ID de sesión dado (totem_ip)
    def start_call(self, session_id):
        if session_id not in self.sessions:
            print(f"Error: No se encontró la sesión {session_id}")
            return
        self.sessions[session_id]['active'] = True
        threading.Thread(target=self.send_audio_to_server, args=(session_id,)).start()
        threading.Thread(target=self.receive_audio_from_server, args=(session_id,)).start()

    # Detener una llamada con el ID de sesión dado (totem_ip)
    def stop_call(self, session_id):
        if session_id in self.sessions and self.sessions[session_id]['active']:
            self.sessions[session_id]['active'] = False
            if self.sessions[session_id]['socket']:
                try:
                    self.sessions[session_id]['socket'].close()
                except Exception as e:
                    print(f"Error al cerrar el socket: {e}")
            del self.sessions[session_id]
        else:
            print(f"Error: No se encontró la sesión {session_id} o ya estaba desconectada")

    # Enviar audio al servidor para la sesión dada (totem_ip)
    def send_audio_to_server(self, session_id):
        if session_id not in self.sessions:
            print(f"Error: No se encontró la sesión {session_id}")
            return
        session = self.sessions[session_id]
        stream_input = self.audio.open(format=self.FORMATO, channels=self.CANALES, rate=self.TASA, input=True, frames_per_buffer=self.FRAGMENTO)
        while session['active']:
            try:
                data = stream_input.read(self.FRAGMENTO)
                session['socket'].sendall(data)
            except Exception as e:
                print(f"Error al enviar datos: {str(e)}")
                self.stop_call(session_id)
                break

    # Recibir audio del servidor para la sesión dada (totem_ip)
    def receive_audio_from_server(self, session_id):
        if session_id not in self.sessions:
            print(f"Error: No se encontró la sesión {session_id}")
            return
        session = self.sessions[session_id]
        stream_output = self.audio.open(format=self.FORMATO, channels=self.CANALES, rate=self.TASA, output=True, frames_per_buffer=self.FRAGMENTO)
        while session['active']:
            try:
                data = session['socket'].recv(self.FRAGMENTO)
                if not data:
                    break
                stream_output.write(data)
            except Exception as e:
                print(f"Error al recibir datos: {str(e)}")
                self.stop_call(session_id)
                break

    # Conectar al servidor con el nombre del tótem y la dirección IP dados
    def connect_to_server(self, totem, ip):
        session_id = f"{totem}_{ip}"
        print(f"Conectando a {totem} en {ip}")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        try:
            # Determinar el puerto basado en el nombre del tótem
            port = self.determine_port(totem)
            client_socket.connect((ip, port))
            self.sessions[session_id] = {'socket': client_socket, 'active': False}
            print(f"Conexión establecida con {ip}")
            self.start_call(session_id)
            # Enviar un mensaje de confirmación al servidor
        except Exception as e:
            print(f"Error al conectarse al servidor {ip}: {e}")
            if session_id in self.sessions:
                del self.sessions[session_id]

    # Determinar el puerto basado en el nombre del tótem
    def determine_port(self, totem):
        port_mapping = {
            "Totem 1": 6788,
            "Totem 2": 6789,
        }
        return port_mapping.get(totem, 67400)

# Función cliente para conectarse al servidor y enviar mensajes
def cliente():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente_socket:
            cliente_socket.connect(('localhost', 9999))
            
            while True:
                mensaje = input("Escribe el mensaje: ")
                cliente_socket.send(mensaje.encode())
                respuesta = cliente_socket.recv(1024).decode()
                print("Respuesta del servidor:", respuesta)

                if mensaje.lower() == 'salir':
                    break
    except ConnectionRefusedError:
        print("No se pudo conectar con el servidor. Asegúrate de que el servidor esté en funcionamiento.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    cliente()
compile