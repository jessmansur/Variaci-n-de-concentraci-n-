import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Balance de Masa CSTR", layout="wide")

def main():
    st.title("🧪 Simulador de Concentración Transitoria (Balance de Masa)")
    
    # --- CARTELES DE SUPUESTOS ---
    st.warning("⚠️ **Supuestos del modelo:**\n"
               "* Se supone **buen mezclado** en el contenedor; la concentración de salida es igual a la del contenido.\n"
               "* Se supone **densidad similar** entre el volumen en el contenedor y el flujo de entrada.\n"
               "* Se supone que **no hay reacciones químicas** dentro del contenedor.")

    # --- BARRA LATERAL: ENTRADA DE DATOS (ORDEN CORREGIDO) ---
    st.sidebar.header("📥 Variables de Entrada")
    
    # 1. Contenido del Contenedor (Masa o Volumen Inicial)
    st.sidebar.subheader("1. Estado Inicial del Contenedor")
    col_v1, col_v2 = st.sidebar.columns([2, 1])
    v0_input = col_v1.number_input("Contenido Inicial (V0 o M0)", value=100.0)
    v0_unit = col_v2.selectbox("Unidad", ["kg", "g", "L", "m3", "gal", "lb"], key="v0_u")

    # 2. Densidad
    st.sidebar.subheader("2. Propiedades Físicas")
    col_rho1, col_rho2 = st.sidebar.columns([2, 1])
    rho_val = col_rho1.number_input("Densidad de la solución (ρ)", value=1000.0)
    rho_unit = col_rho2.selectbox("Unidad", ["kg/m³", "g/cm³"], key="rho_u")
    
    # Conversión de densidad a kg/m3 para cálculos internos
    rho_si = rho_val if rho_unit == "kg/m³" else rho_val * 1000.0

    # 3. Masa del compuesto (D0)
    st.sidebar.subheader("3. Componente de Interés")
    col_d1, col_d2 = st.sidebar.columns([2, 1])
    d0_val = col_d1.number_input("Masa inicial compuesto (D0)", value=10.0)
    d0_unit = col_d2.selectbox("Unidad", ["kg", "g", "lb", "L"], key="d0_u")

    # 4. Flujos (Entrada y Salida)
    st.sidebar.subheader("4. Flujos del Proceso")
    
    # Flujo Entrada
    col_fe1, col_fe2 = st.sidebar.columns([2, 1])
    fe_val = col_fe1.number_input("Flujo de Entrada (Fe
