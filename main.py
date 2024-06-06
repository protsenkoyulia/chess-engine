import sys

from PyQt5.QtWidgets import QApplication

from AI.ChessBot import ChessBot
from QChessBoard import QChessBoard
from UI.Board import Board

if __name__ == "__main__":
    app = QApplication(sys.argv)

    board = QChessBoard()

    AI = ChessBot(board, False)

    board = Board(board)
    board.show()

    sys.exit(app.exec_())
