import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v9.5", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    /* RESET Y CENTRADO GLOBAL */
    html, body, [class*="css"] { 
        font-family: 'Roboto', sans-serif; 
        background-color: #f0f2f5; 
        text-align: center !important;
    }
    
    .block-container {
        padding: 0.5rem !important;
        max-width: 1000px; /* Centra el bloque principal en pantallas grandes */
        margin: 0 auto;
    }

    /* CONTENEDOR CENTRAL MAESTRO */
    [data-testid="stVerticalBlock"] {
        align-items: center !important;
    }

    /* CRONÓMETRO GIGANTE */
    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 6.5rem !important;
        font-weight: 700;
        color: #001A33;
        line-height: 1;
        margin: 10px 0;
    }

    /* BOTÓN START/STOP: SENSIBILIDAD EXTREMA */
    div.stButton > button[key="tm_m"] {
        width: 100% !important;
        max-width: 600px !important;
        height: 100px !important;
        background-color: #003D7A !important;
        color: white !important;
        border: 4px solid #ed1c24 !important;
        border-radius: 20px !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        transition: transform 0.02s ease-in-out !important; /* Reacción inmediata */
        box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important;
    }

    div.stButton > button:active {
        transform: scale(0.96) !important; /* Feedback táctil instantáneo */
        background-color: #ed1c24 !important;
    }

    /* JUGADORES: COLORES INTENSOS */
    .pista-activa { background-color: #00C853 !important; color: white !important; font-weight: 900; }
    .banquillo-espera { background-color: #D50000 !important; color: white !important; font-weight: 900; }

    /* FOOTER */
    .footer-control {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
        margin-top: 20px;
        width: 100%;
    }

    /* AJUSTE DE COLUMNAS PARA QUE TODO ESTÉ CENTRADO */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .timeline-goal {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE ESTADO
if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False,"g":0} for x in n]
    st.session_state.gi, st.session_state.pm, st.session_state.pp = [], 0, 0
    st.session_state.al, st.session_state.rl, st.session_state.ar, st.session_state.rr, st.session_state.ml, st.session_state.mr, st.session_state.fl, st.session_state.fr = 0,0,0,0,0,0,0,0
    st.session_state.ta, st.session_state.ic, st.session_state.on, st.session_state.pa, st.session_state.ex = 0.0,None,False,"1T",False
    st.session_state.rv, st.session_state.fe = "RIVAL", datetime.now().strftime("%d/%m/%Y")
    st.session_state.tm, st.session_state.tm_i = False, None

s = st.session_state
if not s.ex: st_autorefresh(1000, key="f5_v9.5")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_game = int((tr if s.pa=="1T" else tr+1200) // 60)

tm_sec = 0
if s.tm:
    elapsed = ah - s.tm_i
    tm_sec = max(0, 60 - int(elapsed))
    if tm_sec == 0: s.tm = False

# CABECERA
st.markdown("<h2 style='color:#003D7A; margin-bottom:10px;'>LUD MATCH CONTROL</h2>", unsafe_allow_html=True)

# BLOQUE CENTRAL: TIEMPO Y START/STOP
if s.tm:
    st.markdown(f"<div class='stadium-clock' style='color:#FF9800;'>⏱️ {tm_sec}s</div>", unsafe_allow_html=True)
else:
    mr_v, sr_v = divmod(int(rem), 60)
    st.markdown(f"<div class='stadium-clock'>{mr_v:02d}:{sr_v:02d}</div>", unsafe_allow_html=True)

if st.button("▶ START / STOP ⏸", key="tm_m"):
    if not s.on:
        s.ic, s.on, s.tm = ah, True, False
        for j in s.js: 
            if j["p"]: j["i"]=ah
    else:
        s.ta += ah-s.ic; s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d; j["i"]=None
    st.rerun()

# LÍNEA DE TIEMPO
if s.gi:
    tl_html = "<div style='margin:15px 0;'>"
    for g in s.gi:
        bg = "#003D7A" if g["team"]=="LUD" else "#ffffff"
        col = "white" if g["team"]=="LUD" else "#333"
        tl_html += f"<span class='timeline-goal' style='background:{bg}; color:{col}; border:1px solid #ccc;'>{g['m']}' ⚽ {g['name'][:3]}</span>"
    st.markdown(tl_html + "</div>", unsafe_allow_html=True)

# MARCADOR Y CONFIG
c_cfg = st.columns([1, 1, 1.5, 0.5])
with c_cfg[0]: st.metric("LUD", s.ml)
with c_cfg[1]: st.metric(s.rv[:8], s.mr)
with c_cfg[2]: s.rv = st.text_input("Nombre Rival", s.rv).upper()
with c_cfg[3]: 
    if st.button("🗑️"): st.session_state.clear(); st.rerun()

# JUGADORES
st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        estilo = "pista-activa" if j['p'] else "banquillo-espera"
        with st.container(border=True):
            st.markdown(f"<div class='{estilo}' style='padding:10px; border-radius:10px; text-align:center;'>", unsafe_allow_html=True)
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            st.markdown(f"<div style='font-size:1.1rem;'>{j['n']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.8rem;'>{mj:02d}:{vj:02d}</div>", unsafe_allow_html=True)
            if st.button("CAMBIO", key=f"c_{idx}", use_container_width=True):
                if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# FOOTER CONTROL
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([3, 4, 3])
with f1:
    st.markdown("<b>LUD</b>", 1)
    if st.button("❌ FALTA +", key="flp"): s.fl+=1; st.rerun()
    if st.button("⏱️ TM LUD", key="tm_l"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
with f2:
    st.markdown("<b>DISCIPLINA / PORTERO</b>", 1)
    c_t = st.columns(2)
    with c_t[0]:
        if st.button("🟨", key="al1"): s.al+=1; st.rerun()
        if st.button("🟥", key="rl1"): s.rl+=1; st.rerun()
    with c_t[1]:
        if st.button("🟨", key="al2"): s.ar+=1; st.rerun()
        if st.button("🟥", key="rl2"): s.rr+=1; st.rerun()
    st.divider()
    c_p = st.columns(2)
    if c_p[0].button(f"🧤 {s.pm}", key="pm1"): s.pm+=1; st.rerun()
    if c_p[1].button(f"👟 {s.pp}", key="pp1"): s.pp+=1; st.rerun()
with f3:
    st.markdown(f"<b>{s.rv[:5]}</b>", 1)
    if st.button("❌ FALTA +", key="frp"): s.fr+=1; st.rerun()
    if st.button("⏱️ TM RIV", key="tm_r"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
