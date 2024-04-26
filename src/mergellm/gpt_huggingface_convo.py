"""
Manage the conversation between two LLMs to decide on chess moves.
"""
import chess
import re
import outlines.generate as generate



class LLMHuggingfaceConversation:
    def __init__(self, gpt, huggingface, chess_engine, max_rounds=5, color="white"):
        self.gpt = gpt
        self.huggingface = huggingface
        self.engine = chess_engine
        self.max_rounds = max_rounds
        self.init_prompt = (
            f"You are a chess grandmaster of ELO Rating 1800 playing {color}, and your goal is to win with as few moves as possible. "
            "I will provide the current board state and you"
            "must provide the best move in standard algebraic notation notation. You must provide reasoning for each move. "
            "You will be provided with additional feedback "
            "from another player who will be playing on the same team as you. "
            f"You must come to a conclusion about a move within {max_rounds} rounds of discussion. "
            "You must strictly follow this response structure: "
            "'Final move: <move>'. Do not say anything after 'Final Move' so that your answer can be easily extracted. "
        )

        _ = self.gpt.generate_response(self.init_prompt)

    def discuss_move(self, current_state_fen):
        round = 1
        gpt_move = None
        huggingface_move = None

        while round <= self.max_rounds:
            print(round)
            board = chess.Board(current_state_fen)

            if round == 1:
                gpt_prompt = self._generate_prompt(current_state_fen, "Model 1", round)
                gpt_move, gpt_response = self.generate_and_validate_move(self.gpt, gpt_prompt, board)
                huggingface_move = self.get_move_huggingface(self.huggingface, board)

            else:
                gpt_prompt = self._generate_prompt(
                    current_state_fen, "Model 1", round, huggingface_move
                )
                gpt_move, gpt_response = self.generate_and_validate_move(self.gpt, gpt_prompt, board)
            
                huggingface_move = self.get_move_huggingface(self.huggingface, board)
   
            print("GPT Prompt: ", gpt_prompt)
            print("GPT Response: ", gpt_response)
            print("GPT Move: ", gpt_move)
            print("Huggingface Move: ", huggingface_move)
            if gpt_move and huggingface_move: 
                if gpt_move == huggingface_move or huggingface_move in gpt_move:
                    return gpt_move, round
                round += 1
            
            # else:
            #     # if round == self.max_rounds:
            #     #     if not gpt_move and not huggingface_move:
            #     #         top_moves = self.engine.get_top_moves(board)
            #     #         new_prompt = f"Choose the best move from these options: {', '.join(top_moves)}. Simply provide your choice as 'Final move: <move>'."
            #     #         gpt_response = self.gpt.generate_response(new_prompt) 
            #     #         huggingface_response = self.huggingface.generate_response(new_prompt)
            #     #         gpt_move = gpt_response.split("Final move:")[-1].strip().split()[0].strip()
            #     #         huggingface_move = huggingface_response.split("Final move:")[-1].strip().split()[0].strip()
            #     #         print("GPT Response: ", gpt_response)
            #     #         print("Huggingface Response: ", huggingface_response)
            #     #         print("\n")
            #     #         print("GPT Move: ", gpt_move)
            #     #         print("Huggingface Move: ", huggingface_move)
            #     #         if gpt_move == huggingface_move:
            #     #             return gpt_move
            #         if gpt_move:
            #             return gpt_move
            #         if huggingface_move:
            #             return huggingface_move
            #     round += 1

        if gpt_move:
            return gpt_move, round-1
        if huggingface_move:
            return huggingface_move, round-1
        return gpt_move, round-1
    
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
        move_strings = [re.sub(r"[+#]", "", move) for move in move_strings]
        regex_pattern = "|".join(re.escape(move) for move in move_strings)
        return regex_pattern

    def get_move_huggingface(self, llm, board):
        valid_moves = self.get_valid_moves(board)
        move = generate.regex(llm, valid_moves)("1.")
        return move
        
    
    def generate_and_validate_move(self, llm, prompt, board):
        attempts = 0
        max_attempts = 5
        prompt_new = None
        #valid_moves = self.get_valid_moves(board)
        valid_moves = self.engine.get_top_moves(board)
        while attempts < max_attempts:
            prompt += f"\n Choose from the following valid moves for the current position on the board {valid_moves}. "
            prompt += f"\n The current layout of the board is: \n{str(board)}\n The uppercase letters represent white and the lowercase letters represent black. "
            response = llm.generate_response(prompt)
            move = self._extract_move(response)
            if move and self.is_valid_fen_move(board, move):
                return move, response
            prompt_new = prompt + f" The move, {move}, you suggested is an invalid move for the given FEN board state. Review the board and give a valid move. " if not prompt_new else prompt_new
            attempts += 1
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
        if other_model_resp:
            prompt += f"Your teammate suggests the move '{other_model_resp}'. "
            
        prompt += f"This is round {round} of the discussion. The discussion will end after {self.max_rounds} rounds."
        prompt += "Provide your reasoning followed by 'Final move: <move>'. Your move must match SAN format, for example: d3, e1d1, Bxf7+. \n"
        return prompt

    def _extract_move(self, response):
        move = response.split("Final move:")[-1].strip().split()[0].strip()
        move = re.sub(r"[.]", "", move)
        #print(move)
        #return move
        pattern = r"Final move:\s*(?:\d+\.\s*)?([a-h1-8][a-h1-8](?:=[QRBN])?[+#]?|[NBRQK][a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?|O-O-O|O-O)[+#]?"
        match = re.search(pattern, response)
        #print(match)
        if match and self.is_valid_fen_move(self.engine.board, match.group(1)):
            return match.group(1)
        return move
