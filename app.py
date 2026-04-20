import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Don Bosco Salesianos 11-inch", layout="wide")

# --- CSS ULTRA-REDUCIDO CON ESCUDO OFICIAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    /* Reset total de márgenes */
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f8f9fa; overflow: hidden; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }

    .header-container {
        display: flex; align-items: center; justify-content: center; gap: 8px;
        padding: 1px 2px; background: white; border-radius: 0 0 10px 10px;
    }

    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 4.5rem !important;
        font-weight: 700; color: #004a99;
        line-height: 0.8; text-align: center; margin: 1px 0;
    }

    /* Botón START más pequeño */
    div.stButton > button[key="tm_m"] {
        width: 100% !important; max-width: 280px !important;
        height: 42px !important; background-color: #004a99 !important;
        color: white !important; border-radius: 10px !important;
        font-size: 1.1rem !important; font-weight: 900 !important;
        margin: 0 auto !important; display: block !important;
        padding: 0 !important;
    }

    .horizontal-timeline {
        display: flex; overflow-x: auto; background: white;
        padding: 1px 2px; border-radius: 5px; margin: 1px 0;
        border: 1px solid #ddd; gap: 3px;
    }

    /* Fichas minúsculas */
    .pista-activa { background-color: #28a745 !important; color: white !important; border-radius: 6px; padding: 2px; text-align: center; }
    .banquillo-espera { background-color: #dc3545 !important; color: white !important; border-radius: 6px; padding: 2px; text-align: center; }
    
    /* Reducción de botones de cambio */
    div.stButton > button[key^="c_"] { height: 1.6em !important; font-size: 0.7rem !important; padding: 0 !important; margin-top: 1px !important;}

    .footer-control {
        background-color: #ffffff; padding: 2px 4px;
        border-radius: 8px 8px 0 0; border-top: 1px solid #ddd;
        margin-top: 1px;
    }
    
    /* Ajuste de métricas */
    [data-testid="stMetricValue"] { font-size: 1.3rem !important; line-height: 1 !important;}
    [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    div[data-testid="stMetricValue"] > div { display: flex; align-items: center; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

if 'js' not in st.session_state:
    n = ["Jugador 1","Jugador 2","Jugador 3","Jugador 4","Jugador 5","Jugador 6","Jugador 7","Jugador 8","Jugador 9","Jugador 10","Jugador 11","Jugador 12"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n],
        "eventos": [], "pm": 0, "pp": 0, "al": 0, "rl": 0, "ar": 0, "rr": 0, 
        "ml": 0, "mr": 0, "fl": 0, "fr": 0, "ta": 0.0, "ic": None, "on": False, 
        "pa": "1T", "rv": "RIVAL", "tm": False, "tm_i": None, "t1_abs": 0.0, "t2_abs": 0.0
    })

s = st.session_state
st_autorefresh(1000, key="f5_db_salesianos_slim")

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

# CABECERA CON ESCUDO OFICIAL
st.markdown(f'<div class="header-container"><img src="https://i.ibb.co/vzN44Pj/image-0.png" width="28"><b style="color:#004a99; font-size:0.9rem; margin-left: 2px;">C.D. DON BOSCO - SALESIANOS</b></div>', unsafe_allow_html=True)

# CRONO
if s.tm: st.markdown(f"<div class='stadium-clock' style='color:#FF9800; font-size: 3.5rem !important;'>{tm_sec}s</div>", unsafe_allow_html=True)
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

# LÍNEA EVENTOS
if s.eventos:
    tl = "".join([f"<span style='background:#004a99;color:white;padding:1px 3px;border-radius:3px;font-size:0.65rem;margin-right:2px;'>{e['min']}' {e['info']}</span>" for e in s.eventos])
    st.markdown(f"<div class='horizontal-timeline'>{tl}</div>", unsafe_allow_html=True)

# SCORE BAR
c1, c2, c3, c4 = st.columns([1, 1, 2, 1])
with c1: 
    st.metric("DB", s.ml, delta_color="off")
    if st.button("⚽", key="g1", use_container_width=True): 
        s.ml+=1; s.eventos.append({'min':min_act,'info':'⚽DB'}); st.rerun()
with c2: 
    st.metric("RIV", s.mr, delta_color="off")
    if st.button("⚽", key="g2", use_container_width=True): 
        s.mr+=1; s.eventos.append({'min':min_act,'info':'⚽RIV'}); st.rerun()
with c3:
    m1, se1 = divmod(int(s.t1_abs), 60); m2, se2 = divmod(int(s.t2_abs), 60)
    st.markdown(f"<div style='font-size: 0.6rem; color: #666; text-align: center; margin-bottom: -2px;'>1T {m1:02d}:{se1:02d} | 2T {m2:02d}:{se2:02d}</div>", unsafe_allow_html=True)
    s.pa = st.selectbox("", ["1T","2T"], index=0 if s.pa=="1T" else 1, label_visibility="collapsed")
with c4:
    if st.button("🗑️", use_container_width=True): st.session_state.clear(); st.rerun()

# JUGADORES (6 por fila)
st.markdown("<div style='margin-bottom:1px;'></div>", unsafe_allow_html=True)
cols = st.columns(6)
for i, j in enumerate(s.js):
    with cols[i%6]:
        cl = "pista-activa" if j['p'] else "banquillo-espera"
        st.markdown(f"<div class='{cl}'>", unsafe_allow_html=True)
        cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0); mc, vc = divmod(int(cur), 60)
        tot = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0); mt, vt = divmod(int(tot), 60)
        st.markdown(f"<b style='font-size:0.7rem;'>{j['n']}</b>", 1)
        st.markdown(f"<b style='font-size:1rem; line-height: 1.1;'>{mc:02d}:{vc:02d}</b>", 1)
        st.markdown(f"<span style='font-size:0.6rem; line-height: 1;'>Σ{mt:02d}:{vt:02d} R:{j['r']}</span>", 1)
        if st.button("🔄", key=f"c_{i}", use_container_width=True):
            if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1; j["tt"] = 0.0
            elif j["p"]:
                if s.on and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                j["p"], j["i"] = False, None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# FOOTER Ultra-Compacto
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 3, 2])
with f1:
    st.markdown(f"<span style='font-size:0.65rem; color:#666;'>Faltas DB: {s.fl}</span>", unsafe_allow_html=True)
    st.button("F+", key="fdb", use_container_width=True, on_click=lambda: setattr(s, 'fl', s.fl+1))
    if st.button("TM DB", key="tm_l_b", use_container_width=True): stop_match(); s.tm, s.tm_i = True, time.time(); st.rerun()
with f2:
    t1, t2 = st.columns(2)
    t1.button(f"🟨 {s.al}", key="al_b", use_container_width=True, on_click=lambda: setattr(s, 'al', s.al+1))
    t2.button(f"🧤 {s.pm}", key="pm_b", use_container_width=True, on_click=lambda: setattr(s, 'pm', s.pm+1))
    t1.button(f"🟥 {s.rl}", key="rl_b", use_container_width=True, on_click=lambda: setattr(s, 'rl', s.rl+1))
    t2.button(f"👟 {s.pp}", key="pp_b", use_container_width=True, on_click=lambda: setattr(s, 'pp', s.pp+1))
with f3:
    st.markdown(f"<span style='font-size:0.65rem; color:#666;'>Faltas RIV: {s.fr}</span>", unsafe_allow_html=True)
    st.button("F+", key="friv", use_container_width=True, on_click=lambda: setattr(s, 'fr', s.fr+1))
    if st.button("TM RIV", key="tm_r_b", use_container_width=True): stop_match(); s.tm, s.tm_i = True, time.time(); st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
