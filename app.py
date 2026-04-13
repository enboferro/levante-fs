import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v11.1", layout="wide")

# --- CSS ULTRA COMPACTO CON ESCUDO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f5; overflow: hidden; }
    .block-container { padding: 0.2rem !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }

    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 2px;
    }

    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 5.5rem !important;
        font-weight: 700;
        color: #001A33;
        line-height: 0.9;
        text-align: center;
    }

    div.stButton > button[key="tm_m"] {
        width: 100% !important;
        max-width: 420px !important;
        height: 60px !important;
        background-color: #003D7A !important;
        color: white !important;
        border: 3px solid #ed1c24 !important;
        border-radius: 12px !important;
        font-size: 1.5rem !important;
        font-weight: 900 !important;
        margin: 5px auto !important;
        display: block !important;
    }

    .horizontal-timeline {
        display: flex;
        overflow-x: auto;
        white-space: nowrap;
        background: white;
        padding: 4px;
        border-radius: 8px;
        margin: 5px 0;
        border: 1px solid #ddd;
        gap: 5px;
    }
    .horizontal-timeline::-webkit-scrollbar { display: none; }

    .pista-activa { background-color: #00C853 !important; color: white !important; border-radius: 8px; padding: 5px; text-align: center; }
    .banquillo-espera { background-color: #D50000 !important; color: white !important; border-radius: 8px; padding: 5px; text-align: center; }
    
    .footer-control {
        background-color: #ffffff;
        padding: 8px;
        border-radius: 15px 15px 0 0;
        box-shadow: 0 -3px 10px rgba(0,0,0,0.1);
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n]
    st.session_state.eventos = []
    st.session_state.pm, st.session_state.pp = 0, 0
    st.session_state.al, st.session_state.rl, st.session_state.ar, st.session_state.rr, st.session_state.ml, st.session_state.mr, st.session_state.fl, st.session_state.fr = 0,0,0,0,0,0,0,0
    st.session_state.ta, st.session_state.ic, st.session_state.on, st.session_state.pa = 0.0,None,False,"1T"
    st.session_state.rv = "RIVAL"
    st.session_state.tm, st.session_state.tm_i = False, None
    st.session_state.t1_abs, st.session_state.t2_abs = 0.0, 0.0

s = st.session_state
st_autorefresh(1000, key="f5_v11.1")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_act = int((tr if s.pa=="1T" else tr+1200) // 60)

if s.on:
    if s.pa == "1T": s.t1_abs = tr
    else: s.t2_abs = tr

# Lógica TM
tm_sec = 0
if s.tm:
    elap = ah - s.tm_i
    tm_sec = max(0, 60 - int(elap))
    if tm_sec == 0: s.tm = False

def stop_match():
    if s.on:
        now = time.time()
        s.ta += now - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]:
                d = now - j["i"]; j["tot"] += d; j["tt"] += d; j["i"] = None

# --- UI CABECERA CON ESCUDO ---
st.markdown(f"""
    <div class="header-container">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="50">
        <h2 style='color:#003D7A; margin:0;'>LEVANTE UD MATCH CONTROL</h2>
    </div>
    """, unsafe_allow_html=True)

if s.tm:
    st.markdown(f"<div class='stadium-clock' style='color:#FF9800;'>⏱️ {tm_sec}s</div>", unsafe_allow_html=True)
else:
    mv, sv = divmod(int(rem), 60)
    st.markdown(f"<div class='stadium-clock'>{mv:02d}:{sv:02d}</div>", unsafe_allow_html=True)

if st.button("▶ START / STOP ⏸", key="tm_m"):
    if not s.on:
        s.ic, s.on, s.tm = ah, True, False
        for j in s.js: 
            if j["p"]: j["i"]=ah
    else: stop_match()
    st.rerun()

# LÍNEA SUCESOS
if s.eventos:
    tl_html = "<div class='horizontal-timeline'>"
    for ev in s.eventos:
        icon = "⚽" if ev['tipo']=='G' else "🟨" if ev['tipo']=='A' else "🟥"
        bg = "#003D7A" if ev['equipo']=='LUD' else "#eee"; tx = "#fff" if ev['equipo']=='LUD' else "#000"
        tl_html += f"<span class='event-badge' style='background:{bg}; color:{tx};'>{ev['min']}' {icon} {ev['info']}</span>"
    st.markdown(tl_html + "</div>", unsafe_allow_html=True)

# MARCADORES COMPACTOS
c_score = st.columns([1.5, 1.5, 1, 1, 1])
with c_score[0]:
    st.metric("LUD", s.ml)
    with st.popover("⚽ GOL", use_container_width=True):
        p_gol = st.selectbox("Autor", [j['n'] for j in s.js], key="gl")
        if st.button("OK"): s.ml += 1; s.eventos.append({'min':min_act, 'tipo':'G', 'equipo':'LUD', 'info':p_gol}); st.rerun()
with c_score[1]:
    st.metric(s.rv[:8], s.mr)
    with st.popover("⚽ GOL", use_container_width=True):
        d_gol = st.number_input("Dorsal", 1, 99, key="gr")
        if st.button("OK RIVAL"): s.mr += 1; s.eventos.append({'min':min_act, 'tipo':'G', 'equipo':'RIV', 'info':f"#{d_gol}"}); st.rerun()
with c_score[2]:
    m1, se1 = divmod(int(s.t1_abs), 60)
    st.caption(f"1T: {m1:02d}:{se1:02d}")
    m2, se2 = divmod(int(s.t2_abs), 60)
    st.caption(f"2T: {m2:02d}:{se2:02d}")
with c_score[3]:
    s.pa = st.selectbox("P", ["1T", "2T"], index=0 if s.pa=="1T" else 1, label_visibility="collapsed")
with c_score[4]:
    if st.button("🗑️"): st.session_state.clear(); st.rerun()

# JUGADORES
st.markdown("<div style='margin-bottom:5px;'></div>", unsafe_allow_html=True)
cols_j = st.columns(5)
for idx, j in enumerate(s.js):
    with cols_j[idx%5]:
        st_cl = "pista-activa" if j['p'] else "banquillo-espera"
        with st.container():
            st.markdown(f"<div class='{st_cl}'>", unsafe_allow_html=True)
            tc = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0); mj, vj = divmod(int(tc), 60)
            tl = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0); mt, vt = divmod(int(tl), 60)
            st.markdown(f"<b>{j['n']}</b> R:{j['r']}", 1)
            st.markdown(f"<div style='font-size:1.4rem; font-weight:900;'>{mj:02d}:{vj:02d}</div>", 1)
            st.markdown(f"<div style='font-size:0.7rem; opacity:0.8;'>Σ {mt:02d}:{vt:02d}</div>", 1)
            if st.button("🔄", key=f"c_{idx}", use_container_width=True, disabled=s.tm):
                if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1; j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# FOOTER
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
f_cols = st.columns([3, 4, 3])
with f_cols[0]:
    st.caption(f"LUD F: {s.fl}")
    st.button("❌ F+", key="flp", on_click=lambda: setattr(s, 'fl', s.fl+1))
    if st.button("⏱️ TM LUD"): stop_match(); s.tm, s.tm_i = True, time.time(); st.rerun()
with f_cols[1]:
    c_t = st.columns(2)
    with c_t[0]:
        with st.popover("🟨", use_container_width=True):
            p_a = st.selectbox("J", [j['n'] for j in s.js], key="pal")
            if st.button("OK Y"): s.al+=1; s.eventos.append({'min':min_act, 'tipo':'A', 'equipo':'LUD', 'info':p_a}); st.rerun()
        with st.popover("🟥", use_container_width=True):
            p_r = st.selectbox("J", [j['n'] for j in s.js], key="prl")
            if st.button("OK R"): s.rl+=1; s.eventos.append({'min':min_act, 'tipo':'R', 'equipo':'LUD', 'info':p_r}); st.rerun()
    with c_t[1]:
        if st.button(f"🧤 {s.pm}", use_container_width=True): s.pm+=1; st.rerun()
        if st.button(f"👟 {s.pp}", use_container_width=True): s.pp+=1; st.rerun()
with f_cols[2]:
    st.caption(f"RIV F: {s.fr}")
    st.button("❌ F+", key="frp", on_click=lambda: setattr(s, 'fr', s.fr+1))
    if st.button("⏱️ TM RIV"): stop_match(); s.tm, s.tm_i = True, time.time(); st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
