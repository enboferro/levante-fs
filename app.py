import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN
st.set_page_config(page_title="LUD FS PRO", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state

st.markdown("""<style>
    .stApp { background-color: #f8f9fa; }
    .marcador-container { background: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .jugador-card { background: white; border-radius: 10px; padding: 10px; margin-bottom: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN (15 JUGADORES)
if 'js' not in ss:
    nombres_fijos = [
        "Serra", "Julian", "Omar", "Tony", "Rochina",
        "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu",
        "Pedro Toro", "Paco Silla", "Jose", "Coque", "Nacho Gomez"
    ]
    ss.js = []
    for i in range(15):
        ss.js.append({
            "id": i, "n": nombres_fijos[i] if i < len(nombres_fijos) else f"J{i+1}",
            "t_total": 0.0, "ini": None, "p": False, "g": 0, "t": 0, "per": 0, "rec": 0
        })

if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'tiempo_acumulado' not in ss: ss.tiempo_acumulado = 0.0
if 'inicio_cronometro' not in ss: ss.inicio_cronometro = None
if 'corriendo' not in ss: ss.corriendo = False

now = time.time()
tiempo_display = ss.tiempo_acumulado
if ss.corriendo and ss.inicio_cronometro:
    tiempo_display += now - ss.inicio_cronometro

# 3. CABECERA
h1, h2, h3 = st.columns([1, 4, 1])
h1.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=60)
with h2: r_nom = st.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()
if h3.button("🔄 RESET"):
    for j in ss.js: j.update({"t_total":0.0,"ini":None,"p":False,"g":0,"t":0,"per":0,"rec":0})
    ss.ml, ss.mr, ss.fl, ss.fr, ss.tiempo_acumulado, ss.inicio_cronometro, ss.corriendo = 0,0,0,0,0.0,None,False
    st.rerun()

#
