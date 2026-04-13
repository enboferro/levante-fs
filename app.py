import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v8.4", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .block-container {padding-top:0.3rem; padding-bottom:0rem; padding-left:0.3rem; padding-right:0.3rem; background-color: #f5f5f5;}
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
    
    /* TARJETAS COMPACTAS */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        padding: 6px !important;
        margin-bottom: 4px !important;
    }

    /* BOTONES */
    div.stButton > button {
        border-radius: 6px;
        height: 2.5em;
        width: 100% !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        border: none !important;
    }

    .footer-control {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 15px 15px 0 0;
        box-shadow: 0 -3px 10px rgba(0,0,0,0.05);
        margin-top: 5px;
    }

    .mini-chip-container { display: flex; justify-content: center; gap: 4px; margin-top: 2px; }
    .mini-chip { padding: 1px 6px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; background: #eee; color: #444; }
    .bonus-alert { background-color: #d32f2f !important; color: white !important; animation: blink 1s infinite; }
    
    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.4;} 100% {opacity: 1;} }
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
if not s.ex: st_autorefresh(1000, key="f5_8.4")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_game = int((tr if s.pa=="1T" else tr+1200) // 60)

tm_sec = 0
if s.tm:
    elapsed = ah - s.tm_i
    tm_sec = max(0, 60 - int(elapsed))
    if tm_sec == 0: s.tm = False

# MARCADOR
c_sc = st.columns([2.5, 3, 2.5])
with c_sc[0]:
    st.metric("LUD", s.ml)
    f_bonus = "bonus-alert" if s.fl >= 5 else ""
    st.markdown(f'<div class="mini-chip-container"><div class="mini-chip {f_bonus}">F:{s.fl}</div><div class="mini-chip">🟨{s.al}</div><div class="mini-chip">🟥{s.rl}</div></div>', 1)
    if st.button("⚽ GOL LUD", key="btn_lud"):
        s.ml += 1; s.gi.append({"team":"LUD", "name":"LUD", "m":min_game}); st.rerun()

with c_sc[1]:
    if s.tm: st.markdown(f"<h1 style='text-align:center;font-size:2.5rem;color:orange;margin:0;'>{tm_sec}s</h1>",1)
    else:
        mr_v, sr_v = divmod(int(rem), 60)
        st.markdown(f"<h1 style='text-align:center;font-size:3rem;color:#b71c1c;margin:0;font-weight:700;'>{mr_v:02d}:{sr_v:02d}</h1>",1)
    if st.button("▶ START / STOP ⏸", key="tm_m", type="primary"):
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
    fr_bonus = "bonus-alert" if s.fr >= 5 else ""
    st.markdown(f'<div class="mini-chip-container"><div class="mini-chip {fr_bonus}">F:{s.fr}</div><div class="mini-chip">🟨{s.ar}</div><div class="mini-chip">🟥{s.rr}</div></div>', 1)
    if st.button(f"⚽ GOL {s.rv[:8]}", key="btn_riv"):
        s.mr+=1; s.gi.append({"team":"RIVAL", "name":s.rv[:8], "m":min_game}); st.rerun()

# GRID JUGADORES
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        bg_color = "#e8f5e9" if j['p'] else "#ffebee" # Verde suave vs Rojo suave
        txt_color = "#2e7d32" if j['p'] else "#c62828"
        with st.container(border=True):
            st.markdown(f"<div style='background-color:{bg_color}; padding:5px; border-radius:4px;'>", 1)
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mt, vt = divmod(int(tl), 60)
            
            st.markdown(f"<div style='font-size:0.75rem; font-weight:700; color:{txt_color};'>{j['n']} <span style='float:right;'>R:{j['r']}</span></div>", 1)
            st.markdown(f"<div style='text-align:center; font-size:1.4rem; margin:2px 0; font-weight:700; color:{txt_color};'>{mj:02d}:{vj:02d}</div>", 1)
            st.markdown(f"<div style='text-align:center; font-size:0.85rem; color:#666;'>Σ {mt:02d}:{vt:02d}</div>", 1)
            
            if st.button("CAMBIO", key=f"c_{idx}"):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", 1)

# FOOTER CONTROL (Corregido para evitar "False")
st.markdown("<div class='footer-control'>", 1)
b_f = st.columns([3, 4, 3])

with b_f[0]:
    st.markdown("<div style='font-size:0.7rem; font-weight:800; color:#666; text-align:center;'>FALTAS LUD</div>", 1)
    if st.button("FALTA +", key="flp"): s.fl+=1; st.rerun()
    if st.button("FALTA -", key="flm"): s.fl=max(0, s.fl-1); st.rerun()
    if st.button("⏱️ TM LUD", key="tm_l"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()

with b_f[1]:
    st.markdown("<div style='font-size:0.7rem; font-weight:800; color:#666; text-align:center;'>DISCIPLINA / PORTERO</div>", 1)
    c1, c2 = st.columns(2)
    if c1.button(f"🟨 LUD {s.al}", key="al1"): s.al+=1; st.rerun()
    if c1.button(f"🟥 LUD {s.rl}", key="rl1"): s.rl+=1; st.rerun()
    if c2.button(f"🟨 RIV {s.ar}", key="al2"): s.ar+=1; st.rerun()
    if c2.button(f"🟥 RIV {s.rr}", key="rl2"): s.rr+=1; st.rerun()
    st.divider()
    cp1, cp2 = st.columns(2)
    if cp1.button(f"🧤 PARADA {s.pm}", key="pm1"): s.pm+=1; st.rerun()
    if cp2.button(f"👟 PIE {s.pp}", key="pp1"): s.pp+=1; st.rerun()

with b_f[2]:
    st.markdown(f"<div style='font-size:0.7rem; font-weight:800; color:#666; text-align:center;'>FALTAS {s.rv[:8]}</div>", 1)
    if st.button("FALTA +", key="frp"): s.fr+=1; st.rerun()
    if st.button("FALTA -", key="frm"): s.fr=max(0, s.fr-1); st.rerun()
    if st.button("⏱️ TM RIVAL", key="tm_r"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
st.markdown("</div>", 1)
