import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="LUD FS - ANALYTICS PRO", layout="wide", page_icon="🐸")

# Autorefresh cada 1 segundo
st_autorefresh(interval=1000, key="futsalrefresh")

# Alias para session_state
ss = st.session_state

# 2. ESTILOS CSS (DISEÑO GIGANTE)
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    .header-box { background: linear-gradient(90deg, #003D7A, #7A0019); padding: 15px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px; }
    .reloj-box { background-color: #1E1E1E; border: 5px solid #FFD700; border-radius: 30px; padding: 20px; }
    .reloj-text { color: white; font-size: 5rem !important; font-weight: bold; margin: 0; text-align: center; line-height: 1; }
    .marcador-card { padding: 20px; border-radius: 20px; color: white; text-align: center; min-height: 220px; }
    .stButton>button { height: 3.5rem; font-size: 1.1rem !important; border-radius: 10px; font-weight: bold; }
    .jugador-card { background: white; padding: 12px; border-radius: 15px; border-left: 10px solid #D3D3D3; margin-bottom: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); }
    h1 { font-size: 3rem !important; margin: 0; }
    h2 { font-size: 2rem !important; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. INICIALIZACIÓN DE VARIABLES
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"Jugador {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt = 0.0, 0.0, "T1"
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig = False, None
if 'pos_activa' not in ss: ss.pos_activa = "NEUTRAL"
if 't_pos_lud' not in ss: ss.t_pos_lud = 0.0
if 't_pos_riv' not in ss: ss.t_pos_riv = 0.0
if 't_pos_neu' not in ss: ss.t_pos_neu = 0.0
if 'last_pos_check' not in ss: ss.last_pos_check = time.time()

# 4. LÓGICA DE POSESIÓN
ahora = time.time()
if ss.ac:
    diff = ahora - ss.last_pos_check
    if ss.pos_activa == "LUD": ss.t_pos_lud += diff
    elif ss.pos_activa == "RIVAL": ss.t_pos_riv += diff
    else: ss.t_pos_neu += diff
ss.last_pos_check = ahora

# 5. CABECERA (Rival y Fecha)
with st.container():
    c_logo, c_info, c_reset = st.columns([1, 4, 1])
    with c_logo:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=80)
    with c_info:
        col_r, col_f = st.columns(2)
        rival_nombre = col_r.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()
        fecha_partido = col_f.date_input("FECHA", datetime.now(), label_visibility="collapsed")
        st.markdown(f"<div class='header-box'><h1>LEVANTE UD vs {rival_nombre}</h1></div>", unsafe_allow_html=True)
    with c_reset:
        if st.button("⚠️ RESET", key="btn_reset_total", use_container_width=True):
            ss.clear()
            st.rerun()

# 6. MARCADOR Y RELOJ
col_l, col_c, col_r = st.columns([2, 3, 2])

with col_l:
    color_lud = "background-color:#FF0000;" if ss.fl >= 5 else "background-color:#003D7A;"
    st.markdown(f"<div class='marcador-card' style='{color_lud}'><h2>LUD</h2><h1 style='font-size:6rem; color:white;'>{ss.ml}</h1><p>FALTAS: {ss.fl}</p></div>", unsafe_allow_html=True)
    st.write("")
    cl1, cl2 = st.columns(2)
    if cl1.button("⚽ GOL", key="gol_l", use_
