from transformers import LlamaTokenizer, LlamaForCausalLM, pipeline


class LLamaModel:
    def __init__(self, model_name="openlm-research/open_llama_3b"):
        tokenizer = LlamaTokenizer.from_pretrained(model_name)
        model = LlamaForCausalLM.from_pretrained(model_name)
        self.generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

    def generate_response(self, prompt):
        result = self.generator(prompt, max_length=1000, num_return_sequences=1, truncation=True)
        return result[0]["generated_text"].strip()
