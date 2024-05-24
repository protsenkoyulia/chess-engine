import chess

# class for managing game
class GameManager:
    def __init__(self):
        self.board = chess.Board()

    # def makeMove(self, move):
    #     try:
    #         self.board.push(chess.Move.from_uci(move))
    #         return True
    #     except ValueError:
    #         return False

    def getBoard(self):
        return self.board.fen()

    def isCheckmate(self):
        return self.board.is_checkmate()

    def isStalemate(self): # pat
        return self.board.is_stalemate()

    def isInsufficientMaterial(self):
        return self.board.is_insufficient_material()

    def isGameOver(self): # Checkmate or Stalemate or InsufficientMaterial
        return self.board.is_game_over()

    def resetBoard(self):
        self.board.reset()







