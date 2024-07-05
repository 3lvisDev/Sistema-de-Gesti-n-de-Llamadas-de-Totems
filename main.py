import sys
import os
import json
from datetime import datetime
import threading
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import QThread, Signal, QTimer, Qt, QRect, QUrl
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtMultimedia import QSoundEffect
from flask import Flask, request, jsonify

from cliente_au import AudioCommunicator
from interfaz_ui import Ui_MainWindow

flask_app = Flask(__name__)
call_states = {}

class SecuritasStyleNotidication(QWidget):
    def __init__(self, caller, parent=None):
        super(SecuritasStyleNotidication, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        content_widget = QWidget(self)
        content_widget.setObjectName("contentWidget")
        content_widget.setStyleSheet("""
            #contentWidget {
                background-color: #36393f;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2f3136;
                border: none;
                padding: 8px;
                border-radius: 4px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #40444b;
            }
        """)

        layout = QHBoxLayout(content_widget)

        call_icon = QLabel("📞")
        call_icon.setFont(QFont("Arial", 24))
        layout.addWidget(call_icon)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        info_layout = QVBoxLayout()
        caller_label = QLabel(f"Llamada entrante de {caller}")
        caller_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(caller_label)

        status_label = QLabel("Llamada en espera...")
        status_label.setFont(QFont("Arial", 10))
        info_layout.addWidget(status_label)

        layout.addLayout(info_layout)

        button_layout = QHBoxLayout()
        accept_button = QPushButton("Aceptar")
        accept_button.setIcon(QIcon(":/newPrefix/images/accept_call.png"))
        reject_button = QPushButton("Rechazar")
        reject_button.setIcon(QIcon(":/newPrefix/images/reject_call.png"))

        button_layout.addWidget(accept_button)
        button_layout.addWidget(reject_button)
        layout.addLayout(button_layout)

        main_layout.addWidget(content_widget)

        self.accept_button = accept_button
        self.reject_button = reject_button

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(30000)  # La notificación se cierra después de 30 segundos

    def show_notification(self):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            self.setFixedSize(400, 120)
            
            x = screen_geometry.width() - self.width() - 20
            y = screen_geometry.height() - self.height() - 20
            
            self.setGeometry(QRect(x, y, self.width(), self.height()))
            self.show()
        else:
            print("No se pudo obtener la pantalla principal")
            self.show()

class CallLogger:
    def __init__(self, log_file='call_log.json'):
        self.log_file = log_file
        self.logs = self.load_logs()

    def load_logs(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []

    def save_logs(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)

    def add_log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}"
        self.logs.append(log_entry)
        self.save_logs()
        return log_entry

    def get_logs(self):
        return self.logs

class IncomingCallListener(QThread):
    call_received = Signal(dict)

    def run(self):
        flask_app.run(host='0.0.0.0', port=5000)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.communicator = AudioCommunicator()
        self.call_logger = CallLogger()
        self.setWindowTitle("Securitas")
        icon = QIcon(":/newPrefix/images/profile_pic.png")
        
        self.setup_call_log_style()
        self.ui.totem_buttons[0].clicked.connect(lambda: self.initiate_call("Totem 1", "172.21.0.133"))
        self.ui.totem_buttons[1].clicked.connect(lambda: self.initiate_call("Totem 2", "172.21.0.134"))
        self.ui.disconnect_call.clicked.connect(self.disconnect_all_calls)
        self.ui.accept_call.clicked.connect(self.on_accept_call)

        self.load_call_log()
        self.base_status_style = """
            color: white;
            font-size: 16px;
            background-color: #36393f;
            padding: 10px;
            border-radius: 5px;
        """
        self.ui.status_label.setStyleSheet(self.base_status_style)
        self.set_status_label("Estado: Listo")

        self.call_listener = IncomingCallListener()
        self.call_listener.call_received.connect(self.handle_incoming_call)
        self.call_listener.start()

        self.current_call = None
        self.waiting_calls = []
        self.incoming_calls = {}
        self.active_notifications = {}

        self.notification_sound = QSoundEffect()
        sound_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'song', 'ringtone.wav')
        self.notification_sound.setSource(QUrl.fromLocalFile(sound_file))
        self.notification_sound.setLoopCount(-1)  # -1 indica reproducción en bucle infinito
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.check_and_play_sound)

    def set_status_label(self, text, color="white"):
        self.ui.status_label.setText(text)
        self.ui.status_label.setStyleSheet(f"{self.base_status_style}color: {color};")

    def check_and_play_sound(self):
        if self.incoming_calls and not self.current_call:
            if not self.notification_sound.isPlaying():
                self.notification_sound.play()
        else:
            self.notification_sound.stop()

    def setup_call_log_style(self):
        font = QFont("Segoe UI", 12)
        font.setStyleHint(QFont.SansSerif)
        self.ui.call_log.setFont(font)

        self.ui.call_log.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2f3136;
                color: #dcddde;
                border: 1px solid #202225;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        self.ui.call_log.setReadOnly(True)

    def load_call_log(self):
        logs = self.call_logger.get_logs()
        self.ui.call_log.clear()
        self.ui.call_log.appendHtml("<h2 style='color: #ffffff;'>Registro de llamadas:</h2>")
        for log in logs:
            self.format_and_append_log(log)

    def add_to_call_log(self, message):
        log_entry = self.call_logger.add_log(message)
        self.format_and_append_log(log_entry)

    def format_and_append_log(self, log_entry):
        parts = log_entry.split(" - ", 1)
        if len(parts) == 2:
            datetime, message = parts
            formatted_entry = f"<p><span style='color: #72767d;'>{datetime}</span> - <span style='color: #dcddde;'>{message}</span></p>"
        else:
            formatted_entry = f"<p><span style='color: #dcddde;'>{log_entry}</span></p>"
        
        self.ui.call_log.appendHtml(formatted_entry)

    def initiate_call(self, totem, ip):
        print(f"Iniciando llamada con {totem} ({ip})")
        self.communicator.connect_to_server(totem, ip)
        self.add_to_call_log(f"Llamada iniciada: {totem}")
        self.set_status_label(f"Estado: Conectado a {totem}", "#43b581")  # Verde
        call_states[totem] = 'initiated'

    def disconnect_all_calls(self):
        if self.current_call:
            self.reject_incoming_call(self.current_call['totem'])
            self.current_call = None

        for totem in list(self.incoming_calls.keys()):
            self.reject_incoming_call(totem)

        for totem in list(self.active_notifications.keys()):
            self.active_notifications[totem].close()
            del self.active_notifications[totem]

        for totem, ip in [("Totem 1", "172.21.0.133"), ("Totem 2", "172.21.0.134")]:
            session_id = f"{totem}_{ip}"
            self.communicator.stop_call(session_id)
            call_states[totem] = 'disconnected'

        self.add_to_call_log("Todas las llamadas desconectadas")
        self.set_status_label("Estado: Desconectado", "white")

        self.notification_sound.stop()
        self.notification_timer.stop()

    def handle_incoming_call(self, call_info):
        totem = call_info['totem']
        ip = call_info['ip']
        print(f"Llamada entrante recibida de {totem} ({ip})")

        self.add_to_call_log(f"Llamada entrante de {totem}")
        self.incoming_calls[totem] = call_info

        if not self.current_call:
            self.notification_timer.start(100)  # Comprobar cada 100 ms
            self.ui.accept_call.setEnabled(True)
            self.set_status_label(f"Llamada entrante de {totem}", "#FFFFFF")  # Verde
        else:
            self.waiting_calls.append(call_info)
            self.set_status_label(f"Llamada en espera de {totem}", "#FFFFFF")  # Naranja

        self.show_notification(totem)

    def show_notification(self, totem):
        if totem in self.active_notifications:
            self.active_notifications[totem].close()
        
        self.notification = SecuritasStyleNotidication(totem, self)
        self.active_notifications[totem] = self.notification
        self.notification.show_notification()
        self.notification.accept_button.clicked.connect(lambda: self.on_accept_call(totem))
        self.notification.reject_button.clicked.connect(lambda: self.reject_incoming_call(totem))

    def on_accept_call(self, totem=None):
        if not totem:
            if not self.incoming_calls:
                return
            totem, call_info = next(iter(self.incoming_calls.items()))
        else:
            call_info = self.incoming_calls.get(totem)
            if not call_info:
                return

        self.accept_incoming_call(totem, call_info['ip'])
        if totem in self.active_notifications:
            self.active_notifications[totem].close()
            del self.active_notifications[totem]

        self.notification_sound.stop()
        self.notification_timer.stop()

    def accept_incoming_call(self, totem, ip):
        print(f"Aceptando llamada de {totem}")
        self.initiate_call(totem, ip)

        self.current_call = self.incoming_calls.pop(totem, None)
        self.set_status_label(f"Estado: En llamada con {totem}", "#FFFFFF")  # Verde
        call_states[totem] = 'accepted'
        self.ui.accept_call.setEnabled(False)

        if totem in self.active_notifications:
            self.active_notifications[totem].close()
            del self.active_notifications[totem]

        if self.waiting_calls:
            next_call = self.waiting_calls.pop(0)
            self.show_notification(next_call['totem'])

    def reject_incoming_call(self, totem):
        call_info = self.incoming_calls.pop(totem, None)
        if call_info:
            print(f"Rechazando llamada de {call_info['totem']}")
            self.add_to_call_log(f"Llamada rechazada: {call_info['totem']}")
            self.set_status_label("Estado: Llamada rechazada", "#FFFFFF")  # Rojo

            call_states[call_info['totem']] = 'rejected'
            self.communicator.stop_call(f"{call_info['totem']}_{call_info['ip']}")

        if totem in self.active_notifications:
            self.active_notifications[totem].close()
            del self.active_notifications[totem]

        if not self.incoming_calls and not self.waiting_calls:
            self.notification_sound.stop()
            self.notification_timer.stop()

        if self.waiting_calls:
            next_call = self.waiting_calls.pop(0)
            self.show_notification(next_call['totem'])

    def closeEvent(self, event):
        for notification in self.active_notifications.values():
            notification.close()
        self.call_logger.save_logs()
        self.notification_sound.stop()
        self.notification_timer.stop()
        super().closeEvent(event)

@flask_app.route('/incoming_call', methods=['POST'])
def incoming_call():
    data = request.json
    call_info = {'ip': data.get('ip'), 'totem': data.get('totem')}
    main_app.call_listener.call_received.emit(call_info)
    return jsonify({"status": "success"}), 200

@flask_app.route('/call_status', methods=['GET'])
def get_call_status():
    totem = request.args.get('totem')
    status = call_states.get(totem, 'unknown')
    return jsonify({"status": status})

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()

    threading.Thread(target=flask_app.run, kwargs={'host': '0.0.0.0', 'port': 67400}, daemon=True).start()

    sys.exit(qt_app.exec())