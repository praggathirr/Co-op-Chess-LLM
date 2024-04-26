import chess
import re
import random


class LLMCheckmate:
    def __init__(self, llm1, chess_engine):
        self.llm1 = llm1
        self.engine = chess_engine
        self.init_prompt = (
            "You are a chess grandmaster playing white, and your goal is to play a single move that results in a checkmate. "
            "I will provide the previous moves made in the game until this point. "
            "You must provide a singular checkmate move in standard algebraic notation (SAN) notation. "
            "You must strictly follow this response structure: "
            "'Final move: <move>'. Do not say anything after 'Final Move' so that your answer can be easily extracted. "
        )

        _ = self.llm1.generate_response(self.init_prompt)

    def get_move(self, current_state_fen):
        round = 1
        llm1_move = None

        board = chess.Board(current_state_fen)
        # moves_clean = re.sub(r'\d+\.', '', current_state_fen)
        # moves_clean = moves_clean.split()
        # for move_san in moves_clean:
        #     move = board.parse_san(move_san)
        #     board.push(move)
        # fen = board.fen()

        
        llm1_prompt = self._generate_prompt(current_state_fen, "Model 1", round)
        llm1_move, llm1_response = self.generate_and_validate_move(self.llm1, llm1_prompt, board)

        print("LLM Prompt: ", llm1_prompt)
        print("\n")
        print("LLM Response: ", llm1_response)
        print("\n")
        print("LLM Move: ", llm1_move)
            
        return llm1_move
    
    def get_valid_moves(self, board: chess.Board) -> str:
        """
        Generate a regex pattern that matches all legal moves for the given board.

        :param board: The chess board

        Based on a script made by 903124:
        https://gist.github.com/903124/cfbefa24da95e2316e0d5e8ef8ed360d # noqa E501
        See in Outlines:
        https://outlines-dev.github.io/outlines/cookbook/models_playing_chess/ # noqa E501

        """
        legal_moves = list(board.legal_moves)
        move_strings = [board.san(move) for move in legal_moves]
        random.shuffle(move_strings)
        #move_strings = [re.sub(r"[+#]", "", move) for move in move_strings]
        regex_pattern = ", ".join(re.escape(move) for move in move_strings)
        return regex_pattern
    
    def generate_and_validate_move(self, llm, prompt, board):
        valid_moves = self.get_valid_moves(board)
        #valid_moves = self.engine.get_top_moves(board)
        
        prompt += f"\n Choose from the following valid moves for the current position on the board {valid_moves}. "
        #prompt += f"\n The current layout of the board is: \n{str(board)} "
        response = llm.generate_response(prompt)
        move = self._extract_move(response)
        if move:
            return move, response

        return None, response
    
    def is_valid_fen_move(self, board, move):
        if move is None:
            return False
        try:
            chess_move = board.parse_san(move)
        except (ValueError, TypeError):
            return False

        # Check if the move is valid in the current board position
        valid = chess_move in board.legal_moves
        return valid

    def _generate_prompt(self, fen, model_name, round, other_model_resp=None):
        prompt = f"Analyze the current board state:\n{fen}\n"
            
        prompt += f" Stick to the required response format. "
        prompt += "The next move must be a checkmate. Provide your move as 'Final move: <move>'. Your move must match SAN format, for example: d3, e1d1, Bxf7+. \n"
        return prompt

    def _extract_move(self, response):
        move = response.split("Final move:")[-1].strip().split()[0].strip()
        move = re.sub(r"[.+#]", "", move)
        return move
        #move = re.sub(r"[.]", "", move)
        #print(move)
        #return move
        pattern = r"Final move:\s*(?:\d+\.\s*)?([a-h1-8][a-h1-8](?:=[QRBN])?[+#]?|[NBRQK][a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?|O-O-O|O-O)[+#]?"
        match = re.search(pattern, response)
        #print(match)
        if match and self.is_valid_fen_move(self.engine.board, match.group(1)):
            return match.group(1)
        return move
