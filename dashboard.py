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

# prompt: elimina las columnas que contengan los valores 0

# Function to drop columns with any zero values
def drop_columns_with_zeros(df):
  # Select columns where no value is zero
  columns_to_keep = df.columns[(df != 0).all()]
  return df[columns_to_keep]

# Assuming 'all_data' is your combined DataFrame as created in the preceding code
if 'all_data' in locals() and isinstance(all_data, pd.DataFrame):
  # Apply the function to the combined DataFrame
  all_data_cleaned = drop_columns_with_zeros(all_data)

  st.write("Combined Data after dropping columns with zeros:")
  st.dataframe(all_data_cleaned)

# If you want to apply this to individual dataframes before concatenating:
# for df_name, df in dfs.items():
#   dfs[df_name] = drop_columns_with_zeros(df)

# Then concatenate the cleaned individual dataframes
# all_data_cleaned_individual = pd.concat(dfs.values(), ignore_index=True)
# st.write("Combined Data from cleaned individual files:")
# st.dataframe(all_data_cleaned_individual)
