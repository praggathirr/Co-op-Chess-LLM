import re
import chess
import requests


import csv
from mergellm.puzzles.llm_convo_checkmate_multiple import LLMConversation
from mergellm.puzzles.single_llm_checkmate import LLMCheckmate
from mergellm.llms.gpt3 import GPT3Model
from mergellm.llms.gpt3_chat import GPT3ChatModel
from mergellm.stockfish_interface import StockfishInterface
stockfish = StockfishInterface()
gpt3 = GPT3Model(model="gpt-3.5-turbo-instruct", temperature=0.2)
gpt3_chat = GPT3ChatModel(model="gpt-3.5-turbo-0125", temperature=0.2)

llm_convo = LLMConversation(gpt3, gpt3_chat, stockfish, max_rounds=5)

llm_checkmate = LLMCheckmate(gpt3, stockfish)

def is_valid_fen(line):
    return ' ' in line and ('w' in line or 'b' in line) and '/' in line

def read_puzzles_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    content = response.text.split('\n\n')
    puzzles = []
    fen = None
    
    
    for game in content:
        game = game.strip().split('\n')
        for line in game:
            if is_valid_fen(line):
                fen = line
            elif fen and '1.' in line:
                solution = line.split(' ')[1:]
                puzzles.append((fen, ' '.join(solution)))
                fen = None
    return puzzles

# URL to the dataset
url = "https://wtharvey.com/m8n3.txt"
correct_sequences = 0
puzzles = read_puzzles_from_url(url)
total_puzzles = len(puzzles)
print("Total Puzzles: %d" % total_puzzles)

# Function to split the move sequence into a list of moves
def split_solution_sequence(sequence):
    return re.findall(r'[NBRQK]?[a-h1-8]?x?[a-h][1-8](?:=[NBRQK])?[+#]?|[O-O-O|O-O]+', sequence)

# Testing LLMs with puzzles
for i, (fen, solution) in enumerate(puzzles):
    print(f"Processing puzzle {i+1}/{total_puzzles}")
    print(f"FEN: {fen}")
    solution_moves = split_solution_sequence(solution)
    board = chess.Board(fen)
    llm_move_1 = llm_convo.discuss_move(fen)
    llm_move_1 = re.sub(r"[.+#]", "", llm_move_1)
    print(f"Solution: {solution_moves}")

    if llm_move_1 in solution_moves[0]:  # If the first move is correct
        print("First Move Correct")
        board.push_san(llm_move_1)
        board.push_san(solution_moves[1])
        fen = board.fen()
        llm_move_2 = llm_convo.discuss_move(fen)
        llm_move_2 = re.sub(r"[.+#]", "", llm_move_2)

        if llm_move_2 in solution_moves[2]:
            print("Second Move Correct")
            board.push_san(llm_move_2)
            board.push_san(solution_moves[3])
            fen = board.fen()
            llm_move_3 = llm_convo.discuss_move(fen)
            llm_move_3 = re.sub(r"[.+#]", "", llm_move_3)
             
            if llm_move_3 in solution_moves[4]:
                print("Third Move Correct")
                correct_sequences += 1

# Calculate and print the final score
score_percentage = (correct_sequences / total_puzzles) * 100
print(f"GPT 3 Chat correctly solved {correct_sequences}/{total_puzzles} ({score_percentage}%) checkmate-in-two puzzles.")
