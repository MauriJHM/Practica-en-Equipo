# prompt: lee los archivos /content/CAMION M01.xlsx , /content/CAMION M02.xlsx , /content/CAMION M03.xlsx , /content/CAMION M04.xlsx , /content/CAMION M05.xlsx , /content/CAMION M06.xlsx , /content/CAMION M07.xlsx , /content/CAMION M08.xlsx , /content/CAMION M09.xlsx /content/CAMION M10.xlsx /content/CAMION M11.xlsx , /content/CAMION M12.xlsx  para streamlit
import plotly.express as px
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

# prompt: Junta las columnas Fecha y Hora 

# Concatenate 'Fecha' and 'Hora' columns and convert to datetime
all_data_after_drop['Fecha_Hora'] = pd.to_datetime(all_data_after_drop['Fecha'].astype(str) + ' ' + all_data_after_drop['Hora'].astype(str), errors='coerce')

# Display the updated dataframe with the new 'Fecha_Hora' column
st.write("Combined Data with 'Fecha_Hora' column:")
st.dataframe(all_data_after_drop)

# Optionally, drop the original 'Fecha' and 'Hora' columns
all_data_after_drop = all_data_after_drop.drop(columns=['Fecha', 'Hora'])

# Display the dataframe after dropping original columns
st.write("Combined Data after dropping original 'Fecha' and 'Hora' columns:")
st.dataframe(all_data_after_drop)

# prompt: crea una nueva columna al final llamada "Inicio de Ruta Promedio" donde utilices el datetime Fecha_Hora y la hora inicial de cada dia para realizar un promedio de cada dia para cada "CAMION MXX"

# Calculate the average start time for each day and truck
all_data_after_drop['Fecha'] = all_data_after_drop['Fecha_Hora'].dt.date

# Group by 'Nombre Archivo' (which represents the truck) and 'Fecha'
daily_start_times = all_data_after_drop.groupby(['Nombre Archivo', 'Fecha'])['Fecha_Hora'].min()

# Calculate the average start time across all days for each truck
# This part is a bit tricky as averaging datetimes directly isn't standard.
# We can calculate the average time of day.
daily_start_times_time = daily_start_times.dt.time

# To average times, we can convert them to seconds since midnight, average, then convert back
def time_to_seconds(t):
  return t.hour * 3600 + t.minute * 60 + t.second

def seconds_to_time(s):
  hours, remainder = divmod(s, 3600)
  minutes, seconds = divmod(remainder, 60)
  return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

average_start_times_seconds = daily_start_times_time.apply(time_to_seconds).groupby('Nombre Archivo').mean()

# Convert the average seconds back to a time string
average_start_times_str = average_start_times_seconds.apply(seconds_to_time)

# Create a new DataFrame to merge the average start times back
average_start_times_df = average_start_times_str.reset_index()
average_start_times_df.rename(columns={'Fecha_Hora': 'Inicio de Ruta Promedio'}, inplace=True)

# Merge the average start times back to the original dataframe based on 'Nombre Archivo'
all_data_after_drop = pd.merge(all_data_after_drop, average_start_times_df, on='Nombre Archivo', how='left')

# Display the dataframe with the new 'Inicio de Ruta Promedio' column
st.write("Combined Data with 'Inicio de Ruta Promedio' column:")
st.dataframe(all_data_after_drop)

# prompt: crea una nueva columna al final llamada "Final de Ruta Promedio" donde utilices el datetime Fecha_Hora y la hora final de cada dia para realizar un promedio de cada dia para cada "CAMION MXX"

# Calculate the average end time for each day and truck
# Group by 'Nombre Archivo' (which represents the truck) and 'Fecha'
daily_end_times = all_data_after_drop.groupby(['Nombre Archivo', 'Fecha'])['Fecha_Hora'].max()

# Calculate the average end time across all days for each truck
daily_end_times_time = daily_end_times.dt.time

average_end_times_seconds = daily_end_times_time.apply(time_to_seconds).groupby('Nombre Archivo').mean()

# Convert the average seconds back to a time string
average_end_times_str = average_end_times_seconds.apply(seconds_to_time)

