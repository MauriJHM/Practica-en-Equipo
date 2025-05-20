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

# prompt: en la columna estatus elimina todas las letras y reemplazalos por Conductor 1 y Conductor 2

# Replace characters in 'Estatus' column
# Assuming you want to replace specific patterns of letters
# For example, replace any row in 'Estatus' containing letters with 'Conductor 1'
# And other rows in 'Estatus' containing letters with 'Conductor 2'.
# This requires a specific logic to determine which rows get 'Conductor 1' vs 'Conductor 2'.
# As per the prompt, let's assume you want to replace ALL values in 'Estatus' that
# contain letters with EITHER 'Conductor 1' or 'Conductor 2' based on some
# implicit condition not provided.

# A simple interpretation is to just remove the letters and then assign based on some rule.
# Since the rule is not specified, a simple approach is to replace all non-digit
# characters and then perhaps map the resulting values to 'Conductor 1' or 'Conductor 2'.

# Let's assume a different interpretation: replace all values in the 'Estatus' column
# that originally contained any letters with either 'Conductor 1' or 'Conductor 2'.
# The assignment between 'Conductor 1' and 'Conductor 2' is still ambiguous.

# A more concrete interpretation: replace all rows where 'Estatus' contains letters
# with "Conductor 1" if some other condition is met, and "Conductor 2" otherwise.
# Without a condition, let's apply a simpler rule: if the original 'Estatus' contained
# letters, replace it. We'll need a rule to assign 'Conductor 1' or 'Conductor 2'.

# Let's make an assumption:
# If the original value had letters AND ended with '1', replace with 'Conductor 1'.
# If the original value had letters AND ended with '2', replace with 'Conductor 2'.
# If the original value had letters but didn't end with '1' or '2', handle as needed (e.g., default to Conductor 1).
# If the original value did NOT have letters, keep it as is (although the prompt implies replacing where letters exist).

# A simpler interpretation matching the prompt: replace the contents of the 'Estatus'
# column where letters exist, and assign 'Conductor 1' or 'Conductor 2'.
# Let's assume a pattern: If the original 'Estatus' had the letter 'A', replace with 'Conductor 1'.
# If the original 'Estatus' had the letter 'B', replace with 'Conductor 2'.
# This is still an arbitrary assumption.

# Let's try a direct replacement approach based on the likely meaning:
# If a row's original 'Estatus' value had letters, it likely indicates a state or action.
# We need a way to map these states/actions to 'Conductor 1' or 'Conductor 2'.

# A plausible scenario: the original 'Estatus' column contained codes like "Route A1", "Route B2", etc.,
# and you want to assign "Conductor 1" to rows related to "Route A" and "Conductor 2" to "Route B".

# Let's make the most straightforward interpretation based on the request:
# Find rows where 'Estatus' contains letters. For these rows, set 'Estatus' to 'Conductor 1' or 'Conductor 2'.
# How to decide between Conductor 1 and 2? Let's assume alternating assignment or based on the original value.

# Let's try replacing based on whether the original value *contained* a '1' or '2' along with letters.
# This is still making assumptions.

# The most literal interpretation of "elimina todas las letras y reemplazalos por Conductor 1 y Conductor 2"
# is to remove the letters and *then* somehow use the remaining numbers to assign 'Conductor 1' or 'Conductor 2'.
# Example: "AB12CD" -> remove letters -> "12". Then map "12" to 'Conductor 1' or 'Conductor 2'. This seems unlikely.

# Let's go with a more probable intent: The original 'Estatus' values like 'A', 'B', 'C', 'D', etc.,
# represent different states or types, and you want to map some to 'Conductor 1' and others to 'Conductor 2'.

# Let's assume a simple mapping for demonstration:
# If 'Estatus' originally contained 'A', 'B', or 'C', replace with 'Conductor 1'.
# If 'Estatus' originally contained 'D', 'E', or 'F', replace with 'Conductor 2'.
# For any other case where letters exist, we can define a default or add more conditions.

# First, identify which rows in the original 'Estatus' contained letters.
# We should do this *before* modifying the 'Estatus' column.

# Let's create a temporary column to store the original 'Estatus' values if needed,
# or just work directly on the column if the logic is simple replacement.

# Let's assume a pattern based on the number *following* the letters, if any.
# If the original 'Estatus' was something like "ABC1", replace with "Conductor 1".
# If the original 'Estatus' was something like "XYZ2", replace with "Conductor 2".
# If the original 'Estatus' contained letters but no '1' or '2' at the end, what happens?

# Let's use a simpler approach based on checking for the presence of digits 1 or 2 in the original string
# *after* removing other letters, but only for rows that *originally* contained letters.

# Identify rows that originally contained letters
rows_with_letters = all_data_after_drop['Estatus'].astype(str).str.contains(r'[a-zA-Z]', na=False)

# For rows with letters, try to extract the digit (1 or 2) after removing other letters.
# If a '1' is found, assign 'Conductor 1'. If a '2' is found, assign 'Conductor 2'.
# If neither is found or multiple are found, we need a rule.
# Let's assume the rule is: if it contains '1' after removing letters, it's Conductor 1. Otherwise, it's Conductor 2
# (assuming it contained letters in the first place).

def assign_conductor(original_status):
    if pd.isna(original_status):
        return original_status
    original_status_str = str(original_status)
    if any(c.isalpha() for c in original_status_str): # Check if it originally had letters
        # Remove all characters that are not '1' or '2' from the original string
        digits_one_two = ''.join(c for c in original_status_str if c in ['1', '2'])
        if '1' in digits_one_two:
            return 'Conductor 1'
        elif '2' in digits_one_two:
            return 'Conductor 2'
        else:
            # If it had letters but no '1' or '2' after removing other characters,
            # default to Conductor 1 as an example, or handle differently
            return 'Conductor 1' # Defaulting for demonstration
    else:
        # If the original value did not have letters, keep it as is.
        return original_status

# Apply the function to the 'Estatus' column
all_data_after_drop['Estatus'] = all_data_after_drop['Estatus'].apply(assign_conductor)


# Display the dataframe after modifying the 'Estatus' column
st.write("Combined Data after updating 'Estatus' column:")
st.dataframe(all_data_after_drop)
