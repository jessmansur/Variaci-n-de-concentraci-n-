import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Balance de Masa Transitorio", layout="wide")

def main():
    st.title("🧪 Variación de Concentración (Balance de Masa)")
    
    # --- CARTELES DE SUPUESTOS ---
    st.warning("⚠️ **Supuestos del modelo:**\n"
               "* Se supone **buen mezclado** en el contenedor; la concentración de salida es igual a la del contenido.\n"
               "* Se supone **densidad similar** entre el volumen en el contenedor y el flujo de entrada.\n"
               "* Se supone que **no hay reacciones químicas** dentro del contenedor.")

    # --- BARRA LATERAL: ENTRADA DE DATOS ---
    st.sidebar.header("📥 Variables de Entrada")
    
    # 1. Densidad (Variable Crítica)
    st.sidebar.subheader("Propiedades Físicas")
    rho_val = st.sidebar.number_input("Densidad de la solución (ρ)", value=1000.0)
    rho_unit = st.sidebar.selectbox("Unidad Densidad", ["kg/m³", "g/cm³"])
    
    # Conversión de densidad a kg/m3 (SI)
    rho_si = rho_val if rho_unit == "kg/m³" else rho_val * 1000.0

    # 2. Masa inicial del contenedor
    col_m1, col_m2 = st.sidebar.columns(2)
    m0_val = col_m1.number_input("Masa Total Inicial (M0)", value=100.0)
    m_unit = col_m2.selectbox("Unidad Masa M0", ["kg", "g", "lb", "ton"])
    
    # 3. Masa inicial del compuesto (D0) con unidades
    col_d1, col_d2 = st.sidebar.columns(2)
    d0_val = col_d1.number_input("Masa inicial compuesto (D0)", value=10.0)
    d_unit = col_d2.selectbox("Unidad Masa D0", ["kg", "g", "L"])
    
    # 4. Volumen Inicial
    col_v1, col_v2 = st.sidebar.columns(2)
    v0_val = col_v1.number_input("Volumen Inicial (V0)", value=100.0)
    v_unit = col_v2.selectbox("Unidad Vol.", ["L", "m3", "cm3", "gal"])
    
    # 5. Flujos (Volumétricos)
    fe_vol = st.sidebar.number_input("Flujo entrada (Fe) [Vol/min]", value=1.0)
    fs_vol = st.sidebar.number_input("Flujo salida (Fs) [Vol/min]", value=1.0)
    
    # 6. Concentraciones y Tiempo
    ce_tipo = st.sidebar.radio("Tipo de Conc. Entrada", ["Fracción (0-1)", "Porcentaje (%)"])
    ce_val = st.sidebar.number_input("Conc. Entrada (Ce)", value=0.5 if ce_tipo == "Fracción (0-1)" else 50.0)
    
    t_final = st.sidebar.number_input("Tiempo total", value=60.0)
    t_unit = st.sidebar.selectbox("Unidad Tiempo", ["min", "s", "h", "d"])

    # --- CONVERSIÓN DE UNIDADES AL SI (kg, m3, s) ---
    m_conv = {"kg": 1.0, "g": 0.001, "lb": 0.453592, "ton": 1000.0}
    v_conv = {"m3": 1.0, "L": 0.001, "cm3": 1e-6, "gal": 0.00378541}
    t_conv = {"s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0}

    # Si la unidad de D0 es Litros, usamos la densidad para pasar a kg
    if d_unit == "L":
        D0 = d0_val * v_conv["L"] * rho_si
    else:
        D0 = d0_val * m_conv[d_unit]

    M0 = m0_val * m_conv[m_unit]
    V0_m3 = v0_val * v_conv[v_unit]
    T_max = t_final * t_conv[t_unit]
    Ce = ce_val if ce_tipo == "Fracción (0-1)" else ce_val / 100.0

    # --- CONVERSIONES AUTOMÁTICAS BASADAS EN ρ ---
    M_from_V0 = V0_m3 * rho_si
    Fe_masa = (fe_vol * v_conv[v_unit] * rho_si) / 60  # kg/s
    Fs_masa = (fs_vol * v_conv[v_unit] * rho_si) / 60  # kg/s

    # Mostrar conversiones automáticas
    st.subheader("🔄 Conversiones Automáticas (Sistema Internacional)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Masa de V0 (calc)", f"{M_from_V0:.2f} kg")
    c2.metric("Flujo Entrada (Masa)", f"{Fe_masa*60:.2f} kg/min")
    c3.metric("Flujo Salida (Masa)", f"{Fs_masa*60:.2f} kg/min")

    # --- LÓGICA DE CÁLCULO (BALANCE DE MASA) ---
    diff_flujo = abs(Fe_masa - Fs_masa)
    if Fe_masa > 0 and (diff_flujo / Fe_masa) <= 0.01:
        st.success("✅ **Sistema Estacionario detectado:** La masa total se mantiene constante (Fe ≈ Fs).")
    
    t_steps = np.linspace(0, T_max, 500)
    dt = t_steps[1] - t_steps[0]
    
    # Evolución de la Masa Total y Masa del Compuesto
    M_t = [M0]
    D_t = [D0]
    
    for i in range(len(t_steps)-1):
        # Masa total: dM/dt = Fe - Fs
        M_next = M_t[-1] + (Fe_masa - Fs_masa) * dt
        M_t.append(max(M_next, 1e-9))
        
        # Masa compuesto: dD/dt = Fe*Ce - Fs*(D/M)
        dDdt = Fe_masa * Ce - Fs_masa * (D_t[-1] / M_t[-1])
        D_t.append(max(D_t[-1] + dDdt * dt, 0))
    
    M_t = np.array(M_t)
    D_t = np.array(D_t)
    C_t = D_t / M_t

    # --- VISUALIZACIÓN ---
    st.divider()
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("Gráfica de Concentración C(t)")
        fig, ax = plt.subplots()
        ax.plot(t_steps / t_conv[t_unit], C_t, color='#1f77b4', lw=2)
        ax.set_xlabel(f"Tiempo [{t_unit}]")
        ax.set_ylabel("Concentración (masa/masa)")
        # Ajuste de escala vertical: saltos mínimos de 0.001
        ax.yaxis.set_major_locator(ticker.MultipleLocator(0.001))
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

    with col_graf2:
        st.subheader("Masa del Compuesto D(t)")
        fig2, ax2 = plt.subplots()
        ax2.plot(t_steps / t_conv[t_unit], D_t, color='#2ca02c', lw=2)
        ax2.set_xlabel(f"Tiempo [{t_unit}]")
        ax2.set_ylabel("Masa del compuesto [kg]")
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)

if __name__ == "__main__":
    main()
