import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Step 1: Read Data from JSON File
json_file_path = 'D:/IMPORTANT/OMNET++/omnetpp-6.0.2-windows-x86_64/omnetpp-6.0.2/samples/Excercise2/results/dist_1000_gauss.json'
with open(json_file_path, 'r') as f:
    dist_data = json.load(f)

# Step 2: Extract relevant data for plotting
values = dist_data['General-0-20240424-23:59:12-20812']['vectors'][0]['value'] #for every json fileopen the json file and check the General-0-20.... and change it here

# Step 3: Plot Histogram
plt.hist(values, bins=100, color='skyblue', edgecolor='black')
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.title('Histogram for 1000 events')
'''plt.grid(True)
plt.show()'''
mean_val = np.mean(values)
variance_val = np.var(values)
std_dev_val = np.std(values)
max_x = max(values)
margin = 0.2 * max_x
text_x = max_x - margin
text_y = plt.ylim()[1] * 0.9  # Adjust the y-coordinate as needed

# Add annotations for mean, variance, and standard deviation
plt.text(text_x, text_y, f'Mean: {mean_val:.2f}', fontsize=10, ha='center')
plt.text(text_x, text_y - plt.ylim()[1] * 0.05, f'Variance: {variance_val:.2f}', fontsize=10, ha='center')
plt.text(text_x, text_y - plt.ylim()[1] * 0.1, f'Standard Deviation: {std_dev_val:.2f}', fontsize=10, ha='center')
'''
plt.text(mean_val, plt.ylim()[1]*0.9, f'Mean: {mean_val:.2f}', fontsize=10,ha='left')
plt.text(mean_val, plt.ylim()[1]*0.85, f'Variance: {variance_val:.2f}', fontsize=10, ha='left')
plt.text(mean_val, plt.ylim()[1]*0.8, f'Standard Deviation: {std_dev_val:.2f}', fontsize=10, ha='left')'''
plt.grid(True)
plt.show()

