"""
Manage the conversation between two LLMs to decide on chess moves.
"""
import transformers
from transformers import AutoTokenizer
import torch


class LLMConversation:
    def __init__(self, llm1, llm2, max_rounds=5):
        self.llm1 = llm1
        self.llm2 = llm2
        self.max_rounds = max_rounds
        self.init_prompt = f"You are a chess expert who has been playing the game for several years. You are tasked with playing a game of chess against another player. You must beat this player. You will be prompted with a board state and will be required to provide a move. You must provide reasoning for each move as well as the final move based on your reasoning. Structure your response as: 'Reasoning:'  'Final move:' . You may be provided with addtional feedback from another player who will be playing on the same team as you. You can look at their feedback and chose to agree or disagree with them. You must play whatever you think is the best move. You must come to a conclusion about a move within 5 rounds to discussion."
        _ = self.llm1.generate_response(self.init_prompt)
        _ = self.llm2.generate_response(self.init_prompt)


    def discuss_move(self, current_state_fen):
        round = 1
        llm1_move = None
        llm2_move = None

        while round <= self.max_rounds:
            if round == 1:
                llm1_prompt = self._generate_prompt(current_state_fen, "Model 1", round)
                llm2_prompt = self._generate_prompt(current_state_fen, "Model 2", round)
                llm1_response = self.llm1.generate_response(llm1_prompt)
                llm1_move = self._extract_move(llm1_response)
                llm2_response = self.llm2.generate_response(llm2_prompt)
                llm2_move = self._extract_move(llm2_response)

            else:
                llm1_prompt = self._generate_prompt(
                    current_state_fen, "Model 1", round, llm2_response
                )

                llm1_response = self.llm1.generate_response(llm1_prompt)
                llm1_move = self._extract_move(llm1_response)

                llm2_prompt = self._generate_prompt(
                    current_state_fen, "Model 2", round, llm1_move, llm1_response
                )
                llm2_response = self.llm2.generate_response(llm2_prompt)
                llm2_move = self._extract_move(llm2_response)

            if llm1_move == llm2_move:
                break

            round += 1

        final_move = llm1_move
        return final_move

    def _generate_prompt(self, fen, model_name, round, other_model_resp=None):
        prompt = f"Analyze the current board state:\n{fen}\n"

        if other_model_resp:
            prompt += f"Someone suggests {other_model_resp}. Do you agree with this move? If not, what would you suggest? Provide your reasoning. Remember to structure your response as: 'Reasoning:'  'Final move:' "

        prompt += f"Remember, you are discussing this to decide on the best move. This is round {round} of the discussion. You must come to a conclusion about a move within 5 rounds to discussion."

        return prompt

    def _extract_move(self, response):
        move = response.strip().split("Final move")[-1].strip().split()[0].strip()
        return move
