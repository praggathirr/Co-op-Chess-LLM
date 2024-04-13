"""
Implementation of SLERP to combine two LLMs.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import mergekit
from huggingface_hub import HfApi, HfFolder, Repository

import yaml


class MergeLLM:
    def __init__(self, model_name1, model_name2):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name1)
        self.model1name = model_name1
        self.model2name = model_name2
        self.model1 = AutoModelForCausalLM.from_pretrained(model_name1)
        self.model2 = AutoModelForCausalLM.from_pretrained(model_name2)

    def slerp_combine(self):
        """Combine two models using SLERP at interpolation factor t"""
        yaml_config = f"""
        slices:
        - sources:
            - model: {self.model1name}
              layer_range: [0, 32]
            - model: {self.model2name}
              layer_range: [0, 32]
        merge_method: slerp
        base_model: {self.model1name}
        parameters:
        t:
            - filter: self_attn
              value: [0, 0.5, 0.3, 0.7, 1]
            - filter: mlp
              value: [1, 0.5, 0.7, 0.3, 0]
            - value: 0.5
        dtype: bfloat16
        """

        with open('config.yaml', 'w', encoding="utf-8") as f:
            f.write(yaml_config)

    def save_merged_model_local(self, merged_model, path="./merged_model"):
        """Save the combined model to a directory"""
        merged_model.save_pretrained(path)

    def push_to_huggingface(self, merged_model, path, organization="MergeLLMSP24"):
        """Save the combined model to the Huggingface Model Hub"""
        # Create a repository in the Hf Hub and get the local path
        api = HfApi()
        token = HfFolder.get_token()
        namespace = organization if organization is not None else api.whoami(token)["name"]
        repo_url = api.create_repo(token, path, organization=organization, exist_ok=True, repo_type="model")
        local_path = f"./{path}"
        repo = Repository(local_path, clone_from=repo_url, use_auth_token=token)

        self.save_merged_model_local(merged_model, local_path)
        merged_model.save_pretrained(local_path)
        self.tokenizer.save_pretrained(local_path)

        repo.push_to_huggingface(commit_message="Upload combined model to Huggingface")

        print(f"Model is available at: https://{namespace}.huggingface.co/{path}")


if __name__ == "__main__":
    chess_model_1 = "EleutherAI/pythia-70m-deduped"
    chess_model_2 = "mlabonne/chesspythia-70m"

    merge = MergeLLM("EleutherAI/pythia-70m-deduped", "mlabonne/chesspythia-70m")

    merged_model = merge.slerp_combine()

    #merge.save_merged_model_local(merged_model, path="./merged_model")
    #merge.push_to_huggingface(merged_model, "MergeLLM")

