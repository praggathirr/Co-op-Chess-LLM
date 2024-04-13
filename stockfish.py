"""
Handle interactions with the Stockfish chess engine.
"""

import chess
import chess.engine

class Stockfish:
    def __init__(self, path_to_engine='path/to/stockfish'):
        self.engine = chess.engine.SimpleEngine.popen_uci(path_to_engine)
        self.board = chess.Board()

    def get_current_fen(self):
        return self.board.fen()

    def make_move(self, move):
        try:
            move = self.board.parse_san(move)
            self.board.push(move)
            return True
        except ValueError:
            return False

    def __del__(self):
        self.engine.quit()
