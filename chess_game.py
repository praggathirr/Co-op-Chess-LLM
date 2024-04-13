"""
Main Driver File. Initialize the chess game, interface with Stockfish and your LLM models, and manage the flow of the game.
"""

from stockfish import Stockfish
from slerp import LLMCombiner
from llm_convo import LLMConversation

class ChessGame:
    def __init__(self):
        self.stockfish = StockfishInterface()
        self.llm_combiner = LLMSlerp()
        self.llm_convo = LLMConversation()
        self.current_game_state = None

    def play_game(self):
        continue_game = True
        while continue_game:
            self.current_game_state = self.stockfish.get_current_fen()

            suggested_move = self.llm_convo.decide_move(self.current_game_state)

            continue_game = self.stockfish.make_move(suggested_move)

            if not continue_game:
                print("Game Over")
                break

if __name__ == "__main__":
    game = ChessGame()
    game.play_game()
