from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QFont

class PieceType:
    WHITE_KING = 0
    WHITE_QUEEN = 1
    WHITE_ROOK = 2
    WHITE_BISHOP = 3
    WHITE_KNIGHT = 4
    WHITE_PAWN = 5
    BLACK_KING = 6
    BLACK_QUEEN = 7
    BLACK_ROOK = 8
    BLACK_BISHOP = 9
    BLACK_KNIGHT = 10
    BLACK_PAWN = 11

class Piece(QWidget):
    on_piece_move = pyqtSignal(QWidget)
    on_piece_pressed = pyqtSignal(QWidget)

    def __init__(self, piece_type, parent=None):
        super().__init__(parent)
        self.type = piece_type
        self.imagePiece = None
        self.oldPos = QPoint()
        self.initImage()
        self.board = parent.board

    def initImage(self):
        self.imagePiece = QLabel(self)
        font = QFont()
        font.setPointSize(92)
        self.imagePiece.setFont(font)
        self.imagePiece.setAlignment(Qt.AlignCenter)
        self.imagePiece.setGeometry(0, 0, 100, 100)
        self.imagePiece.setText(self.convertTypeToUNICODE(self.type))

    def convertTypeToUNICODE(self, piece_type):
        switcher = {
            PieceType.WHITE_KING: "\u2654",
            PieceType.WHITE_QUEEN: "\u2655",
            PieceType.WHITE_ROOK: "\u2656",
            PieceType.WHITE_BISHOP: "\u2657",
            PieceType.WHITE_KNIGHT: "\u2658",
            PieceType.WHITE_PAWN: "\u2659",
            PieceType.BLACK_KING: "\u265A",
            PieceType.BLACK_QUEEN: "\u265B",
            PieceType.BLACK_ROOK: "\u265C",
            PieceType.BLACK_BISHOP: "\u265D",
            PieceType.BLACK_KNIGHT: "\u265E",
            PieceType.BLACK_PAWN: "\u265F"
        }
        return switcher.get(piece_type, "")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.pos()
            self.on_piece_pressed.emit(self)
            print(f"Piece clicked: {self.type}")

    def mouseMoveEvent(self, event):
        delta = event.pos() - self.oldPos
        self.move(self.pos() + delta)

    def mouseReleaseEvent(self, event):
        new_x = (self.pos().x() + 50) // 100
        new_y = (self.pos().y() + 50) // 100
        self.move(new_x * 100, new_y * 100)
        self.on_piece_move.emit(self)
        print(f"Piece moved: {self.type}")