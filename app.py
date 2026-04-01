import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="LUD FS - Match Center", layout="wide")

# Estilos CSS para el iPad (Botones grandes y legibles)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .st-emotion-cache-12w0qpk { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES ---
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = [
        {"id": i, "nombre": f"Jugador {i+1}", "total": 0.0, "inicio": None, 
         "pista": False, "ent": 0, "goles": 0} for i in range(14)
    ]
if 'faltas_lud' not in st.session_state: st.session_state.faltas_lud = 0
if 'faltas_rival' not in st.session_state: st.session_state.faltas_rival = 0
if 'marcador_lud' not in st.session_state: st.session_state.marcador_lud = 0
if 'marcador_rival' not in st.session_state: st.session_state.marcador_rival = 0
if 'activo' not in st.session_state: st.session_state.activo = False

# --- CABECERA Y MARCADOR ---
st.title("🐸 Levante UD FS - Panel de Control")

# Sección de Marcador y Faltas
with st.container(border=True):
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.subheader("🏠 LEVANTE UD")
        st.title(f"{st.session_state.marcador_lud}")
        c1, c2 = st.columns(2)
        if c1.button("⚽ GOL LUD", key="gol_lud"): st.session_state.marcador_lud += 1; st.rerun()
        if c2.button("❌ -1 GOL", key="reset_lud"): st.session_state.marcador_lud -= 1; st.rerun()
        st.warning(f"Faltas: {st.session_state.faltas_lud}")
        f1, f2 = st.columns(2)
        if f1.button("+ Falta LUD"): st.session_state.faltas_lud += 1; st.rerun()
        if f2.button("Reset Faltas LUD"): st.session_state.faltas_lud = 0; st.rerun()

    with col2:
        st.write("")
        st.header("VS")
        if st.button("🔄 RESET TODO"): st.session_state.clear(); st.rerun()

    with col3:
        rival_nombre = st.text_input("Rival:", "Rival")
        st.title(f"{st.session_state.marcador_rival}")
        c3, c4 = st.columns(2)
        if c3.button("⚽ GOL RIVAL"): st.session_state.marcador_rival += 1; st.rerun()
        if c4.button("❌ -1 GOL", key="reset_riv"): st.session_state.marcador_rival -= 1; st.rerun()
        st.error(f"Faltas: {st.session_state.faltas_rival}")
        f3, f4 = st.columns(2)
        if f3.button("+ Falta RIVAL"): st.session_state.faltas_rival += 1; st.rerun()
        if f4.button("Reset Faltas RIVAL"): st.session_state.faltas_rival = 0; st.rerun()

# --- CONTROL DEL TIEMPO ---
st.divider()
if not st.session_state.activo:
    if st.button("▶ REANUDAR RELOJ DE JUEGO", type="primary"):
        st.session_state.activo = True
        t = time.time()
        for j in st.session_state.jugadores:
            if j["pista"]: j["inicio"] = t
        st.rerun()
else:
    if st.button("⏸ PAUSAR (BALÓN PARADO)", type="secondary"):
        st.session_state.activo = False
        t = time.time()
        for j in st.session_state.jugadores:
            if j["pista"] and j["inicio"]:
                j["total"] += t - j["inicio"]
                j["inicio"] = None
        st.rerun()

# --- GESTIÓN DE JUGADORES ---
st.subheader("🏃‍♂️ Plantilla y Rotaciones")
for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        j_idx = i + idx
        j = st
