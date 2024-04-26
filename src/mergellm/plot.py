import numpy as np
import matplotlib.pyplot as plt

# Function to check the largest power of 2 that divides k
def f(k):
    power_of_2 = 1
    while k % 2 == 0 and k > 0:
        k = k // 2
        power_of_2 *= 2
    return power_of_2

# Summing up the function and computing the amortized cost for each n
def compute_amortized_costs(N):
    total_cost = 0
    amortized_costs = []
    for k in range(1, N + 1):
        total_cost += f(k)
        amortized_costs.append(total_cost / k)
    return amortized_costs

# Let's compute the amortized costs for n up to 1000
N = 1000
amortized_costs = compute_amortized_costs(N)
n_values = np.arange(1, N + 1)

# Plotting the amortized cost over n
plt.figure(figsize=(10, 6))
plt.plot(n_values, amortized_costs, label='Amortized Cost of f(k)')
plt.xlabel('n (number of operations)')
plt.ylabel('Amortized Cost')
plt.title('Amortized Cost of f(k) Over n Operations')
plt.legend()
plt.grid(True)
plt.show()
