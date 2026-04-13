import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v9.3", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    /* RESET GENERAL */
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f5; }
    .block-container {padding: 0.5rem !important;}

    /* CONTENEDOR MAESTRO DEL TIEMPO (FORZAR CENTRADO) */
    .timer-master-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin: 10px 0;
    }

    /* CRONÓMETRO */
    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 6rem !important;
        font-weight: 700;
        color: #001A33;
        line-height: 1;
        text-align: center;
    }

    /* EL BOTÓN "INDOMABLE" START/STOP */
    div.stButton > button[key="tm_m"] {
        width: 80vw !important; /* 80% del ancho de la ventana */
        height: 100px !important; /* Altura masiva */
        background-color: #003D7A !important;
        color: white !important;
        border: 5px solid #ed1c24 !important;
        border-radius: 15px !important;
        font-size: 2rem !important; /* Texto muy grande */
        font-weight: 900 !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3) !important;
        display: block !important;
        margin: 20px auto !important;
    }

    /* CARTULINAS FOOTER */
    button[key^="al"] { background-color: #FFEB3B !important; color: #000 !important; font-size: 1.5rem !important;}
    button[key^="rl"] { background-color: #F44336 !important; color: #FFF !important; font-size: 1.5rem !important;}

    /* ESTILO JUGADORES */
    .pista-activa { background-color: #00C853 !important; color: white !important; }
    .banquillo-espera { background-color: #FF5252 !important; color: #b71c1c !important; }

    .footer-control {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px 20px 0 0;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.1);
        width: 100%;
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
if not s.ex: st_autorefresh(1000, key="f5_stadium")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_game = int((tr if s.pa=="1T" else tr+1200) // 60)

tm_sec = 0
if s.tm:
    elapsed = ah - s.tm_i
    tm_sec = max(0, 60 - int(elapsed))
    if tm_sec == 0: s.tm = False

# HEADER
st.markdown(f'<div style="text-align:center;"><h2 style="color:#003D7A; margin:0; font-weight:700;">MATCH CONTROL v9.3</h2></div>', unsafe_allow_html=True)

# PARTE SUPERIOR: MARCADOR Y CONFIG
c_top = st.columns([1, 2, 1])
with c_top[0]:
    st.metric("LUD", s.ml)
    if st.button("⚽ GOL LUD", key="g_l"): s.ml+=1; st.rerun()
with c_top[1]:
    # BLOQUE CRONO CENTRAL
    if s.tm:
        st.markdown(f"<div class='timer-master-container'><div class='stadium-clock' style='color:#FF9800;'>⏱️ {tm_sec}s</div></div>", unsafe_allow_html=True)
    else:
        mr_v, sr_v = divmod(int(rem), 60)
        st.markdown(f"<div class='timer-master-container'><div class='stadium-clock'>{mr_v:02d}:{sr_v:02d}</div></div>", unsafe_allow_html=True)
    
    # EL BOTÓN GIGANTE
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
with c_top[2]:
    st.metric(s.rv[:8], s.mr)
    if st.button(f"⚽ GOL {s.rv[:5]}", key="g_r"): s.mr+=1; st.rerun()

# JUGADORES
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        estilo = "pista-activa" if j['p'] else "banquillo-espera"
        with st.container(border=True):
            st.markdown(f"<div class='{estilo}' style='padding:10px; border-radius:8px;'>", 1)
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            st.markdown(f"<div style='font-size:1rem; font-weight:900;'>{j['n']}</div>", 1)
            st.markdown(f"<div style='text-align:center; font-size:1.8rem; font-weight:900;'>{mj:02d}:{vj:02d}</div>", 1)
            if st.button("🔄 CAMBIO", key=f"c_{idx}"):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", 1)

# FOOTER REFORZADO
st.markdown("<div class='footer-control'>", 1)
f1, f2, f3 = st.columns([3, 4, 3])
with f1:
    st.markdown("<div style='text-align:center; font-weight:900;'>LUD</div>", 1)
    if st.button("❌ FALTA +", key="flp"): s.fl+=1; st.rerun()
    if st.button("⏱️ TM", key="tm_l"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
with f2:
    st.markdown("<div style='text-align:center; font-weight:900;'>DISCIPLINA / PORTERO</div>", 1)
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
    st.markdown("<div style='text-align:center; font-weight:900;'>RIVAL</div>", 1)
    if st.button("❌ FALTA +", key="frp"): s.fr+=1; st.rerun()
    if st.button("⏱️ TM", key="tm_r"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
st.markdown("</div>", 1)
