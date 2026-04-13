import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v8.3", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .block-container {padding-top:0.5rem; padding-bottom:0rem; padding-left:0.5rem; padding-right:0.5rem; background-color: #f5f5f5;}
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
    
    /* CARDS MATERIAL */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
        padding: 10px !important;
        margin-bottom: 8px !important;
    }

    /* BOTONES */
    div.stButton > button {
        border-radius: 8px;
        height: 2.8em;
        width: 100% !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        border: none !important;
        transition: all 0.2s ease;
    }

    /* BOTÓN START/STOP */
    div.stButton > button[key="tm_m"] {
        background-color: #6200EE !important;
        color: white !important;
        box-shadow: 0 4px 6px rgba(98,0,238,0.3);
    }

    /* SUB-MARCADOR DE FALTAS Y TARJETAS */
    .mini-chip-container {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 5px;
    }
    .mini-chip {
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        background: #eeeeee;
        color: #424242;
    }
    .bonus-alert { background-color: #B00020 !important; color: white !important; animation: blink 1s infinite; }

    .footer-control {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px 20px 0 0;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.05);
        margin-top: 10px;
    }

    .label-x {
        font-size: 0.65rem;
        font-weight: 800;
        color: #9e9e9e;
        text-align: center;
        margin-bottom: 4px;
        text-transform: uppercase;
    }

    .status-dot { height: 6px; width: 100%; border-radius: 3px; margin-bottom: 8px; }
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
if not s.ex: st_autorefresh(1000, key="f5_8.3")

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
st.markdown(f'<div style="text-align:center;"><h2 style="color:#003D7A; margin:0; font-weight:700; font-size:1rem;">LUD MATCH CONTROL v8.3</h2></div>', unsafe_allow_html=True)

d_top = st.columns([1.5, 1, 1, 0.5])
s.rv = d_top[0].text_input("R", s.rv, label_visibility="collapsed").upper()
s.fe = d_top[1].text_input("F", s.fe, label_visibility="collapsed")
with d_top[2]:
    with st.popover("BANQUILLO", use_container_width=True):
        cp = sum(1 for x in s.js if x["p"])
        for j in s.js:
            if st.button(f"{'🟢' if j['p'] else '⚪'} {j['n']}", key=f"init_{j['n']}", use_container_width=True):
                if j["p"]: j["p"], j["i"], j["r"] = False, None, 0
                elif cp < 5: j["p"], j["r"] = True, 1; j["i"] = ah if s.on else None
                st.rerun()
d_top[3].button("🗑️", key="reset_btn")

# SCOREBOARD CON DATOS EXTRA
c_sc = st.columns([2.5, 3, 2.5])

