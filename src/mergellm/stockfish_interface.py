"""
Handle interactions with the Stockfish chess engine.
"""

import chess
import chess.engine
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class StockfishInterface:
    def __init__(self, path_to_engine="stockfish/16.1/bin/stockfish"):
        self.engine = chess.engine.SimpleEngine.popen_uci(os.path.join(ROOT_DIR, path_to_engine))
        self.engine.configure({"Skill Level": 1})
        self.board = chess.Board()

    def get_current_fen(self):
        return self.board.fen()

    def make_move(self, move):
        try:
            move = self.board.parse_san(move)
            self.board.push(move)
            self.print_board()
            return True
        except ValueError:
            return False
    
    def print_board(self):
        print("Current board layout:")
        print(self.board) 
    
    def engine_move(self, time_limit=0.1):
        self.engine.configure({"Skill Level": 1})
        if not self.board.is_game_over():
            result = self.engine.play(self.board, chess.engine.Limit(depth=0))
            self.board.push(result.move)
            self.print_board()
    
    def get_top_moves(self, board, num_moves=3):
        self.engine.configure({"Skill Level": 15})
        depth = 20
        mate = 15
        if board.fullmove_number > 20:
            depth=10
            mate = 5 
        if board.fullmove_number > 30:
            depth=5
            mate = 1 
        if not self.board.is_game_over():
            print(depth, mate)
            result = self.engine.analyse(board, chess.engine.Limit(depth=depth, mate=mate), multipv=num_moves)
            top_moves = [info['pv'][0].uci() for info in result]
            self.engine.configure({"Skill Level": 1})
            return top_moves
        return None

    # def __del__(self):
    #     self.engine.quit()
