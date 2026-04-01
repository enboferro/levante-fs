import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="LUD PRO", layout="wide")
ss = st.session_state

# 1. Configuración de Tema
if 'tm' not in ss: ss.tm = "Oscuro"
bg, tx, cd = ("#1E1E1E","#FFF","#2D2D2D") if ss.tm=="Oscuro" else ("#FFF","#000","#F0F2F6")

st.markdown(f"""<style>
    .stApp {{background:{bg};}}
    h1,h2,h3,p,b,span,div {{color:{tx}!important;}}
    .reloj {{font-size:45px;color:#7A0019;text-align:center;font-weight:bold;}}
    [data-testid="stVerticalBlockBorderWrapper"] {{background:{cd};border-radius:10px;padding:10px;}}
</style>""", unsafe_allow_html=True)

# 2. Inicialización
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt = 0.0, 0.0, "T1"
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig = False, None

# 3. Cabecera
c_t1, c_t2 = st.columns([3, 1])
with c_t1: st.title("🐸 LUD FS")
with c_t2: ss.tm = st.selectbox("Modo:", ["Oscuro", "Claro"])

c1, c2, c3 = st.columns(3)
with c1:
    st.write(f"LUD: {ss.ml}")
    if st.button("+GOL LUD"): ss.ml+=1; st.rerun()
    st.write(f"Faltas: {ss.fl}")
    if st.button("+FALTA"): ss.fl+=1; st.rerun()
with c2:
    ss.pt = st.radio("Tiempo:",["T1","T2"], horizontal=True)
    if st.button("RESET"): ss.clear(); st.rerun()
with c3:
    st.write(f"RIV: {ss.mr}")
    if st.button("+GOL RIV"): ss.mr+=1; st.rerun()
    st.write(f"Faltas: {ss.fr}")
    if st.button("+RIVAL"): ss.fr+=1; st.rerun()

st.divider()

# 4. Reloj
tg = ss.rt1 if ss.pt=="T1" else ss.rt2
if ss
