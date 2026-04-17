import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Balance de Masa", layout="wide")

def main():
    st.title("🧪 Balance de Masa y Concentración")
    
    # Carteles informativos
    st.info("💡 **Supuestos del modelo:**\n"
            "* Buen mezclado (C_salida = C_contenedor).\n"
            "* Densidad similar entre flujo de entrada y contenido.\n"
            "* No ocurren reacciones químicas.")

    st.sidebar.header("📥 Configuración de Variables")

    # 1. CONTENIDO INICIAL
    st.sidebar.subheader("1. Contenido Inicial")
    col_v1, col_v2 = st.sidebar.columns([2, 1])
    v0_input = col_v1.number_input("Cantidad inicial", value=100.0)
    v0_unit = col_v2.selectbox("Unidad", ["kg", "g", "L", "m3", "gal", "lb"], key="u_v0")

    # 2. DENSIDAD
    st.sidebar.subheader("2. Densidad (ρ)")
    col_r1, col_r2 = st.sidebar.columns([2, 1])
    rho_input = col_r1.number_input("Valor de ρ", value=1000.0)
    rho_unit = col_r2.selectbox("Unidad", ["kg/m³", "g/cm³"], key="u_rho")
    rho_si = rho_input if rho_unit == "kg/m³" else rho_input * 1000.0

    # 3. MASA DEL COMPUESTO (D0)
    st.sidebar.subheader("3. Masa del Compuesto (D0)")
    col_d1, col_d2 = st.sidebar.columns([2, 1])
    d0_input = col_d1.number_input("Masa inicial D", value=10.0)
    d0_unit = col_d2.selectbox("Unidad", ["kg", "g", "lb", "L"], key="u_d0")

    # Factores de conversión al SI (kg, m3, s)
    m_conv = {"kg": 1.0, "g": 0.001, "lb": 0.453592}
    v_conv = {"m3": 1.0, "L": 0.001, "gal": 0.00378541}
    t_conv = {"s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0}

    # Conversión de Contenido Inicial a MASA (M0)
    if v0_unit in m_conv:
        M0 = v0_input * m_conv[v0_unit]
    else:
        M0 = v0_input * v_conv[v0_unit] * rho_si

    # Conversión de D0 a MASA
    if d0_unit == "L":
        D0 = d0_input * v_conv["L"] * rho_si
    else:
        D0 = d0_input * m_conv[d0_unit]

    # 4. FLUJOS
    st.sidebar.subheader("4. Flujos de Proceso")
    units_flow = [
        "kg/s", "kg/min", "kg/h", "g/s", "g/min", "g/h",
        "L/s", "L/min", "L/h", "gal/s", "gal/min", "gal/h",
        "lb/s", "lb/min", "lb/h"
    ]
    
    c_fe1, c_fe2 = st.sidebar.columns([2, 1])
    fe_val = c_fe1.number_input("Flujo Entrada (Fe)", value=10.0)
    fe_unit = c_fe2.selectbox("Unidad", units_flow, key="u_fe")

    c_fs1, c_fs2 = st.sidebar.columns([2, 1])
    fs_val = c_fs1.number_input("Flujo Salida (Fs)", value=10.0)
    fs_unit = c_fs2.selectbox("Unidad", units_flow, key="u_fs")

    def to_mass_flow(val, unit, dens):
        u_base, u_time = unit.split('/')
        if u_base in m_conv: mass = val * m_conv[u_base]
        elif u_base in v_conv: mass = val * v_conv[u_base] * dens
        else: mass = val * 0.453592 # lb case
        return mass / t_conv[u_time]

    Fe_si = to_mass_flow(fe_val, fe_unit, rho_si)
    Fs_si = to_mass_flow(fs_val, fs_unit, rho_si)

    # 5. CONCENTRACIÓN Y TIEMPO
    st.sidebar.subheader("5. Tiempo y Entrada")
    ce_input = st.sidebar.number_input("Conc. Entrada (Ce) [0-1]", value=0.2)
    t_total = st.sidebar.number_input("Tiempo simulación", value=100.0)
    t_unit = st.sidebar.selectbox("Unidad", ["s", "min", "h", "d"], key="u_t")
    T_max = t_total * t_conv[t_unit]

    # CÁLCULOS
    t_steps = np.linspace(0, T_max, 1000)
    dt = t_steps[1] - t_steps[0]
    M_t, D_t = [M0], [D0]

    for i in range(len(t_steps)-1):
        M_next = M_t[-1] + (Fe_si - Fs_si) * dt
        M_t.append(max(M_next, 1e-6))
        dDdt = (Fe_si * ce_input) - (Fs_si * (D_t[-1] / M_t[-1]))
        D_t.append(max(D_t[-1] + dDdt * dt, 0))

    C_t = np.array(D_t) / np.array(M_t)

    # MOSTRAR CONVERSIONES
    st.subheader("📊 Resumen de Conversión (SI)")
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Masa Inicial", f"{M0:.2f} kg")
    col_r2.metric("Fe", f"{Fe_si*3600:.2f} kg/h")
    col_r3.metric("Fs", f"{Fs_si*3600:.2f} kg/h")

    if abs(Fe_si - Fs_si) < (0.01 * Fe_si):
        st.success("✨ El sistema está en Estado Estacionario (Fe ≈ Fs)")

    # GRÁFICAS
    c1, c2 = st.columns(2)
    with c1:
        fig1, ax1 = plt.subplots()
        ax1.plot(t_steps / t_conv[t_unit], C_t)
        ax1.set_title("Concentración vs Tiempo")
        ax1.yaxis.set_major_locator(ticker.MultipleLocator(0.001))
        st.pyplot(fig1)
    with c2:
        fig2, ax2 = plt.subplots()
        ax2.plot(t_steps / t_conv[t_unit], D_t, color='green')
        ax2.set_title("Masa del Compuesto (D) vs Tiempo")
        st.pyplot(fig2)

if __name__ == "__main__":
    main()
