import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="LUD FS PRO", layout="wide")
# Estilos: Reloj global en grande y oscuro
st.markdown("<style>h1,h2,h3,p{color:black!important;font-weight:bold;} .reloj-match{font-size:50px!important; color:#7A0019!important; text-align:center;}</style>",unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'js' not in st.session_state:
    st.session_state.js = [{"id":i,"n":f"Jug {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'reloj_t1' not in st.session_state: st.session_state.reloj_t1 = 0.0
if 'reloj_t2' not in st.session_state: st.session_state.reloj_t2 = 0.0
if 'pt' not in st.session_state: st.session_state.pt = "T1"
if 'ml' not in st.session_state: st.session_state.ml = 0
if 'mr' not in st.session_state: st.session_state.mr = 0
if 'fl' not in st.session_state: st.session_state.fl = 0
if 'fr' not in st.session_state: st.session_state.fr = 0
if 'ac' not in st.session_state: st.session_state.ac = False
if 'ini_global' not in st.session_state: st.session_state.ini_global = None

# --- MARCADOR ---
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader(f"LUD: {st.session_state.ml}")
    if st.button("+GOL LUD"): st.session_state.ml+=1; st.rerun()
    st.write(f"Faltas: {st.session_state.fl}")
    if st.button("+FL"): st.session_state.fl+=1; st.rerun()
with c2:
    st.session_state.pt = st.radio("Tiempo:",["T1","T2"], horizontal=True)
    if st.button("RESET PARTIDO"): st.session_state.clear(); st.rerun()
with c3:
    st.subheader(f"RIV
