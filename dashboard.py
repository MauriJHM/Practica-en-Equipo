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
# prompt: En cada dataframe agrega una columna al inicio con el nombre del archivo en el que esta como por ejemplo "CAMION M01"

# Add a column with the file name to each dataframe
for df_name, df in dfs.items():
  df.insert(0, 'Nombre Archivo', df_name)

# You can re-concatenate them after adding the column if needed
all_data_with_filename = pd.concat(dfs.values(), ignore_index=True)
st.write("Combined Data from all files with added column:")
st.dataframe(all_data_with_filename)

# prompt: Elimina las columnas SD, ST, BD, BT, AD, AT, BLD, BLT, Vel. Max., Cred. Adu, Cred. Est, Cred. Disc, Cred. Gral

columns_to_drop = [
    'SD', 'ST', 'BD', 'BT', 'AD', 'AT', 'BLD', 'BLT', 'Vel. Max.',
    'Cred. Adu', 'Cred. Est', 'Cred. Disc', 'Cred. Gral'
]

for df_name, df in dfs.items():
  # Check if columns exist before dropping
  cols_to_drop_existing = [col for col in columns_to_drop if col in df.columns]
  if cols_to_drop_existing:
    dfs[df_name] = df.drop(columns=cols_to_drop_existing)
    st.write(f"Dropped columns {cols_to_drop_existing} from {df_name}")
  else:
    st.write(f"None of the specified columns to drop were found in {df_name}")



# Re-concatenate the dataframes after dropping columns
all_data_after_drop = pd.concat(dfs.values(), ignore_index=True)
st.write("Combined Data from all files after dropping columns:")
st.dataframe(all_data_after_drop)

# prompt: Elimina las letras de la Columna Hora y deja solo los numeros y los signos de puntuacion

# Assuming 'all_data_after_drop' is your combined DataFrame
# Apply a regular expression to remove letters from the 'Hora' column
all_data_after_drop['Hora'] = all_data_after_drop['Hora'].astype(str).str.replace(r'[a-zA-Z]', '', regex=True)

# Display the updated dataframe
st.write("Combined Data after removing letters from 'Hora' column:")
st.dataframe(all_data_after_drop)

# prompt: Agrega al final la columna "Promedio Inicio de Ruta" y despues usando la columna hora, saca el promedio de cada hora inicial del dia transformado la columna Horas a segundos para cada apartado de la Columna "Nombre Archivo"

# Function to convert 'HH:MM:SS' time string to seconds
def time_to_seconds(time_str):
    if pd.isna(time_str):
        return None
    try:
        # Handle potential whitespace and split by colon
        parts = str(time_str).strip().split(':')
        # Ensure there are at least 3 parts for HH:MM:SS format
        if len(parts) >= 3:
            h, m, s = map(int, parts[:3])
            return h * 3600 + m * 60 + s
        elif len(parts) == 2: # Handle HH:MM format if necessary
             h, m = map(int, parts[:2])
             return h * 3600 + m * 60
        else:
            return None # Or handle other formats/errors
    except ValueError:
        return None # Handle cases where conversion to int fails

# Apply the conversion function to the 'Hora' column to create 'Hora_segundos'
all_data_after_drop['Hora_segundos'] = all_data_after_drop['Hora'].apply(time_to_seconds)

# Calculate the average of 'Hora_segundos' for each 'Nombre Archivo'
average_start_time_seconds = all_data_after_drop.groupby('Nombre Archivo')['Hora_segundos'].mean().reset_index()

# Rename the column to "Promedio Inicio de Ruta"
average_start_time_seconds.rename(columns={'Hora_segundos': 'Promedio Inicio de Ruta'}, inplace=True)

# Merge the average start time back to the original combined dataframe if needed,
# or you can display the average start time separately.
# For this task, we will add it as a new column to a summary DataFrame
# showing the average for each file.

# Display the average start times per file
st.write("Average Start Time (in seconds) per File:")
st.dataframe(average_start_time_seconds)

# You can convert the average seconds back to HH:MM:SS format for better readability
def seconds_to_time(seconds):
    if pd.isna(seconds):
        return None
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f'{h:02d}:{m:02d}:{s:02d}'

average_start_time_seconds['Promedio Inicio de Ruta (HH:MM:SS)'] = average_start_time_seconds['Promedio Inicio de Ruta'].apply(seconds_to_time)

st.write("Average Start Time (in HH:MM:SS) per File:")
st.dataframe(average_start_time_seconds[['Nombre Archivo', 'Promedio Inicio de Ruta (HH:MM:SS)']])

# If you want to add the average back to the main dataframe, you might repeat
# the average value for all rows belonging to that 'Nombre Archivo'.
# This might not be the desired output based on the prompt ("Agrega al final la columna 'Promedio Inicio de Ruta'").
# Assuming the user wants a summary table as calculated above,
# the 'average_start_time_seconds' DataFrame is the result.

# If the intention was to add a column to the *original* dataframes with the overall average
# for that file repeated in each row, you would do something like this:
# For each dataframe in the dfs dictionary:
#   file_name = df_name
#   avg_time = average_start_time_seconds[average_start_time_seconds['Nombre Archivo'] == file_name]['Promedio Inicio de Ruta'].iloc[0]
#   dfs[df_name]['Promedio Inicio de Ruta'] = avg_time

# Let's assume the user wants the summary table. The calculated `average_start_time_seconds`
# DataFrame already contains the required information.

# The prompt asks to add the column "Promedio Inicio de Ruta" "al final".
# If this means appending the summary table to the display of the main dataframe,
# we have already done that by displaying `average_start_time_seconds`.

# If it means adding the average for each file back into the `all_data_after_drop` dataframe,
# repeating the average for each row of a given 'Nombre Archivo':
all_data_with_avg = pd.merge(all_data_after_drop, average_start_time_seconds[['Nombre Archivo', 'Promedio Inicio de Ruta']], on='Nombre Archivo', how='left')

st.write("Combined Data with 'Promedio Inicio de Ruta' column:")
st.dataframe(all_data_with_avg)