# LADO LUD
with c_sc[0]:
    st.metric("LUD", s.ml)
    # Mini chips informativos
    f_bonus = "bonus-alert" if s.fl >= 5 else ""
    st.markdown(f"""
        <div class="mini-chip-container">
            <div class="mini-chip {f_bonus}">❌ {s.fl}</div>
            <div class="mini-chip">🟨 {s.al}</div>
            <div class="mini-chip">🟥 {s.rl}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("⚽ GOL LUD", key="btn_lud"):
        s.ml += 1; s.gi.append({"team":"LUD", "name":"LUD", "m":min_game}); st.rerun()

# CENTRO CRONO
with c_sc[1]:
    if s.tm: st.markdown(f"<h1 style='text-align:center;font-size:2.8rem;color:#FF9800;margin:0;'>{tm_sec}s</h1>",1)
    else:
        mr_v, sr_v = divmod(int(rem), 60)
        st.markdown(f"<h1 style='text-align:center;font-size:3.2rem;color:#B00020;margin:0;font-weight:700;'>{mr_v:02d}:{sr_v:02d}</h1>",1)
    if st.button("▶ START / STOP ⏸", key="tm_m", type="primary", use_container_width=True):
        if not s.on:
            s.ic, s.on, s.tm = ah, True, False
            for j in s.js: 
                if j["p"]: j["i"]=ah
        else:
            s.ta += ah-s.ic; s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d; j["i"]=None
        st.rerun()

# LADO RIVAL
with c_sc[2]:
    st.metric(s.rv[:8], s.mr)
    # Mini chips informativos
    fr_bonus = "bonus-alert" if s.fr >= 5 else ""
    st.markdown(f"""
        <div class="mini-chip-container">
            <div class="mini-chip {fr_bonus}">❌ {s.fr}</div>
            <div class="mini-chip">🟨 {s.ar}</div>
            <div class="mini-chip">🟥 {s.rr}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button(f"⚽ GOL {s.rv[:8]}", key="btn_riv"):
        s.mr+=1; s.gi.append({"team":"RIVAL", "name":s.rv[:8], "m":min_game}); st.rerun()

# GRID JUGADORES
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        with st.container(border=True):
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mt, vt = divmod(int(tl), 60)
            st.markdown(f"<div class='status-dot' style='background-color:{'#4CAF50' if j['p'] else '#E0E0E0'};'></div>", 1)
            st.markdown(f"<div style='font-size:0.75rem; font-weight:700;'>{j['n']} <span style='float:right; color:#9E9E9E;'>R:{j['r']}</span></div>", 1)
            fatiga_c = "color:#FB8C00; font-weight:900;" if mj >= 5 else "color:#212121;"
            st.markdown(f"<div style='text-align:center; font-size:1.4rem; margin:2px 0; {fatiga_c}'>{mj:02d}:{vj:02d}</div>", 1)
            st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:0.8rem; color:#616161;'><span>⚽ {j['g']}</span><span>Σ {mt:02d}:{vt:02d}</span></div>", 1)
            if st.button("CAMBIO", key=f"c_{idx}"):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()

# FOOTER CONTROL
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
b_f = st.columns([3, 4, 3])

with b_f[0]: # LUD
    st.markdown(f"<div class='label-x'>LUD | FALTAS</div>", 1)
    if st.button("FALTA +", key="flp"): s.fl+=1; st.rerun()
    if st.button("FALTA -", key="flm"): s.fl=max(0, s.fl-1); st.rerun()
    if st.button("⏱️ TM LUD", key="tm_l"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()

with b_f[1]: # CENTRO
    st.markdown("<div class='label-x'>DISCIPLINA Y PORTERÍA</div>", 1)
    c_t1, c_t2 = st.columns(2)
    c_t1.button(f"🟨 LUD ({s.al})", key="al1") and exec("s.al+=1; st.rerun()")
    c_t1.button(f"🟥 LUD ({s.rl})", key="rl1") and exec("s.rl+=1; st.rerun()")
    c_t2.button(f"🟨 RIV ({s.ar})", key="al2") and exec("s.ar+=1; st.rerun()")
    c_t2.button(f"🟥 RIV ({s.rr})", key="rl2") and exec("s.rr+=1; st.rerun()")
    st.markdown("<hr style='margin:10px 0; border:0; border-top:1px solid #eee;'>", 1)
    c_p1, c_p2 = st.columns(2)
    c_p1.button(f"🧤 MANO: {s.pm}", key="pm1") and exec("s.pm+=1; st.rerun()")
    c_p2.button(f"👟 PIE: {s.pp}", key="pp1") and exec("s.pp+=1; st.rerun()")

with b_f[2]: # RIVAL
    st.markdown(f"<div class='label-x'>{s.rv[:8]} | FALTAS</div>", 1)
    if st.button("FALTA +", key="frp"): s.fr+=1; st.rerun()
    if st.button("FALTA -", key="frm"): s.fr=max(0, s.fr-1); st.rerun()
    if st.button("⏱️ TM RIVAL", key="tm_r"):
        if s.on: s.ta += ah-s.ic; s.on, s.ic = False, None
        s.tm, s.tm_i = True, ah; st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
