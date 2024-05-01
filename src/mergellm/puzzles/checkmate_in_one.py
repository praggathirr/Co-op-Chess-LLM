import csv
import json
import re

import requests

from mergellm.llms.gpt3 import GPT3Model
from mergellm.llms.gpt3_chat import GPT3ChatModel
from mergellm.puzzles.llm_convo_checkmate import LLMConversation
from mergellm.puzzles.single_llm_checkmate import LLMCheckmate
from mergellm.stockfish_interface import StockfishInterface

response = requests.get(
    "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/checkmate_in_one/task.json"
)
data = response.json()["examples"]


stockfish = StockfishInterface()
gpt3 = GPT3Model(model="gpt-3.5-turbo-instruct", temperature=0.2)
gpt3_chat = GPT3ChatModel(model="gpt-3.5-turbo-0125", temperature=0.2)

llm_convo = LLMConversation(gpt3, gpt3_chat, stockfish, max_rounds=5)

llm_checkmate = LLMCheckmate(gpt3_chat, stockfish)

correct_moves = 0
total = 0

# Prepare a CSV file to store the results
with open("checkmate_results_mergellm.csv", "w", newline="") as csvfile:
    fieldnames = ["Game", "Winner Move", "LLM Move", "Correct"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i, item in enumerate(data):
        current_state_fen = item["input"]
        correct_move = item["target"].strip()
        # correct_move = re.sub(r"[.+#]", "", correct_move)

        llm_move = llm_convo.discuss_move(current_state_fen)

        print("Correct Move: ", correct_move)
        print("LLM Move: ", llm_move)
        is_correct = False
        if llm_move:
            is_correct = llm_move.lower() == correct_move.lower()
        correct_moves += int(is_correct)
        total += 1

        # Write the result of each game to the CSV file
        writer.writerow(
            {
                "Game": i + 1,
                "Winner Move": correct_move,
                "LLM Move": llm_move,
                "Correct": is_correct,
            }
        )

        print(
            f"Game {i+1}: Correct move - {correct_move}, LLM move - {llm_move}, Correct - {is_correct}"
        )

# Calculate and print the final score
score_percentage = (correct_moves / total) * 100
print(f"The LLMs made the correct checkmate move in {score_percentage}% of the cases.")

# Optionally, you might want to write the final score to the CSV as well.
with open("checkmate_results_mergellm.csv", "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([])
    writer.writerow(["Final Score", f"{correct_moves}/{total}", f"{score_percentage}%"])