# Create a new DataFrame to merge the average end times back
average_end_times_df = average_end_times_str.reset_index()
average_end_times_df.rename(columns={'Fecha_Hora': 'Final de Ruta Promedio'}, inplace=True)

# Merge the average end times back to the original dataframe based on 'Nombre Archivo'
all_data_after_drop = pd.merge(all_data_after_drop, average_end_times_df, on='Nombre Archivo', how='left')

# Display the dataframe with the new 'Final de Ruta Promedio' column
st.write("Combined Data with 'Final de Ruta Promedio' column:")
st.dataframe(all_data_after_drop)

# prompt: Usando la columna de inicio de ruta promedio y final de ruta promedio haz una grafica lineal

import plotly.express as px

# Create a DataFrame with the average start and end times for each truck
average_times_for_plot = all_data_after_drop[['Nombre Archivo', 'Inicio de Ruta Promedio', 'Final de Ruta Promedio']].drop_duplicates()

# Convert the time strings back to datetime objects for plotting
# We can use a dummy date since we are only interested in the time component for comparison
average_times_for_plot['Inicio de Ruta Promedio_dt'] = pd.to_datetime(average_times_for_plot['Inicio de Ruta Promedio'], format='%H:%M:%S')
average_times_for_plot['Final de Ruta Promedio_dt'] = pd.to_datetime(average_times_for_plot['Final de Ruta Promedio'], format='%H:%M:%S')

# Melt the DataFrame to long format for Plotly Express
average_times_melted = average_times_for_plot.melt(
    id_vars=['Nombre Archivo'],
    value_vars=['Inicio de Ruta Promedio_dt', 'Final de Ruta Promedio_dt'],
    var_name='Tipo de Tiempo',
    value_name='Tiempo Promedio'
)

# Create the line plot
fig = px.line(average_times_melted,
              x='Nombre Archivo',
              y='Tiempo Promedio',
              color='Tipo de Tiempo',
              markers=True,
              title='Inicio y Fin de Ruta Promedio por Camión')

# Update layout for better readability
fig.update_layout(
    xaxis_title='Camión',
    yaxis_title='Tiempo Promedio',
    legend_title='Tipo de Tiempo'
)

# Display the plot
st.plotly_chart(fig)

# prompt: en la columna Estatus cambia los nombres y reemplazalos por Conductor 1 y Conductor 2 respectivamente por cada camion

# Replace the values in the 'Estatus' column
# We need to iterate through the dataframes in the dictionary 'dfs'
# or if you want to apply it to the combined dataframe, use all_data_after_drop
# Let's apply it to the combined dataframe 'all_data_after_drop' as it seems more likely this is the goal
# based on the subsequent plotting code.

# Map original values to new values
# Assuming 'Conductor 1' and 'Conductor 2' are the specific names you want to replace with.
# You might need to identify which original names correspond to which new names.
# For example, if the original names are 'OriginalName1' and 'OriginalName2'
# replacement_map = {'OriginalName1': 'Conductor 1', 'OriginalName2': 'Conductor 2'}

# Since the request is to replace existing names by 'Conductor 1' and 'Conductor 2'
# respectively for *each truck*, it implies there are likely two primary status values per truck
# that need renaming. Without knowing the original values, we'll assume they are
# consistent across trucks or you intend to replace *all* values in 'Estatus'
# with 'Conductor 1' and 'Conductor 2' in some pattern.

# A common scenario might be replacing the first occurrence (or a specific value)
# with 'Conductor 1' and the second (or another specific value) with 'Conductor 2'.
# If there are only two distinct status values per truck, you could map them.

# Example: If the original values are 'Driver A' and 'Driver B'
# replacement_map = {'Driver A': 'Conductor 1', 'Driver B': 'Conductor 2'}
# all_data_after_drop['Estatus'] = all_data_after_drop['Estatus'].replace(replacement_map)

# If the goal is simpler and you just want to rename existing values to these two,
# you need to know what the original values are. Let's assume you have identified
# the two main statuses you want to rename, for example 'Active' and 'Inactive'.
# replacement_map = {'Active': 'Conductor 1', 'Inactive': 'Conductor 2'}
# all_data_after_drop['Estatus'] = all_data_after_drop['Estatus'].replace(replacement_map)

