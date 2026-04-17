import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Balance de Masa Transitorio", layout="wide")

def main():
    st.title("🧪 Variación de Concentración en Tiempo Real")
    
    # --- CARTELES DE SUPUESTOS ---
    st.warning("⚠️ **Supuestos del modelo:**\n"
               "* Se supone **buen mezclado** en el contenedor; la concentración de salida es igual a la del contenido.\n"
               "* Se supone **densidad similar** entre el volumen en el contenedor y el flujo de entrada.\n"
               "* Se supone que **no hay reacciones químicas** dentro del contenedor.")

    # --- BARRA LATERAL: ENTRADA DE DATOS ---
    st.sidebar.header("📥 Variables de Entrada")
    
    # Masa inicial y compuesto
    col_m1, col_m2 = st.sidebar.columns(2)
    m0_val = col_m1.number_input("Masa Inicial (M0)", value=100.0)
    m_unit = col_m2.selectbox("Unidad Masa", ["kg", "g", "lb", "ton"])
    
    d0_val = st.sidebar.number_input("Masa inicial compuesto (D0)", value=10.0)
    
    # Volumen Inicial
    col_v1, col_v2 = st.sidebar.columns(2)
    v0_val = col_v1.number_input("Volumen Inicial (V0)", value=1000.0)
    v_unit = col_v2.selectbox("Unidad Vol.", ["L", "m3", "cm3", "gal"])
    
    # Flujos
    fe = st.sidebar.number_input("Flujo entrada (Fe) [Unidad Vol/min]", value=10.0)
    fs = st.sidebar.number_input("Flujo salida (Fs) [Unidad Vol/min]", value=10.0)
    
    # Concentraciones
    ce_tipo = st.sidebar.radio("Tipo de Conc. Entrada", ["Fracción (0-1)", "Porcentaje (%)"])
    ce_val = st.sidebar.number_input("Conc. Entrada (Ce)", value=0.5 if ce_tipo == "Fracción (0-1)" else 50.0)
    
    # Tiempo
    col_t1, col_t2 = st.sidebar.columns(2)
    t_final = col_t1.number_input("Tiempo total", value=60.0)
    t_unit = col_t2.selectbox("Unidad Tiempo", ["min", "s", "h", "d"])

    # --- CONVERSIÓN DE UNIDADES AL SI ---
    # Conversión Masa a kg
    m_conv = {"kg": 1.0, "g": 0.001, "lb": 0.453592, "ton": 1000.0}
    M0 = m0_val * m_conv[m_unit]
    D0 = d0_val * m_conv[m_unit]
    
    # Conversión Volumen a m3
    v_conv = {"m3": 1.0, "L": 0.001, "cm3": 1e-6, "gal": 0.00378541}
    V0 = v0_val * v_conv[v_unit]
    Fe_si = (fe * v_conv[v_unit]) / 60 # m3/s
    Fs_si = (fs * v_conv[v_unit]) / 60 # m3/s
    
    # Conversión Tiempo a s
    t_conv = {"s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0}
    T_max = t_final * t_conv[t_unit]
    
    # Concentración Ce (Normalizada a fracción)
    Ce = ce_val if ce_tipo == "Fracción (0-1)" else ce_val / 100.0
    C0 = D0 / M0 if M0 > 0 else 0

    # --- LÓGICA DE CÁLCULO (BALANCE) ---
    # Verificación de estado estacionario (1% tolerancia)
    diff_flujo = abs(Fe_si - Fs_si)
    if Fe_si > 0 and (diff_flujo / Fe_si) <= 0.01:
        st.success("✅ **Sistema Estacionario detectado:** La variación de volumen es despreciable (Fe ≈ Fs).")
    
    # Resolución temporal
    t_steps = np.linspace(0, T_max, 200)
    V_t = V0 + (Fe_si - Fs_si) * t_steps
    
    # Evitar volúmenes negativos o cero
    V_t = np.maximum(V_t, 1e-9)
    
    # Integración del componente: dD/dt = Fe*Ce - Fs*(D/V)
    # Usamos Euler simple para la integración temporal
    dt = t_steps[1] - t_steps[0]
    D_t = [D0]
    for i in range(len(t_steps)-1):
        dDdt = Fe_si * Ce - Fs_si * (D_t[-1] / V_t[i])
        D_t.append(D_t[-1] + dDdt * dt)
    
    D_t = np.array(D_t)
    C_t = D_t / (V_t * 1000) # Concentración (Masa Compuesto / Masa Total aproximada)

    # --- VISUALIZACIÓN ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Gráfica de Concentración C(t)")
        fig, ax = plt.subplots()
        ax.plot(t_steps / t_conv[t_unit], C_t, color='blue', lw=2)
        ax.set_xlabel(f"Tiempo [{t_unit}]")
        ax.set_ylabel("Concentración (fracción)")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

    with col2:
        st.subheader("Masa del Compuesto D(t)")
        fig2, ax2 = plt.subplots()
        ax2.plot(t_steps / t_conv[t_unit], D_t, color='green', lw=2)
        ax2.set_xlabel(f"Tiempo [{t_unit}]")
        ax2.set_ylabel("Masa del compuesto [kg]")
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)

if __name__ == "__main__":
    main()
