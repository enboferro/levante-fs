import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="LUD FS - Control de Tiempos", layout="wide")
st_autorefresh(interval=1000, key="f5")
s = st.session_state

# TÍTULO DEL PROGRAMA
st.markdown("<h1 style='text-align: center;'>Control de Tiempos en partido</h1>", unsafe_allow_html=True)

# INICIALIZACIÓN DE JUGADORES Y ESTADO
if 'js' not in s:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    s.js = [{"n":x,"t":0.0,"i":None,"p":False,"g":0,"s":0,"e":0,"r":0} for x in n]
    s.ml, s.mr, s.ta, s.ic, s.on = 0, 0, 0.0, None, False

ah = time.time()
td = s.ta + (ah - s.ic if s.on and s.ic else 0)

# CABECERA Y RESET
c1, c2 = st.columns([4,1])
rv = c1.text_input("RIVAL", "RIVAL").upper()
if c2.button("RESET"): s.clear(); st.rerun()

# MARCADOR CENTRAL
m1, m2, m3 = st.columns(3)
m1.metric("LUD", s.ml)
if m1.button("⚽ GOL LUD"): s.ml+=1; st.rerun()

mm, sv = divmod(int(td), 60)
m2.markdown(f"<h1 style='text-align:center; font-size: 3.5rem;'>{mm:02d}:{sv:02d}</h1>", unsafe_allow_html=True)
if not s.on:
    if m2.button("▶ START", use_container_width=True):
        s.ic, s.on = ah, True
        for j in s.js: 
            if j["p"]: j["i"] = ah
        st.rerun()
else:
    if m2.button("⏸ STOP", use_container_width=True):
        s.ta += ah - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]: j["t"] += ah - j["i"]; j["i"] = None
        st.rerun()

m3.metric(rv[:8], s.mr)
if m3.button(f"⚽ GOL {rv[:3]}"): s.mr+=1; st.rerun()

# CONTADOR DE PISTA
st.divider()
en_pista = sum(1 for x in s.js if x["p"])
st.subheader(f"🏃 JUGADORES EN PISTA: {en_pista} / 5")

# LISTA DE JUGADORES
cols = st.columns(3)
for idx, j in enumerate(s.js):
    with cols[idx % 3]:
        with st.container(border=True):
            # Cálculo de tiempo individual en tiempo real
            tt = j["t"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, sj =
