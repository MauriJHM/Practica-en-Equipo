# prompt: lee los archivos /content/CAMION M01.xlsx , /content/CAMION M02.xlsx , /content/CAMION M03.xlsx , /content/CAMION M04.xlsx , /content/CAMION M05.xlsx , /content/CAMION M06.xlsx , /content/CAMION M07.xlsx , /content/CAMION M08.xlsx , /content/CAMION M09.xlsx /content/CAMION M10.xlsx /content/CAMION M11.xlsx , /content/CAMION M12.xlsx  para streamlit

import pandas as pd
import streamlit as st

# List of file paths
file_paths = [
    'CAMION M01.xlsx',
    'CAMION M02.xlsx',
    'CAMION M03.xlsx',
    'CAMION M04.xlsx',
    'CAMION M05.xlsx',
    'CAMION M06.xlsx',
    'CAMION M07.xlsx',
    'CAMION M08.xlsx',
    'CAMION M09.xlsx',
    'CAMION M10.xlsx',
    'CAMION M11.xlsx',
    'CAMION M12.xlsx',
]

# Dictionary to store dataframes
dfs = {}

# Read each Excel file into a pandas DataFrame
for file_path in file_paths:
    try:
        df_name = file_path.split('/')[-1].replace('.xlsx', '')
        dfs[df_name] = pd.read_excel(file_path)
        st.write(f"Successfully loaded {file_path}")
    except FileNotFoundError:
        st.error(f"Error: File not found at {file_path}")
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")

# Now you can access the dataframes using the dictionary 'dfs'
# For example, to display the first dataframe:
if 'CAMION M01' in dfs:
    st.write("Contents of CAMION M01.xlsx:")
    st.dataframe(dfs['CAMION M01'])

# You can perform operations on the loaded dataframes here
# For example, concatenate them:
all_data = pd.concat(dfs.values(), ignore_index=True)
st.write("Combined Data from all files:")
st.dataframe(all_data)

# prompt: elimina los valores 0

# Eliminate rows where the value in a specific column is 0
# Assuming you want to remove rows where a column named 'ColumnName' has a value of 0
# Replace 'ColumnName' with the actual name of the column you want to check
column_to_check = 'CONSUMO (Lts.)' # Replace with the actual column name

# Filter out rows where the specified column has a value of 0 for each dataframe
for df_name, df in dfs.items():
    if column_to_check in df.columns:
        dfs[df_name] = df[df[column_to_check] != 0]
        st.write(f"Removed rows with 0 in '{column_to_check}' from {df_name}")
    else:
        st.warning(f"Column '{column_to_check}' not found in {df_name}")

# Re-concatenate the dataframes after removing zeros
all_data_no_zeros = pd.concat(dfs.values(), ignore_index=True)
st.write("Combined Data after removing rows with 0 in 'CONSUMO (Lts.)':")
st.dataframe(all_data_no_zeros)
