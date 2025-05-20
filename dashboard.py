import streamlit as st
import pandas as pd
import plotly.express as px

# prompt: lee los archivos /content/CAMION M01.xlsx , /content/CAMION M02.xlsx , /content/CAMION M03.xlsx , /content/CAMION M04.xlsx , /content/CAMION M05.xlsx , /content/CAMION M05.xlsx , /content/CAMION M06.xlsx , /content/CAMION M07.xlsx , /content/CAMION M08.xlsx , /content/CAMION M09.xlsx /content/CAMION M10.xlsx /content/CAMION M11.xlsx , /content/CAMION M12.xlsx

import pandas as pd

file_paths = [
    '/content/CAMION M01.xlsx',
    '/content/CAMION M02.xlsx',
    '/content/CAMION M03.xlsx',
    '/content/CAMION M04.xlsx',
    '/content/CAMION M05.xlsx',
    '/content/CAMION M06.xlsx',
    '/content/CAMION M07.xlsx',
    '/content/CAMION M08.xlsx',
    '/content/CAMION M09.xlsx',
    '/content/CAMION M10.xlsx',
    '/content/CAMION M11.xlsx',
    '/content/CAMION M12.xlsx',
]

dataframes = {}

for file_path in file_paths:
    try:
        df = pd.read_excel(file_path)
        # You can store the dataframe in a dictionary using the filename as the key
        file_name = file_path.split('/')[-1].split('.')[0]
        dataframes[file_name] = df
        print(f"Successfully read: {file_path}")
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

# Now you can access each dataframe by its filename, for example:
# df_m01 = dataframes['CAMION M01']
# df_m02 = dataframes['CAMION M02']
# ...

 prompt: elimina las columnas que poseen 0s

# Create a new dictionary to store dataframes with columns containing zeros removed
dataframes_cleaned = {}

# Iterate through the loaded dataframes
for name, df in dataframes.items():
  # Identify columns that contain at least one zero
  cols_with_zeros = (df == 0).any()
  # Get the names of the columns to keep (those that do NOT have any zeros)
  cols_to_keep = cols_with_zeros[~cols_with_zeros].index
  # Create a new dataframe with only the columns to keep
  df_cleaned = df[cols_to_keep]
  # Store the cleaned dataframe in the new dictionary
  dataframes_cleaned[name] = df_cleaned
  print(f"Cleaned dataframe '{name}'. Removed {len(df.columns) - len(df_cleaned.columns)} columns with zeros.")

# Now you can access the cleaned dataframes from dataframes_cleaned

 prompt: muestrame el excel

# To display the contents of the first cleaned dataframe, for example:
if dataframes_cleaned:
  first_df_name = list(dataframes_cleaned.keys())[0]
  print(f"\nDisplaying the first cleaned dataframe: {first_df_name}")
  print(dataframes_cleaned[first_df_name].head()) # Display the first few rows
else:
  print("No dataframes were successfully cleaned and loaded.")

# You can display any other cleaned dataframe by changing the key:
# print(dataframes_cleaned['CAMION M02'].head())
