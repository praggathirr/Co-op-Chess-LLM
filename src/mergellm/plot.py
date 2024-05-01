import matplotlib.pyplot as plt
import numpy as np

data = {
    "GPT + Finetuned Model": {
        "1": 1,
        "2": 10,
        "3": 15,
        "4": 8,
        "5": 6,
        "6": 6,
        "NC": 25,
    },
    "GPT + Mistral": {"1": 3, "2": 5, "3": 8, "4": 12, "5": 7, "6": 10, "NC": 10},
    "GPT + GPT": {"1": 5, "2": 7, "3": 5, "4": 12, "5": 7, "6": 3, "NC": 8},
}

percent_data = {}
for model, counts in data.items():
    total = sum(counts.values())
    percent_data[model] = {
        round_key: count / total * 100 for round_key, count in counts.items()
    }

rounds = ["1", "2", "3", "4", "5", "6", "NC"]

values1 = [
    percent_data["GPT + Finetuned Model"].get(round_key, 0) for round_key in rounds
]
values2 = [percent_data["GPT + Mistral"].get(round_key, 0) for round_key in rounds]
values3 = [percent_data["GPT + GPT"].get(round_key, 0) for round_key in rounds]

fig, ax = plt.subplots()
bar_width = 0.25
index = np.arange(len(rounds))

bar1 = ax.bar(index, values1, bar_width, label="GPT + Finetuned Model")
bar2 = ax.bar(index + bar_width, values2, bar_width, label="GPT + Mistral")
bar3 = ax.bar(index + 2 * bar_width, values3, bar_width, label="GPT + GPT")

ax.set_xlabel("Rounds")
ax.set_ylabel("Percentage of Consensus Reached")
ax.set_title("Consensus Reached by Round Across Models")
ax.set_xticks(index + bar_width)
ax.set_xticklabels(rounds)
ax.legend()

plt.show()
