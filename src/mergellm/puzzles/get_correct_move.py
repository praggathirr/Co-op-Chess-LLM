import pandas as pd

# Replace 'your_file.csv' with the path to your CSV file
df = pd.read_csv('./checkmate_results.csv')
df['Correct'] = df['Correct'].astype(bool)
percentage_true = (df['Correct'].sum() / len(df['Correct'])) * 100
print(f"Percentage of True values: {percentage_true:.2f}%")

