"""
Main Driver File. Initialize the chess game, interface with Stockfish and your LLM models, and manage the flow of the game.
"""

from llm_convo import LLMConversation
from llms.gpt3 import GPT3Model
from llms.gpt3_chat import GPT3ChatModel
from llms.llama import LLamaModel
#from slerp import LLMCombiner
from stockfish_interface import StockfishInterface


class ChessGame:
    def __init__(self):
        self.stockfish = StockfishInterface()
        self.gpt3 = GPT3Model(model="gpt-3.5-turbo-instruct", temperature=0.5)
        self.gpt3_2 = GPT3ChatModel(model="gpt-3.5-turbo-0125", temperature=0.2)
        #self.llama = LLamaModel()
        self.llm_convo = LLMConversation(self.gpt3, self.gpt3_2)
        self.current_game_state = None

    def play_game(self):
        continue_game = True
        self.stockfish.print_board()
        while continue_game:
            self.current_game_state = self.stockfish.get_current_fen()

            suggested_move = self.llm_convo.discuss_move(self.current_game_state)

            move_successful = self.stockfish.make_move(suggested_move)

            if not move_successful:
                print("Illegal move suggested by LLM.")
                continue
        
            self.stockfish.engine_move()

            if self.stockfish.board.is_game_over():
                print("Checkmate!")
                print("Result:", self.stockfish.board.result())
                break

if __name__ == "__main__":
    game = ChessGame()
    game.play_game()
