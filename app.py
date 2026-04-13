import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v8.0", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top:0rem; padding-bottom:0rem; padding-left:0.2rem; padding-right:0.2rem;}
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
    
    /* ELIMINAR PADDING DE COLUMNAS PARA ALINEACIÓN REAL */
    [data-testid="column"] {
        padding: 0px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    div.stButton > button {
        border-radius: 8px;
        height: 3em;
        width: 100% !important;
        font-size: 1rem !important;
        font-weight: 900 !important;
        padding: 0px !important;
        margin-bottom: 2px !important;
    }

    /* BOTÓN START/STOP: ANCHO TOTAL DEL CONTENEDOR CENTRAL */
    div.stButton > button[key="tm_m"] {
        height: 4em !important;
        background-color: #003D7A !important;
        border: 3px solid #ed1c24 !important;
        color: white !important;
        width: 100% !important;
        max-width: none !important;
    }

    div.stButton > button:active {
        transform: scale(0.96) !important;
        background-color: #003D7A !important;
    }

    .label-x {font-size:0.75rem; font-weight:900; text-align:center; color:#fff; text-transform: uppercase; margin-bottom: 4px; background: #333; padding: 4px; border-radius: 4px; width: 100%;}
    .footer-control { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 3px solid #003D7A; margin-top: 10px; width: 100%;}
    
    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.3;} 100% {opacity: 1;} }
    .blink { animation: blink 1s infinite; }
    .bonus-faltas { color: #ff0000; font-weight: 950; animation: blink 0.8s infinite; background: white; padding: 2px 5px; border-radius: 4px; }
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
if not s.ex: st_autorefresh(1000, key="f5_refresh")

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
st.markdown(f'<div style="text-align:center; border-bottom: 2px solid #ed1c24; margin-bottom:5px; width: 100%;"><h1 style="color:#003D7A; margin:0; font-size:1.2rem;">LUD MATCH CONTROL</h1></div>', unsafe_allow_html=True)

d_top = st.columns([1.5, 1, 1, 0.5])
s.rv = d_top[0].text_input("R", s.rv, key="irv", label_visibility="collapsed").upper()
s.fe = d_top[1].text_input("F", s.fe, key="ife", label_visibility="collapsed")
with d_top[2]:
    with st.popover("5 INICIAL", use_container_width=True):
        cp = sum(1 for x in s.js if x["p"])
        for j in s.js:
            if st.button(f"{'✅' if j['p'] else '⬜'} {j['n']}", key=f"init_{j['n']}", use_container_width=True):
                if j["p"]: j["p"], j["i"], j["r"] = False, None, 0
                elif cp < 5: j["p"], j["r"] = True, 1; j["i"] = ah if s.on else None
                st.rerun()
if d_top[3].button("🗑️", key="main_reset_btn", use_container_width=True): st.session_state.clear(); st.rerun()

# MARCADOR CENTRAL
c_sc = st.columns([2, 4, 2])
with c_sc[0]:
    st.metric("LUD", s.ml)
    if st.button("⚽ GOL LUD", key="btn_gol_lud"):
        s.ml += 1; s.gi.append({"team":"LUD", "name":"LUD", "m":min_game}); st.rerun()

with c_sc[1]:
    # El tiempo y el botón ahora están en el mismo contenedor flex, alineados al centro
    if s.tm:
        st.markdown(f"<h1 style='font-size:2.5rem;color:orange;margin:0;text-align:center;'>TM {tm_sec}s</h1>", unsafe_allow_html=True)
    else:
        mr_v, sr_v = divmod(int(rem), 60)
        st.markdown(f"<h1 style='font-size:3rem;color:red;margin:0;line-height:1;text-align:center;'>{mr_v:02d}:{sr_v:02d}</h1>", unsafe_allow_html=True)
    
    if st.button("▶ START / STOP ⏸", key="tm_m", use_container_width=True):
        if not s.on:
            s.ic, s.on, s.tm = ah, True, False
            for j in s.js: 
                if j["p"]: j["i"]=ah
        else:
            s.ta += ah-s.ic; s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d; j["i"]=None
        st.rerun()

with c_sc[2]:
    st.metric(s.rv[:8], s.mr)
    if st.button(f"⚽ GOL {s.rv[:8]}", key="gr_r_dyn"):
        s.mr+=1; s.gi.append({"team":"RIVAL", "name":s.rv[:8], "m":min_game}); st.rerun()

# JUGADORES
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        with st.container(border=True):
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mt, vt = divmod(int(tl), 60)
            fat = "<span class='blink' style='color:orange;'>⚠️</span>" if mj >= 5 else ""
            st.markdown(f"<p style='margin:0;font-size:0.7rem;'>{'🟢' if j['p'] else '🔴'} <b>{j['n']}</b> <span style='float:right; font-weight:900;'>R:{j['r']}</span></p>", 1)
            st.markdown(f"<h4 style='margin:0;text-align:center;font-size:1.1rem;'>{mj:02d}:{vj:02d} {fat}</h4>", 1)
            st.markdown(f"<div style='display:flex;justify-content:space-between;font-size:0.9rem;font-weight:900;'><span>⚽ {j['g']}</span><span>Σ {mt:02d}:{vt:02d}</span></div>", 1)
            if st.button("CAMBIO", key=f"c_{idx}", use_container_width=True):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()

# FOOTER REORGANIZADO
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
b_f = st.columns([3.5, 3, 3.5])

with b_f[0]: # LUD
    st.markdown(f"<div class='label-x'>LUD | FALTAS: <span class='{'bonus-faltas' if s.fl>=5 else ''}'>{s.fl}</span></div>", 1)
    if st.button("FALTA +", key="flp_big"): s.fl+=1; st.rerun()
    if st.button("FALTA -", key="flm_big"): s.fl=max(0, s.fl-1); st.rerun()
    if st.button("⏱️ TIEMPO MUERTO", key="tm_l_btn"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
    if st.button(f"🟨 AMARILLA ({s.al})", key="tal_l_btn"): s.al+=1; st.rerun()
    if st.button(f"🟥 ROJA ({s.rl})", key="trl_l_btn"): s.rl+=1; st.rerun()

with b_f[1]: # PORTERÍA
    st.markdown("<div class='label-x'>PORTERÍA</div>", 1)
    if st.button(f"🧤 PARADA: {s.pm}", key="pm_b_btn"): s.pm+=1; st.rerun()
    if st.button(f"👟 PIE: {s.pp}", key="pp_b_btn"): s.pp+=1; st.rerun()

with b_f[2]: # RIVAL
    st.markdown(f"<div class='label-x'>{s.rv[:8]} | FALTAS: <span class='{'bonus-faltas' if s.fr>=5 else ''}'>{s.fr}</span></div>", 1)
    if st.button("FALTA +", key="frp_big"): s.fr+=1; st.rerun()
    if st.button("FALTA -", key="frm_big"): s.fr=max(0, s.fr-1); st.rerun()
    if st.button("⏱️ TIEMPO MUERTO", key="tm_r_btn"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
    if st.button(f"🟨 AMARILLA ({s.ar})", key="tar_r_btn"): s.ar+=1; st.rerun()
    if st.button(f"🟥 ROJA ({s.rr})", key="trr_r_btn"): s.rr+=1; st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
