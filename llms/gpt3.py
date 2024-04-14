import openai
import time
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class GPT3Model:
    def __init__(self, model, temperature):
        with open(os.path.join(ROOT_DIR, 'openai_key.txt'), 'r') as f:
            key = f.readline().strip()
            openai.api_key = key
        self.model = model
        self.temperature = temperature

    def generate_response(self, prompt):
        response = None
        received = False
        while not received:
            try:
                response = openai.Completion.create(engine=self.model, prompt=prompt, temperature=self.temperature, stop=None, n=1)
                received = True
            except:
                error = sys.exc_info()[0]
                if error == openai.error.InvalidRequestError: # something is wrong: e.g. prompt too long
                    print(f"InvalidRequestError\nPrompt passed in:\n\n{prompt}\n\n")
                    assert False

                print("API error:", error)
                time.sleep(1)
        return response
