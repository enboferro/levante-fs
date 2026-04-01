import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD FS PRO", layout="wide", page_icon="🐸")
st_autorefresh(interval=1000, key="futsalrefresh")
ss = st.session_state

st.markdown("""<style>
    .stApp { background-color: #F0F2F6; }
    .header-box { background: linear-gradient(90deg, #003D7A, #7A0019); padding: 15px; border-radius: 15px; color: white; text-align: center; }
    .reloj-box { background-color: #1E1E1E; border: 5px solid #FFD700; border-radius: 30px; padding: 20px; }
    .reloj-text { color: white; font-size: 5rem !important; font-weight: bold; text-align: center; margin: 0; }
    .marcador-card { padding: 20px; border-radius: 20px; color: white; text-align: center; min-height: 200px; }
    .stButton>button { height: 3.5rem; font-weight: bold; border-radius: 10px; }
    .jugador-card { background: white; padding: 10px; border-radius: 12px; border-left: 10px solid #D3D3D3; margin-bottom: 10px; }
</style>""", unsafe_allow_html=True)

if 'js' not in ss:
    ss.js = [{"id":i,"n":f"Jugador {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt, ss.ml, ss.mr, ss.fl, ss.fr = 0.0, 0.0, "T1", 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig, ss.pos_activa = False, None, "NEUTRAL"
if 't_pos_lud' not in ss: ss.t_pos_lud, ss.t_pos_riv, ss.t_pos_neu = 0.0, 0.0, 0.0
if 'lpc' not in ss: ss.lpc = time.time()

ahora = time.time()
if ss.ac:
    diff = ahora - ss.lpc
    if ss.pos_activa == "LUD": ss.t_pos_lud += diff
    elif ss.pos_activa == "RIVAL": ss.t_pos_riv += diff
    else: ss.t_pos_neu += diff
ss.lpc = ahora

with st.container():
    c_l, c_i, c_r = st.columns([1, 4, 1])
    c_l.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=80)
    with c_i:
        r_col, f_col = st.columns(2)
        riv_n = r_col.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()
        f_p = f_col.date_input("FECHA", datetime.now(), label_visibility="collapsed")
        st.markdown(f"<div class='header-box'><h1>LUD vs {riv_n}</h1></div>", unsafe_allow_html=True)
    if c_r.button("⚠️ RESET"): ss.clear(); st.rerun()

col_l, col_c, col_r = st.columns([2, 3, 2])
with col_l:
    c_lud = "#FF0000" if ss.fl >= 5 else "#003D7A"
    st.markdown(f
