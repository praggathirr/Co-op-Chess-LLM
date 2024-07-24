# Co-op LLM: LLMs Working Together to Play Chess

## Abstract
Large language models (LLMs) have demonstrated remarkable capabilities across a range of tasks, from natural language processing to content generation. However, their ability to make strategic game play decisions, in a game like chess, remains an area with a lot of scope for research. In this paper, "Co-op LLM: LLMs Working Together to Play Chess," we aim to explore the integration of two distinct LLMs to challenge state-of-the-art chess AIs. We propose two innovative approaches: first, merging two LLMs using Spherical Linear Interpolation (SLERP) (Fong and Leung, 2022) to create a hybrid model with potentially improved capabilities; and second, facilitating a structured debate or conversation between two LLMs to collaboratively decide on chess moves, given the current state of the board. This research seeks to uncover whether cooperative models can outperform existing AI chess players, thereby opening new avenues for the application of LLMs in strategic reasoning and decision-making.

## Novelty
The novelty in our project comes from:
1. The method of merging two LLMs is relatively very new and experimental. While there exists merged models on Hugging Face (like [Marcoro14-7B-slerp](https://huggingface.co/mlabonne/Marcoro14-7B-slerp)), they have not been used in the context of logical reasoning or chess.
2. Using two LLMs in a debate-style format to work on a common task. Previous work used multiple LLMs working together where each model was assigned a particular role.
3. We do not use sampling or majority voting, but instead force the two models to come to a consensus and converge on a move.
4. Finally, previous work on using LLMs in chess evaluate the performance on just the accuracy and feasibility of a given move. We, on the other hand, will also simulate entire games against a chess AI of varying difficulty levels.

## How to run code
Before you run any code, you must set up a virtual environment and install the necessary libraries in the `requirements.txt` file.
The driver file is found in `src/mergellm/chess_game.py`. In this file, you can set the models to use, whether to play individually or in the conversational setting, as well as other configuration options such as number of games to play. Experimental results can be reproduced using this file. If you want to use GPT 3.5, you will have to include your Open AI API Key in a txt file called `openai_key.txt`. If you want to use a Huggingface model, you will have to login to Huggingface through the CLI (`huggingface-cli`).

To run SLERP, you must first install mergekit as:
```
git clone https://github.com/arcee-ai/mergekit.git
cd mergekit

pip install -e .  # install the package and make scripts available
```
Then, run the following command: `mergekit-yaml config.yaml merge --copy-tokenizer --allow-crimes --out-shard-size 1B --lazy-unpickle`.
