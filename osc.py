import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = "data.csv"  # Replace with the correct filename if needed
df = pd.read_csv(file_path)

# Print the column names to verify
print("Column names:", df.columns.tolist())

# Strip extra spaces in column names (if any)
df.columns = df.columns.str.strip()

# Drop rows with missing values (if any)
df_clean = df.dropna(subset=['Time', 'Amplitude'])

# Extract the values
x = df_clean['Time']
y = df_clean['Amplitude']

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(x, y, label='Amplitude', color='blue')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude (V)')
plt.title('Amplitude vs Time')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
