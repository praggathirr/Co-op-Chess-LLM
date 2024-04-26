import chess
import re
import outlines.generate as generate

def get_valid_moves(board: chess.Board) -> str:
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

def get_move_huggingface(llm, board):
    valid_moves = get_valid_moves(board)
    move = generate.regex(llm, valid_moves)("1.")
    return move