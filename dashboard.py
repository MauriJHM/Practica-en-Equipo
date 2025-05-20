
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

# prompt: realiza una tabla donde se enseñen los resultados

# We'll create a summary table showing the number of rows and columns for each dataframe.

summary_data = []
for name, df in dataframes.items():
    summary_data.append({
        'File': name,
        'Number of Rows': df.shape[0],
        'Number of Columns': df.shape[1]
    })

summary_df = pd.DataFrame(summary_data)

# Display the summary table
print("Summary of Loaded DataFrames:")
display(summary_df)
