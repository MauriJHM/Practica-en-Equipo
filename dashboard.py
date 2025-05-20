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

# prompt: Usando la columna de inicio de ruta promedio y final de ruta promedio haz una grafica por camion por cada dia

import plotly.express as px

# Ensure 'Inicio de Ruta Promedio' and 'Final de Ruta Promedio' are in datetime format for plotting
# We'll need to convert the string representation back to datetime, assuming a dummy date.
# A common approach is to use a fixed date like the start of an epoch or the current day.
# For simplicity in plotting time of day, we can use a fixed date like '2000-01-01'.
all_data_after_drop['Inicio de Ruta Promedio_dt'] = pd.to_datetime('2000-01-01 ' + all_data_after_drop['Inicio de Ruta Promedio'])
all_data_after_drop['Final de Ruta Promedio_dt'] = pd.to_datetime('2000-01-01 ' + all_data_after_drop['Final de Ruta Promedio'])

# Group by truck and date to get the daily average start and end times
daily_avg_times = all_data_after_drop.groupby(['Nombre Archivo', 'Fecha']).agg(
    {'Inicio de Ruta Promedio_dt': 'first',
     'Final de Ruta Promedio_dt': 'first'}
).reset_index()

# Create a list of trucks to iterate through
truck_names = daily_avg_times['Nombre Archivo'].unique()

# Create a plot for each truck
for truck in truck_names:
    truck_data = daily_avg_times[daily_avg_times['Nombre Archivo'] == truck]

    # Create a scatter plot
    fig = px.scatter(
        truck_data,
        x='Fecha',
        y=['Inicio de Ruta Promedio_dt', 'Final de Ruta Promedio_dt'],
        title=f'Inicio y Final de Ruta Promedio Diario para {truck}',
        labels={'Fecha': 'Fecha', 'value': 'Hora Promedio'},
        color_discrete_map={
            'Inicio de Ruta Promedio_dt': 'blue',
            'Final de Ruta Promedio_dt': 'red'
        }
    )

    # Customize the y-axis to display time format
    fig.update_yaxes(tickformat='%H:%M')

    # Show the plot using st.plotly_chart
    st.plotly_chart(fig)

