import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Nueva App de Concentraciones", layout="centered")

def main():
    st.title("📊 Nueva Aplicación de Análisis")
    st.info("Este es el punto de partida para tu nuevo proyecto.")

    # Sidebar para controles
    st.sidebar.header("Ajustes del Modelo")
    dato_ejemplo = st.sidebar.slider("Selecciona un valor inicial", 0, 100, 50)

    # Cuerpo principal
    st.subheader("Visualización de Datos")
    st.write(f"El valor seleccionado actualmente es: **{dato_ejemplo}**")
    
    # Ejemplo de gráfico simple para verificar que todo carga bien
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C']
    )
    st.line_chart(chart_data)

if __name__ == "__main__":
    main()
