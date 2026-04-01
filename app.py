import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# 1. Configuración de página
st.set_page_config(page_title="LUD FS - PRO Match Center", layout="wide", page_icon="🐸")

# Autorefresh cada 1 segundo para el cronómetro
st_autorefresh(interval=1000, key="futsalrefresh")

ss = st.session_state

# --- ESTILOS PERSONALIZADOS AVANZADOS ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .reloj-box { background-color: #1E1E1E; border: 4px solid #7A0019; border-radius: 25px; padding: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .stButton>button { border-radius: 10px; font-weight: bold; height: 3em; transition: all 0.3s; }
    .stButton>button:hover { transform: scale(1.02); }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .bonus-alert { background-color: #FF0000 !important; animation: blink 1s infinite; }
    h1, h2, h3 { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"Jugador {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt = 0.0, 0.0, "T1"
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig = False, None
if 'pos' not in ss: ss.pos = "Neutral"

# 3. CABECERA Y RESET
col_esc, col_tit, col_res = st.columns([1, 4, 1])
with col_esc:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=80)
with col_tit:
    st.title("LEVANTE UD FS - PRO CENTER")
with col_res:
    if st.button("🔄 REINICIAR PARTIDO"): ss.clear(); st.rerun()

# 4. MARCADOR DINÁMICO
m_col1, m_col2, m_col3 = st.columns([2, 2, 2])

with m_col1:
    # Lógica de color si hay bonus de faltas (5 o más)
    bg_lud = "background:linear-gradient(135deg, #FF0000, #b30000);" if ss.fl >= 5 else "background:#003D7A;"
    clase_lud = "bonus-alert" if ss.fl >= 5 else ""
    st.markdown(f"<div class='{clase_lud}' style='text-align:center; {bg_lud} padding:15px; border-radius:15px; color:white;'> <h2 style='color:white !important; margin:0;'>LUD: {ss.ml}</h2><small>{'⚠️ DOBLE PENALTI' if ss.fl >= 5 else 'FALTAS: ' + str(ss.fl)}</small></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("⚽ GOL LUD", use_container_width=True): ss.ml+=1; st.rerun()
    if c2.button(f"⚠️ FALTA (+1)", key="f_lud", use_container_width=True): ss.fl+=1; st.rerun()

with m_col2:
    # CRONÓMETRO CENTRAL
    tg = ss.rt1 if ss.pt=="T1" else ss.rt2
    if ss.ac and ss.ig: tg += time.time() - ss.ig
    m, s = divmod(int(tg), 60)
    st.markdown(f"<div class='reloj-box'><h1 style='text-align:center; color:#FFFFFF; margin:0; font-size: 3.5rem;'>{m:02d}:{s:02d}</h1></div>", unsafe_allow_html=True)
    
    ss.pt = st.radio("Periodo:", ["T1", "T2"], horizontal=True, label_visibility="collapsed")
    
    if not ss.ac:
        if st.button("▶ INICIAR TIEMPO", type="primary", use_container_width=True):
            ss.ac, now = True, time.time()
            ss.ig = now
            for j in ss.js:
                if j["p"]: j["ini"] = now
            st.rerun()
    else:
        if st.button("⏸ PARAR TIEMPO", type="secondary", use_container_width=True):
            ss.ac, now = False, time.time()
            if ss.pt=="T1": ss.rt1 += now - ss.ig
            else: ss.rt2 += now - ss.ig
            for j in ss.js:
                if j["p"] and j["ini"]:
                    if ss.pt=="T1": j["t1"] += now - j["ini"]
                    else: j["t2"] += now - j["ini"]
                    j["ini"] = None
            ss.ig = None; st.rerun()
    
    # Ajuste fino del reloj
    a1, a2 = st.columns(2)
    if a1.button("-1s", use_container_width=True): 
        if ss.pt=="T1": ss.rt1 = max(0, ss.rt1 - 1)
        else: ss.rt2 = max(0, ss.rt2 - 1)
        st.rerun()
    if a2.button("+1s", use_container_width=True):
        if ss.pt=="T1": ss.rt1 += 1
        else: ss.rt2 += 1
        st.rerun()

with m_col3:
    bg_riv = "background:linear-gradient(135deg, #FF0000, #b30000);" if ss
