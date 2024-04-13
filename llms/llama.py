from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

class LLamaModel:
    def __init__(self, model_name):
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        self.generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

    def generate_response(self, prompt):
        result = self.generator(prompt, max_length=150, num_return_sequences=1)
        return result[0]['generated_text'].strip()
