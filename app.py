import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. CONFIG
st.set_page_config(page_title="LUD FS", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state

# 2. INICIALIZACIÓN
if 'js' not in ss:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    ss.js = [{"n":x,"t_t":0.0,"ini":None,"p":False,"g":0,"t":0,"per":0,"rec":0} for x in n]
if 'ml' not in ss:
    ss.ml, ss.mr, ss.fl, ss.fr, ss.t_a, ss.i_c, ss.run = 0, 0, 0, 0, 0.0, None, False

ah = time.time()
td = ss.t_a + (ah - ss.i_c if ss.run and ss.i_c else 0)

# 3. CABECERA
c1, c2, c3 = st.columns([1,4,1])
with c1: 
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=50)
with c2: 
    riv = st.text_input("R", "RIVAL", label_visibility="collapsed").upper()
with c3: 
    if st.button("🔄 RESET"):
        ss.clear()
        st.rerun()

# 4. MARCADOR
m1, m2, m3 = st.columns([2,3,2])
with m1:
    st.metric("LUD", ss.ml, f"Faltas: {ss.fl}")
    if st.button("⚽ GOL LUD", key="gl"): ss.ml+=1; st.rerun()
    if st.button("⚠️ FALTA LUD", key="fl"): ss.fl+=1; st.rerun()

with m2:
    mm, sv = divmod(int(td), 60)
    st.markdown(f"<h1 style='text-align:center; font-size:4rem;'>{mm:02d}:{sv:02d}</h1>", unsafe_allow_html=True)
    if not ss.run:
        if st.button("▶ START", type="primary", use_container_width=True):
            ss.i_c, ss.run = ah, True
            for j in ss.js: 
                if j["p"]: j["ini"] = ah
            st.rerun()
    else:
        if st.button("⏸ STOP", type="secondary", use_container_width=True):
            ss.t_a += ah - ss.i_c
            ss.run, ss.i_c = False, None
            for j in ss.js:
                if j["p"] and j["ini"]: 
                    j["t_t"] += ah - j["ini"]
                    j["ini"] = None
            st.rerun()

with m3:
    st.metric(riv[:8], ss.mr, f"Faltas: {ss.fr}")
    if st.button(f"⚽ GOL {riv[:3]}", key="gr"): ss.mr+=1; st.rerun()
    if st.button(f"⚠️ FALTA {riv[:3]}", key="
