import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v5.7", layout="wide")

# CSS PARA COMPRESIÓN DE ESPACIO AL MÁXIMO
st.markdown("""
    <style>
    .block-container {padding-top:0rem; padding-bottom:0rem; padding-left:1rem; padding-right:1rem;}
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
    [data-testid="stMetric"] { padding: 0px !important; }
    
    /* Eliminar espacios entre filas de columnas */
    div[data-testid="column"] { padding: 0px !important; }
    
    div.stButton > button {
        border-radius: 6px;
        height: 2.1em;
        width: 100%;
        font-size: 0.9rem !important;
        font-weight: bold !important;
        transition: none !important;
    }
    
    div.stButton > button:active { transform: scale(0.92); background-color: #003D7A !important; }

    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        border-bottom: 2px solid #ed1c24;
        margin-bottom: 5px;
        padding-top: 5px;
    }

    .title {color:#003D7A; font-size:1.5rem; font-weight:bold; margin:0;}
    .label-x {font-size:0.7rem; font-weight:bold; text-align:center; color:#444; margin-top:2px;}
    
    hr { margin: 0.5rem 0px !important; } /* Divisor más fino */

    button[key*="dok_btn"] { background-color: #e8f5e9 !important; border: 1px solid #28a745 !important; }
    button[key*="dko_btn"] { background-color: #ffebee !important; border: 1px solid #dc3545 !important; }
    </style>
    """, unsafe_allow_html=True)

if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False,"g":0} for x in n]
    st.session_state.gi, st.session_state.pm, st.session_state.pp, st.session_state.dok, st.session_state.dko = [],0,0,0,0
    st.session_state.al, st.session_state.rl, st.session_state.ar, st.session_state.rr, st.session_state.ml, st.session_state.mr, st.session_state.fl, st.session_state.fr = 0,0,0,0,0,0,0,0
    st.session_state.ta, st.session_state.ic, st.session_state.on, st.session_state.pa, st.session_state.ex = 0.0,None,False,"1T",False
    st.session_state.rv, st.session_state.fe = "RIVAL", datetime.now().strftime("%d/%m/%Y")

s = st.session_state
if not s.ex: st_autorefresh(1000, key="f5_refresh_v57")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
mp, sp = divmod(int(tr if s.pa=="1T" else tr+1200), 60)

# CABECERA
st.markdown(f"""
    <div class="header-container">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="40">
        <h1 class="title">MATCH CONTROL</h1>
    </div>
    """, unsafe_allow_html=True)

# FILA RIVAL Y FECHA (Compacta)
d1, d2, d3 = st.columns([2, 1, 1])
s.rv = d1.text_input("RIVAL", s.rv, key="irv", label_visibility="collapsed").upper()
s.fe = d2.text_input("FECHA", s.fe, key="ife", label_visibility="collapsed")
if d3.button("🗑️ RESET", key="main_rst"):
    st.session_state.clear()
    st.rerun()

# MARCADOR CENTRAL
c1, c2, c3 = st.columns([3, 2.5, 3])

with c1:
    st.metric(f"LUD | ⚽ {s.ml} | ❌ {s.fl}", s.ml)
    cg, cf1, cf2 = st.columns([1.5,1,1])
    with cg:
        with st.popover("⚽ GOL", use_container_width=True):
            for i,j in enumerate(s.js):
                if st.button(j["n"], key=f"gp_lud_{i}"):
                    s.ml+=1; j["g"]+=1; s.gi.append({"j":j["n"],"m":f"{mp:02d}:{sp:02d}"})
                    st.rerun()
    if cf1.button("F+", key="flp_btn"): s.fl+=1; st.rerun()
    if cf2.button("F-", key="flm_btn"): s.fl=max(0, s.fl-1); st.rerun()
    t1,t2 = st.columns(2)
    if t1.button(f"🟨 {s.al}", key="btn_tal"): s.al+=1; st.rerun()
    if t2.button(f"🟥 {s.rl}", key="btn_trl"): s.rl+=1; st.rerun()
    p_col, d_col = st.columns(2)
    with p_col:
        st.markdown("<div class='label-x'>🧤 PORT</div>", 1)
        px1, px2 = st.columns(2)
        if px1.button(f"🧤{s.pm}", key="pm_btn"): s.pm += 1; st.rerun()
        if px2.button(f"👟{s.pp}", key="pp_btn"): s.pp += 1; st.rerun()
    with d_col:
        tot_d = s.dok + s.dko
        perc = (s.dok/tot_d*100) if tot_d > 0 else 0
        st.markdown(f"<div class='label-x'>⚔️ ({perc:.0f}%)</div>", 1)
        dx1, dx2 = st.columns(2)
        if dx1.button(f"✅{s.dok}", key="dok_btn"): s.dok += 1; st.rerun()
        if dx2.button(f"❌{s.dko}", key="dko_btn"): s.dko += 1; st.rerun()

