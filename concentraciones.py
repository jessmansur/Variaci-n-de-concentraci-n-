import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Balance de Masa", layout="wide")

def main():
    st.title("🧪 Balance de Masa y Concentración")
    
    st.info("💡 **Supuestos:** Buen mezclado, densidad constante y sin reacciones.")

    st.sidebar.header("📥 Configuración de Variables")

    # 1. CONTENIDO INICIAL
    st.sidebar.subheader("1. Contenido del Contenedor")
    c_v1, c_v2 = st.sidebar.columns([2, 1])
    v0_input = c_v1.number_input("Cantidad inicial", value=100.0)
    v0_unit = c_v2.selectbox("Unidad", ["kg", "g", "L", "m3", "gal", "lb"], key="u_v0")

    # 2. DENSIDAD
    st.sidebar.subheader("2. Densidad (ρ)")
    c_r1, c_r2 = st.sidebar.columns([2, 1])
    rho_input = c_r1.number_input("Valor de ρ", value=1000.0)
    rho_unit = c_r2.selectbox("Unidad", ["kg/m³", "g/cm³"], key="u_rho")
    rho_si = rho_input if rho_unit == "kg/m³" else rho_input * 1000.0

    # 3. COMPUESTO (D0 y C0)
    st.sidebar.subheader("3. Componente de Interés")
    c_d1, c_d2 = st.sidebar.columns([2, 1])
    d0_input = c_d1.number_input("Masa inicial D0", value=10.0)
    d0_unit = c_d2.selectbox("Unidad", ["kg", "g", "lb", "L"], key="u_d0")

    # Conversiones base
    m_conv = {"kg": 1.0, "g": 0.001, "lb": 0.453592}
    v_conv = {"m3": 1.0, "L": 0.001, "gal": 0.00378541}
    t_conv = {"s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0}

    # Masa Inicial Total (M0) y del Compuesto (D0)
    M0 = v0_input * m_conv[v0_unit] if v0_unit in m_conv else v0_input * v_conv[v0_unit] * rho_si
    D0 = d0_input * v_conv["L"] * rho_si if d0_unit == "L" else d0_input * m_conv[d0_unit]

    # Concentración Inicial (C0)
    c0_manual = st.sidebar.number_input("Concentración Inicial C0 (opcional)", value=0.0, format="%.4f", help="Si es 0, se calcula como D0/M0")
    C0 = c0_manual if c0_manual > 0 else D0 / M0

    # 4. FLUJOS
    st.sidebar.subheader("4. Flujos")
    flow_units = ["kg/s", "kg/min", "kg/h", "L/s", "L/min", "L/h", "gal/min", "lb/min"]
    
    cf1, cf2 = st.sidebar.columns([2, 1])
    fe_val = cf1.number_input("Flujo Entrada", value=1.0)
    fe_unit = cf2.selectbox("Unidad", flow_units, key="u_fe")

    cf3, cf4 = st.sidebar.columns([2, 1])
    fs_val = cf3.number_input("Flujo Salida", value=1.0)
    fs_unit = cf4.selectbox("Unidad", flow_units, key="u_fs")

    def to_kg_s(val, unit, dens):
        u_b, u_t = unit.split('/')
        mass = val * m_conv[u_b] if u_b in m_conv else val * v_conv[u_b] * dens
        return mass / t_conv[u_t]

    Fe_si = to_kg_s(fe_val, fe_unit, rho_si)
    Fs_si = to_kg_s(fs_val, fs_unit, rho_si)

    # 5. ENTRADA Y TIEMPO
    ce_input = st.sidebar.number_input("Conc. Entrada (Ce)", value=0.1)
    t_input = st.sidebar.number_input("Tiempo total", value=60.0)
    t_unit = st.sidebar.selectbox("Unidad", ["s", "min", "h", "d"], key="u_t")
    T_max = t_input * t_conv[t_unit]

    # CÁLCULOS
    t_steps = np.linspace(0, T_max, 1000)
    dt = t_steps[1] - t_steps[0]
    M_t, D_t = [M0], [M0 * C0]

    for i in range(len(t_steps)-1):
        M_next = M_t[-1] + (Fe_si - Fs_si) * dt
        M_t.append(max(M_next, 1e-6))
        dDdt = (Fe_si * ce_input) - (Fs_si * (D_t[-1] / M_t[-1]))
        D_t.append(max(D_t[-1] + dDdt * dt, 0))

    M_t, D_t = np.array(M_t), np.array(D_t)
    C_t = D_t / M_t

    # MÉTRICAS NORMALIZADAS
    st.subheader("📊 Resumen de Flujos Masicos")
    m1, m2 = st.columns(2)
    # Normalización automática para la visualización
    if Fe_si < 0.01: label, factor = "kg/h", 3600
    elif Fe_si > 10: label, factor = "kg/s", 1
    else: label, factor = "kg/min", 60

    m1.metric("Entrada Real", f"{Fe_si * factor:.3f} {label}")
    m2.metric("Salida Real", f"{Fs_si * factor:.3f} {label}")

    # GRÁFICAS
    g1, g2 = st.columns(2)
    with g1:
        fig1, ax1 = plt.subplots()
        ax1.plot(t_steps / t_conv[t_unit], C_t)
        ax1.set_title("Evolución de la Concentración")
        ax1.set_xlabel(f"Tiempo [{t_unit}]")
        ax1.set_ylabel("Concentración [kg compuesto / kg total]")
        ax1.grid(True, alpha=0.3)
        st.pyplot(fig1)

    with g2:
        fig2, ax2 = plt.subplots()
        ax2.plot(t_steps / t_conv[t_unit], D_t, color='green')
        ax2.set_title("Masa del Compuesto en el Tiempo")
        ax2.set_xlabel(f"Tiempo [{t_unit}]")
        ax2.set_ylabel("Masa [kg]")
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)

if __name__ == "__main__":
    main()
