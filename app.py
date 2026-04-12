import streamlit as st
import pandas as pd
import time
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v5.0", layout="wide")

# CSS para estilo y colores de botones
st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-bottom: 0rem;}
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
        margin-bottom: 0.2rem;
        border-bottom: 2px solid #ed1c24;
    }
    .label-mini { 
        font-size: 0.75rem; 
        font-weight: bold; 
        text-align: center; 
        color: #666; 
        margin-top: 8px;
        border-top: 1px solid #eee;
        padding-top: 3px;
    }
    /* Estilo para los botones de duelos */
    button[key*="btn_ok"] { border: 2px solid #28a745 !important; }
    button[key*="btn_ko"] { border: 2px solid #dc3545 !important; }
    </style>
    """, unsafe_allow_html=True)

def init_state(force=False):
    if 'js' not in st.session_state or force:
        n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
        st.session_state.js = [{"n":x,"t_turno":0.0,"t_total":0.0,"rot":0,"i":None,"p":False,"g":0} for x in n]
        st.session_state.goles_info = []
        # Estadísticas globales
        st.session_state.p_mano, st.session_state.p_pie = 0, 0
        st.session_state.d_ok, st.session_state.d_ko = 0, 0
        st.session_state.ta_l, st.session_state.tr_l, st.session_state.ta_r, st.session_state.tr_r = 0, 0, 0, 0
        st.session_state.ml, st.session_state.mr, st.session_state.fl, st.session_state.fr = 0, 0, 0, 0
        # Cronómetro
        st.session_state.ta, st.session_state.ic, st.session_state.on, st.session_state.pa = 0.0, None, False, "1T"
        st.session_state.rival_name = "RIVAL"
        st.session_state.fecha_partido = datetime.now().strftime("%d/%m/%Y")
        st.session_state.ex = False

init_state()
s = st.session_state
if not s.ex: st_autorefresh(1000, key="f5_v50")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_p, seg_p = divmod(int(tr if s.pa=="1T" else tr+1200), 60)

st.markdown("<div class='main-title'>M A T C H &nbsp; C O N T R O L</div>", unsafe_allow_html=True)

# DATOS PARTIDO
d1, d2, d3 = st.columns([2, 1, 1])
s.rival_name = d1.text_input("EQUIPO RIVAL", s.rival_name).upper()
s.fecha_partido = d2.text_input("FECHA", s.fecha_partido)
if d3.button("🗑️ RESET TOTAL", key="reset_all", use_container_width=True):
    init_state(True); st.rerun()

st.divider()

# CABECERA
c1, c2, c3 = st.columns([2.5, 3, 2.5])

with c1: # COLUMNA IZQUIERDA: LUD + PORTERO + DUELOS
    st.metric(f"LUD | ⚽ {s.ml} | ❌ {s.fl}", s.ml)
    
    cg, cf1, cf2 = st.columns([2,1,1])
    with cg:
        with st.popover("⚽ GOL", use_container_width=True):
            for j in s.js:
                if st.button(j["n"], key=f"gol_lud_{j['n']}"):
                    s.ml += 1; j["g"] += 1
                    s.goles_info.append({"jugador":j["n"],"min":f"{min_p:02d}","seg":f"{seg_p:02d}"})
                    st.rerun()
    if cf1.button("F+", key="flp", use_container_width=True): s.fl+=1; st.rerun()
    if cf2.button("F-", key="flm", use_container_width=True): s.fl=max(0, s.fl-1); st.rerun()

    t1, t2 = st.columns(2)
    if t1.button(f"🟨 {s.ta_l}", key="tal", use_container_width=True): s.ta_l+=1; st.rerun()
    if t2.button(f"🟥 {s.tr_l}", key="trl", use_container_width=True): s.tr_l+=1; st.rerun()
    
    # SECCIÓN PORTERO
    st.markdown("<div class='label-mini'>🧤 PORTERO</div>", unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    if p1.button(f"🧤 {s.p_mano}", key="kp1", use_container_width=True): s.p_mano+=1; st.rerun()
    if p2.button(f"👟 {s.p_pie}", key="kp2", use_container_width=True): s.p_pie+=1; st.rerun()

    # SECCIÓN DUELOS (NUEVA)
    st.markdown("<div class='label-mini'>⚔️ DUELOS</div>", unsafe_allow_html=True)
    d_ok_col, d_ko_col = st.columns(2)
    if d_ok_col.button(f"✅ {s.d_ok}", key="btn_ok", use_container_width=True):
        s.d_ok += 1; st.rerun()
    if d_ko_col.button(f"❌ {s.d_ko}", key="btn_ko", use_container_width=True):
        s.d_ko += 1; st.rerun()

with c2: # COLUMNA CENTRAL: RELOJ
    m_r, s_r = divmod(int(rem), 60)
    st.markdown(f"<h1 style='text-align:center;font-size:3.8rem;color:red;margin:0;line-height:1;'>{m_r:02d}:{s_r:02d}</h1>",1)
    if st.button("▶ START / ⏸ STOP", use_container_width=1, key="main_timer", type="primary"):
        if not s.on:
            s.ic, s.on = ah, True
            for j in s.js: 
                if j["p"]: j["i"] = ah
        else:
            s.ta += ah - s.ic; s.on, s.ic = False, None
            for j in s.js:
                if j["p"] and j["i"]: 
                    dur = ah - j["i"]; j["t_turno"] += dur; j["t_total"] += dur; j["i"] = None
        st.rerun()
    with st.expander("⚽ ÚLTIMOS GOLES", expanded=True):
        for g in s.goles_info[-2:]: st.markdown(f"<div class='goleador-box'>{g['min']}:{g['seg']} - {g['jugador']}</div>", 1)

with c3: # COLUMNA DERECHA: RIVAL
    st.metric(f"{s.rival_name[:8]} | ⚽ {s.mr} | ❌ {s.fr}", s.mr)
    cg_r, cf1_r, cf2_r = st.columns([2,1,1])
    if cg_r.button("⚽ GOL", key="gr", use_container_width=True):
        s.mr += 1
        s.goles_info.append({"jugador":s.rival_name,"min":f"{min_p:02d}","seg":f"{seg_p:02d}"})
        st.rerun()
    if cf1_r.button("F+", key="frp", use_container_width=True): s.fr+=1; st.rerun()
    if cf2_r.button("F-", key="frm", use_container_width=True): s.fr=max(0, s.fr-1); st.rerun()

    tr1, tr2 = st.columns(2)
    if tr1.button(f"🟨 {s.ta_r}", key="tar", use_container_width=True): s.ta_r+=1; st.rerun()
    if tr2.button(f"🟥 {s.tr_r}", key="trr", use_container_width=True): s.tr_r+=1; st.rerun()

st.divider()

# JUGADORES
cols = st.columns(5)
for idx, j in enumerate(s.js):
    with cols[idx%5]:
        with st.container(border=True):
            t_c = j["t_turno"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, vj = divmod(int(t_c), 60)
            st.markdown(f"<p style='margin:0;font-size:0.8rem;'>{'🟢' if j['p'] else '🔴'} <b>{j['n']}</b> <small>(R:{j['rot']})</small></p>", 1)
            st.markdown(f"<h3 style='margin:0;text-align:center;'>{mj:02d}:{vj:02d}</h3>", 1)
            if st.button("CAMBIO", key=f"c_{idx}", use_container_width=1):
                if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                    j["p"], j["i"], j["rot"] = True, (ah if s.on else None), j["rot"]+1
                    j["t_turno"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: 
                        dur = ah - j["i"]; j["t_total"] += dur; j["t_turno"] += dur
                    j["p"], j["i"] = False, None
                st.rerun()

# INFORME
t1_inf, t2_inf = st.tabs(["📊 TOTALES", "💾 EXCEL"])
with t1_inf:
    st.write(f"**Duelos:** ✅ Ganados: {s.d_ok} | ❌ Perdidos: {s.d_ko}")
    st.write(f"**Portero:** 🧤 Manos: {s.p_mano} | 👟 Pies: {s.p_pie}")
    mc = st.columns(5)
    for idx, j in enumerate(s.js):
        t_l = j["t_total"] + (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
        mt, vt = divmod(int(t_l), 60)
        mc[idx%5].write(f"**{j['n']}**: {mt:02d}:{vt
