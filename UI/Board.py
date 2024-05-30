from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QPoint
import chess

from AI.ChessBot import ChessBot
from UI.Piece import Piece, PieceType


class Board(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cells = [[None for _ in range(8)] for _ in range(8)]
        self.pieces = [[None for _ in range(8)] for _ in range(8)]
        self.initCells()
        self.addNumeration()
        self.board = chess.Board()
        self.ai = ChessBot(self.board)
        self.setStartPosition()
        self.oldPos = QPoint(0, 0)

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
        piece.pieceClicked.connect(self.showPossibleMoves)
        return piece

    def handleMove(self, piece):
        try:
            old_x = (self.oldPos.x())
            old_y = (self.oldPos.y())
            new_x = (piece.pos().x() + 50) // 100
            new_y = (piece.pos().y() + 50) // 100
            print("old_x = ",old_x)
            print("old_y = ",old_y)
            print("new_x = ", new_x)
            print("new_y = ", new_y)

            if old_x != new_x or old_y != new_y:
                move = chess.Move(
                    chess.square(old_x, 7 - old_y),
                    chess.square(new_x, 7 - new_y)
                )
                print(f"Attempting move: {move}")
                if move in self.board.legal_moves:
                    print("Move is legal")
                    self.board.push(move)
                    self.board.set_fen(self.board.fen())
                    if self.pieces[new_x][new_y]:
                        self.pieces[new_x][new_y].hide()
                        self.pieces[new_x][new_y] = None
                    self.pieces[old_x][old_y] = None
                    self.pieces[new_x][new_y] = piece
                    piece.setGeometry(self.cells[new_x][new_y].geometry())
                else:
                    print("Move is illegal")
                    piece.setGeometry(self.cells[old_x][old_y].geometry())


            print(f"Piece clicked: {piece.type} at ({old_x}, {old_y})")
            print(f"Piece moved: {piece.type} to ({new_x}, {new_y})")

            best_move = self.ai.getBestMove(self.board, 3)
            if best_move:
                self.board.push(best_move)
                from_square = best_move.from_square
                to_square = best_move.to_square
                print(f"AI move from {from_square} to {to_square}")
                piece = self.pieces[chess.square_file(from_square)][7 - chess.square_rank(from_square)]
                if piece is None:
                    print("Error: No piece found at AI's from_square")
                    return
                self.pieces[chess.square_file(from_square)][7 - chess.square_rank(from_square)] = None
                self.pieces[chess.square_file(to_square)][7 - chess.square_rank(to_square)] = piece
                piece.setGeometry(self.cells[chess.square_file(to_square)][7 - chess.square_rank(to_square)].geometry())
                print(f"AI moved: {best_move}")

            self.clearHighlights()

            print("Current board state:")
            print(self.board)

        except Exception as e:
            print(f"An error occurred during move handling: {e}")

    def showPossibleMoves(self, piece):
        self.clearHighlights()
        piece_position = (piece.pos().x() // 100, piece.pos().y() // 100)
        self.oldPos = QPoint(piece_position[0], piece_position[1])
        square = chess.square(piece_position[0], 7 - piece_position[1])
        legal_moves = list(self.board.legal_moves)
        print(f"Showing moves for piece at {piece_position} (square: {square}) of type {piece.type}")
        possible_moves_found = False
        for move in legal_moves:
            if move.from_square == square:
                to_square = move.to_square
                row = chess.square_file(to_square)
                column = 7 - chess.square_rank(to_square)
                self.highlightCell(row, column)
                print(f"Possible move to: ({row}, {column})")
                possible_moves_found = True
        if not possible_moves_found:
            print("No possible moves found")

    def highlightCell(self, row, column):
        cell = self.cells[row][column]
        cell.setStyleSheet("background-color: rgb(50, 205, 50)")

    def clearHighlights(self):
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    self.cells[i][j].setStyleSheet("background-color: rgb(192, 192, 192)")
                else:
                    self.cells[i][j].setStyleSheet("background-color: rgb(64, 64, 64)")

    def parseFen(self, fen):
        fen_rows = fen.split("/")
        for row in range(8):
            col = 0
            for char in fen_rows[row]:
                if char.isdigit():
                    col += int(char)
                else:
                    piece = self.createPiece(self.parseFenToPieceType(char))
                    point = self.cells[col][row].pos()
                    piece.setGeometry(point.x(), point.y(), 100, 100)
                    self.pieces[col][row] = piece
                    col += 1

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
