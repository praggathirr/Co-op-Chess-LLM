"""
Manage the conversation between two LLMs to decide on chess moves.
"""
import chess
import re
import random


class LLMConversation:
    def __init__(self, llm1, llm2, chess_engine, max_rounds=5):
        self.llm1 = llm1
        self.llm2 = llm2
        self.engine = chess_engine
        self.max_rounds = max_rounds
        self.init_prompt = (
            "You are a chess grandmaster playing white, and your goal is to play a single move that results in a checkmate. "
            "I will provide the board state using FEN notation. "
            "You must provide a singular checkmate move in standard algebraic notation (SAN) notation. "
            "You will be provided with additional feedback "
            "from another player who will be playing on the same team as you. "
            f"You must come to a conclusion about a move within {max_rounds} rounds of discussion. "
            "You will have one round of discussion at a time.  "
            "You must strictly follow this response structure: "
            "'Final move: <move>'. Do not say anything after 'Final Move' so that your answer can be easily extracted. "
        )

        _ = self.llm1.generate_response(self.init_prompt)
        _ = self.llm2.generate_response(self.init_prompt)

    def discuss_move(self, current_state_fen):
        round = 1
        llm1_move = None
        llm2_move = None

        while round <= self.max_rounds:
            print(round)
            board = chess.Board(current_state_fen)
            # moves_clean = re.sub(r'\d+\.', '', current_state_fen)
            # moves_clean = moves_clean.split()
            # for move_san in moves_clean:
            #     move = board.parse_san(move_san)
            #     board.push(move)
            # fen = board.fen()

            if round == 1:
                llm1_prompt = self._generate_prompt(current_state_fen, "Model 1", round)
                llm2_prompt = self._generate_prompt(current_state_fen, "Model 2", round)
                llm1_move, llm1_response = self.generate_and_validate_move(self.llm1, llm1_prompt, board)
                llm2_move, llm2_response = self.generate_and_validate_move(self.llm2, llm2_prompt, board)

            else:
                llm1_prompt = self._generate_prompt(
                    current_state_fen, "Model 1", round, llm2_response
                )
                llm1_move, llm1_response = self.generate_and_validate_move(self.llm1, llm1_prompt, board)

                llm2_prompt = self._generate_prompt(
                    current_state_fen, "Model 2", round, llm1_response
                )
                llm2_move, llm2_response = self.generate_and_validate_move(self.llm1, llm2_prompt, board)

            print("LLM 1 Prompt: ", llm1_prompt)
            print("LLM 2 Prompt: ", llm2_prompt)
            print("\n")
            print("LLM 1 Response: ", llm1_response)
            print("LLM 2 Response: ", llm2_response)
            print("\n")
            print("LLM 1 Move: ", llm1_move)
            print("LLM 2 Move: ", llm2_move)
            if llm1_move and llm2_move: 
                if llm1_move == llm2_move:
                    return llm1_move
                round += 1
            
            else:
                if round == self.max_rounds:
                    # if not llm1_move and not llm2_move:
                    #     top_moves = self.engine.get_top_moves(board)
                    #     new_prompt = f"Choose the best move from these options: {', '.join(top_moves)}. Simply provide your choice as 'Final move: <move>'."
                    #     llm1_response = self.llm1.generate_response(new_prompt) 
                    #     llm2_response = self.llm2.generate_response(new_prompt)
                    #     llm1_move = llm1_response.split("Final move:")[-1].strip().split()[0].strip()
                    #     llm2_move = llm2_response.split("Final move:")[-1].strip().split()[0].strip()
                    #     print("LLM 1 Response: ", llm1_response)
                    #     print("LLM 2 Response: ", llm2_response)
                    #     print("\n")
                    #     print("LLM 1 Move: ", llm1_move)
                    #     print("LLM 2 Move: ", llm2_move)
                    #     if llm1_move == llm2_move:
                    #         return llm1_move
                    # self.engine.engine.configure({"Skill Level": 15})
                    # best_move = self.engine.play(board, chess.engine.Limit(depth=20)).move.uci()
                    # self.engine.engine.configure({"Skill Level": 0})
                    # return best_move
                    if llm1_move:
                        return llm1_move
                    if llm2_move:
                        return llm2_move
                    return None
                round += 1

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
        attempts = 0
        max_attempts = 5
        prompt_new = None
        valid_moves = self.get_valid_moves(board)
        #valid_moves = self.engine.get_top_moves(board)
        while attempts < max_attempts:
            prompt += f"\n Choose from the following valid moves for the current position on the board {valid_moves}. "
            response = llm.generate_response(prompt)
            move = self._extract_move(response)
            if move: #and self.is_valid_fen_move(board, move):
                return move, response
            prompt_new = prompt + f" The move, {move}, you suggested is an invalid move for the given board state. Review the board and give a valid move. " if not prompt_new else prompt_new
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
            prompt += f"Your teammate suggests '{other_model_resp}'. You may or may not agree with this move. "
            
        prompt += f" Stick to the required response format. This is round {round} of the discussion. The discussion will end after {self.max_rounds} rounds."
        prompt += "The next move must be a checkmate. Provide your move as 'Final move: <move>'. Your move must match SAN format, for example: d3, e1d1, Bxf7+. \n"
        return prompt

    def _extract_move(self, response):
        move = response.split("Final move:")[-1].strip().split()[0].strip()
        move = re.sub(r"[.+#]", "", move)
        #move = re.sub(r"[.]", "", move)
        return move
        pattern = r"Final move:\s*(?:\d+\.\s*)?([a-h1-8][a-h1-8](?:=[QRBN])?[+#]?|[NBRQK][a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?|O-O-O|O-O)[+#]?"
        match = re.search(pattern, response)
        #print(match)
        if match and self.is_valid_fen_move(self.engine.board, match.group(1)):
            return match.group(1)
        return move
