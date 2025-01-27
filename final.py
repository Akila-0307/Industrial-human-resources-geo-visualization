import pandas as pd  
import plotly.express as px  
import os
import glob
import re
import streamlit as st  

st.title("Data Analysis Dashboard")

# Define folder path
folderpath = os.path.join(os.path.dirname(__file__), "DataSets")

# Load CSV files with optimization
csv_files = glob.glob(os.path.join(folderpath, "*.csv"))

if not csv_files:
    st.error("❌ No CSV files found in the 'DataSets' folder!")
    st.stop()

# Read only necessary columns if known
dfs = []
for file in csv_files:
    try:
        df_temp = pd.read_csv(file, encoding='latin1', low_memory=False)
        dfs.append(df_temp)
    except Exception as e:
        st.error(f"❌ Error loading {file}: {e}")

if not dfs:
    st.error("❌ No valid CSV data found!")
    st.stop()

df = pd.concat(dfs, ignore_index=True)

# Convert column names to a cleaner format
df.columns = [re.sub(r'[^A-Za-z0-9]+', ' ', col).strip().title() for col in df.columns]

# Preview dataset
st.write("✅ **First few rows:**")
st.dataframe(df.head(50))  # Show only 50 rows instead of full table

# Memory-efficient column cleaning
string_cols = df.select_dtypes(include=['object']).columns
df[string_cols] = df[string_cols].astype(str).applymap(lambda x: re.sub(r'[^A-Za-z0-9 ]+', '', x).strip())

# Handling missing values
st.write("🔍 **Missing Values per Column:**")
st.write(df.isnull().sum())

df.fillna(0, inplace=True)  # Fill missing values efficiently

# Convert numeric columns safely
numeric_cols = ['Marginal Workers Total Persons', 'Main Workers - Total - Persons']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Rename columns if necessary
if 'Main Workers - Total - Persons' in df.columns:
    df.rename(columns={'Main Workers - Total - Persons': 'Main Workers Total Persons'}, inplace=True)

# Generate summary statistics
st.write("📊 **Summary Statistics:**")
st.write(df.describe().transpose())  # Transpose for better readability

# **Bar Chart: Male vs Female Workers**
try:
    if {'India States', 'Marginal Workers Total Males', 'Marginal Workers Total Females'}.issubset(df.columns):
        bar_fig = px.bar(df.sample(5000),  # Sample only 5000 rows for performance
                         x='India States', 
                         y=['Marginal Workers Total Males', 'Marginal Workers Total Females'], 
                         title="Main Workers by Gender",
                         labels={'value': 'Number of Workers', 'variable': 'Gender'},
                         barmode='group')
        st.plotly_chart(bar_fig)
    else:
        st.warning("⚠️ Required columns for the bar chart are missing!")
except Exception as e:
    st.error(f"❌ Error creating bar chart: {e}")

# **Choropleth Map**
try:
    if {'India States', 'Main Workers Total Persons'}.issubset(df.columns):
        choropleth_fig = px.choropleth(df.sample(5000),  # Sample for performance
                                       locations='India States',
                                       color='Main Workers Total Persons',
                                       hover_name='India States',
                                       color_continuous_scale='Viridis',
                                       title="State-wise Main Workers Distribution")
        st.plotly_chart(choropleth_fig)
    else:
        st.warning("⚠️ Required columns for the choropleth map are missing!")
except Exception as e:
    st.error(f"❌ Error creating choropleth map: {e}")

# **Grouped Data**
try:
    if {'Division', 'Main Workers Total Persons'}.issubset(df.columns):
        grouped_data = df.groupby('Division', as_index=False).agg({'Main Workers Total Persons': 'sum'})
        st.write("✅ **Grouped Data by Division:**")
        st.write(grouped_data)
    else:
        st.warning("⚠️ 'Division' column is missing for grouping!")
except Exception as e:
    st.error(f"❌ Error grouping data: {e}")
