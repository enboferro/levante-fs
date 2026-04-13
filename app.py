import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v16.0", layout="wide")

# --- CSS MEJORADO: TRIPLE BOTÓN Y SIMETRÍA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f5; overflow-x: hidden; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }

    /* RELOJ CENTRAL */
    .stadium-clock { 
        font-family: 'Roboto Mono', monospace; 
        font-size: 5.5rem !important; 
        font-weight: 700; 
        color: #003D7A; 
        text-align: center; 
        margin: 5px 0;
    }

    /* ESTILO DE LOS 3 BOTONES START/STOP */
    div.stButton > button[key^="tm_"] {
        width: 100% !important;
        height: 75px !important; 
        background-color: #ffffff !important;
        color: #003D7A !important;
        border: 4px solid #ed1c24 !important;
        border-radius: 12px !important;
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        box-shadow: 0 5px 0 #cc0000 !important;
        transition: transform 0.05s ease;
    }
    
    div.stButton > button[key^="tm_"]:active {
        transform: translateY(3px) !important;
        box-shadow: 0 2px 0 #cc0000 !important;
    }

    /* SEMÁFORO DE JUGADORES */
    .pista-verde { background-color: #28a745 !important; color: white !important; border-radius: 8px; padding: 3px; text-align: center; font-weight: 900; }
    .pista-naranja { background-color: #FF5E00 !important; color: white !important; border-radius: 8px; padding: 3px; text-align: center; font-weight: 900; }
    .pista-roja { background-color: #FF0000 !important; color: white !important; border-radius: 8px; padding: 3px; text-align: center; font-weight: 900; animation: blink 0.8s infinite; }
    .banquillo { background-color: #757575 !important; color: #ddd !important; border-radius: 8px; padding: 3px; text-align: center; }

    @keyframes blink { 50% { opacity: 0.5; } }

    .footer-control {
        background-color: #ffffff; padding: 5px;
        border-radius: 15px 15px 0 0; border-top: 4px solid #003D7A;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE SESIÓN ---
if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n],
        "eventos": [], "pm": 0, "pp": 0, "al": 0, "rl": 0, "ar": 0, "rr": 0, 
        "ml": 0, "mr": 0, "fl": 0, "fr": 0, "ta": 0.0, "ic": None, "on": False, 
        "pa": "1T", "rv": "RIVAL", "tm": False, "tm_i": None, "t1_abs": 0.0, "t2_abs": 0.0
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v16")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_act = int((tr if s.pa=="1T" else tr+1200) // 60)

if s.on:
    if s.pa == "1T": s.t1_abs = tr
    else: s.t2_abs = tr

tm_sec = max(0, 60 - int(ah - s.tm_i)) if s.tm and s.tm_i else 0
if s.tm and tm_sec == 0: s.tm = False

# Lógica compartida de inicio/parada
def toggle_timer():
    if not s.on:
        s.ic, s.on, s.tm = time.time(), True, False
        for j in s.js: 
            if j["p"]: j["i"] = s.ic
    else:
        now = time.time()
        s.ta += now - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]:
                d = now - j["i"]; j["tot"] += d; j["tt"] += d; j["i"] = None

# --- RELOJ Y TRIPLE BOTÓN ---
mv, sv = divmod(int(rem), 60)
timer_display = f"{tm_sec}s" if s.tm else f"{mv:02d}:{sv:02d}"

# Fila superior de control
c_timer = st.columns([1, 2, 1])
with c_timer[0]:
    if st.button("START/STOP L", key="tm_l"):
        toggle_timer(); st.rerun()
with c_timer[1]:
    st.markdown(f"<div class='stadium-clock'>{timer_display}</div>", unsafe_allow_html=True)
    if st.button("▶ START / STOP ⏸", key="tm_m"):
        toggle_timer(); st.rerun()
with c_timer[2]:
    if st.button("START/STOP R", key="tm_r"):
        toggle_timer(); st.rerun()

# --- MARCADOR Y CONFIGURACIÓN ---
st.markdown("---")
c_score = st.columns([1, 1, 1, 1, 1])
c_score[0].metric("LUD", s.ml)
with c_score[1]:
    if st.button("⚽ GOL LUD"): s.ml += 1; st.rerun()
c_score[2].metric("RIVAL", s.mr)
with c_score[3]:
    if st.button("⚽ GOL RIV"): s.mr += 1; st.rerun()
with c_score[4]:
    if st.button("🗑️ RESET"): 
        st.session_state.clear()
        st.rerun()

# --- JUGADORES ---
st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
cols = st.columns(6)
for i, j in enumerate(s.js):
    with cols[i%6]:
        cur_sec = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        tot_sec = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        cl = "banquillo" if not j['p'] else ("pista-verde" if cur_sec < 240 else ("pista-naranja" if cur_sec < 360 else "pista-roja"))
        st.markdown(f"<div class='{cl}'>", unsafe_allow_html=True)
        mc, vc = divmod(int(cur_sec), 60); mt, vt = divmod(int(tot_sec), 60)
        st.markdown(f"<b>{j['n']}</b><br>{mc:02d}:{vc:02d}<br>Σ{mt:02d}:{vt:02d}", unsafe_allow_html=True)
        if st.button("🔄", key=f"c_{i}", use_container_width=True):
            if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1; j["tt"] = 0.0
            elif j["p"]:
                if s.on and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                j["p"], j["i"] = False, None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 4, 2])
with f1:
    st.caption(f"Faltas LUD: {s.fl}")
    st.button("F+", key="flud", use_container_width=True, on_click=lambda: setattr(s, 'fl', s.fl+1))
with f2:
    t1, t2, t3, t4 = st.columns(4)
    if t1.button("🟨", key="alud_btn", use_container_width=True): s.al+=1; st.rerun()
    if t2.button("🟥", key="rlud_btn", use_container_width=True): s.rl+=1; st.rerun()
    if t3.button("🧤", key="pm_btn", use_container_width=True): s.pm+=1; st.rerun()
    if t4.button("👟", key="pp_btn", use_container_width=True): s.pp+=1; st.rerun()
with f3:
    st.caption(f"Faltas RIV: {s.fr}")
    st.button("F+", key="friv", use_container_width=True, on_click=lambda: setattr(s, 'fr', s.fr+1))
st.markdown("</div>", unsafe_allow_html=True)
