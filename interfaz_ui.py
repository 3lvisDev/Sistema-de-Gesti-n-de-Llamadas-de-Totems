from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QPlainTextEdit, QPushButton,
                               QSizePolicy, QSpacerItem, QStackedWidget, QVBoxLayout,
                               QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1136, 662)

        # Definición de estilos para botones
        button_style = """
        QPushButton {
            background-color: #1e3d59;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            margin: 4px 2px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #2e5d79;
        }
        QPushButton:pressed {
            background-color: #0e2d49;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        """
        # Definición de estilos para botones del menú lateral
        sidebar_button_style = """
        QPushButton {
            background-color: #1e3d59;
            color: white;
            border: none;
            padding: 10px;
            text-align: left;
            text-decoration: none;
            font-size: 14px;
            margin: 4px 2px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #1E3D55; 
        }
        QPushButton:pressed {
            background-color: #3B698D;
        }
        QPushButton:checked {
            background-color: #2E5675;
        }
        """
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: rgb(239, 240, 241);") # Fondo gris claro
        MainWindow.setCentralWidget(self.centralwidget)

        self.main_layout = QHBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Icono lateral y botones de menú lateral
        self.icon_only = QWidget()
        self.icon_only.setStyleSheet("""
            QWidget { background-color: rgb(3, 31, 48); }
            QPushButton {
                color: white;
                height: 30px;
                border: none;
                border-radius: 10px;
            }
            QPushButton:checked {
                background-color: #F5FAFE;
                color: #1F95EF;
                font-weight: bold;
            }
        """)
        self.icon_layout = QVBoxLayout(self.icon_only)
        
        self.profile_pic = QLabel()
        self.profile_pic.setPixmap(QPixmap(":/newPrefix/images/profile_pic.png"))
        self.profile_pic.setFixedSize(40, 40)
        self.profile_pic.setScaledContents(True)
        self.icon_layout.addWidget(self.profile_pic)

        self.dashboard_button = QPushButton()
        self.dashboard_button.setIcon(QIcon(":/newPrefix/images/dashboard_white.png"))
        self.dashboard_button.setCheckable(True)
        self.icon_layout.addWidget(self.dashboard_button)

        self.icon_layout.addStretch()

        self.signout_button = QPushButton()
        self.signout_button.setIcon(QIcon(":/newPrefix/images/log_out_white.png"))
        self.signout_button.setCheckable(True)
        self.icon_layout.addWidget(self.signout_button)

        self.main_layout.addWidget(self.icon_only)

        # Menú lateral extendido
        self.icon_name = QWidget()
        self.icon_name.setStyleSheet("""
            QWidget {
                background-color: rgb(3, 31, 48);
                color: white;
            }
            QPushButton {
                color: white;
                text-align: left;
                height: 30px;
                border: none;
                padding-left: 10px;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
            QPushButton:checked {
                background-color: #F5FAFE;
                color: #1F95EF;
                font-weight: bold;
            }
        """)
        self.icon_name.hide()
        self.icon_name_layout = QVBoxLayout(self.icon_name)

        self.sidebar_header = QHBoxLayout()
        self.sidebar_logo = QLabel()
        self.sidebar_logo.setPixmap(QPixmap(":/newPrefix/images/profile_pic.png"))
        self.sidebar_logo.setFixedSize(40, 40)
        self.sidebar_logo.setScaledContents(True)
        self.sidebar_header.addWidget(self.sidebar_logo)
        self.sidebar_title = QLabel("Sidebar")
        self.sidebar_title.setFont(QFont("Arial", 12, QFont.Bold))
        self.sidebar_header.addWidget(self.sidebar_title)
        self.icon_name_layout.addLayout(self.sidebar_header)

        self.totem_buttons = []
        for i in range(1, 3):  # Selecciona el rango de botones de totem a mostrar 1 a 3 - Default y el maximo que desee.
            button = QPushButton(f"Totem {i}")
            button.setIcon(QIcon(":/newPrefix/images/dashboard_white.png"))
            button.setCheckable(True)
            button.setStyleSheet(sidebar_button_style)
            button.setMinimumSize(200, 40)
            self.totem_buttons.append(button)
            self.icon_name_layout.addWidget(button)

        self.icon_name_layout.addStretch()

        self.signout_sidebar = QPushButton("Sign Out")
        self.signout_sidebar.setIcon(QIcon(":/newPrefix/images/log_out_white.png"))
        self.signout_sidebar.setCheckable(True)
        self.signout_sidebar.setStyleSheet(sidebar_button_style)
        self.icon_name_layout.addWidget(self.signout_sidebar)

        self.main_layout.addWidget(self.icon_name)

        # Área principal de la interfaz
        self.main_area = QWidget()
        self.main_area.setStyleSheet("background-color: white;")
        self.main_area_layout = QVBoxLayout(self.main_area)

        # Cabecera de la interfaz
        self.header = QWidget()
        self.header.setStyleSheet("background-color: rgb(172, 194, 221); border: none;")
        self.header_layout = QHBoxLayout(self.header)

        self.menu_button = QPushButton()
        self.menu_button.setIcon(QIcon(":/newPrefix/images/menu.png"))
        self.menu_button.setStyleSheet("border: none;")
        self.menu_button.setCheckable(True)
        self.header_layout.addWidget(self.menu_button)

        self.header_layout.addStretch()

        self.search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setStyleSheet("background-color: white;")
        self.search_button = QPushButton()
        self.search_button.setIcon(QIcon(":/newPrefix/images/search.png"))
        self.search_layout.addWidget(self.search_bar)
        self.search_layout.addWidget(self.search_button)
        self.header_layout.addLayout(self.search_layout)

        self.header_layout.addStretch()

        self.profile_button = QPushButton()
        self.profile_button.setIcon(QIcon(":/newPrefix/images/image.png"))
        self.profile_button.setStyleSheet("border: none;")
        self.header_layout.addWidget(self.profile_button)

        self.main_area_layout.addWidget(self.header)

        self.content = QStackedWidget()
        self.content.setStyleSheet("background-color: rgb(3, 31, 48);")

        self.dashboard_page = QWidget()
        self.dashboard_layout = QGridLayout(self.dashboard_page)

        self.call_log = QPlainTextEdit()
        self.call_log.setStyleSheet("background-color: white;")
        self.dashboard_layout.addWidget(self.call_log, 0, 0)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            color: red;
            font-size: 20px;
            background-color: lightgray;
            border: 2px solid darkred;
            padding: 10px;
            border-radius: 5px;
        """)
        self.dashboard_layout.addWidget(self.status_label, 1, 0)

        self.button_panel = QWidget()
        self.button_panel.setStyleSheet("background-color: rgb(172, 194, 221); border: none;")
        self.button_layout = QHBoxLayout(self.button_panel)

        self.accept_call = QPushButton("Aceptar Llamada")
        self.accept_call.setFont(QFont("Arial", 12, QFont.Bold))
        self.accept_call.setStyleSheet(button_style)
        self.accept_call.setMinimumSize(200, 50)
        self.accept_call.setMaximumSize(200, 50)
        self.accept_call.setCheckable(True)

        self.disconnect_call = QPushButton("Cortar llamada")
        self.disconnect_call.setFont(QFont("Arial", 12, QFont.Bold))
        self.disconnect_call.setStyleSheet(button_style)
        self.disconnect_call.setMinimumSize(200, 50)
        self.disconnect_call.setMaximumSize(200, 50)
        self.disconnect_call.setCheckable(True)

        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.accept_call)
        self.button_layout.addSpacing(20)
        self.button_layout.addWidget(self.disconnect_call)
        self.button_layout.addStretch(1)

        self.dashboard_layout.addWidget(self.button_panel, 2, 0)
        self.content.addWidget(self.dashboard_page)
        self.main_area_layout.addWidget(self.content)
        self.main_layout.addWidget(self.main_area, 1)

        self.retranslateUi(MainWindow)
        self.menu_button.toggled.connect(self.icon_only.setHidden)
        self.menu_button.toggled.connect(self.icon_name.setVisible)
        self.signout_button.toggled.connect(MainWindow.close)
        self.signout_sidebar.toggled.connect(MainWindow.close)
        self.dashboard_button.toggled.connect(self.icon_name.setHidden)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "MainWindow", None))
        self.sidebar_title.setText(QCoreApplication.translate("MainWindow", "Sidebar", None))
        for i, button in enumerate(self.totem_buttons, 1):
            button.setText(QCoreApplication.translate("MainWindow", f"Totem {i}", None))
        self.signout_sidebar.setText(QCoreApplication.translate("MainWindow", "Sign Out", None))
        self.accept_call.setText(QCoreApplication.translate("MainWindow", "Aceptar Llamada", None))
        self.disconnect_call.setText(QCoreApplication.translate("MainWindow", "Cortar llamada", None))
