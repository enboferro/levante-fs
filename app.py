import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Configuración para iPad
st.set_page_config(page_title="LUD FS - Control", layout="wide")

# Estilos para que los números se vean oscuros y grandes
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    h1, h2, h3 { color: #000000 !important; }
    .tiempo-label { font-size: 24px; font-weight: bold; color: #000000; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = [
        {"id": i, "nombre": f"Jugador {i+1}", "t1": 0.0, "t2": 0.0, 
         "inicio": None, "pista": False, "ent": 0, "goles": 0} for i in range(14)
    ]
if 'parte' not in st.session_state: st.session_state.parte = "1ª Parte"
if 'f_lud' not in st.session_state: st.session_state.f_lud = 0
if 'f_riv' not in st.session_state: st.session_state.f_riv = 0
if 'm_lud' not in st.session_state: st.session_state.m_lud = 0
if 'm_riv' not in st.session_state: st.session_state.m_riv = 0
if 'activo' not in st.session_state: st.session_state.activo = False

# --- CABECERA Y MARCADOR ---
st.title("🐸 LUD FS - Match Center")

# Selector de Parte del Partido
st.session_state.parte = st.radio("Periodo Actual:", ["1ª Parte", "2ª Parte"], horizontal=True)

with st.container(border=True):
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.subheader("🏠 LEVANTE UD")
        st.title(f"{st.session_state.m_lud}")
        if st.button("⚽ GOL LUD"): 
            st.session_state.m_lud += 1
            st.rerun()
        st.write(f"**Faltas:** {st.session_state.f_lud}")
        if st.button("+ Falta LUD"): 
            st.session_state.f_lud += 1
            st.rerun()
    with c2:
        st.write("---")
        if st.button("🔄 RESET"): st.session_state.clear(); st.rerun()
    with c3:
        rival = st.text_input("Rival:", "Rival")
        st.title(f"{st.session_state.m_riv}")
        if st.button("⚽ GOL RIVAL"): 
            st.session_state.m_riv += 1
            st.rerun()
        st.write(f"**Faltas:** {st.session_state.f_riv}")
        if st.button("+ Falta RIVAL"): 
            st.session_state.f_riv += 1
            st.rerun()

# --- CONTROL DEL RELOJ ---
st.divider()
if not st.session_state.activo:
    if st.button("▶ REANUDAR RELOJ (TIEMPO DE JUEGO)", type="primary"):
        st.session_state.activo = True
        t = time.time()
        for j in st.session_state.jugadores:
            if j["pista"]: j["inicio"] = t
        st.rerun()
else:
    if st.button("⏸ PAUSAR RELOJ (BALÓN PARADO)", type
