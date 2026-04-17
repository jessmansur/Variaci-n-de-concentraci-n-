import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Balance de Masa", layout="wide")

# Estilo personalizado
st.markdown("""
    <style>
    .pink-box {
        background-color: #FFE4E1;
        padding: 12px;
        border-radius: 8px;
        color: #5D4037;
        margin-bottom: 15px;
        border: 1px solid #FFC0CB;
    }
    .unit-hint {
        color: #BC8F8F;
        font-size: 0.85rem;
        margin-top: -15px;
        margin-bottom: 10px;
        font-weight: 500;
    }
    .validation-hint {
        color: #8B4513;
        font-size: 0.8rem;
        margin-top: -10px;
        margin-bottom: 15px;
        font-style: italic;
    }
    .footer-image-container {
        display: flex;
        justify-content: flex-end;
        padding-top: 50px;
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Función para formatear números: 1.234,56
def fmt(valor, decimales=2):
    try:
        if valor is None: return "0,00"
        # Formatear con separador de miles inglés (,) y decimal (.)
        s = f"{valor:,.{decimales}f}"
        # Intercambiar: coma por punto y punto por coma
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valor)

def main():
    st.title("🧪 Balance de Masa y Concentración")
    
    st.markdown('<div class="pink-box">💡 <b>Supuestos:</b> Buen mezclado; no hay reacciones químicas; densidades homogéneas entre contenido inicial del recipiente y flujos de circulación.</div>', unsafe_allow_html=True)

    st.sidebar.header("📥 Configuración de Variables")

    # Factores de conversión
    m_conv = {"kg": 1.0, "g": 0.001, "lb": 0.453592}
    v_conv = {"m3": 1.0, "L": 0.001, "gal": 0.00378541}
    t_conv = {"s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0}

    # 1. CONTENIDO DEL RECIPIENTE
    st.sidebar.subheader("1. Contenido del Recipiente")
    c_v1, c_v2 = st.sidebar.columns([2, 1])
    v0_input = c_v1.number_input("Cantidad inicial", value=100.0, step=0.1)
    v0_unit = c_v2.selectbox("Unidad", ["kg", "g", "L", "m3", "gal", "lb"], key="u_v0")
    
    # 2. DENSIDAD
    st.sidebar.subheader("2. Densidad (ρ)")
    c_r1, c_r2 = st.sidebar.columns([2, 1])
    rho_input = c_r1.number_input("Valor de ρ", value=1000.0, step=0.1)
    rho_unit = c_r2.selectbox("Unidad", ["kg/m³", "g/cm³"], key="u_rho")
    rho_si = rho_input if rho_unit == "kg/m³" else rho_input * 1000.0
    st.sidebar.markdown(f'<p class="unit-hint">SI: {fmt(rho_si)} kg/m³</p>', unsafe_allow_html=True)

    M0 = v0_input * m_conv[v0_unit] if v0_unit in m_conv else v0_input * v_conv[v0_unit] * rho_si
    st.sidebar.markdown(f'<p class="unit-hint">SI: {fmt(M0, 3)} kg</p>', unsafe_allow_html=True)

    # 3. COMPONENTE DE INTERÉS
    st.sidebar.subheader("3. Componente de Interés")
    c_d1, c_d2 = st.sidebar.columns([2, 1])
    d0_input = c_d1.number_input("Cantidad inicial (compuesto)", value=10.0, step=0.1)
    d0_unit = c_d2.selectbox("Unidad", ["kg", "g", "lb", "L"], key="u_d0")
    st.sidebar.markdown('<p class="validation-hint">si no se carga cantidad inicial del compuesto, se requiere cargar concentración inicial</p>', unsafe_allow_html=True)
    
    D0 = d0_input * v_conv["L"] * rho_si if d0_unit == "L" else d0_input * m_conv[d0_unit]
    st.sidebar.markdown(f'<p class="unit-hint">SI: {fmt(D0, 3)} kg</p>', unsafe_allow_html=True)

    c0_manual = st.sidebar.number_input("Concentración Inicial (opcional)", value=0.0, format="%.4f", step=0.0001)
    st.sidebar.markdown('<p class="validation-hint">si no se carga concentración inicial, se requiere cargar cantidad inicial del compuesto (en proporción masa en masa)</p>', unsafe_allow_html=True)
    
    C0 = c0_manual if c0_manual > 0 else (D0 / M0 if M0 > 0 else 0.0)
    st.sidebar.markdown(f'<p class="unit-hint">Concentración calculada: {fmt(C0, 4)} kg/kg</p>', unsafe_allow_html=True)

    # 4. FLUJOS
    st.sidebar.subheader("4. Flujos")
    flow_units = ["kg/s", "kg/min", "kg/h", "L/s", "L/min", "L/h", "gal/min", "lb/min"]
    
    cf1, cf2 = st.sidebar.columns([2, 1])
    fe_val = cf1.number_input("Flujo de Entrada", value=1.0, format="%.3f", step=0.001)
    fe_unit = cf2.selectbox("Unidad", flow_units, key="u_fe")
    
    # Función auxiliar para conversión de flujos
    def to_kg_s_fixed(val, unit, dens, mc, vc, tc):
        u_b, u_t = unit.split('/')
        mass = val * mc[u_b] if u_b in mc else val * vc[u_b] * dens
        return mass / tc[u_t]

    Fe_si = to_kg_s_fixed(fe_val, fe_unit, rho_si, m_conv, v_conv, t_conv)
    st.sidebar.markdown(f'<p class="unit-hint">SI: {fmt(Fe_si, 5)} kg/s</p>', unsafe_allow_html=True)

    cf3, cf4 = st.sidebar.columns([2, 1])
    fs_val = cf3.number_input("Flujo de Salida", value=1.0, format="%.3f", step=0.001)
    fs_unit = cf4.selectbox("Unidad", flow_units, key="u_fs")
    Fs_si = to_kg_s_fixed(fs_val, fs_unit, rho_si, m_conv, v_conv, t_conv)
    st.sidebar.markdown(f'<p class="unit-hint">SI: {fmt(Fs_si, 5)} kg/s</p>', unsafe_allow_html=True)

    # 5. PARÁMETROS SIMULACIÓN
    st.sidebar.subheader("5. Parámetros de Simulación")
    ce_input = st.sidebar.number_input("Concentración de Entrada", value=0.1, format="%.4f", step=0.0001)
    st.sidebar.markdown('<p class="validation-hint">concentración solicitada en proporción masa en masa</p>', unsafe_allow_html=True)
    
    c_t1, c_t2 = st.sidebar.columns([2, 1])
    t_input = c_t1.number_input("Tiempo total", value=60.0, step=1.0)
    t_unit = c_t2.selectbox("Unidad", ["s", "min", "h", "d"], key="u_t")
    T_max = t_input * t_conv[t_unit]

    # --- CÁLCULO ---
    t_steps = np.linspace(0, T_max, 1000)
    dt = t_steps[1] - t_steps[0]
    M_t, D_t = [M0], [M0 * C0]

    for i in range(len(t_steps)-1):
        M_next = M_t[-1] + (Fe_si - Fs_si) * dt
        M_t.append(max(M_next, 1e-6))
        dDdt = (Fe_si * ce_input) - (Fs_si * (D_t[-1] / M_t[-1]))
        D_t.append(max(D_t[-1] + dDdt * dt, 0))

    M_t, D_t, C_t = np.array(M_t), np.array(D_t), np.array(D_t) / np.array(M_t)

    # --- RESULTADOS ---
    st.subheader("📊 Análisis de Masa")
    delta_m = M_t[-1] - M0
    if abs(Fe_si - Fs_si) < 1e-7:
        st.markdown(f'<div class="pink-box">✅ <b>Estado Estacionario:</b> Masa constante en {fmt(M0)} kg.</div>', unsafe_allow_html=True)
    else:
        txt = "aumentó" if delta_m > 0 else "disminuyó"
        st.markdown(f'<div class="pink-box">⚖️ <b>Sistema Dinámico:</b> La masa {txt} {fmt(abs(delta_m))} kg.</div>', unsafe_allow_html=True)

    # --- GRÁFICAS ---
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        fig1, ax1 = plt.subplots()
        ax1.plot(t_steps / t_conv[t_unit], C_t, color='#FFC0CB', lw=2)
        ax1.set_title("Concentración vs Tiempo")
        ax1.set_ylabel("Concentración [kg/kg]")
        # Configurar formato de ejes para evitar amontonamiento
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: fmt(x, 3)))
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.plot(t_steps / t_conv[t_unit], D_t, color='#B2EC5D', lw=2)
        ax2.set_title("Masa del Compuesto vs Tiempo")
        ax2.set_ylabel("Masa [kg]")
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: fmt(x, 1)))
        st.pyplot(fig2)

    # --- FOOTER SEGURO ---
    if os.path.exists("footer_image.png"):
        st.markdown('<div class="footer-image-container">', unsafe_allow_html=True)
        st.image("footer_image.png", width=250)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
