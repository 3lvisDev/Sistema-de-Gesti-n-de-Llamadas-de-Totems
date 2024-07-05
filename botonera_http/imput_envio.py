import sys
import requests
import json
import time
import threading
import RPi.GPIO as GPIO
import subprocess

# Configuración del GPIO
BUTTON_PIN = 17 # GPIO 17 (pin 11)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

TOTEM_ACTUAL = "Totem2"  # Cambia esto según el totem que sea
TOTEM_IP = "172.21.0.134"  # Dirección IP del Totem actual

URL_SERVIDOR = 'http://172.21.0.7:67400/incoming_call'
URL_ESTADO = 'http://172.21.0.7:67400/call_status'

# Variable para controlar la reproducción del sonido
sound_process = None

def play_sound():
    global sound_process
    sound_process = subprocess.Popen(["aplay", "song/call.wav", "-q"])

def stop_sound():
    global sound_process
    if sound_process:
        sound_process.terminate()
    sound_process = None

def check_call_status():
    global sound_process
    while sound_process and sound_process.poll() is None:
        try:
            response = requests.get(f"{URL_ESTADO}?totem={TOTEM_ACTUAL}")
            if response.status_code == 200:
                status = response.json().get('status')
                if status in ['accepted', 'rejected', 'disconnected']:
                    stop_sound()
                    break
        except requests.RequestException as e:
            print(f"Error al verificar el estado de la llamada: {e}")
        time.sleep(1)  # Esperar 1 segundo antes de la próxima verificación

def enviar_llamada():
    print("Enviando señal de llamada al servidor...")
    data = {
        'ip': TOTEM_IP,
        'totem': TOTEM_ACTUAL
    }
    try:
        response = requests.post(URL_SERVIDOR, json=data)
        if response.status_code == 200:
            print("Señal de llamada enviada correctamente.")
            play_sound()
            # Iniciar un hilo para verificar el estado de la llamada
            threading.Thread(target=check_call_status, daemon=True).start()
        else:
            print("Error al enviar la señal de llamada. Código de estado:", response.status_code)
            print("Contenido de la respuesta:", response.content)
    except Exception as e:
        print("Error de conexión:", str(e))

print(f"Esperando que se presione el botón en el GPIO {BUTTON_PIN}...")

try:
    button_state = GPIO.input(BUTTON_PIN)
    while True:
        new_state = GPIO.input(BUTTON_PIN)
        if new_state != button_state:
            if new_state == GPIO.LOW and not sound_process:
                print("Botón presionado, iniciando llamada...")
                enviar_llamada()
            button_state = new_state
        time.sleep(0.05)  # Pequeña pausa para no sobrecargar la CPU
except KeyboardInterrupt:
    print("Programa terminado por el usuario.")
finally:
    stop_sound()
    GPIO.cleanup()  # Limpiar la configuración de GPIO al salir