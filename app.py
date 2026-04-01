import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN
st.set_page_config(page_title="LUD PRO", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state

# Estilos divididos para evitar cortes de línea largos
style = """
<style>
    .stApp{background:#F0F2F6}
    .h-box{background:linear-gradient(90deg,#003D7A,#7A0019);padding:10px;border-radius:10px;color:white;text-align:center}
    .rel-box{background:#1E1E1E;border:3px solid #FFD700;border-radius:20px;padding:10px}
    .rel-txt{color:white;font-size:4rem!important;font-weight:bold;text-align:center;margin:0}
    .m-card{padding:15px;border-radius:15px;color:white;text-align:center;min-height:180px}
    .stButton>button{height:3rem;font-weight:bold}
    .j-card{background:white;padding:8px;border-radius:10px;border-left:8px solid #D3D3D3;margin-bottom:5px}
    .pist{text-align:center;padding:10px;background:white;border-radius:10px;border:2px solid #003D7A;margin-top:10px}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss:
    ss.rt1, ss.rt2, ss.pt, ss.ml, ss.mr, ss.fl, ss.fr = 0.0, 0.0, "T1", 0, 0, 0, 0
if 'ac' not in ss:
    ss.ac, ss.ig, ss.pos = False, None, "NEU"
if 'tpl' not in ss:
    ss.tpl, ss.tpr, ss.tpn, ss.lpc = 0.0, 0.0, 0.0, time.time()

now = time.time()
if ss.ac:
    d = now - ss.lpc
    if ss.pos == "LUD": ss.tpl += d
    elif ss.pos == "RIV": ss.tpr += d
    else: ss.tpn += d
ss.lpc = now

# 3. CABECERA
cl, ci, cr = st.columns([1, 4, 1])
cl.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=60)
with ci:
    r1, r2 = st.columns(2)
    rvn = r1.text_input("RIV", "RIVAL", key="input_riv", label_visibility="collapsed").upper()
    fp = r2.date_input("FEC", datetime.now(), key="input_
