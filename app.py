import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v9.1", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .block-container {padding-top:0.3rem; padding-bottom:0rem; padding-left:0.3rem; padding-right:0.3rem; background-color: #f0f2f5;}
    
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* CRONÓMETRO GIGANTE */
    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 5.5rem !important;
        font-weight: 700;
        color: #001A33;
        line-height: 1;
        margin-bottom: 0px;
        text-align: center;
        width: 100%;
    }
    
    .stadium-tm {
        font-family: 'Roboto Mono', monospace;
        font-size: 4.5rem !important;
        color: #FF9800;
        line-height: 1;
        text-align: center;
    }

    /* BOTÓN START/STOP: AJUSTADO AL ANCHO DEL CRONO */
    div.stButton > button[key="tm_m"] {
        height: 3.5em !important;
        width: 380px !important; /* Ancho ajustado para casar con el texto del crono */
        background-color: #003D7A !important;
        border: 4px solid #ed1c24 !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 900 !important;
        margin-top: 5px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    /* CARTULINAS PURAS (SIN NÚMERO) */
    button[key^="al"] { 
        background-color: #FFEB3B !important; 
        color: transparent !important; /* Escondemos el texto para que solo sea color */
        border-radius: 4px !important; 
        height: 3.5em !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2) !important;
    }
    button[key^="rl"] { 
        background-color: #F44336 !important; 
        color: transparent !important; 
        border-radius: 4px !important; 
        height: 3.5em !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2) !important;
    }

    /* FICHAS JUGADORES */
    .pista-activa { background-color: #00C853 !important; color: white !important; }
    .banquillo-espera { background-color: #FF5252 !important; color: #b71c1c !important; }

    .footer-control {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 15px 15px 0 0;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
        margin-top: 10px;
        width: 100%;
    }

    div.stButton > button {
        border-radius: 6px;
        height: 2.8em;
        width: 98% !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        border: none !important;
    }

    .mini-chip-container { display: flex; justify-content: center; gap: 4px; margin-top: 2px; }
    .mini-chip { padding: 1px 6px; border-radius: 12px; font-size: 0.7rem; font-weight: 800; background: #333; color: #fff; }
    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.2;} 100% {opacity: 1;} }
    .bonus-alert { background-color: #ff0000 !important; animation: blink 0.8s infinite; }
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
st.markdown(f'<div style="text-align:center; width:100%;"><h2 style="color:#003D7A; margin:0; font-weight:700; font-size:1rem;">LUD MATCH CONTROL</h2></div>', unsafe_allow_html=True)

d_top = st.columns([1.5, 1, 1, 0.5])
s.rv = d_top[0].text_input("R", s.rv, key="irv", label_visibility="collapsed").upper()
s.fe = d_top[1].text_input("F", s.fe, key="ife", label_visibility="collapsed")
with d_top[2]:
    with st.popover("👥 5 INICIAL", use_container_width=True):
        cp = sum(1 for x in s.js if x["p"])
        for j in s.js:
            if st.button(f"{'🟢' if j['p'] else '⚪'} {j['n']}", key=f"init_{j['n']}", use_container_width=True):
                if j["p"]: j["p"], j["i"], j["r"] = False, None, 0
                elif cp < 5: j["p"], j["r"] = True, 1; j["i"] = ah if s.on else None
                st.rerun()
d_top[3].button("🗑️", key="reset_btn")

# MARCADOR CENTRAL GIGANTE
c_sc = st.columns([2, 5, 2])
with c_sc[0]:
    st.metric("LUD", s.ml)
    f_bonus = "bonus-alert" if s.fl >= 5 else ""
    st.markdown(f'<div class="mini-chip-container"><div class="mini-chip {f_bonus}">❌ {s.fl}</div><div class="mini-chip" style="background:#FFEB3B; color:#000;">{s.al}</div><div class="mini-chip" style="background:#F44336; color:#fff;">{s.rl}</div></div>', 1)
    if st.button("⚽ GOL", key="btn_lud"):
        s.ml += 1; s.gi.append({"team":"LUD", "name":"LUD", "m":min_game}); st.rerun()

with c_sc[1]:
    if s.tm:
        st.markdown(f"<div class='stadium-tm'>{tm_sec}s</div>", unsafe_allow_html=True)
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

with c_sc[2]:
    st.metric(s.rv[:8], s.mr)
    fr_bonus = "bonus-alert" if s.fr >= 5 else ""
    st.markdown(f'<div class="mini-chip-container"><div class="mini-chip {fr_bonus}">❌ {s.fr}</div><div class="mini-chip" style="background:#FFEB3B; color:#000;">{s.ar}</div><div class="mini-chip" style="background:#F44336; color:#fff;">{s.rr}</div></div>', 1)
    if st.button("⚽ GOL", key="btn_riv"):
        s.mr+=1; s.gi.append({"team":"RIVAL", "name":s.rv[:8], "m":min_game}); st.rerun()

# GRID JUGADORES
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        estilo_ficha = "pista-activa" if j['p'] else "banquillo-espera"
        color_sub = "rgba(255,255,255,0.8)" if j['p'] else "#b71c1c"
        with st.container(border=True):
            st.markdown(f"<div class='{estilo_ficha}' style='padding:6px; width:100%; border-radius:4px;'>", 1)
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mt, vt = divmod(int(tl), 60)
            st.markdown(f"<div style='font-size:0.8rem; font-weight:900;'>{j['n']} <span style='float:right;'>R:{j['r']}</span></div>", 1)
            st.markdown(f"<div style='text-align:center; font-size:1.5rem; margin:2px 0; font-weight:900;'>{mj:02d}:{vj:02d}</div>", 1)
            st.markdown(f"<div style='text-align:center; font-size:0.8rem; font-weight:700; color:{color_sub};'>Σ {mt:02d}:{vt:02d}</div>", 1)
            if st.button("🔄 CAMBIO", key=f"c_{idx}", use_container_width=True):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", 1)

# FOOTER CONTROL
st.markdown("<div class='footer-control'>", 1)
b_footer = st.columns([3, 4, 3])

with b_footer[0]:
    st.markdown("<div style='font-size:0.7rem; font-weight:900; color:#333; text-align:center;'>LUD</div>", 1)
    if st.button("❌ F+", key="flp"): s.fl+=1; st.rerun()
    if st.button("F-", key="flm"): s.fl=max(0, s.fl-1); st.rerun()
    if st.button("⏱️ TM", key="tm_l"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()

with b_footer[1]:
    st.markdown("<div style='font-size:0.7rem; font-weight:900; color:#666; text-align:center;'>CARTULINAS Y PORTERO</div>", 1)
    c_t = st.columns(2)
    with c_t[0]:
        if st.button(".", key="al1"): s.al+=1; st.rerun()
        if st.button(".", key="rl1"): s.rl+=1; st.rerun()
    with c_t[1]:
        if st.button(".", key="al2"): s.ar+=1; st.rerun()
        if st.button(".", key="rl2"): s.rr+=1; st.rerun()
    st.markdown("<hr style='margin:8px 0; width:100%;'>", 1)
    c_p = st.columns(2)
    if c_p[0].button(f"🧤 {s.pm}", key="pm1"): s.pm+=1; st.rerun()
    if c_p[1].button(f"👟 {s.pp}", key="pp1"): s.pp+=1; st.rerun()

with b_footer[2]:
    st.markdown(f"<div style='font-size:0.7rem; font-weight:900; color:#333; text-align:center;'>{s.rv[:5]}</div>", 1)
    if st.button("❌ F+", key="frp"): s.fr+=1; st.rerun()
    if st.button("F-", key="frm"): s.fr=max(0, s.fr-1); st.rerun()
    if st.button("⏱️ TM", key="tm_r"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()
st.markdown("</div>", 1)
