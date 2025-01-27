import pandas as pd  
import numpy as np  
import plotly.express as px  
import os
import glob
import re
import streamlit as st  
import io  # For handling df.info() output

st.title("Data Analysis Dashboard")

# Define folder path
folderpath = os.path.join(os.path.dirname(__file__), "DataSets")

# Load all CSV files efficiently
csv_files = glob.glob(os.path.join(folderpath, "*.csv"))
dfs = [pd.read_csv(file, encoding='latin1', usecols=lambda col: col not in ['UnnecessaryColumn']) for file in csv_files]  # Adjust usecols as needed
df = pd.concat(dfs, ignore_index=True)

# Clean data efficiently
df.replace({r'[^A-Za-z0-9 ]+': ''}, regex=True, inplace=True)

# Clean column names
df.columns = [re.sub(r'[^A-Za-z0-9]+', ' ', col).strip().title() for col in df.columns]

# Save cleaned data (optional)
output_file = os.path.join(os.path.dirname(__file__), "cleaned_data.csv")
df.to_csv(output_file, index=False)

# Display data in Streamlit
st.write("First few rows of the dataset:")
st.write(df.head())

# Display dataset info properly
buffer = io.StringIO()
df.info(buf=buffer)
st.text(buffer.getvalue())

# Display missing values
st.write("Missing values in each column:")
st.write(df.isnull().sum())

# Handle missing values
df.fillna(0, inplace=True)

# Convert numeric columns safely
if 'Marginal Workers Total Persons' in df.columns:
    df['Marginal Workers Total Persons'] = pd.to_numeric(df['Marginal Workers Total Persons'], errors='coerce')

if 'Main Workers - Total - Persons' in df.columns:
    df.rename(columns={'Main Workers - Total - Persons': 'Main Workers Total Persons'}, inplace=True)

# Summary statistics
st.write("Summary statistics:")
st.write(df.describe())

# **Bar Plot: Male vs Female Workers** (Using Plotly instead of Matplotlib for better performance)
if 'India States' in df.columns and 'Marginal Workers Total Males' in df.columns and 'Marginal Workers Total Females' in df.columns:
    bar_fig = px.bar(df, 
                     x='India States', 
                     y=['Marginal Workers Total Males', 'Marginal Workers Total Females'], 
                     title="Main Workers by Gender",
                     labels={'value': 'Number of Workers', 'variable': 'Gender'},
                     barmode='group',
                     color_discrete_map={'Marginal Workers Total Males': 'blue', 'Marginal Workers Total Females': 'pink'})
    st.plotly_chart(bar_fig)

# **Choropleth Map**
if 'India States' in df.columns and 'Main Workers Total Persons' in df.columns:
    choropleth_fig = px.choropleth(df, 
                                   locations='India States',
                                   color='Main Workers Total Persons',
                                   hover_name='India States',
                                   color_continuous_scale='Viridis',
                                   title="State-wise Main Workers Distribution")
    st.plotly_chart(choropleth_fig)

# **Grouped Data**
if 'Division' in df.columns and 'Main Workers Total Persons' in df.columns:
    grouped_data = df.groupby('Division', as_index=False).agg({'Main Workers Total Persons': 'sum'})
    st.write("Grouped Data by Division (Total Main Workers):")
    st.write(grouped_data)

# **Calculate Gender Ratio**
if 'Main Workers Total Persons' in df.columns and 'Main Workers Total Males' in df.columns and 'Main Workers Total Females' in df.columns:
    df['Gender Ratio'] = df['Main Workers Total Persons'] / (df['Main Workers Total Males'] + df['Main Workers Total Females'])
    st.write("First few rows with Gender Ratio feature:")
    st.write(df[['India States', 'Gender Ratio']].head())

# **Heatmap: Gender Distribution** (Using Plotly for performance)
if 'India States' in df.columns and 'Main Workers Total Males' in df.columns and 'Main Workers Total Females' in df.columns:
    heatmap_fig = px.imshow(df[['Main Workers Total Males', 'Main Workers Total Females']].T, 
                            labels=dict(x="States", y="Gender", color="Count"),
                            x=df['India States'], 
                            y=['Males', 'Females'],
                            color_continuous_scale='coolwarm',
                            title="Heatmap: Gender Distribution in Main Workers by State")
    st.plotly_chart(heatmap_fig)
