import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v9.8", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f5; }
    .block-container { padding: 0.5rem !important; max-width: 1200px; margin: 0 auto; }

    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 6.5rem !important;
        font-weight: 700;
        color: #001A33;
        line-height: 1;
        text-align: center;
        width: 100%;
        margin: 10px 0;
    }

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
        transition: transform 0.02s ease-in-out !important;
        margin: 0 auto !important;
        display: block !important;
    }

    div.stButton > button:active { transform: scale(0.95) !important; }

    .pista-activa { background-color: #00C853 !important; color: white !important; border-radius: 10px; padding: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    .banquillo-espera { background-color: #D50000 !important; color: white !important; border-radius: 10px; padding: 10px; text-align: center; opacity: 0.9; }

    .footer-control {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
        margin-top: 20px;
    }

    .mini-chip { padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 800; background: #333; color: #fff; margin: 2px; }
    .bonus-alert { background-color: #ff0000 !important; animation: blink 0.8s infinite; }
    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.3;} 100% {opacity: 1;} }
    
    .stats-box { background: #e3e8ed; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #c0c9d1; }
    </style>
    """, unsafe_allow_html=True)

if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n]
    st.session_state.gi, st.session_state.pm, st.session_state.pp = [], 0, 0
    st.session_state.al, st.session_state.rl, st.session_state.ar, st.session_state.rr, st.session_state.ml, st.session_state.mr, st.session_state.fl, st.session_state.fr = 0,0,0,0,0,0,0,0
    st.session_state.ta, st.session_state.ic, st.session_state.on, st.session_state.pa, st.session_state.ex = 0.0,None,False,"1T",False
    st.session_state.rv, st.session_state.fe = "RIVAL", datetime.now().strftime("%d/%m/%Y")
    st.session_state.tm, st.session_state.tm_i = False, None
    st.session_state.t1_abs, st.session_state.t2_abs = 0.0, 0.0 # Tiempos absolutos por parte

s = st.session_state
if not s.ex: st_autorefresh(1000, key="f5_v9.8")

ah = time.time()
# Cálculo de tiempo de juego
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_game = int((tr if s.pa=="1T" else tr+1200) // 60)

# Guardar tiempo absoluto de la parte actual
if s.on:
    if s.pa == "1T": s.t1_abs = tr
    else: s.t2_abs = tr

# Lógica del cronómetro de Tiempo Muerto (1 min)
tm_sec = 0
if s.tm:
    elapsed = ah - s.tm_i
    tm_sec = max(0, 60 - int(elapsed))
    if tm_sec == 0: s.tm = False

def stop_match():
    if s.on:
        ah_now = time.time()
        s.ta += ah_now - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]:
                d_d = ah_now - j["i"]
                j["tot"] += d_d
                j["tt"] += d_d
                j["i"] = None

# HEADER
st.markdown("<h3 style='text-align:center; color:#003D7A; margin:0;'>LUD MATCH CONTROL v9.8</h3>", unsafe_allow_html=True)

# CRONO Y BOTÓN PRINCIPAL
st.markdown("<div style='width:100%; text-align:center;'>", unsafe_allow_html=True)
if s.tm:
    st.markdown(f"<div class='stadium-clock' style='color:#FF9800;'>⏱️ TM: {tm_sec}s</div>", unsafe_allow_html=True)
else:
    mr_v, sr_v = divmod(int(rem), 60)
    st.markdown(f"<div class='stadium-clock'>{mr_v:02d}:{sr_v:02d}</div>", unsafe_allow_html=True)

if st.button("▶ START / STOP ⏸", key="tm_m"):
    if not s.on:
        s.ic, s.on, s.tm = ah, True, False
        for j in s.js: 
            if j["p"]: j["i"]=ah
    else:
        stop_match()
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ESTADÍSTICAS DE TIEMPO ABSOLUTO
c_abs = st.columns(2)
m1, s1 = divmod(int(s.t1_abs), 60)
m2, s2 = divmod(int(s.t2_abs), 60)
c_abs[0].markdown(f"<div class='stats-box'><b>⏱ ABSOLUTO 1T</b><br>{m1:02d}:{s1:02d}</div>", 1)
c_abs[1].markdown(f"<div class='stats-box'><b>⏱ ABSOLUTO 2T</b><br>{m2:02d}:{s2:02d}</div>", 1)

# MARCADORES
st.markdown("<br>", unsafe_allow_html=True)
c_sc = st.columns([2, 2, 2, 1])
with c_sc[0]:
    st.metric("LUD", s.ml)
    if st.button("⚽ GOL LUD", key="btn_g_l"):
        s.ml += 1; s.gi.append({"team":"LUD", "name":"LUD", "m":min_game}); st.rerun()
with c_sc[1]:
    st.metric(s.rv[:8], s.mr)
    if st.button(f"⚽ GOL {s.rv[:5]}", key="btn_g_r"):
        s.mr += 1; s.gi.append({"team":"RIVAL", "name":s.rv[:8], "m":min_game}); st.rerun()
with c_sc[2]:
    s.rv = st.text_input("Rival", s.rv).upper()
    s.pa = st.selectbox("Parte", ["1T", "2T"], index=0 if s.pa=="1T" else 1)
with c_sc[3]:
    if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

# JUGADORES
st.markdown("<div style='margin:10px 0;'></div>", unsafe_allow_html=True)
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        st_class = "pista-activa" if j['p'] else "banquillo-espera"
        with st.container():
            st.markdown(f"<div class='{st_class}'>", unsafe_allow_html=True)
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mt, vt = divmod(int(tl), 60)
            st.markdown(f"<div style='font-size:0.9rem; font-weight:900;'>{j['n']} <span style='float:right;'>R:{j['r']}</span></div>", 1)
            st.markdown(f"<div style='font-size:1.8rem; font-weight:900;'>{mj:02d}:{vj:02d}</div>", 1)
            st.markdown(f"<div style='font-size:0.8rem; font-weight:700; opacity:0.8;'>Σ {mt:02d}:{vt:02d}</div>", 1)
            if st.button("🔄 CAMBIO", key=f"c_{idx}", use_container_width=True, disabled=s.tm):
                if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# FOOTER
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
f_cols = st.columns([3, 4, 3])
with f_cols[0]:
    st.markdown(f"<b>LUD</b> <span class='mini-chip {'bonus-alert' if s.fl>=5 else ''}'>❌ {s.fl}</span>", 1)
    st.button("❌ FALTA +", key="flp", on_click=lambda: setattr(s, 'fl', s.fl+1))
    if st.button("⏱️ TM LUD", key="tm_l"):
        stop_match()
        s.tm, s.tm_i = True, time.time(); st.rerun()
with f_cols[1]:
    st.markdown("<center><b>DISCIPLINA</b></center>", 1)
    c_t = st.columns(2)
    with c_t[0]:
        st.button(f"🟨 {s.al}", key="al1", on_click=lambda: setattr(s, 'al', s.al+1))
        st.button(f"🟥 {s.rl}", key="rl1", on_click=lambda: setattr(s, 'rl', s.rl+1))
    with c_t[1]:
        st.button(f"🟨 {s.ar}", key="al2", on_click=lambda: setattr(s, 'ar', s.ar+1))
        st.button(f"🟥 {s.rr}", key="rl2", on_click=lambda: setattr(s, 'rr', s.rr+1))
with f_cols[2]:
    st.markdown(f"<b>{s.rv[:5]}</b> <span class='mini-chip {'bonus-alert' if s.fr>=5 else ''}'>❌ {s.fr}</span>", 1)
    st.button("❌ FALTA +", key="frp", on_click=lambda: setattr(s, 'fr', s.fr+1))
    if st.button("⏱️ TM RIV", key="tm_r"):
        stop_match()
        s.tm, s.tm_i = True, time.time(); st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
