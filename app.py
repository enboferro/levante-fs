import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v11.4", layout="wide")

# --- CSS CON COLORES DINÁMICOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f4f4f4; overflow: hidden; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }

    .header-container {
        display: flex; align-items: center; justify-content: center; gap: 10px;
        padding: 2px; background: white; border-radius: 0 0 12px 12px;
        border-bottom: 2px solid #003D7A;
    }

    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 4.2rem !important;
        font-weight: 700; color: #003D7A;
        line-height: 0.8; text-align: center; margin: 1px 0;
    }

    /* ESTILOS DE FICHAS DINÁMICAS */
    .pista-verde { background-color: #28a745 !important; color: white !important; border-radius: 6px; padding: 2px; text-align: center; }
    .pista-naranja { background-color: #FF9800 !important; color: white !important; border-radius: 6px; padding: 2px; text-align: center; border: 2px solid white; }
    .pista-roja-alerta { background-color: #d32f2f !important; color: white !important; border-radius: 6px; padding: 2px; text-align: center; border: 2px solid yellow; animation: blinker 1s linear infinite; }
    .banquillo-espera { background-color: #757575 !important; color: white !important; border-radius: 6px; padding: 2px; text-align: center; opacity: 0.8; }

    @keyframes blinker { 50% { opacity: 0.7; } }
    
    div.stButton > button[key="tm_m"] {
        width: 100% !important; max-width: 280px !important;
        height: 40px !important; background-color: #003D7A !important;
        color: white !important; border: 2px solid #ed1c24 !important;
        border-radius: 10px !important; font-size: 1.1rem !important;
        font-weight: 900 !important; margin: 2px auto !important; display: block !important;
    }

    .horizontal-timeline {
        display: flex; overflow-x: auto; background: white;
        padding: 2px; border-radius: 5px; margin: 2px 0;
        border: 1px solid #003D7A; gap: 4px; height: 28px;
    }

    .footer-control {
        background-color: #ffffff; padding: 2px 4px;
        border-radius: 10px 10px 0 0; border-top: 2px solid #003D7A;
        margin-top: 1px;
    }
    
    [data-testid="stMetricValue"] { font-size: 1.3rem !important; color: #003D7A !important; line-height: 1 !important; }
    </style>
    """, unsafe_allow_html=True)

if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n],
        "eventos": [], "pm": 0, "pp": 0, "al": 0, "rl": 0, "ar": 0, "rr": 0, 
        "ml": 0, "mr": 0, "fl": 0, "fr": 0, "ta": 0.0, "ic": None, "on": False, 
        "pa": "1T", "rv": "RIVAL", "tm": False, "tm_i": None, "t1_abs": 0.0, "t2_abs": 0.0
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v11.4")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_act = int((tr if s.pa=="1T" else tr+1200) // 60)

if s.on:
    if s.pa == "1T": s.t1_abs = tr
    else: s.t2_abs = tr

tm_sec = max(0, 60 - int(ah - s.tm_i)) if s.tm and s.tm_i else 0
if s.tm and tm_sec == 0: s.tm = False

def stop_match():
    if s.on:
        now = time.time()
        s.ta += now - s.ic; s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]:
                d = now - j["i"]; j["tot"] += d; j["tt"] += d; j["i"] = None

# CABECERA
st.markdown(f'<div class="header-container"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="30"><b style="color:#003D7A; font-size:0.9rem;">LEVANTE UD CONTROL</b></div>', unsafe_allow_html=True)

# CRONO
if s.tm: st.markdown(f"<div class='stadium-clock' style='color:#FF9800;'>{tm_sec}s</div>", unsafe_allow_html=True)
else:
    m, sec = divmod(int(rem), 60)
    st.markdown(f"<div class='stadium-clock'>{m:02d}:{sec:02d}</div>", unsafe_allow_html=True)

if st.button("▶ START / STOP ⏸", key="tm_m"):
    if not s.on:
        s.ic, s.on, s.tm = ah, True, False
        for j in s.js: 
            if j["p"]: j["i"]=ah
    else: stop_match()
    st.rerun()

# JUGADORES (6 por fila)
st.markdown("<div style='margin-bottom:1px;'></div>", unsafe_allow_html=True)
cols = st.columns(6)
for i, j in enumerate(s.js):
    with cols[i%6]:
        # CÁLCULO DE COLOR DINÁMICO
        cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        tot = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        
        if not j['p']:
            cl = "banquillo-espera"
        else:
            if cur < 240: # Menos de 4 min
                cl = "pista-verde"
            elif cur < 360: # Entre 4 y 6 min
                cl = "pista-naranja"
            else: # Más de 6 min
                cl = "pista-roja-alerta"

        st.markdown(f"<div class='{cl}'>", unsafe_allow_html=True)
        mc, vc = divmod(int(cur), 60)
        mt, vt = divmod(int(tot), 60)
        st.markdown(f"<b style='font-size:0.75rem;'>{j['n']}</b>", 1)
        st.markdown(f"<b style='font-size:1.1rem;'>{mc:02d}:{vc:02d}</b>", 1)
        st.markdown(f"<span style='font-size:0.6rem;'>Σ{mt:02d}:{vt:02d} R:{j['r']}</span>", 1)
        if st.button("🔄", key=f"c_{i}", use_container_width=True):
            if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1; j["tt"] = 0.0
            elif j["p"]:
                if s.on and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                j["p"], j["i"] = False, None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Resto de la interfaz (Score, Timeline, Footer) igual que v11.3...
# (He omitido el resto del código repetitivo por brevedad, pero incluye los popovers de tarjetas rival)
