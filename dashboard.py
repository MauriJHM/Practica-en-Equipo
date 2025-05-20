# prompt: lee los archivos /content/CAMION M01.xlsx , /content/CAMION M02.xlsx , /content/CAMION M03.xlsx , /content/CAMION M04.xlsx , /content/CAMION M05.xlsx , /content/CAMION M05.xlsx , /content/CAMION M06.xlsx , /content/CAMION M07.xlsx , /content/CAMION M08.xlsx , /content/CAMION M09.xlsx /content/CAMION M10.xlsx /content/CAMION M11.xlsx , /content/CAMION M12.xlsx y mezcla sus dataframes para exponer en streamlit


import plotly.express as px
import pandas as pd
import streamlit as st

file_paths = [
    'CAMION M01.xlsx', '/content/CAMION M02.xlsx', '/content/CAMION M03.xlsx',
    '/content/CAMION M04.xlsx', '/content/CAMION M05.xlsx', '/content/CAMION M06.xlsx',
    '/content/CAMION M07.xlsx', '/content/CAMION M08.xlsx', '/content/CAMION M09.xlsx',
    '/content/CAMION M10.xlsx', '/content/CAMION M11.xlsx', '/content/CAMION M12.xlsx'
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
