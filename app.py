import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="LUD PRO SCORER", layout="wide")

ss = st.session_state

# 1. Selector de Modo Visual (Arriba del todo)
if 'tema' not in ss: ss.tema = "Oscuro"

# Configuración de Colores según el tema
if ss.tema == "Oscuro":
    bg, txt, card, bor = "#1E1E1E", "#FFFFFF", "#2D2D2D", "#444444"
else:
    bg, txt, card, bor = "#FFFFFF", "#000000", "#F0F2F6", "#DDDDDD"

# Aplicar Estilos CSS Dinámicos
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; }}
    h1, h2, h3, p, b, span, div {{ color: {txt} !important; }}
    .stButton>button {{ border-radius: 10px; font-weight: bold; }}
    .reloj {{ font-size: 45px; color: #7A0019; text-align: center; font-weight: bold; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ 
        background-color: {card}; border: 1px solid {bor}; border-radius: 10px; padding: 10px; 
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de datos
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt = 0.0, 0.0, "T1"
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig = False, None

# --- CABECERA ---
c_t1, c_t2 = st.columns([3, 1])
with c_t1: st.title("🐸 LUD FS - Match Center")
with c_t2: ss.tema = st.selectbox("Apariencia:", ["Oscuro", "Claro"])

# Marcador
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader(f"LUD: {ss.ml}")
    if st.button("⚽ +GOL LUD"): ss.ml+=1; st.rerun()
    st.write(f"Faltas: {ss.fl}")
    if st.button("➕ FALTA"): ss.fl+=1; st.rerun()
with c2:
    ss.pt = st.radio("Tiempo:",["T1","T2"], horizontal=True)
    if st.button("🔄 REINICIAR"): ss.clear(); st.rerun()
with c3:
    st.subheader(f"RIV: {ss.mr}")
    if st.button("⚽ +GOL RIVAL"): ss.mr+=1; st.rerun()
    st.write(f"Faltas: {ss.fr}")
    if st.button("➕ RIVAL"): ss.fr+=1; st.rerun()

st.divider()

# 3. Reloj Efectivo
tg = ss.rt1 if ss.pt=="T1" else ss.rt2
if ss.ac and ss.ig: tg += time.time() - ss.ig
mg, sg = divmod(int(tg), 60)

cx, cy = st.columns(2)
with cx:
    if not ss.ac:
        if st.button("▶ START RELOJ", type="primary", use_container_width=True):
            ss.ac, now = True, time.time()
            ss.ig = now
            for j in ss.js:
                if j["p"]: j["ini"] = now
            st.rerun()
    else:
        if st.button("
