import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v9.4", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f5; }
    .block-container {padding: 0.5rem !important;}

    /* CONTENEDOR CENTRAL DEL CRONO Y BOTÓN START */
    .main-timer-zone {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }

    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 6.5rem !important;
        font-weight: 700;
        color: #001A33;
        line-height: 1;
        text-align: center;
    }

    /* FORZAR BOTÓN START/STOP GIGANTE */
    div.stButton > button[key="tm_m"] {
        width: 90% !important; 
        height: 110px !important;
        background-color: #003D7A !important;
        color: white !important;
        border: 6px solid #ed1c24 !important;
        border-radius: 20px !important;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        margin-top: 20px !important;
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* ESTILO JUGADORES ALTA VISIBILIDAD */
    .pista-activa { background-color: #00C853 !important; color: white !important; }
    .banquillo-espera { background-color: #D50000 !important; color: white !important; }

    .footer-control {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px 20px 0 0;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.1);
        margin-top: 15px;
    }
    
    .timeline-goal {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False,"g":0} for x in n]
    st.session_state.gi, st.session_state.pm, st.session_state.pp = [], 0, 0
    st.session_state.al, st.session_state.rl, st.session_state.ar, st.session_state.rr, st.session_state.ml, st.session_state.mr, st.session_state.fl, st.session_state.fr = 0,0,0,0,0,0,0,0
    st.session_state.ta, st.session_state.ic, st.session_state.on, st.session_state.pa, st.session_state.ex = 0.0,None,False,"1T",False
    st.session_state.rv, st.session_state.fe = "RIVAL", datetime.now().strftime("%d/%m/%Y")
    st.session_state.tm, st.session_state.tm_i = False, None

s = st.session_state
if not s.ex: st_autorefresh(1000, key="f5_stadium_v94")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_game = int((tr if s.pa=="1T" else tr+1200) // 60)

tm_sec = 0
if s.tm:
    elapsed = ah - s.tm_i
    tm_sec = max(0, 60 - int(elapsed))
    if tm_sec == 0: s.tm = False

# BLOQUE CRONO Y START (FUERA DE COLUMNAS PARA QUE SEA GIGANTE)
st.markdown("<div class='main-timer-zone'>", unsafe_allow_html=True)
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
st.markdown("</div>", unsafe_allow_html=True)

# LÍNEA DE TIEMPO DE GOLES
if s.gi:
    tl_html = "<div style='text-align:center; margin-bottom:10px;'>"
    for g in s.gi:
        bg = "#003D7A" if g["team"]=="LUD" else "#ffffff"
        col = "white" if g["team"]=="LUD" else "black"
        bor = "none" if g["team"]=="LUD" else "1px solid #ccc"
        tl_html += f"<span class='timeline-goal' style='background:{bg}; color:{col}; border:{bor};'>{g['m']}' ⚽ {g['name'][:3]}</span>"
    st.markdown(tl_html + "</div>", unsafe_allow_html=True)

# MARCADOR Y CONFIG (FILA SECUNDARIA)
c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c1:
    st.metric("LUD", s.ml)
    if st.button("⚽ GOL LUD", key="g_l"): s.ml+=1; s.gi.append({"team":"LUD", "name":"LUD", "m":min_game}); st.rerun()
with c2:
    st.metric(s.rv[:8], s.mr)
    if st.button(f"⚽ GOL {s.rv[:5]}", key="g_r"): s.mr+=1; s.gi.append({"team":"RIVAL", "name":s.rv[:8], "m":min_game}); st.rerun()
with c3:
    s.rv = st.text_input("Rival", s.rv).upper()
with c4:
    if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

# JUGADORES
st.markdown("<br>", unsafe_allow_html=True)
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        estilo = "pista-activa" if j['p'] else "banquillo-espera"
        with st.container(border=True):
            st.markdown(f"<div class='{estilo}' style='padding:10px; border-radius:8px; text-align:center;'>", unsafe_allow_html=True)
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            st.markdown(f"<div style='font-size:1.1rem; font-weight:900;'>{j['n']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.8rem; font-weight:900;'>{mj:02d}:{vj:02d}</div>", unsafe_allow_html=True)
            if st.button("🔄 CAMBIO", key=f"c_{idx}"):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
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
    st.markdown("<div style='text-align:center; font-weight:900;'>LUD</div>", unsafe_allow_html=True)
    if st.button("❌ FALTA +", key="flp"): s.fl+=1; st.rerun()
    if st.button("⏱️ TM LUD", key="tm_l"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
with f2:
    st.markdown("<div style='text-align:center; font-weight:900;'>DISCIPLINA / PORTERO</div>", unsafe_allow_html=True)
    c_tar = st.columns(2)
    with c_tar[0]:
        if st.button("🟨", key="al1"): s.al+=1; st.rerun()
        if st.button("🟥", key="rl1"): s.rl+=1; st.rerun()
    with c_tar[1]:
        if st.button("🟨", key="al2"): s.ar+=1; st.rerun()
        if st.button("🟥", key="rl2"): s.rr+=1; st.rerun()
    st.divider()
    c_port = st.columns(2)
    if c_port[0].button(f"🧤 {s.pm}", key="pm1"): s.pm+=1; st.rerun()
    if c_port[1].button(f"👟 {s.pp}", key="pp1"): s.pp+=1; st.rerun()
with f3:
    st.markdown("<div style='text-align:center; font-weight:900;'>RIVAL</div>", unsafe_allow_html=True)
    if st.button("❌ FALTA +", key="frp"): s.fr+=1; st.rerun()
    if st.button("⏱️ TM RIV", key="tm_r"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
