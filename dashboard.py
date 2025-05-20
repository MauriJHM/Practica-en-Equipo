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

# prompt: elimina las columnas que poseen 0s

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
# prompt: muestrame el excel

# To display the contents of the first cleaned dataframe, for example:
if dataframes_cleaned:
  first_df_name = list(dataframes_cleaned.keys())[0]
  print(f"\nDisplaying the first cleaned dataframe: {first_df_name}")
  print(dataframes_cleaned[first_df_name].head()) # Display the first few rows
else:
  print("No dataframes were successfully cleaned and loaded.")

# You can display any other cleaned dataframe by changing the key:
# print(dataframes_cleaned['CAMION M02'].head())
# prompt: agrega 1 columna al principio que indique su nombre de archivo que el ejemplo seria "CAMION M01"

# Create a new dictionary to store dataframes with the filename column added
dataframes_with_filename = {}

# Iterate through the cleaned dataframes
for name, df in dataframes_cleaned.items():
  # Create a new column 'Nombre de Archivo' and assign the filename to all rows
  df['Nombre de Archivo'] = name
  # Reorder the columns to put 'Nombre de Archivo' at the beginning
  cols = ['Nombre de Archivo'] + [col for col in df.columns if col != 'Nombre de Archivo']
  df_with_filename = df[cols]
  # Store the modified dataframe in the new dictionary
  dataframes_with_filename[name] = df_with_filename
  print(f"Added 'Nombre de Archivo' column to dataframe '{name}'.")

# Now you can access the dataframes with the filename column from dataframes_with_filename

# To display the contents of the first dataframe with the filename column, for example:
if dataframes_with_filename:
  first_df_name = list(dataframes_with_filename.keys())[0]
  print(f"\nDisplaying the first dataframe with filename column: {first_df_name}")
  print(dataframes_with_filename[first_df_name].head()) # Display the first few rows
else:
  print("No dataframes were successfully processed to add the filename column.")

# You can display any other dataframe with the filename column by changing the key:
# print(dataframes_with_filename['CAMION M02'].head())

# prompt: Mezcla todos los exceles en 1 mismo

# Concatenate all dataframes in the dataframes_with_filename dictionary into a single dataframe
combined_df = pd.concat(dataframes_with_filename.values(), ignore_index=True)

# Display the first few rows of the combined dataframe
print("\nDisplaying the combined dataframe:")
print(combined_df.head())

# Optionally, save the combined dataframe to a new Excel file
# output_file_path = '/content/CAMIONES_COMBINADO.xlsx'
# combined_df.to_excel(output_file_path, index=False)
# print(f"\nCombined dataframe saved to: {output_file_path}")

# prompt: agrega 1 columna al final que se llame "Promedio Inicio de Ruta" en donde se haga un promedio en donde se tome la primera hora de cada dia 

# Convert 'Hora' column to datetime objects, handling potential errors
combined_df['Hora'] = pd.to_datetime(combined_df['Hora'], errors='coerce').dt.time

# Ensure 'Fecha' column is datetime objects
combined_df['Fecha'] = pd.to_datetime(combined_df['Fecha'], errors='coerce')

# Remove rows where 'Fecha' or 'Hora' could not be converted
combined_df.dropna(subset=['Fecha', 'Hora'], inplace=True)

# Group by 'Nombre de Archivo' and 'Fecha' to get the first hour of each day for each truck
first_hours = combined_df.groupby(['Nombre de Archivo', combined_df['Fecha'].dt.date])['Hora'].agg(lambda x: min(x))

# Calculate the average of these first hours for each truck
# We need a way to average times. One way is to convert time to seconds since midnight, average, then convert back.
def time_to_seconds(t):
    return t.hour * 3600 + t.minute * 60 + t.second

def seconds_to_time(s):
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Create a time object
    return pd.to_datetime(f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}').time()

average_start_time_seconds = first_hours.apply(time_to_seconds).groupby('Nombre de Archivo').mean()

# Convert the average seconds back to time format
average_start_time = average_start_time_seconds.apply(seconds_to_time)

# Convert the Series to a DataFrame for merging
average_start_time_df = average_start_time.reset_index(name='Promedio Inicio de Ruta')

# Merge this average back into the combined dataframe
# We'll merge on 'Nombre de Archivo'
combined_df = pd.merge(combined_df, average_start_time_df, on='Nombre de Archivo', how='left')

# Display the first few rows of the combined dataframe with the new column
print("\nDisplaying the combined dataframe with 'Promedio Inicio de Ruta' column:")
print(combined_df.head())

# prompt: agrega 1 columna al final que se llame "Promedio Final de Ruta" en donde se haga un promedio en donde se tome la ultima hora de cada dia 

# Group by 'Nombre de Archivo' and 'Fecha' to get the last hour of each day for each truck
last_hours = combined_df.groupby(['Nombre de Archivo', combined_df['Fecha'].dt.date])['Hora'].agg(lambda x: max(x))

# Calculate the average of these last hours for each truck
average_end_time_seconds = last_hours.apply(time_to_seconds).groupby('Nombre de Archivo').mean()

# Convert the average seconds back to time format
average_end_time = average_end_time_seconds.apply(seconds_to_time)

# Convert the Series to a DataFrame for merging
average_end_time_df = average_end_time.reset_index(name='Promedio Final de Ruta')

# Merge this average back into the combined dataframe
# We'll merge on 'Nombre de Archivo'
combined_df = pd.merge(combined_df, average_end_time_df, on='Nombre de Archivo', how='left')

# Display the first few rows of the combined dataframe with the new column
print("\nDisplaying the combined dataframe with 'Promedio Final de Ruta' column:")
print(combined_df.head())
