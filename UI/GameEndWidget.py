import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont


class GameEndWidget(QtWidgets.QMainWindow):
    restart = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конец игры")
        self.resize(400, 200)

        self.message = QtWidgets.QLabel("Информационное сообщение")
        self.message.setText("Это информационное сообщение.")
        self.message.setAlignment(Qt.AlignCenter)

        close_button = QtWidgets.QPushButton("Закрыть")
        start_again_button = QtWidgets.QPushButton("Начать заново")

        font = QFont()
        font.setPointSize(18)
        self.message.setFont(font)
        close_button.setFont(font)
        start_again_button.setFont(font)

        layout = QtWidgets.QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.message)
        layout.addStretch(1)
        layout.addWidget(close_button)
        layout.addWidget(start_again_button)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        close_button.clicked.connect(self.on_close_click)
        start_again_button.clicked.connect(self.on_start_again_click)

    def show(self, message):
        self.message.setText(message)
        super().show()
    def on_start_again_click(self):
        self.hide()
        self.restart.emit()

    def on_close_click(self):
        sys.exit()