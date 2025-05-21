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


# prompt: en la columna Estatus reemplaza los nombres con Conductores

all_data_after_drop['Estatus'] = 'Conductores'

# Display the dataframe after replacing values in 'Estatus'
st.write("Combined Data after replacing 'Estatus' with 'Conductores':")
st.dataframe(all_data_after_drop)

# prompt: haz una grafica de lineas usando la columna Inicio de Ruta Promedio y Final de Ruta Promedio usando como eje x la columna Fecha para streamlit y como eje y las horas del dia de 00:00 a 23:59 del año 2025 y si hay valores nulos, ignoralos, segmentando cada camion con su propio concepto

import altair as alt
import pandas as pd

# Ensure 'Fecha_Hora' is datetime and extract date
all_data_after_drop['Fecha_Hora'] = pd.to_datetime(all_data_after_drop['Fecha_Hora'])
all_data_after_drop['Fecha'] = all_data_after_drop['Fecha_Hora'].dt.date

# Convert average time strings to datetime objects (using a dummy date)
dummy_date = pd.to_datetime('2025-01-01')
all_data_after_drop['Inicio de Ruta Promedio_dt'] = pd.to_datetime(dummy_date.strftime('%Y-%m-%d') + ' ' + all_data_after_drop['Inicio de Ruta Promedio'], errors='coerce')
all_data_after_drop['Final de Ruta Promedio_dt'] = pd.to_datetime(dummy_date.strftime('%Y-%m-%d') + ' ' + all_data_after_drop['Final de Ruta Promedio'], errors='coerce')

# Filter for the year 2025
data_2025 = all_data_after_drop[all_data_after_drop['Fecha_Hora'].dt.year == 2025].copy()

# Drop rows with NaN values in the relevant columns
data_2025.dropna(subset=['Inicio de Ruta Promedio_dt', 'Final de Ruta Promedio_dt', 'Fecha', 'Nombre Archivo'], inplace=True)

# Create the line chart for 'Inicio de Ruta Promedio'
chart_inicio = alt.Chart(data_2025).mark_line().encode(
    x=alt.X('Fecha:T', title='Fecha'),
    y=alt.Y('hours(Inicio de Ruta Promedio_dt):Q', title='Hora del Día (00:00 - 23:59)', axis=alt.Axis(format='%H:%M')),
    color='Nombre Archivo:N',
    tooltip=['Fecha:T', 'Inicio de Ruta Promedio:N', 'Nombre Archivo:N']
).properties(
    title='Inicio de Ruta Promedio por Camión en 2025'
)

# Create the line chart for 'Final de Ruta Promedio'
chart_final = alt.Chart(data_2025).mark_line().encode(
    x=alt.X('Fecha:T', title='Fecha'),
    y=alt.Y('hours(Final de Ruta Promedio_dt):Q', title='Hora del Día (00:00 - 23:59)', axis=alt.Axis(format='%H:%M')),
    color='Nombre Archivo:N',
    tooltip=['Fecha:T', 'Final de Ruta Promedio:N', 'Nombre Archivo:N']
).properties(
    title='Final de Ruta Promedio por Camión en 2025'
)

# Display the charts in Streamlit
st.altair_chart(chart_inicio, use_container_width=True)
st.altair_chart(chart_final, use_container_width=True)

# prompt: realiza una grafica de pastel de la diferencia entre la hora de inicio y la hora final para streamlit

# Calculate the difference in time for each truck
# We can calculate the difference in seconds and then convert to a more readable format if needed
average_start_times_seconds = all_data_after_drop.groupby('Nombre Archivo')['Inicio de Ruta Promedio_dt'].min().apply(lambda x: x.timestamp()) # Use min as all rows for a truck will have the same value after merge
average_end_times_seconds = all_data_after_drop.groupby('Nombre Archivo')['Final de Ruta Promedio_dt'].min().apply(lambda x: x.timestamp()) # Use min as all rows for a truck will have the same value after merge

time_difference_seconds = average_end_times_seconds - average_start_times_seconds

# Convert time difference in seconds to hours for easier interpretation in a pie chart
time_difference_hours = time_difference_seconds / 3600

