import pandas as pd  # For data manipulation
import numpy as np  # For numerical operations
import matplotlib.pyplot as plt  # For basic plotting
import seaborn as sns  # For statistical visualizations
import plotly.express as px  # For interactive plotting
import glob
import os
import sys
import pprint
import re

# Define the folder path
folderpath = "C:\\Users\\DELL\\Downloads\\DataSetsNew\\DataSets"

# Use glob to find all CSV files in the folder
csv_files = glob.glob(os.path.join(folderpath, "*.csv"))

# Read and concatenate all CSV files into a single DataFrame
dfs = [pd.read_csv(file, encoding='latin1') for file in csv_files]
inputfile = pd.concat(dfs, ignore_index=True)

# Clean data: Remove commas, backticks, and whitespace only for string columns
df_cleaned = inputfile.apply(lambda col: col.map(lambda x: str(x).replace(",", "").replace("`", "").strip() if isinstance(x, str) else x) if col.dtypes == 'object' else col)

# Function to clean values inside columns (for your existing logic)
def clean_column_values(x):
    if isinstance(x, str):
        # Remove commas, backticks, and extra whitespace
        x = x.replace(",", "").replace("`", "").strip()
        # Remove any special characters except for spaces
        x = re.sub(r'[^A-Za-z0-9 ]+', '', x)
    return x

# Apply the cleaning function to the entire DataFrame
df_cleaned = inputfile.apply(lambda col: col.map(lambda x: str(x).replace(",", "").replace("`", "").strip() if isinstance(x, str) else x) if col.dtypes == 'object' else col)


# Function to clean column names to make them readable
def clean_column_names(name):
    # Replace non-alphanumeric characters with space and capitalize words
    name = re.sub(r'[^A-Za-z0-9]+', ' ', name).strip()  # Remove special characters and replace with space
    name = name.replace('_', ' ').replace('-', ' ')  # Replace underscores and hyphens with spaces
    return name.title()  # Capitalize words to make it more readable

# Clean the column names
df_cleaned.columns = [clean_column_names(col) for col in df_cleaned.columns]


# Save the cleaned DataFrame to a new CSV file
output_file = "C:\\Users\\DELL\\Downloads\\DataSetsNew\\all_combined_cleaned.csv"
try:
    if os.path.exists(output_file):
        os.remove(output_file)  
        # Remove the file if it already exists
except PermissionError:
    print(f"PermissionError: The file {output_file} is beAing used by another process. Please close it and try again.")
    sys.exit()

df_cleaned.to_csv(output_file, index=False)

# Step 3: Load the dataset
# Replace 'data.csv' with the path to your actual dataset file
df = pd.read_csv(output_file)

#Step 4: Inspecting the first few rows of the data
print("First few rows of the dataset:")
print(df.head())

# Step 5: Check the general structure of the dataset (columns, data types, etc.)
print("\nDataset information (data types and non-null values):")
df.info()

print("\nMissing values in each column:")
print(df.isnull().sum())

#Step 7: Clean the data - Handle missing values by filling them with 0 (or handle differently if needed)
df.fillna(0, inplace=True)  # Replacing missing values with 0 (you can use different strategies here)

print('df.columns.tolist()')
print(df.columns.tolist())

# Step 8: Ensure correct data types - Convert necessary columns to numeric if they are not already
df['Marginal Workers Total Persons'] = pd.to_numeric(df['Marginal Workers Total Persons'], errors='coerce')

# Step 9: Check column names and clean them (remove extra spaces if any)
df.columns = df.columns.str.strip()  # Remove extra spaces from column names

# Step 10: Rename columns for readability (optional)
df.rename(columns={'Main Workers - Total - Persons': 'Main Workers Total Persons'}, inplace=True)

# Step 11: Check basic summary statistics for numerical columns
print("\nSummary statistics (describe):")
print(df.describe())

# Step 12: Data visualization - Bar plot of Main Workers by Males vs Females across States
plt.figure(figsize=(10,6))
sns.barplot(x='India States', y='Marginal Workers Total Males', data=df, label='Males', color='blue')
sns.barplot(x='India States', y='Marginal Workers Total Females', data=df, label='Females', color='pink')

# Adding labels and title
plt.xlabel('States')
plt.ylabel('Main Workers')
plt.title('Main Workers by Gender')
plt.xticks(rotation=90)
plt.legend()
plt.show()

# Step 13: Visualizing state-wise distribution of main workers using Plotly (interactive map)
fig = px.choropleth(df, 
                    locations='India States',  # Column with state names
                    color='Main Workers Total Persons',  # Column to use for color scale
                    hover_name='India States',  # Information to show when hovering over a state
                    color_continuous_scale='Viridis',  # Color scale for the map
                    title="State-wise Main Workers Distribution")  # Title for the map
fig.show()

# Step 14: Grouping data by Division and calculating total number of main workers per division
grouped_data = df.groupby('Division')['Main Workers Total Persons'].sum().reset_index()

# Display the grouped data
print("\nGrouped data by Division (total main workers):")
print(grouped_data)

# Step 15: Feature Engineering - Adding a new feature for Gender Ratio (Males to Total Workers)
df['Gender_Ratio'] = df['Main Workers Total Persons'] / (df['Main Workers Total Males'] + df['Main Workers Total Females'])

# Display the new Gender Ratio feature for the first few rows
print("\nFirst few rows with the new Gender Ratio feature:")
print(df[['India States', 'Gender_Ratio']].head())

# Step 16: Save the cleaned and processed dataset to a new CSV file
#df.to_csv('cleaned_data.csv', index=False)

# #Step 17: Bonus Visualization - A Heatmap of Gender Distribution in Main Workers
# # A heatmap for visualizing gender differences across states (Main Workers)
# gender_data = df[['India States', 'Main Workers Total Males', 'Main Workers Total Females']].set_index('India States')
# plt.figure(figsize=(12,6))
# sns.heatmap(gender_data.T, annot=True, cmap='coolwarm', fmt='g', cbar=True)
# plt.title('Heatmap: Gender Distribution in Main Workers by State')
# plt.show()