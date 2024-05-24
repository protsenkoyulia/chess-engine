from PyQt5.QtWidgets import QWidget , QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
from UI.Piece import Piece, PieceType
import chess


class Board(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cells = [[None for _ in range(8)] for _ in range(8)]
        self.pieces = [[None for _ in range(8)] for _ in range(8)]
        self.initCells()
        #self.parseFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.addNumeration()
        self.board = chess.Board()
        self.setStartPosition()


    def createCell(self, row, column):
        cell = QWidget(self)
        cell.setGeometry(row * 100, column * 100, 100, 100)
        if (row + column) % 2 == 0:
            cell.setStyleSheet("background-color: rgb(192, 192, 192)")
        else:
            cell.setStyleSheet("background-color: rgb(64, 64, 64)")
        return cell

    def initCells(self):
        for i in range(8):
            for j in range(8):
                self.cells[i][j] = self.createCell(i, j)

    def createPiece(self, piece_type):
        piece = Piece(piece_type, self)
        piece.doMove.connect(self.handleMove)
        return piece

    def handleMove(self, piece):
        x = (piece.pos().x() + 50) // 100
        y = (piece.pos().y() + 50) // 100
        cell = self.cells[x][y]
        piece.setGeometry(cell.x(), cell.y(), 100, 100)

    def parseFen(self, fen):
        for i in range(8):
            index = fen.find("/")
            left = fen[:index] if index != -1 else fen
            fen = fen[index + 1:] if index != -1 else ""
            for j in range(len(left)):
                if not left[j].isdigit():
                    piece = self.createPiece(self.parseFenToPieceType(left[j]))
                    point = self.cells[j][i].pos()
                    piece.setGeometry(point.x(), point.y(), 100, 100)
                    self.pieces[j][i] = piece

    def parseFenToPieceType(self, symbol):
        switcher = {
            'K': PieceType.WHITE_KING,
            'Q': PieceType.WHITE_QUEEN,
            'R': PieceType.WHITE_ROOK,
            'B': PieceType.WHITE_BISHOP,
            'N': PieceType.WHITE_KNIGHT,
            'P': PieceType.WHITE_PAWN,
            'k': PieceType.BLACK_KING,
            'q': PieceType.BLACK_QUEEN,
            'r': PieceType.BLACK_ROOK,
            'b': PieceType.BLACK_BISHOP,
            'n': PieceType.BLACK_KNIGHT,
            'p': PieceType.BLACK_PAWN
        }
        return switcher.get(symbol, None)

    def addNumeration(self):
        for i in range(8):
            label_row = QLabel(str(8 - i), self)
            label_row.setGeometry(8 * 100, i * 100, 50, 100)
            label_row.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            label_column = QLabel(chr(65 + i), self)
            label_column.setGeometry(i * 100, 800, 100, 50)
            label_column.setAlignment(Qt.AlignCenter)

            font = label_row.font()
            font.setPointSize(14)
            font.setBold(True)
            label_row.setFont(font)

            font = label_column.font()
            font.setPointSize(14)
            font.setBold(True)
            label_column.setFont(font)

    def setStartPosition(self):
        startFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        self.board.set_fen(startFen)
        self.parseFen(startFen)