with c2:
    mr_v, sr_v = divmod(int(rem), 60)
    st.markdown(f"<h1 style='text-align:center;font-size:3.5rem;color:red;margin:0;line-height:1;'>{mr_v:02d}:{sr_v:02d}</h1>",1)
    if st.button("▶ START / ⏸ STOP", use_container_width=True, key="tm_main", type="primary"):
        if not s.on:
            s.ic, s.on = ah, True
            for j in s.js: 
                if j["p"]: j["i"]=ah
        else:
            s.ta += ah-s.ic; s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: d_d = ah-j["i"]; j["tt"]+=d_d; j["tot"]+=d_d; j["i"]=None
        st.rerun()
    for g in s.gi[-1:]: # Solo mostramos el último gol para ahorrar espacio
        st.markdown(f"<p style='font-size:0.8rem;margin:0;text-align:center;'><b>{g['m']}</b> {g['j']}</p>", 1)

with c3:
    st.metric(f"{s.rv[:8]} | ⚽ {s.mr} | ❌ {s.fr}", s.mr)
    cg_r, cf1_r, cf2_r = st.columns([1.5,1,1])
    if cg_r.button("⚽ GOL", key="gr_btn_r"):
        s.mr+=1; s.gi.append({"j":s.rv,"m":f"{mp:02d}:{sp:02d}"}); st.rerun()
    if cf1_r.button("F+", key="frp_btn"): s.fr+=1; st.rerun()
    if cf2_r.button("F-", key="frm_btn"): s.fr=max(0, s.fr-1); st.rerun()
    tr1, tr2 = st.columns(2)
    if tr1.button(f"🟨 {s.ar}", key="tar_r_btn"): s.ar+=1; st.rerun()
    if tr2.button(f"🟥 {s.rr}", key="trr_r_btn"): s.rr+=1; st.rerun()

st.divider()

# JUGADORES
cols = st.columns(5)
for idx, j in enumerate(s.js):
    with cols[idx%5]:
        with st.container(border=True):
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(tc), 60)
            st.markdown(f"<p style='margin:0;font-size:0.8rem;'>{'🟢' if j['p'] else '🔴'} <b>{j['n']}</b> <small>(R:{j['r']})</small></p>", 1)
            st.markdown(f"<h4 style='margin:0;text-align:center;'>{mj:02d}:{vj:02d}</h4>", 1)
            if st.button("CAMBIO", key=f"c_idx_{idx}", use_container_width=1):
                if not j["p"] and sum(1 for x in s.js if x["p"])<5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1
                    j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d_d = ah-j["i"]; j["tot"]+=d_d; j["tt"]+=d_d
                    j["p"], j["i"] = False, None
                st.rerun()

tab1, tab2 = st.tabs(["📊 TOTALES", "💾 EXCEL"])
with tab1:
    st.write(f"Duelos: ✅{s.dok} ❌{s.dko} ({perc:.1f}%) | Port: 🧤{s.pm} 👟{s.pp}")
    mc = st.columns(5)
    for idx, j in enumerate(s.js):
        tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        mt, vt = divmod(int(tl), 60)
        mc[idx%5].write(f"**{j['n']}**: {mt:02d}:{vt:02d}")
