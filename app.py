import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v8.1", layout="wide")

# CSS: MATERIAL DESIGN GOOGLE STYLE
st.markdown("""
    <style>
    /* Importar fuente roboto para el toque Google */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }

    .block-container {padding-top:0.5rem; padding-bottom:0rem; padding-left:0.5rem; padding-right:0.5rem; background-color: #f5f5f5;}
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
    
    /* TARJETAS MATERIAL DESIGN */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        padding: 10px !important;
        transition: box-shadow 0.3s ease;
        margin-bottom: 8px !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 8px 15px rgba(0,0,0,0.15) !important;
    }

    /* BOTONES MATERIAL */
    div.stButton > button {
        border-radius: 8px;
        height: 2.5em;
        width: 100% !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }

    /* BOTÓN START/STOP ESTILO MATERIAL PRIMARY */
    div.stButton > button[key="tm_m"] {
        height: 3.5em !important;
        background-color: #6200EE !important; /* Púrpura Material */
        color: white !important;
        box-shadow: 0 3px 5px rgba(0,0,0,0.2);
    }

    /* BOTÓN CAMBIO (Toque de color corporativo) */
    div.stButton > button[key^="c_"] {
        background-color: #003D7A !important;
        color: white !important;
    }

    /* FOOTER CONTROL */
    .footer-control {
        background-color: white;
        padding: 15px;
        border-radius: 16px 16px 0 0;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
        margin-top: 15px;
    }

    .label-x {
        font-size: 0.7rem;
        font-weight: 700;
        color: #757575;
        text-align: center;
        margin-bottom: 5px;
    }

    .status-dot {
        height: 10px;
        width: 100%;
        border-radius: 5px;
        margin-bottom: 5px;
    }

    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.4;} 100% {opacity: 1;} }
    .blink { animation: blink 1s infinite; }
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
if not s.ex: st_autorefresh(1000, key="f5_material")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_game = int((tr if s.pa=="1T" else tr+1200) // 60)

# LOGICA TM
tm_sec = 0
if s.tm:
    elapsed = ah - s.tm_i
    tm_sec = max(0, 60 - int(elapsed))
    if tm_sec == 0: s.tm = False

# CABECERA LIMPIA
st.markdown(f'<div style="text-align:center; padding: 10px;"><h2 style="color:#003D7A; margin:0; font-weight:700; letter-spacing:-1px;">MATCH CONTROL</h2></div>', unsafe_allow_html=True)

# FILA CONFIG
d_top = st.columns([1.5, 1, 1, 0.5])
s.rv = d_top[0].text_input("Rival", s.rv, label_visibility="collapsed").upper()
s.fe = d_top[1].text_input("Fecha", s.fe, label_visibility="collapsed")
with d_top[2]:
    with st.popover("Banquillo", use_container_width=True):
        cp = sum(1 for x in s.js if x["p"])
        for j in s.js:
            if st.button(f"{'🟢' if j['p'] else '⚪'} {j['n']}", key=f"init_{j['n']}", use_container_width=True):
                if j["p"]: j["p"], j["i"], j["r"] = False, None, 0
                elif cp < 5: j["p"], j["r"] = True, 1; j["i"] = ah if s.on else None
                st.rerun()
d_top[3].button("🗑️", key="reset_btn")

# SCOREBOARD
c_sc = st.columns([2, 4, 2])
with c_sc[0]:
    st.metric("LUD", s.ml)
    if st.button("⚽ GOL", key="btn_lud"):
        s.ml += 1; s.gi.append({"team":"LUD", "name":"LUD", "m":min_game}); st.rerun()

with c_sc[1]:
    if s.tm:
        st.markdown(f"<h1 style='text-align:center;font-size:3rem;color:#FF9800;margin:0;'>{tm_sec}s</h1>",1)
    else:
        mr_v, sr_v = divmod(int(rem), 60)
        st.markdown(f"<h1 style='text-align:center;font-size:3.5rem;color:#B00020;margin:0;font-weight:700;'>{mr_v:02d}:{sr_v:02d}</h1>",1)
    
    st.button("▶ START / STOP ⏸", key="tm_m", type="primary", use_container_width=True)
    if st.session_state.tm_m:
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
    if st.button("⚽ GOL", key="btn_riv"):
        s.mr+=1; s.gi.append({"team":"RIVAL", "name":s.rv[:8], "m":min_game}); st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# GRID JUGADORES MATERIAL CARDS
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        with st.container(border=True):
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mt, vt = divmod(int(tl), 60)
            
            # Línea de estado superior (Material color)
            color_st = "#4CAF50" if j['p'] else "#F44336"
            st.markdown(f"<div class='status-dot' style='background-color:{color_st};'></div>", unsafe_allow_html=True)
            
            # Nombre y Rotación
            st.markdown(f"<div style='font-size:0.8rem; font-weight:700; color:#424242;'>{j['n']} <span style='float:right;'>R:{j['r']}</span></div>", unsafe_allow_html=True)
            
            # Tiempo de Turno Principal
            fatiga_css = "color:#FB8C00; font-weight:700;" if mj >= 5 else "color:#212121;"
            st.markdown(f"<div style='text-align:center; font-size:1.5rem; margin:5px 0; {fatiga_css}'>{mj:02d}:{vj:02d}</div>", unsafe_allow_html=True)
            
            # Datos secundarios
            st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:0.85rem; color:#757575;'><span>⚽ <b>{j['g']}</b></span><span>Σ <b>{mt:02d}:{vt:02d}</b></span></div>", unsafe_allow_html=True)
            
            if st.button("CAMBIO", key=f"c_{idx}", use_container_width=True):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()

# FOOTER CONTROL
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
b_f = st.columns([3.5, 3, 3.5])

with b_f[0]: # LUD
    st.markdown(f"<div class='label-x'>FALTAS LUD: {s.fl}</div>", 1)
    c_f1, c_f2 = st.columns(2)
    if c_f1.button("FALTA +", key="flp"): s.fl+=1; st.rerun()
    if c_f2.button("FALTA -", key="flm"): s.fl=max(0, s.fl-1); st.rerun()
    if st.button("⏱️ TIEMPO MUERTO", key="tm_l"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
    c_t1, c_t2 = st.columns(2)
    if c_t1.button(f"🟨 {s.al}", key="al1"): s.al+=1; st.rerun()
    if c_t2.button(f"🟥 {s.rl}", key="rl1"): s.rl+=1; st.rerun()

with b_f[1]: # TÉCNICO
    st.markdown("<div class='label-x'>PORTERÍA</div>", 1)
    if st.button(f"🧤 PARADA: {s.pm}", key="pm1"): s.pm+=1; st.rerun()
    if st.button(f"👟 PIE: {s.pp}", key="pp1"): s.pp+=1; st.rerun()

with b_f[2]: # RIVAL
    st.markdown(f"<div class='label-x'>FALTAS RIVAL: {s.fr}</div>", 1)
    c_fr1, c_fr2 = st.columns(2)
    if c_fr1.button("FALTA +", key="frp"): s.fr+=1; st.rerun()
    if c_fr2.button("FALTA -", key="frm"): s.fr=max(0, s.fr-1); st.rerun()
    if st.button("⏱️ TIEMPO MUERTO", key="tm_r"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
    c_tr1, c_tr2 = st.columns(2)
    if c_tr1.button(f"🟨 {s.ar}", key="al2"): s.ar+=1; st.rerun()
    if c_tr2.button(f"🟥 {s.rr}", key="rl2"): s.rr+=1; st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
