import pandas as pd
import numpy as np
import os

if not os.path.exists('data'):
    os.makedirs('data')

num_labs = 25
true_value = 100

data = {
    'Lab ID': [f'Lab {i}' for i in range(1, num_labs + 1)],
    'Sample 1': true_value + np.random.normal(0, 2, num_labs) + np.random.normal(0, 1.5, num_labs),
    'Sample 2': true_value + np.random.normal(0, 2, num_labs) + np.random.normal(0, 1.5, num_labs)
}

df = pd.DataFrame(data)

# Add some precise outliers and proportional bias
df.loc[4, ['Sample 1', 'Sample 2']] = [115, 115]  # Proportional outlier
df.loc[12, ['Sample 1', 'Sample 2']] = [118, 90]  # pure random/scatter outlier
df.loc[20, ['Sample 1', 'Sample 2']] = [85, 87]  # Proportional outlier

df.to_excel('data/dummy.xlsx', index=False, sheet_name='Vitamin D')
print("Created dummy data in data/dummy.xlsx")
