import chess
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtWidgets import QWidget, QLabel, QScrollArea, QVBoxLayout

from UI.GameEndWidget import GameEndWidget
from UI.Piece import Piece, PieceType


class Board(QWidget):
    def __init__(self, chessBoard, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Шахматы")

        self.cells = [[None for _ in range(8)] for _ in range(8)]
        self.pieces = [[None for _ in range(8)] for _ in range(8)]
        self.end_widget = GameEndWidget()
        self.board = chessBoard

        self.initCells()
        self.addNumeration()
        self.initMoveHistory()
        self.init_move_order()

        self.end_widget.restart.connect(self.reset_game)

        self.update_board()
        self.board.update.connect(self.update_board)
        self.board.game_over.connect(
            lambda is_white: self.end_widget.show("Белые выиграли!" if is_white else "Черные выиграли!"))

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
        piece.on_piece_move.connect(self.handleMove)
        piece.on_piece_move.connect(self.clear_highlights)
        piece.on_piece_pressed.connect(self.showPossibleMoves)
        return piece

    def handleMove(self, piece):
        old_x = (self.oldPos.x())
        old_y = (self.oldPos.y())
        new_x = (piece.pos().x() + 50) // 100
        new_y = (piece.pos().y() + 50) // 100

        if old_x != new_x or old_y != new_y:
            print(f"old_x = {old_x} old_y = {old_y} --> new_x = {new_x} new_y = {new_y}")

            self.board.do_move(chess.Move(chess.square(old_x, 7 - old_y), chess.square(new_x, 7 - new_y)))

    def showPossibleMoves(self, piece):
        self.clear_highlights()
        piece_position = (piece.pos().x() // 100, piece.pos().y() // 100)
        self.oldPos = QPoint(piece_position[0], piece_position[1])
        square = chess.square(piece_position[0], 7 - piece_position[1])
        legal_moves = self.board.get_possible_move()
        print(f"Showing moves for piece at {piece_position} (square: {square}) of type {piece.type}")
        possible_moves_found = False
        for move in legal_moves:
            if move.from_square == square:
                to_square = move.to_square
                row = chess.square_file(to_square)
                column = 7 - chess.square_rank(to_square)
                self.highlight_cell(row, column)
                print(f"Possible move to: ({row}, {column})")
                possible_moves_found = True
        if not possible_moves_found:
            print("No possible moves found")

    def highlight_cell(self, row, column):
        cell = self.cells[row][column]
        cell.setStyleSheet("background-color: rgb(50, 205, 50)")

    def clear_highlights(self):
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    self.cells[i][j].setStyleSheet("background-color: rgb(192, 192, 192)")
                else:
                    self.cells[i][j].setStyleSheet("background-color: rgb(64, 64, 64)")

    def clear_board(self):
        self.clear_highlights()

        for i in range(8):
            for j in range(8):
                if self.pieces[i][j]:
                    self.pieces[i][j].hide()
                    self.pieces[i][j] = None

    def update_board(self):
        self.clear_board()

        fen_parameters = self.board.fen().split(" ")

        print(fen_parameters)

        fen_rows = fen_parameters[0].split("/")
        for row in range(8):
            col = 0
            for char in fen_rows[row]:
                if char.isdigit():
                    col += int(char)
                else:
                    piece = self.createPiece(self.parseFenToPieceType(char))
                    point = self.cells[col][row].pos()
                    piece.setGeometry(point.x(), point.y(), 100, 100)
                    piece.show()
                    self.pieces[col][row] = piece
                    col += 1

        fen_move_order = fen_parameters[1]

        if (fen_move_order == "w"):
            self.move_order_label.setText("Ход белых")
        else:
            self.move_order_label.setText("Ход черных")

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
            label_row = QLabel(str(8 - i), self, )
            label_row.setGeometry(8 * 100, i * 100, 50, 100)
            label_row.setAlignment(Qt.AlignCenter)

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

    def initMoveHistory(self):

        move_history_label = QLabel("История ходов", self)
        move_history_label.setGeometry(850, 60,  250, 25)

        font = move_history_label.font()
        font.setPointSize(18)
        move_history_label.setFont(font)
        move_history_label.setAlignment(Qt.AlignCenter)

        move_history_container = QWidget(self)
        scroll = QScrollArea(self)

        self.move_history = QVBoxLayout()

        move_history_container.setLayout(self.move_history)

        scroll.setGeometry(850, 100, 250, 700)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(move_history_container)

        self.board.made_move.connect(self.add_move_into_history)

    def add_move_into_history(self, move):
        stretch = self.move_history.itemAt(self.move_history.count() - 1)
        self.move_history.removeItem(stretch)
        self.move_history.addWidget(QLabel(f'{move.uci()}'))
        self.move_history.addStretch()

    def init_move_order(self):
        self.move_order_label = QLabel("Б", self)
        self.move_order_label.setGeometry(850, 20,  250, 25)

        font = self.move_order_label.font()
        font.setPointSize(18)
        self.move_order_label.setFont(font)
        self.move_order_label.setAlignment(Qt.AlignCenter)

    def reset_game(self):
        self.board.reset()

        while self.move_history.count():
            item = self.move_history.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()