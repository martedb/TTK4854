import csv
from collections import defaultdict

# Input and output file paths
input_file = 'nets.csv'  # Replace with your actual CSV file path
output_file = 'nets_org.csv'  # Desired output file path

# Create a dictionary to hold latitude, longitude and their corresponding weights
location_count = defaultdict(int)

# Read the input CSV and count occurrences of each latitude, longitude pair
with open(input_file, 'r') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        # Check if the row has valid latitude and longitude
        if len(row) < 2 or row[0].strip() == '' or row[1].strip() == '':
            continue  # Skip invalid rows

        try:
            latitude = float(row[0].strip())
            longitude = float(row[1].strip())
            location_count[(latitude, longitude)] += 1
        except ValueError as e:
            print(f"Skipping row due to error: {e} (Row: {row})")
            continue  # Skip rows with invalid latitude or longitude values

# Write the output CSV with latitude, longitude, and weight (duplicates count)
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['latitude', 'longitude', 'weight'])  # Write header
    
    # Write the data rows
    for (latitude, longitude), weight in location_count.items():
        writer.writerow([latitude, longitude, weight])  # Write data rows

print(f"CSV file saved as {output_file}")
