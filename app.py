import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="LUD PRO", layout="wide")
st.markdown("<style>h1,h2,h3,p{color:black!important;font-weight:bold;} .reloj{font-size:45px;color:#7A0019;text-align:center;}</style>",unsafe_allow_html=True)

# 1. Datos iniciales
if 'js' not in st.session_state:
    st.session_state.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in st.session_state: st.session_state.rt1 = 0.0
if 'rt2' not in st.session_state: st.session_state.rt2 = 0.0
if 'pt' not in st.session_state: st.session_state.pt = "T1"
if 'ml' not in st.session_state: st.session_state.ml = 0
if 'mr' not in st.session_state: st.session_state.mr = 0
if 'fl' not in st.session_state: st.session_state.fl = 0
if 'fr' not in st.session_state: st.session_state.fr = 0
if 'ac' not in st.session_state: st.session_state.ac = False
if 'ig' not in st.session_state: st.session_state.ig = None

# 2. Marcador
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader(f"LUD: {st.session_state.ml}")
    if st.button("+GOL LUD"): st.session_state.ml+=1; st.rerun()
    st.write(f"F: {st.session_state.fl}"); 
    if st.button("+FL"): st.session_state.fl+=1; st.rerun()
with c2:
    st.session_state.pt = st.radio("Parte:",["T1","T2"], horizontal=True)
    if st.button("RESET"): st.session_state.clear(); st.rerun()
with c3:
    st.subheader(f"RIV: {st.session_state.mr}")
    if st.button("+GOL RIV"): st.session_state.mr+=1; st.rerun()
    st.write(f"F: {st.session_state.fr}"); 
    if st.button("+FR"): st.session_state.fr+=1; st.rerun()

st.divider()

# 3. Reloj y Control
tg = st.session_state.rt1 if st.session_state.pt=="T1" else st.session_state.rt2
if st.session_state.ac and st.session_state.ig: tg += time.time()-st.session_state.ig
mg, sg = divmod(int(tg), 60)

cx, cy = st.columns(2)
with cx:
    if not st.session_state.ac:
        if st.button("▶ START", type="primary", use_container_width=True):
            st.session_state.ac, now = True, time.time()
            st.session_state.ig = now
            for j in st.session_state.js:
                if j["p"]: j["ini"] = now
            st.rerun
