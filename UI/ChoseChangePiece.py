from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal


class ChoseChangePiece(QtWidgets.QMainWindow):
    chose = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выберите фигуру")
        self.resize(400, 200)

        dropdown_list = QtWidgets.QComboBox()

        # Добавление элементов в список
        for item in ["Слон", "Конь", "Ладья", "Ферзь"]:
            dropdown_list.addItem(item)

        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(dropdown_list)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        dropdown_list.setCurrentIndex(-1)
        dropdown_list.currentIndexChanged.connect(self.close)

        self.switcher = {
            0: 'b',
            1: 'k',
            2: 'r',
            3: 'q'
        }

    def shoe(self):
        super().show()

    def close(self, i):
        self.chose.emit(self.switcher.get(i, None))
        super().close()
