import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Balance de Masa", layout="wide")

# Estilo personalizado para los carteles Beige Rosado
st.markdown("""
    <style>
    .beige-box {
        background-color: #F2D2BD;
        padding: 10px;
        border-radius: 5px;
        color: #5D4037;
        margin-bottom: 10px;
        border: 1px solid #E1C1A1;
    }
    .unit-hint {
        color: #BC8F8F;
        font-size: 0.85rem;
        margin-top: -15px;
        margin-bottom: 10px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🧪 Balance de Masa y Concentración")
    
    # Cartel de supuestos en Beige Rosado
    st.markdown('<div class="beige-box">💡 <b>Supuestos:</b> Buen mezclado, densidad constante y sin reacciones.</div>', unsafe_allow_html=True)

    st.sidebar.header("📥 Configuración de Variables")

    # Factores de conversión
    m_conv = {"kg": 1.0, "g": 0.001, "lb": 0.453592}
    v_conv = {"m3": 1.0, "L": 0.001, "gal": 0.00378541}
    t_conv = {"s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0}

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
    st.sidebar.markdown(f'<p class="unit-hint">SI: {rho_si} kg/m³</p>', unsafe_allow_html=True)

    # Cálculo de Masa Inicial Total (M0)
    M0 = v0_input * m_conv[v0_unit] if v0_unit in m_conv else v0_input * v_conv[v0_unit] * rho_si
    st.sidebar.markdown(f'<p class="unit-hint">SI: {M0:.3f} kg</p>', unsafe_allow_html=True)

    # 3. COMPUESTO
    st.sidebar.subheader("3. Componente de Interés")
    c_d1, c_d2 = st.sidebar.columns([2, 1])
    d0_input = c_d1.number_input("Masa inicial", value=10.0)
    d0_unit = c_d2.selectbox("Unidad", ["kg", "g", "lb", "L"], key="u_d0")
    
    D0 = d0_input * v_conv["L"] * rho_si if d0_unit == "L" else d0_input * m_conv[d0_unit]
    st.sidebar.markdown(f'<p class="unit-hint">SI: {D0:.3f} kg</p>', unsafe_allow_html=True)

    # Concentración Inicial
    c0_manual = st.sidebar.number_input("Concentración Inicial (opcional)", value=0.0, format="%.4f")
    C0 = c0_manual if c0_manual > 0 else (D0 / M0 if M0 > 0 else 0.0)
    st.sidebar.markdown(f'<p class="unit-hint">C0: {C0:.4f} kg/kg</p>', unsafe_allow_html=True)

    # 4. FLUJOS
    st.sidebar.subheader("4. Flujos")
    flow_units = ["kg/s", "kg/min", "kg/h", "L/s", "L/min", "L/h", "gal/min", "lb/min"]
    
    cf1, cf2 = st.sidebar.columns([2, 1])
    fe_val = cf1.number_input("Flujo Entrada", value=1.0)
    fe_unit = cf2.selectbox("Unidad", flow_units, key="u_fe")

    def to_kg_s(val, unit, dens):
        u_b, u_t = unit.split('/')
        mass = val * m_conv[u_b] if u_b in m_conv else val * v_conv[u_b] * dens
        return mass / t_conv[u_t]

    Fe_si = to_kg_s(fe_val, fe_unit, rho_si)
    st.sidebar.markdown(f'<p class="unit-hint">SI: {Fe_si:.5f} kg/s</p>', unsafe_allow_html=True)

    cf3, cf4 = st.sidebar.columns([2, 1])
    fs_val = cf3.number_input("Flujo Salida", value=1.0)
    fs_unit = cf4.selectbox("Unidad", flow_units, key="u_fs")
    
    Fs_si = to_kg_s(fs_val, fs_unit, rho_si)
    st.sidebar.markdown(f'<p class="unit-hint">SI: {Fs_si:.5f} kg/s</p>', unsafe_allow_html=True)

    # 5. ENTRADA Y TIEMPO
    st.sidebar.subheader("5. Parámetros de Simulación")
    ce_input = st.sidebar.number_input("Concentración Entrada", value=0.1)
    
    c_t1, c_t2 = st.sidebar.columns([2, 1])
    t_input = c_t1.number_input("Tiempo total", value=60.0)
    t_unit = c_t2.selectbox("Unidad", ["s", "min", "h", "d"], key="u_t")
    T_max = t_input * t_conv[t_unit]
    st.sidebar.markdown(f'<p class="unit-hint">SI: {T_max} s</p>', unsafe_allow_html=True)

    # --- LÓGICA DE CÁLCULO ---
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

    # --- AVISO ESTADO ESTACIONARIO ---
    st.subheader("📊 Análisis de Masa")
    if abs(Fe_si - Fs_si) < 1e-7:
        st.markdown(f'<div class="beige-box">✅ <b>Estado Estacionario Detectado:</b> Los flujos son iguales. La masa total se mantiene constante en {M0:.2f} kg.</div>', unsafe_allow_html=True)
    else:
        delta_m = M_t[-1] - M0
        st.markdown(f'<div class="beige-box">⚖️ <b>Sistema Dinámico:</b> La masa total {"aumentó" if delta_m > 0 else "disminuyó"} en {abs(delta_m):.2f} kg durante el proceso.</div>', unsafe_allow_html=True)

    # --- GRÁFICAS ---
    st.divider()
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Concentración vs Tiempo")
        fig1, ax1 = plt.subplots()
        ax1.plot(t_steps / t_conv[t_unit], C_t, color='#FFC0CB', lw=2.5) # Rosa
        ax1.set_xlabel(f"Tiempo [{t_unit}]")
        ax1.set_ylabel("Concentración [kg/kg]")
        ax1.grid(True, alpha=0.2)
        st.pyplot(fig1)
        st.metric(label=f"Concentración final (t={t_input})", value=f"{C_t[-1]:.3f} kg/kg")

    with g2:
        st.subheader("Masa vs Tiempo")
        fig2, ax2 = plt.subplots()
        ax2.plot(t_steps / t_conv[t_unit], D_t, color='#B2EC5D', lw=2.5) # Verde Manzana Pastel
        ax2.set_xlabel(f"Tiempo [{t_unit}]")
        ax2.set_ylabel("Masa [kg]")
        ax2.grid(True, alpha=0.2)
        st.pyplot(fig2)
        st.metric(label=f"Masa final del compuesto (t={t_input})", value=f"{D_t[-1]:.3f} kg")

if __name__ == "__main__":
    main()
