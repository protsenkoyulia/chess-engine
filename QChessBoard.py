import chess
from PyQt5.QtCore import *


class QChessBoard(QObject):
    update = pyqtSignal()
    made_move = pyqtSignal(chess.Move)
    move_order = pyqtSignal(bool)
    game_over = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.is_white_move = True
        self.board = chess.Board(chess960=True)

    def reset(self):
        self.board.reset()
        self.is_white_move = True

        self.update.emit()

    def do_move(self, move):
        if self.is_valid_move(move):
            self.board.push(move)
            self.is_white_move = not self.is_white_move
            self.made_move.emit(move)

        self.update.emit()

        if (self.board.is_game_over()):
            self.game_over.emit(not self.is_white_move)
        else:
            self.move_order.emit(self.is_white_move)

    def is_valid_move(self, move):
        return move in self.get_possible_move()

    def get_possible_move(self):
        return list(self.board.legal_moves)

    def fen(self):
        return self.board.fen()

    def get_chess_board(self):
        return self.board
