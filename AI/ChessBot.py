import chess
import chess.engine
import math


class ChessBot:
    def __init__(self, board):
        self.board = board

    def evaluateBoard(self, board):
        material_score = self.calculateMaterial(board)
        mobility_score = self.calculateMobility(board)

        total_score = material_score + mobility_score
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


    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return self.evaluateBoard(board)

        if maximizing_player:
            max_eval = -math.inf
            for move in board.legal_moves:
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
            for move in board.legal_moves:
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
        best_value = -math.inf
        for move in board.legal_moves:
            board.push(move)
            board_value = self.minimax(board, depth - 1, -math.inf, math.inf, False)
            board.pop()
            if board_value > best_value:
                best_value = board_value
                best_move = move
        return best_move
