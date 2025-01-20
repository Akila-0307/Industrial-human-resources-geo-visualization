import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
import seaborn as sns  
import plotly.express as px  
import os
import glob
import re
import streamlit as st  

st.title("Data Analysis Dashboard")
st.sidebar.header("Upload CSV Files")

# Define folder path
folderpath = os.path.join(os.path.dirname(__file__), "DataSets")

# Load all CSV files
csv_files = glob.glob(os.path.join(folderpath, "*.csv"))
dfs = [pd.read_csv(file, encoding='latin1') for file in csv_files]
df = pd.concat(dfs, ignore_index=True)

# Clean data
df = df.apply(lambda col: col.map(lambda x: re.sub(r'[^A-Za-z0-9 ]+', '', str(x)).strip() if isinstance(x, str) else x) if col.dtypes == 'object' else col)

# Clean column names
df.columns = [re.sub(r'[^A-Za-z0-9]+', ' ', col).strip().title() for col in df.columns]

# Save cleaned data
output_file = os.path.join(os.path.dirname(__file__), "cleaned_data.csv")
df.to_csv(output_file, index=False)

# Display data
st.write("First few rows of the dataset:")
st.write(df.head())

st.write("Dataset Information:")
st.text(df.info())

st.write("Missing values in each column:")
st.write(df.isnull().sum())

# Handle missing values
df.fillna(0, inplace=True)

# Convert numeric columns
df['Marginal Workers Total Persons'] = pd.to_numeric(df['Marginal Workers Total Persons'], errors='coerce')
df.rename(columns={'Main Workers - Total - Persons': 'Main Workers Total Persons'}, inplace=True)

st.write("Summary statistics:")
st.write(df.describe())

# **Bar Plot: Male vs Female Workers**
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='India States', y='Marginal Workers Total Males', data=df, label='Males', color='blue', ax=ax)
sns.barplot(x='India States', y='Marginal Workers Total Females', data=df, label='Females', color='pink', ax=ax)
ax.set_xlabel('States')
ax.set_ylabel('Main Workers')
ax.set_title('Main Workers by Gender')
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
ax.legend()
plt.tight_layout()
st.pyplot(fig)  # Display Matplotlib plot

# **Choropleth Map**
fig = px.choropleth(df, 
                    locations='India States',
                    color='Main Workers Total Persons',
                    hover_name='India States',
                    color_continuous_scale='Viridis',
                    title="State-wise Main Workers Distribution")
st.plotly_chart(fig)  # Display Plotly chart

# **Grouped Data**
grouped_data = df.groupby('Division')['Main Workers Total Persons'].sum().reset_index()
st.write("Grouped Data by Division (Total Main Workers):")
st.write(grouped_data)

# **Calculate Gender Ratio**
df['Gender Ratio'] = df['Main Workers Total Persons'] / (df['Main Workers Total Males'] + df['Main Workers Total Females'])
st.write("First few rows with Gender Ratio feature:")
st.write(df[['India States', 'Gender Ratio']].head())

# **Heatmap: Gender Distribution**
gender_data = df[['India States', 'Main Workers Total Males', 'Main Workers Total Females']].set_index('India States')
fig, ax = plt.subplots(figsize=(12,6))
sns.heatmap(gender_data.T, annot=True, cmap='coolwarm', fmt='g', cbar=True, ax=ax)
ax.set_title('Heatmap: Gender Distribution in Main Workers by State')
plt.tight_layout()
st.pyplot(fig)  # Display heatmap
