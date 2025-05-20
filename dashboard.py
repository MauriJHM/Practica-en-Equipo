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
