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

# prompt: Agrega al final la columna "Promedio Inicio de Ruta" y despues usando la columna hora, saca el promedio de cada hora inicial del dia 

# Add "Promedio Inicio de Ruta" column
all_data_after_drop["Promedio Inicio de Ruta"] = ""

# Ensure 'Hora' is in a suitable format (like datetime or just seconds since midnight)
# For averaging, converting to seconds since midnight might be easiest.
# Assuming 'Hora' is now a string in HH:MM:SS format after removing letters.
def time_to_seconds(time_str):
  if pd.isna(time_str) or time_str == '':
    return 0
    


all_data_after_drop['Hora_seconds'] = all_data_after_drop['Hora'].apply(time_to_seconds)

# Calculate the average 'Hora_seconds' for each day (assuming 'Fecha' column exists and is date)
# If 'Fecha' is not a date, you'll need to adjust this grouping.
if 'Fecha' in all_data_after_drop.columns:
    # Ensure 'Fecha' is datetime
    all_data_after_drop['Fecha'] = pd.to_datetime(all_data_after_drop['Fecha'], errors='coerce')

    # Group by 'Fecha' and calculate the mean of 'Hora_seconds'
    average_start_time_seconds_per_day = all_data_after_drop.groupby(all_data_after_drop['Fecha'].dt.date)['Hora_seconds'].mean()

    # Map the average seconds back to the original DataFrame based on the date
    # Create a dictionary for easier mapping
    avg_time_dict = average_start_time_seconds_per_day.to_dict()

    # Function to convert seconds back to HH:MM:SS format
    def seconds_to_time_string(seconds):
        if pd.isna(seconds):
            return ''
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours:02}:{minutes:02}:{seconds:02}'

    # Apply the average time to the new column based on the date
    all_data_after_drop['Promedio Inicio de Ruta'] = all_data_after_drop['Fecha'].dt.date.map(avg_time_dict).apply(seconds_to_time_string)

    # Display the dataframe with the average start time per day
    st.write("Combined Data with 'Promedio Inicio de Ruta' calculated per day:")
    st.dataframe(all_data_after_drop)
else:
    st.warning("'Fecha' column not found. Cannot calculate average start time per day.")
    # If no 'Fecha' column, perhaps calculate the average of all start times across all data?
    average_start_time_seconds_overall = all_data_after_drop['Hora_seconds'].mean()
    average_start_time_overall_string = seconds_to_time_string(average_start_time_seconds_overall)
    all_data_after_drop['Promedio Inicio de Ruta'] = average_start_time_overall_string
    st.write("Combined Data with 'Promedio Inicio de Ruta' calculated as overall average:")
    st.dataframe(all_data_after_drop)

# Drop the temporary 'Hora_seconds' column
all_data_after_drop = all_data_after_drop.drop(columns=['Hora_seconds'])

# Display the final dataframe
st.write("Final Combined Data:")
st.dataframe(all_data_after_drop)
