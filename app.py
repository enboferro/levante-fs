import streamlit as st
import pandas as pd
import time
import io
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control", layout="wide")

# CSS para alineación y estética
st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-bottom: 0rem;}
    [data-testid="stVerticalBlock"] > div { gap: 0.1rem; }
    div.stButton > button {
        border-radius: 5px;
        height: 2em;
        font-size: 0.85rem !important;
    }
    .main-title {
        text-align: center;
        color: #003D7A;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #ed1c24;
    }
    .goleador-box { background-color: #f0f2f6; padding: 4px; border-radius: 5px; font-size: 0.8rem; border-left: 3px solid #003D7A; }
    .label-mini { font-size: 0.75rem; font-weight: bold; text-align: center; color: #666; margin-top: 5px;}
    </style>
    """, unsafe_allow_html=True)

def init_state(force=False):
    if 'js' not in st.session_state or force:
        n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
        st.session_state.js = [{"n":x,"t_turno":0.0,"t_total":0.0,"rot":0,"i":None,"p":False,"g":0} for x in n]
        st.session_state.goles_info = []
        st.session_state.p_mano, st.session_state.p_pie = 0, 0
        st.session_state.ta_l, st.session_state.tr_l, st.session_state.ta_r, st.session_state.tr_r = 0, 0, 0, 0
        st.session_state.ml, st.session_state.mr, st.session_state.fl, st.session_state.fr = 0, 0, 0, 0
        st.session_state.ta, st.session_state.ic, st.session_state.on, st.session_state.pa = 0.0, None, False, "1T"
        st.session_state.ex = False

init_state()
s = st.session_state
if not s.ex: st_autorefresh(1000, key="f5_v48")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_p, seg_p = divmod(int(tr if s.pa=="1T" else tr+1200), 60)

# TÍTULO PRINCIPAL
st.markdown("<div class='main-title'>M A T C H &nbsp; C O N T R O L</div>", unsafe_allow_html=True)

# --- CABECERA ALINEADA ---
c1, c2, c3 = st.columns([2.5, 3, 2.5])

with c1: # BLOQUE LUD
    st.metric(f"LUD | ⚽ {s.ml} | ❌ {s.fl}", s.ml)
    
    # Goles y Faltas alineados
    col_g, col_f = st.columns(2)
    with col_g:
        with st.popover("⚽ GOL", use_container_width=True):
            for j in s.js:
                if st.button(j["n"], key=f"gsel_{j['n']}"):
                    s.ml += 1; j["g"] += 1
                    s.goles_info.append({"jugador":j["n"],"min":f"{min_p:02d}","seg":f"{seg_p:02d}"})
                    st.rerun()
    with col_f:
        if st.button("F+", key="k_flp", use_container_width=True): s.fl+=1; st.rerun()

    # Tarjetas y Portero debajo alineados
    t1, t2 = st.columns(2)
    if t1.button(f"🟨 {s.ta_l}", key="k_tal", use_container_width=True): s.ta_l+=1; st.rerun()
    if t2.button(f"🟥 {s.tr_l}", key="k_trl", use_container_width=True): s.tr_l+=1; st.rerun()
    
    st.markdown("<div class='label-mini'>🧤 PORTERO</div>",1)
    p1, p2 = st.columns(2)
    if p1.button(f"🧤 {s.p_mano}", key="kp1", use_container_width=True): s.p_mano+=1; st.rerun()
    if p2.button(f"👟 {s.p_pie}", key="kp2", use_container_width=True): s.p_pie+=1; st.rerun()

with c2: # BLOQUE CENTRAL: CRONO
    m, v = divmod(int(rem), 60)
    st.markdown(f"<h1 style='text-align:center;font-size:3.8rem;color:red;margin:0;line-height:1;'>{m:02d}:{v:02d}</h1>",1)
    if st.button("▶ START / ⏸ STOP", use_container_width=1, key="k_timer", type="primary"):
        if not s.on:
            s.ic, s.on = ah, True
            for j in s.js: 
                if j["p"]: j["i"]=ah
        else:
            s.ta += ah-s.ic; s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: 
                    dur = ah-j["i"]; j["t_turno"]+=dur; j["t_total"]+=dur; j["i"]=None
        st.rerun()
    with st.expander("⚽ ÚLTIMOS GOLES", expanded=True):
        for g in s.goles_info[-2:]: st.markdown(f"<div class='goleador-box'>{g['min']}:{g['seg']} - {g['jugador']}</div>", 1)
    if st.button("🗑️ RESET", use_container_width=1, key="k_res"): init_state(True); st.rerun()

with c3: # BLOQUE RIVAL
    st.metric(f"RIVAL | ⚽ {s.mr} | ❌ {s.fr}", s.mr)
    
    col_gr, col_fr = st.columns(2)
    with col_gr:
        if st.button("⚽ GOL", key="k_gr", use_container_width=True):
            s.mr+=1
            s.goles_info.append({"jugador":"RIVAL","min":f"{min_p:02d}","seg":f"{seg_p:02d}"})
            st.rerun()
    with col_fr:
        if st.button("F+", key="k_frp", use_container_width=True): s.fr+=1; st.rerun()

    tr1, tr2 = st.columns(2)
    if tr1.button(f"🟨 {s.ta_r}", key="k_tar", use_container_width=True): s.ta_r+=1; st.rerun()
    if tr2.button(f"🟥 {s.tr_r}", key="k_trr", use_container_width=True): s.tr_r+=1; st.rerun()
    
    # Espacio para mantener alineación con el portero del LUD
    st.markdown("<div style='height:45px;'></div>", 1) 
    if st.button("F- RIVAL", key="k_frm", use_container_width=True): s.fr=max(0, s.fr-1); st.rerun()

st.divider()

# --- JUGADORES (VISTA COMPACTA) ---
cols = st.columns(5)
for idx, j in enumerate(s.js):
    with cols[idx%5]:
        with st.container(border=True):
            t_disp = j["t_turno"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(t_disp), 60)
            st.markdown(f"<p style='margin:0;font-size:0.8rem;'>{'🟢' if j['p'] else '🔴'} <b>{j['n']}</b> <small>(R:{j['rot']})</small></p>", 1)
            st.markdown(f"<h3 style='margin:0;text-align:center;'>{mj:02d}:{vj:02d}</h3>", 1)
            
            if st.button("CAMBIO", key=f"c{idx}", use_container_width=1):
                if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                    j["p"], j["i"], j["rot"] = True, (ah if s.on else None), j["rot"]+1
                    j["t_turno"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: 
                        dur = ah - j["i"]; j["t_total"] += dur; j["t_turno"] += dur
                    j["p"], j["i"] = False, None
                st.rerun()

# --- PESTAÑAS ---
t_tot, t_ex = st.tabs(["📊 TOTALES", "💾 INFORME"])
with t_tot:
    st.write(f"Portero: 🧤 {s.p_mano} | 👟 {s.p_pie}")
    mc = st.columns(5)
    for idx, j in enumerate(s.js):
        t_tot_val = j["t_total"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
        mt, vt = divmod(int(t_tot_val), 60)
        mc[idx%5].write(f"**{j['n']}**: {mt:02d}:{vt:02d} (G:{j['g']})")