# If the requirement is to assign 'Conductor 1' and 'Conductor 2' based on some other logic,
# or if the existing 'Estatus' values are the actual names that need changing,
# please clarify the exact mapping or logic.

# As a general example, if you want to replace all instances of a specific value:
# all_data_after_drop['Estatus'] = all_data_after_drop['Estatus'].replace('Existing_Status_1', 'Conductor 1')
# all_data_after_drop['Estatus'] = all_data_after_drop['Estatus'].replace('Existing_Status_2', 'Conductor 2')

# If the intention is to *categorize* entries within each truck's data
# and assign 'Conductor 1' or 'Conductor 2' based on that categorization,
# you would need logic to define which entries get which conductor.

# Assuming you want to replace existing distinct values in 'Estatus' with 'Conductor 1' and 'Conductor 2'.
# Let's find the unique values in the 'Estatus' column to see what needs replacing.
unique_statuses = all_data_after_drop['Estatus'].unique()
st.write("Unique statuses before replacement:", unique_statuses)

# You need to define the mapping based on the `unique_statuses`.
# For demonstration, let's assume the first unique status found will be replaced by 'Conductor 1'
# and the second by 'Conductor 2', if there are at least two unique statuses.
if len(unique_statuses) >= 2:
    replacement_map = {unique_statuses[0]: 'Conductor 1', unique_statuses[1]: 'Conductor 2'}
    all_data_after_drop['Estatus'] = all_data_after_drop['Estatus'].replace(replacement_map)
    st.write(f"Replaced {unique_statuses[0]} with Conductor 1 and {unique_statuses[1]} with Conductor 2")
elif len(unique_statuses) == 1:
    # If there's only one unique status, you might replace it with 'Conductor 1'
    replacement_map = {unique_statuses[0]: 'Conductor 1'}
    all_data_after_drop['Estatus'] = all_data_after_drop['Estatus'].replace(replacement_map)
    st.write(f"Replaced {unique_statuses[0]} with Conductor 1 (only one unique status found)")
else:
    st.write("No unique statuses found in the 'Estatus' column.")


# Display the dataframe after the replacement
st.write("Combined Data after replacing 'Estatus' values:")
st.dataframe(all_data_after_drop)

# If the replacement needs to happen *per truck* and the status values
# to be replaced are different for each truck, you would need to iterate
# through the individual dataframes in the `dfs` dictionary.
# For example:
# for df_name, df in dfs.items():
#     # Identify the specific status values to replace for this truck (df_name)
#     # This logic would depend on how you identify which values correspond to 'Conductor 1' and 'Conductor 2'
#     # within this specific truck's data.
#     # Example: Assuming for CAMION M01, you replace 'Driver_A_M01' with 'Conductor 1' and 'Driver_B_M01' with 'Conductor 2'
#     if df_name == 'CAMION M01':
#         truck_replacement_map = {'Driver_A_M01': 'Conductor 1', 'Driver_B_M01': 'Conductor 2'}
#     elif df_name == 'CAMION M02':
#         truck_replacement_map = {'Driver_C_M02': 'Conductor 1', 'Driver_D_M02': 'Conductor 2'}
#     # ... add conditions for other trucks
#     else:
#         truck_replacement_map = {} # No specific replacement for this truck

#     if truck_replacement_map:
#         dfs[df_name]['Estatus'] = dfs[df_name]['Estatus'].replace(truck_replacement_map)
#         st.write(f"Replaced statuses in {df_name} based on truck-specific map.")
#     else:
#         st.write(f"No specific status replacement defined for {df_name}.")

# After modifying individual dataframes in `dfs`, you would then re-concatenate them:
# all_data_after_drop = pd.concat(dfs.values(), ignore_index=True)
# st.write("Combined Data after replacing 'Estatus' values (per truck):")
# st.dataframe(all_data_after_drop)
# Then continue with the plotting code using this new `all_data_after_drop`
