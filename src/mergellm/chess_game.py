"""
Main Driver File. Initialize the chess game, interface with Stockfish and your LLM models, and manage the flow of the game.
"""

import csv
import json
import time

import chess
import outlines.generate as generate
import outlines.models as models

from mergellm.gpt_huggingface_convo import LLMHuggingfaceConversation
from mergellm.huggingface_chess import get_move_huggingface
from mergellm.llm_convo import LLMConversation
from mergellm.llms.gpt3 import GPT3Model
from mergellm.llms.gpt3_chat import GPT3ChatModel
from mergellm.llms.llama import LLamaModel
from mergellm.llms.mistral import Mistral
from mergellm.single_llm_chess import LLMChess
# from slerp import LLMCombiner
from mergellm.stockfish_interface import StockfishInterface


class ChessGame:
    def __init__(self, white_player="llm", round=6):
        self.stockfish = StockfishInterface()
        self.gpt3 = GPT3Model(model="gpt-3.5-turbo-instruct", temperature=0.3)
        self.gpt3_chat = GPT3ChatModel(model="gpt-3.5-turbo-0125", temperature=0.2)
        # self.mistral = Mistral()
        self.huggingface = models.transformers("mlabonne/chesspythia-70m")
        # self.llama = LLamaModel()
        # self.llm_convo = LLMHuggingfaceConversation(self.gpt3_chat, self.huggingface, self.stockfish, max_rounds=8)
        self.rounds = round
        if white_player == "llm":
            self.llm_convo = LLMHuggingfaceConversation(
                self.gpt3_chat, self.huggingface, self.stockfish, max_rounds=self.rounds
            )
            # self.llm_convo = LLMConversation(self.gpt3_chat, self.gpt3, self.stockfish, max_rounds=self.rounds)
            # self.llm_chess = LLMChess(self.mistral, self.stockfish)
        else:
            self.llm_convo = LLMHuggingfaceConversation(
                self.gpt3_chat,
                self.huggingface,
                self.stockfish,
                max_rounds=self.rounds,
                color="black",
            )
            # self.llm_convo = LLMConversation(self.gpt3_chat, self.gpt3, self.stockfish, max_rounds=self.rounds, color="black")
            # self.llm_chess = LLMChess(self.gpt3_chat, self.stockfish, color="black")
        self.current_game_state = None
        self.white_player = white_player

    def play_game(self):
        self.stockfish.board.reset()
        self.stockfish.print_board()
        move_count = 0
        self.round_usage_count = {i: 0 for i in range(1, self.rounds + 1)}
        while True:
            if self.white_player == "llm":
                self.current_game_state = self.stockfish.get_current_fen()
                suggested_move, round = self.llm_convo.discuss_move(
                    self.current_game_state
                )
                self.round_usage_count[round] += 1
                # get_move_huggingface(self.huggingface, self.stockfish.board)
                # self.llm_convo.discuss_move(self.current_game_state)
                _ = self.stockfish.make_move(suggested_move)
                self.stockfish.engine_move()
                if self.stockfish.board.is_game_over():
                    break

            else:
                self.stockfish.engine_move()
                if self.stockfish.board.is_game_over():
                    break
                self.current_game_state = self.stockfish.get_current_fen()
                suggested_move, round = self.llm_convo.discuss_move(
                    self.current_game_state
                )
                self.round_usage_count[round] += 1
                # get_move_huggingface(self.huggingface, self.stockfish.board)
                # self.llm_convo.discuss_move(self.current_game_state)
                _ = self.stockfish.make_move(suggested_move)

            move_count += 2

            # if not move_successful:
            #     print("Illegal move suggested by LLM.")
            #     continue

        print("Checkmate!")
        print("Total Moves: ", move_count)
        print("Full Move Number: ", self.stockfish.board.fullmove_number)
        self.stockfish.print_board()
        print("Result:", self.stockfish.board.result())
        return self.stockfish.board.result(), self.stockfish.board.fullmove_number


if __name__ == "__main__":
    # game = ChessGame()
    # game.play_game()
    # with open('discussion_rounds_gpt_huggingface.txt', 'w') as f:
    #     f.write(json.dumps(game.round_usage_count))
    # exit()
    # game.generate_regex(game.stockfish.board)
    num_games = 10
    detailed_fieldnames = [
        "Game",
        "Winner",
        "Color",
        "Number of Moves",
        "Game Duration",
    ]
    summary_fieldnames = [
        "LLM Wins (White)",
        "Stockfish Wins (Black)",
        "LLM Wins (Black)",
        "Stockfish Wins (White)",
    ]
    results = {field: 0 for field in summary_fieldnames}
    total_time = 0
    rounds = [5]
    for round_num in rounds:
        with open(
            f"detailed_chess_game_results_round_sf1.csv", "w", newline=""
        ) as file_detailed, open(
            f"chess_game_results_round_sf1.csv", "w", newline=""
        ) as file_summary:
            detailed_writer = csv.DictWriter(
                file_detailed, fieldnames=detailed_fieldnames
            )
            summary_writer = csv.DictWriter(file_summary, fieldnames=summary_fieldnames)

            detailed_writer.writeheader()
            summary_writer.writeheader()
        for i in range(num_games):
            print(f"Game {i}")
            start_time = time.time()

            if i < num_games / 2:
                game = ChessGame(white_player="llm", round=round_num)
                color = "White"
            else:
                game = ChessGame(white_player="stockfish", round=round_num)
                color = "Black"

            result, num_moves = game.play_game()
            game_duration = time.time() - start_time
            total_time += game_duration

            winner = (
                "LLM"
                if (result == "1-0" and color == "White")
                or (result == "0-1" and color == "Black")
                else "Stockfish"
            )
            winner = "LLM" if (result == "1/2-1/2") else winner
            print(f"Winner: {winner}")

            results[f"{winner} Wins ({color})"] += 1

            with open(
                f"detailed_chess_game_results_round_sf1.csv", "a", newline=""
            ) as file_detailed:
                detailed_writer = csv.DictWriter(
                    file_detailed, fieldnames=detailed_fieldnames
                )
                game_detail = {
                    "Game": i + 1,
                    "Winner": winner,
                    "Color": color,
                    "Number of Moves": num_moves,
                    "Game Duration": round(game_duration, 2),
                }
                detailed_writer.writerow(game_detail)

            with open(
                f"chess_game_results_round_sf1.csv", "a", newline=""
            ) as file_summary:
                summary_writer = csv.DictWriter(
                    file_summary, fieldnames=summary_fieldnames
                )
                summary_writer.writerow(results)

    # average_time = total_time / num_games
    # print(f"Average Game Duration: {average_time:.2f} seconds")

    # with open('average_game_duration_huggingface.txt', 'w') as f:
    #     f.write(f"Average Game Duration: {average_time:.2f} seconds")
