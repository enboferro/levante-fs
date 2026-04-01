import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD FS PRO", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state

# 1. INICIALIZACIÓN SEGURA
if 'js' not in ss:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    ss.js = [{"n":n[i],"t_t":0.0,"ini":None,"p":False,"g":0,"t":0,"per":0,"rec":0} for i in range(15)]
if 'ml' not in ss: 
    ss.ml, ss.mr, ss.fl, ss.fr, ss.t_a, ss.i_c, ss.run = 0, 0, 0, 0, 0.0, None, False

# 2. LÓGICA DE TIEMPO (Ahora después de la inicialización)
ah = time.time()
t_disp = ss.t_a 
if ss.run and ss.i_c:
    t_disp += (ah - ss.i_c)

st.markdown("""<style>
.stApp{background:#f8f9fa}.m-box{background:white;padding:15px;border-radius:12px;text-align:center;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.j-card{background:white;border-radius:8px;padding:8px;margin-bottom:4px;border-left:5px solid #ccc;box-shadow:0 2px 3px rgba(0,0,0,0.05)}
.p-act{border-left:5px solid #003D7A!important}
</style>""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1,4,1])
with c1: st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=50)
with c2: riv = st.text_input("R", "RIVAL", label_visibility="collapsed").upper()
with c3: 
    if st.button("🔄"): ss.clear(); st.rerun()

m1, m2, m3 = st.columns([2,3,2])
with m1:
    st.markdown(f"<div class='m-box'><h3>LUD</h3><h1 style='color:#003D7A'>{ss.ml}</h1><p>F: {ss.fl}</p></div>", unsafe_allow_html=True)
    if st.button("⚽ GOL LUD", use_container_width=True): ss.ml+=1; st.rerun()
    if st.button("⚠️ FALTA LUD", use_container_width=True): ss.fl+=1; st.rerun()
with m2:
    mm, sv = divmod(int(t_disp), 60)
    st.markdown(f"<div class='m-box'><h1 style='font-size:4rem'>{mm:02d}:{sv:02d}</h1></div>", unsafe_allow_html=True)
    if not ss.run:
        if st.button("▶ INICIAR", type="primary", use_container_width=True):
            ss.i_c, ss.run = ah, True
            for j in ss.js: 
                if j["p"]: j["ini"] = ah
            st.rerun()
    else:
        if st.button("⏸ PAUSAR", type="secondary", use_
