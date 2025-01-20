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
import streamlit as st  # Import Streamlit

st.title("Data Analysis Dashboard")
st.sidebar.header("Upload CSV Files")

# Define the folder path
folderpath = os.path.join(os.path.dirname(__file__), "DataSets")

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
    name = re.sub(r'[^A-Za-z0-9]+', ' ', name).strip()  # Remove special characters and replace with space
    name = name.replace('_', ' ').replace('-', ' ')  # Replace underscores and hyphens with spaces
    return name.title()  # Capitalize words to make it more readable

# Clean the column names
df_cleaned.columns = [clean_column_names(col) for col in df_cleaned.columns]

# Get the current script directory
current_folder = os.path.dirname(__file__)

# Define the output file path in the same folder as the script
output_file = os.path.join(current_folder, "all_combined_cleaned.csv")

df_cleaned.to_csv(output_file, index=False)
try:
    if os.path.exists(output_file):
        os.remove(output_file)  
except PermissionError:
    st.error(f"PermissionError: The file {output_file} is being used by another process. Please close it and try again.")
    sys.exit()

df_cleaned.to_csv(output_file, index=False)

df = pd.read_csv(output_file)
st.write("First few rows of the dataset:")
st.write(df.head())

st.write("\nDataset information (data types and non-null values):")
st.write(df.info())

st.write("\nMissing values in each column:")
st.write(df.isnull().sum())

df.fillna(0, inplace=True)
st.write('df.columns.tolist()')
st.write(df.columns.tolist())

df['Marginal Workers Total Persons'] = pd.to_numeric(df['Marginal Workers Total Persons'], errors='coerce')
df.columns = df.columns.str.strip()
df.rename(columns={'Main Workers - Total - Persons': 'Main Workers Total Persons'}, inplace=True)

st.write("\nSummary statistics:")
st.write(df.describe())

fig, ax = plt.subplots(figsize=(10,6))
sns.barplot(x='India States', y='Marginal Workers Total Males', data=df, label='Males', color='blue', ax=ax)
sns.barplot(x='India States', y='Marginal Workers Total Females', data=df, label='Females', color='pink', ax=ax)
ax.set_xlabel('States')
ax.set_ylabel('Main Workers')
ax.set_title('Main Workers by Gender')
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
ax.legend()
st.pyplot(fig)

fig = px.choropleth(df, 
                    locations='India States',
                    color='Main Workers Total Persons',
                    hover_name='India States',
                    color_continuous_scale='Viridis',
                    title="State-wise Main Workers Distribution")
st.plotly_chart(fig)

grouped_data = df.groupby('Division')['Main Workers Total Persons'].sum().reset_index()
st.write("\nGrouped data by Division (total main workers):")
st.write(grouped_data)

df['Gender_Ratio'] = df['Main Workers Total Persons'] / (df['Main Workers Total Males'] + df['Main Workers Total Females'])
st.write("\nFirst few rows with the new Gender Ratio feature:")
st.write(df[['India States', 'Gender_Ratio']].head())

df.to_csv('cleaned_data.csv', index=False)

gender_data = df[['India States', 'Main Workers Total Males', 'Main Workers Total Females']].set_index('India States')
fig, ax = plt.subplots(figsize=(12,6))
sns.heatmap(gender_data.T, annot=True, cmap='coolwarm', fmt='g', cbar=True, ax=ax)
ax.set_title('Heatmap: Gender Distribution in Main Workers by State')
st.pyplot(fig)
