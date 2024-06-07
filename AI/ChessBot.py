import math

import chess
import chess.engine
from PyQt5.QtCore import *


class Worker(QObject):

    def __init__(self, task):
        super().__init__()
        self.task = task

    def start(self):
        self.task()

class ChessBot(QObject):
    def __init__(self, q_chess_board, color, parent=None):
        super().__init__(parent)

        self.board = q_chess_board.get_chess_board()
        self.q_board = q_chess_board
        self.color = color

        self.thread_worker = QThread()

        self.worker = Worker(self.do_best_move)

        self.worker.moveToThread(self.thread_worker)
        self.thread_worker.started.connect(self.worker.start)
        self.thread_worker.start()

        self.canDoMove = False

        q_chess_board.move_order.connect(self.on_change_move_order)

    def on_change_move_order(self, move_order):
        if move_order == self.color:
            self.canDoMove = True

    def do_best_move(self):
        while True:
            if self.canDoMove:
                self.q_board.do_move(self.getBestMove(self.board, 3))
                self.canDoMove = False

    def evaluateBoard(self, board):
        material_score = self.calculateMaterial(board)
        mobility_score = self.calculateMobility(board)
        connected_pawn_score = self.calculateConnectedPawn(board)
        double_pawn_score = self.calculateDoublePawn(board)
        crashed_castling_score = self.calculateCrashedCastling(board)
        two_bishops_score = self.calculateTwoBishops(board)
        endgame_score = self.calculateEndgame(board)

        total_score = (material_score + mobility_score + connected_pawn_score
                       + double_pawn_score + crashed_castling_score + two_bishops_score
                       + endgame_score)
        return total_score

    # Материал показывает количество фигур
    # возвращается разница в материале между белыми и чёрными
    def calculateMaterial(self, board):
        material_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 305,
            chess.BISHOP: 333,
            chess.ROOK: 563,
            chess.QUEEN: 950,
            chess.KING: 0,
        }
        material_score = 0
        for piece_type, value in material_values.items():
            material_score += value * len(board.pieces(piece_type, chess.WHITE))
            material_score -= value * len(board.pieces(piece_type, chess.BLACK))
        return material_score

    # Чем больше развиты фигуры (то есть чем больше полей они бьют), тем лучше
    # тип фигуры оценивается по количеству атакуемых клеток, и это значение добавляется к общей оценке мобильности
    def calculateMobility(self, piece):
        mobility_values = {
            chess.KNIGHT: 9,
            chess.BISHOP: 4,
            chess.ROOK: 3,
            chess.QUEEN: 3,
        }
        mobility_score = 0
        for piece_type, value in mobility_values.items():
            for square in self.board.pieces(piece_type, chess.WHITE):
                mobility_score += value * len(self.board.attacks(square))
            for square in self.board.pieces(piece_type, chess.BLACK):
                mobility_score -= value * len(self.board.attacks(square))
        return mobility_score

    def isConnectedPawn(self, board, square, color):
        adjacent_files = [chess.square_file(square) - 1, chess.square_file(square) + 1]
        for file in adjacent_files:
            if 0 <= file <= 7:
                for rank in range(8):
                    adjacent_square = chess.square(file, rank)
                    if board.piece_at(adjacent_square) == chess.Piece(chess.PAWN, color):
                        return True
        return False

    # Соединенная пешка - пешка, защищенная другой
    # Наличие таких пешек является одним из признаков хорошей пешечной структуры
    # Улучшает оценку на 12
    def calculateConnectedPawn(self, board):
        connected_pawn_score = 0
        for square in chess.SQUARES:
            if board.piece_at(square) == chess.Piece(chess.PAWN, chess.WHITE):
                if self.isConnectedPawn(board, square, chess.WHITE):
                    connected_pawn_score += 12
            elif board.piece_at(square) == chess.Piece(chess.PAWN, chess.BLACK):
                if self.isConnectedPawn(board, square, chess.BLACK):
                    connected_pawn_score -= 12
        return connected_pawn_score

    # Сдвоенные пешки обладают меньшей подвижностью, они больше подвержены нападению неприятельских фигур
    # Ухудшает оценку на 25
    def calculateDoublePawn(self, board):
        double_pawn_score = 0
        for file in range(8):
            white_pawn_in_file = sum(
                1 for square in range(file, 64, 8) if board.piece_at(square) == chess.Piece(chess.PAWN, chess.WHITE))
            black_pawn_in_file = sum(
                1 for square in range(file, 64, 8) if board.piece_at(square) == chess.Piece(chess.PAWN, chess.BLACK))
            if white_pawn_in_file > 1:
                double_pawn_score -= 25 * (white_pawn_in_file - 1)
            if black_pawn_in_file > 1:
                double_pawn_score += 25 * (black_pawn_in_file - 1)

            return double_pawn_score

    # Если король потерял рокировку не рокировавшись, то это считается серьезной слабостью для безопасности короля.
    # ухудшает свою оценку на 50 за каждую потерянную рокировку:
    def calculateCrashedCastling(self, board):
        crashed_castling_score = 0
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        if white_king_square is not None and white_king_square != chess.E1:
            if not board.has_kingside_castling_rights(chess.WHITE):
                crashed_castling_score -= 50
            if not board.has_queenside_castling_rights(chess.WHITE):
                crashed_castling_score -= 50
        if black_king_square is not None and black_king_square != chess.E8:
            if not board.has_kingside_castling_rights(chess.BLACK):
                crashed_castling_score += 50
            if not board.has_queenside_castling_rights(chess.BLACK):
                crashed_castling_score += 50
        return crashed_castling_score

    # Два слона вместе могут отрезать пешки или короля.
    # улучшают оценку на 50
    def calculateTwoBishops(self, board):
        two_bishops_score = 0
        if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
            two_bishops_score += 50
        if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
            two_bishops_score -= 50
        return two_bishops_score

    # Оценка для эндшпиля. Она учитывает близость короля побеждающей стороны к королю проигрывающей,
    # а также расстояние проигрывающего короля от центра
    # Эндшпиль - когда оставется менее 9 фигур
    def calculateEndgame(self, board):
        MaximumPiecesForEndgame = 8
        AttackerKingProximityToDefenderKing = 10
        DistanceBetweenDefenderKingAndMiddle = 10

        endgame_score = 0
        pieces_count = sum(
            len(board.pieces(piece_type, chess.WHITE)) + len(board.pieces(piece_type, chess.BLACK)) for piece_type in
            chess.PIECE_TYPES)

        if pieces_count > MaximumPiecesForEndgame:
            return endgame_score

        white_material = self.calculateMaterial(board) > 0
        black_material = self.calculateMaterial(board) < 0
        white_leading = white_material and not black_material
        black_leading = black_material and not white_material

        if white_leading:
            attacker_king_square = board.king(chess.WHITE)
            defender_king_square = board.king(chess.BLACK)
        elif black_leading:
            attacker_king_square = board.king(chess.BLACK)
            defender_king_square = board.king(chess.WHITE)
        else:
            return endgame_score

        attacker_king_x, attacker_king_y = chess.square_file(attacker_king_square), chess.square_rank(
            attacker_king_square)
        defender_king_x, defender_king_y = chess.square_file(defender_king_square), chess.square_rank(
            defender_king_square)

        proximity = 16 - (abs(attacker_king_x - defender_king_x) + abs(attacker_king_y - defender_king_y))
        distance_to_center = abs(defender_king_x - 3) + abs(defender_king_y - 4)

        endgame_score += AttackerKingProximityToDefenderKing * proximity
        endgame_score += DistanceBetweenDefenderKingAndMiddle * distance_to_center

        if black_leading:
            endgame_score = -endgame_score

        return endgame_score

    def orderMoves(self, board, moves):
        captures = []
        non_captures = []
        for move in moves:
            if board.is_capture(move):
                captures.append(move)
            else:
                non_captures.append(move)
        return captures + non_captures

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return self.evaluateBoard(board)

        if maximizing_player:
            max_eval = -math.inf
            moves = self.orderMoves(board, list(board.legal_moves))
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            moves = self.orderMoves(board, list(board.legal_moves))
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def getBestMove(self, board, depth):
        best_move = None
        best_value = -math.inf if self.color == chess.WHITE else math.inf
        maximizing_player = (self.color == chess.WHITE)

        for move in board.legal_moves:
            board.push(move)
            board_value = self.minimax(board, depth - 1, -math.inf, math.inf, not maximizing_player)
            board.pop()

            if maximizing_player and board_value > best_value:
                best_value = board_value
                best_move = move
            elif not maximizing_player and board_value < best_value:
                best_value = board_value
                best_move = move

        return best_move

