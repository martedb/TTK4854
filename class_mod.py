import pandas as pd

# Load CSV file
input_file = "nets_org.csv"  # Change to your actual file name
output_file = "ghost_nets.csv"

# Define priority function
def assign_priority(weight):
    if weight >= 20:
        return "High"
    elif 10 <= weight < 20:
        return "Medium"
    else:
        return "Low"

# Read the CSV file
data = pd.read_csv(input_file)

# Assign priority levels
data["priority"] = data["weight"].apply(assign_priority)

# Save the updated file
data.to_csv(output_file, index=False)

print(f"Updated CSV with priority saved as {output_file}")
