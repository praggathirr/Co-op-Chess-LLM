from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


class Mistral:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.2"):
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def generate_response(self, prompt):
        result = self.generator(prompt, max_length=1000, num_return_sequences=1, truncation=True)
        # messages = [
        #     {"role": "user", "content": prompt}
        # ]

        # encodeds = self.tokenizer.apply_chat_template(messages, return_tensors="pt")

        # model_inputs = encodeds

        # generated_ids = self.model.generate(model_inputs, max_new_tokens=1000, do_sample=True)
        # decoded = self.tokenizer.batch_decode(generated_ids)
        # return decoded[0]
        return result[0]["generated_text"].strip()
