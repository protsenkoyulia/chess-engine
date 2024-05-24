import sys
from PyQt5.QtWidgets import QApplication
from UI.Board import Board

if __name__ == "__main__":
    app = QApplication(sys.argv)
    board = Board()
    board.show()
    sys.exit(app.exec_())
