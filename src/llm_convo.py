"""
Manage the conversation between two LLMs to decide on chess moves.
"""
import chess
import re


class LLMConversation:
    def __init__(self, llm1, llm2, max_rounds=5):
        self.llm1 = llm1
        self.llm2 = llm2
        self.max_rounds = max_rounds
        self.init_prompt = (
            "You are a chess expert that must beat a top-ranked player. You will be prompted with a board state and "
            "will be required to provide a singular move. You must provide reasoning for each move. "
            "Your final move must be in standard algebraic notation (SAN) notation. You may be provided with additional feedback "
            "from another player who will be playing on the same team as you. "
            "You must come to a conclusion about a move within 5 rounds of discussion. "
            "You will have one round of discussion at a time.  "
            "You must strictly follow this response structure: "
            "'Final move: <move>' Do not say anything after 'Final Move' so that your answer can be easily extracted. "
        )

        _ = self.llm1.generate_response(self.init_prompt)
        _ = self.llm2.generate_response(self.init_prompt)

    def discuss_move(self, current_state_fen):
        round = 1
        llm1_move = None
        llm2_move = None

        while round <= self.max_rounds:
            print(round)
            if round == 1:
                llm1_prompt = self._generate_prompt(current_state_fen, "Model 1", round)
                llm2_prompt = self._generate_prompt(current_state_fen, "Model 2", round)
                llm1_prompt_new = None
                while True:
                    llm1_prompt = llm1_prompt_new if llm1_prompt_new else llm1_prompt
                    print("LLM 1 Prompt: ", llm1_prompt)
                    llm1_response = self.llm1.generate_response(llm1_prompt)
                    llm1_move = self._extract_move(llm1_response)
                    if self.is_valid_fen_move(current_state_fen, llm1_move):
                        break
                    else: 
                        llm1_prompt_new = llm1_prompt + f" The move, {llm1_move}, you suggested is an invalid move for the given FEN state. " if not llm1_prompt_new else llm1_prompt_new
                llm2_prompt_new = None
                while True:
                    llm2_prompt = llm2_prompt_new if llm2_prompt_new else llm2_prompt
                    print("LLM 2 Prompt: ", llm2_prompt)
                    llm2_response = self.llm2.generate_response(llm2_prompt)
                    llm2_move = self._extract_move(llm2_response)
                    if self.is_valid_fen_move(current_state_fen, llm2_move):
                        break
                    else: 
                        llm2_prompt_new = llm2_prompt + f" The move, {llm2_move}, you suggested is an invalid move for the given FEN state. " if not llm2_prompt_new else llm2_prompt_new
            else:
                llm1_prompt = self._generate_prompt(
                    current_state_fen, "Model 1", round, llm2_response
                )
                llm1_prompt_new = None
                while True:
                    llm1_prompt = llm1_prompt_new if llm1_prompt_new else llm1_prompt
                    print("LLM 1 Prompt: ", llm1_prompt)
                    llm1_response = self.llm1.generate_response(llm1_prompt)
                    llm1_move = self._extract_move(llm1_response)
                    if self.is_valid_fen_move(current_state_fen, llm1_move):
                        break
                    else: 
                        llm1_prompt_new = llm1_prompt + f" The move, {llm1_move}, you suggested is an invalid move for the given FEN state. " if not llm1_prompt_new else llm1_prompt_new

                llm2_prompt = self._generate_prompt(
                    current_state_fen, "Model 2", round, llm1_response
                )
                llm2_prompt_new = None
                while True:
                    llm2_prompt = llm2_prompt_new if llm2_prompt_new else llm2_prompt
                    print("LLM 2 Prompt: ", llm2_prompt)
                    llm2_response = self.llm2.generate_response(llm2_prompt)
                    llm2_move = self._extract_move(llm2_response)
                    if self.is_valid_fen_move(current_state_fen, llm2_move):
                        break
                    else: 
                        llm2_prompt_new = llm2_prompt + f" The move, {llm2_move}, you suggested is an invalid move for the given FEN state. " if not llm2_prompt_new else llm2_prompt_new
                

            print("LLM 2 Prompt: ", llm2_prompt)
            print("\n")
            print("LLM 1 Response: ", llm1_response)
            print("LLM 2 Response: ", llm2_response)
            print("\n")
            print("LLM 1 Move: ", llm1_move)
            print("LLM 2 Move: ", llm2_move)
            if llm1_move == llm2_move:
                break

            round += 1

        final_move = llm1_move
        return final_move
    
    def is_valid_fen_move(self, fen, move):
        if move is None:
            return False
        print("MOVE:  ", move)
        board = chess.Board(fen)
        try:
            chess_move = board.parse_san(move)
        except (ValueError, TypeError):
            return False

        # Check if the move is valid in the current board position
        valid = chess_move in board.legal_moves
        print(valid)
        return valid

    def _generate_prompt(self, fen, model_name, round, other_model_resp=None):
        prompt = f"Analyze the current board state:\n{fen}\n"
        if other_model_resp:
            prompt += f"Your teammate suggests '{other_model_resp}'. Do you agree with this move? If not, what would you suggest? Provide your reasoning followed by 'Final move: <move>'."
        else:
            prompt += "Provide your reasoning followed by 'Final move: <move>'."

        prompt += f" Stick to the required response format. This is round {round} of the discussion."
        return prompt

    def _extract_move(self, response):
        move = response.split("Final move:")[-1].strip().split()[0].strip()
        print(move)
        # return move
        pattern = r"Final move: (\S+)"
        match = re.search(pattern, response)
        if match:
            return match.group(1)
        print(match)
        return move
