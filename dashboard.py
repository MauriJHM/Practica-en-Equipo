# prompt: lee los archivos /content/CAMION M01.xlsx , /content/CAMION M02.xlsx , /content/CAMION M03.xlsx , /content/CAMION M04.xlsx , /content/CAMION M05.xlsx , /content/CAMION M05.xlsx , /content/CAMION M06.xlsx , /content/CAMION M07.xlsx , /content/CAMION M08.xlsx , /content/CAMION M09.xlsx /content/CAMION M10.xlsx /content/CAMION M11.xlsx , /content/CAMION M12.xlsx y mezcla sus dataframes para exponer en streamlit


import plotly.express as px
import pandas as pd
import streamlit as st

file_paths = [
    'CAMION M01.xlsx', 'CAMION M02.xlsx', 'CAMION M03.xlsx',
    'CAMION M04.xlsx', 'CAMION M05.xlsx', 'CAMION M06.xlsx',
    'CAMION M07.xlsx', 'CAMION M08.xlsx', 'CAMION M09.xlsx',
    'CAMION M10.xlsx', 'CAMION M11.xlsx', 'CAMION M12.xlsx'
]

all_data = pd.DataFrame()

for file_path in file_paths:
    try:
        df = pd.read_excel(file_path)
        all_data = pd.concat([all_data, df], ignore_index=True)
    except FileNotFoundError:
        st.error(f"Error: El archivo no se encuentra - {file_path}")
    except Exception as e:
        st.error(f"Error al leer el archivo {file_path}: {e}")

st.title('Datos Combinados de Camiones')

if not all_data.empty:
    st.write("Mostrando las primeras 5 filas de los datos combinados:")
    st.dataframe(all_data.head())

    st.write("Estadísticas descriptivas de los datos combinados:")
    st.dataframe(all_data.describe())

    st.write("Dimensiones de los datos combinados:")
    st.write(f"Filas: {all_data.shape[0]}, Columnas: {all_data.shape[1]}")

    # You can add more visualizations or analysis here using Streamlit components

else:
    st.warning("No se pudo cargar datos de ningún archivo.")

# prompt: agrega al principio la columna del archivo al que corresponda como por ejemplo "CAMION M01"

import pandas as pd
import streamlit as st
import plotly.express as px



file_paths = [
    '/content/CAMION M01.xlsx', '/content/CAMION M02.xlsx', '/content/CAMION M03.xlsx',
    '/content/CAMION M04.xlsx', '/content/CAMION M05.xlsx', '/content/CAMION M06.xlsx',
    '/content/CAMION M07.xlsx', '/content/CAMION M08.xlsx', '/content/CAMION M09.xlsx',
    '/content/CAMION M10.xlsx', '/content/CAMION M11.xlsx', '/content/CAMION M12.xlsx'
]

all_data = pd.DataFrame()

for file_path in file_paths:
    try:
        df = pd.read_excel(file_path)
        # Extract the file name (e.g., 'CAMION M01') and add it as a new column at the beginning
        file_name = file_path.split('/')[-1].split('.')[0]
        df.insert(0, 'Origen', file_name)
        all_data = pd.concat([all_data, df], ignore_index=True)
    except FileNotFoundError:
        st.error(f"Error: El archivo no se encuentra - {file_path}")
    except Exception as e:
        st.error(f"Error al leer el archivo {file_path}: {e}")

st.title('Datos Combinados de Camiones')

if not all_data.empty:
    st.write("Mostrando las primeras 5 filas de los datos combinados:")
    st.dataframe(all_data.head())

    st.write("Estadísticas descriptivas de los datos combinados:")
    st.dataframe(all_data.describe())

    st.write("Dimensiones de los datos combinados:")
    st.write(f"Filas: {all_data.shape[0]}, Columnas: {all_data.shape[1]}")

    # You can add more visualizations or analysis here using Streamlit components

else:
    st.warning("No se pudo cargar datos de ningún archivo.")

# To run this Streamlit app in Colab:
# 1. Save this code as a Python file (e.g., app.py)
# 2. Run the following command in a new cell:
#    !streamlit run app.py & npx localtunnel --port 8501