# Create a DataFrame for the pie chart
pie_data = pd.DataFrame({
    'Nombre Archivo': time_difference_hours.index,
    'Duración de Ruta (Horas)': time_difference_hours.values
})

# Create the pie chart using Altair
pie_chart = alt.Chart(pie_data).mark_arc(outerRadius=120).encode(
    theta=alt.Theta(field="Duración de Ruta (Horas)", type="quantitative"),
    color=alt.Color(field="Nombre Archivo", type="nominal"),
    order=alt.Order(field="Duración de Ruta (Horas)", sort="descending"),
    tooltip=["Nombre Archivo", "Duración de Ruta (Horas)"]
).properties(
    title='Distribución de la Duración Promedio de Ruta por Camión'
)

# Add text labels to the pie chart
text = pie_chart.mark_text(radius=140).encode(
    text=alt.Text(field="Duración de Ruta (Horas)", type="quantitative", format='.1f'),
    order=alt.Order(field="Duración de Ruta (Horas)", sort="descending"),
    color=alt.value("black")  # Set the color of the labels to black
)

# Combine the pie chart and the text
final_pie_chart = pie_chart + text

# Display the pie chart in Streamlit
st.altair_chart(final_pie_chart, use_container_width=True)

# prompt: realiza un histograma de la diferencia entre la hora de inicio y la hora final para streamlit

# Calculate the difference between 'Final de Ruta Promedio_dt' and 'Inicio de Ruta Promedio_dt'
# This will be a Timedelta object
data_2025['Duracion Ruta Promedio'] = data_2025['Final de Ruta Promedio_dt'] - data_2025['Inicio de Ruta Promedio_dt']

# Convert the Timedelta to total minutes or hours for the histogram
# Let's use total hours for better readability in the histogram
data_2025['Duracion Ruta Promedio (horas)'] = data_2025['Duracion Ruta Promedio'].dt.total_seconds() / 3600

# Create the histogram
chart_duracion = alt.Chart(data_2025).mark_bar().encode(
    alt.X("Duracion Ruta Promedio (horas):Q", bin=True, title="Duración de Ruta Promedio (horas)"),
    alt.Y("count()", title="Frecuencia"),
    tooltip=[
        alt.Tooltip("Duracion Ruta Promedio (horas)", bin=True, title="Rango de Duración (horas)"),
        "count()"
        ]
).properties(
    title='Distribución de la Duración Promedio de Ruta (en horas)'
)

# Display the histogram in Streamlit
st.altair_chart(chart_duracion, use_container_width=True)

# prompt: en base a los dias faltantes genera una grafica de pastel contando los dias que si se asistio contra los dias que no solo tomandolo base a un mes de 31 dias con diferentes colores para cada "CAMION MXX"

# Assume `dfs` is the dictionary containing dataframes for each truck, already loaded and cleaned

# Number of days in the month (assuming 31 as specified)
total_days_in_month = 31

# Create a list to store data for the pie chart
pie_chart_data = []

for truck_name, df in dfs.items():
    # Count the number of unique dates for each truck
    days_worked = df['Fecha'].nunique()

    # Calculate the number of days not worked
    days_not_worked = total_days_in_month - days_worked

    # Append data for this truck to the list
    pie_chart_data.append({'CAMION': truck_name, 'Tipo': 'Asistencia', 'Dias': days_worked})
    pie_chart_data.append({'CAMION': truck_name, 'Tipo': 'Falta', 'Dias': days_not_worked})

# Convert the list of dictionaries into a pandas DataFrame
pie_chart_df = pd.DataFrame(pie_chart_data)

# Create the pie chart using Altair
pie_chart = alt.Chart(pie_chart_df).mark_arc(outerRadius=120).encode(
    theta=alt.Theta(field="Dias", type="quantitative"),
    color=alt.Color(field="Tipo", type="nominal"),
    facet=alt.Facet("CAMION:N", columns=4), # Create separate pie charts for each truck
    tooltip=["CAMION", "Tipo", "Dias", alt.Tooltip("Dias", aggregate="sum", title="Total Días")]
).properties(
    title="Días de Asistencia vs Faltas por Camión (Basado en 31 Días)"
)

# Display the chart in Streamlit
st.altair_chart(pie_chart, use_container_width=True)
