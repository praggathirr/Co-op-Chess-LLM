"""
Main Driver File. Initialize the chess game, interface with Stockfish and your LLM models, and manage the flow of the game.
"""

from stockfish import Stockfish
from slerp import LLMCombiner
from llm_convo import LLMConversation
from llms.gpt3 import GPT3Model
from llms.llama import LLamaModel

class ChessGame:
    def __init__(self):
        self.stockfish = Stockfish()
        self.gpt3 = GPT3Model(temperature=0.6)
        self.llama = LLamaModel()
        self.llm_convo = LLMConversation(self.gpt3, self.llama)
        self.current_game_state = None

    def play_game(self):
        continue_game = True
        while continue_game:
            self.current_game_state = self.stockfish.get_current_fen()

            suggested_move = self.llm_convo.discuss_move(self.current_game_state)

            continue_game = self.stockfish.make_move(suggested_move)

            if not continue_game:
                print("Game Over")
                break

if __name__ == "__main__":
    game = ChessGame()
    game.play_game()
