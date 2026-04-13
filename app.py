import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Levante UD Match Control v11.3", layout="wide")

# --- CSS ULTRA-REDUCIDO PARA IPAD 11" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f4f4f4; overflow: hidden; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }

    .header-container {
        display: flex; align-items: center; justify-content: center; gap: 10px;
        padding: 2px; background: white; border-radius: 0 0 12px 12px;
        border-bottom: 2px solid #003D7A;
    }

    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 4.2rem !important;
        font-weight: 700; color: #003D7A;
        line-height: 0.8; text-align: center; margin: 1px 0;
    }

    div.stButton > button[key="tm_m"] {
        width: 100% !important; max-width: 280px !important;
        height: 40px !important; background-color: #003D7A !important;
        color: white !important; border: 2px solid #ed1c24 !important;
        border-radius: 10px !important; font-size: 1.1rem !important;
        font-weight: 900 !important; margin: 2px auto !important; display: block !important;
    }

    .horizontal-timeline {
        display: flex; overflow-x: auto; background: white;
        padding: 2px; border-radius: 5px; margin: 2px 0;
        border: 1px solid #003D7A; gap: 4px; height: 28px;
    }

    .pista-activa { background-color: #00C853 !important; color: white !important; border-radius: 6px; padding: 2px; text-align: center; }
    .banquillo-espera { background-color: #ed1c24 !important; color: white !important; border-radius: 6px; padding: 2px; text-align: center; }
    
    .footer-control {
        background-color: #ffffff; padding: 2px 4px;
        border-radius: 10px 10px 0 0; border-top: 2px solid #003D7A;
        margin-top: 1px;
    }
    
    [data-testid="stMetricValue"] { font-size: 1.3rem !important; color: #003D7A !important; line-height: 1 !important; }
    </style>
    """, unsafe_allow_html=True)

if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n],
        "eventos": [], "pm": 0, "pp": 0, "al": 0, "rl": 0, "ar": 0, "rr": 0, 
        "ml": 0, "mr": 0, "fl": 0, "fr": 0, "ta": 0.0, "ic": None, "on": False, 
        "pa": "1T", "rv": "RIVAL", "tm": False, "tm_i": None, "t1_abs": 0.0, "t2_abs": 0.0
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v11.3")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_act = int((tr if s.pa=="1T" else tr+1200) // 60)

if s.on:
    if s.pa == "1T": s.t1_abs = tr
    else: s.t2_abs = tr

tm_sec = max(0, 60 - int(ah - s.tm_i)) if s.tm and s.tm_i else 0
if s.tm and tm_sec == 0: s.tm = False

def stop_match():
    if s.on:
        now = time.time()
        s.ta += now - s.ic; s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]:
                d = now - j["i"]; j["tot"] += d; j["tt"] += d; j["i"] = None

# CABECERA
st.markdown(f'<div class="header-container"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="30"><b style="color:#003D7A; font-size:0.9rem;">LEVANTE UD CONTROL</b></div>', unsafe_allow_html=True)

# CRONO
if s.tm: st.markdown(f"<div class='stadium-clock' style='color:#FF9800;'>{tm_sec}s</div>", unsafe_allow_html=True)
else:
    m, sec = divmod(int(rem), 60)
    st.markdown(f"<div class='stadium-clock'>{m:02d}:{sec:02d}</div>", unsafe_allow_html=True)

if st.button("▶ START / STOP ⏸", key="tm_m"):
    if not s.on:
        s.ic, s.on, s.tm = ah, True, False
        for j in s.js: 
            if j["p"]: j["i"]=ah
    else: stop_match()
    st.rerun()

# LINEA EVENTOS
if s.eventos:
    tl = "".join([f"<span style='background:#003D7A;color:white;padding:1px 3px;border-radius:3px;font-size:0.65rem;margin-right:2px;'>{e['min']}' {e['info']}</span>" for e in s.eventos])
    st.markdown(f"<div class='horizontal-timeline'>{tl}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='horizontal-timeline'></div>", unsafe_allow_html=True)

# SCORE BAR
c1, c2, c3, c4 = st.columns([1, 1, 2, 1])
with c1: 
    st.metric("LUD", s.ml)
    with st.popover("⚽ GOL", use_container_width=True):
        p_gol = st.selectbox("Jugador", [j['n'] for j in s.js], key="gl")
        if st.button("OK LUD"): s.ml+=1; s.eventos.append({'min':min_act,'info':f'⚽{p_gol}'}); st.rerun()
with c2: 
    st.metric("RIV", s.mr)
    with st.popover("⚽ GOL", use_container_width=True):
        d_gol = st.number_input("Dorsal", 1, 99, key="gr")
        if st.button("OK RIVAL"): s.mr+=1; s.eventos.append({'min':min_act,'info':f'⚽#{d_gol}'}); st.rerun()
with c3:
    m1, se1 = divmod(int(s.t1_abs), 60); m2, se2 = divmod(int(s.t2_abs), 60)
    st.markdown(f"<div style='font-size:0.6rem;text-align:center;'>1T {m1:02d}:{se1:02d} | 2T {m2:02d}:{se2:02d}</div>", unsafe_allow_html=True)
    s.pa = st.selectbox("", ["1T","2T"], index=0 if s.pa=="1T" else 1, label_visibility="collapsed")
with c4:
    if st.button("🗑️", use_container_width=True): st.session_state.clear(); st.rerun()

# JUGADORES (6 por fila)
st.markdown("<div style='margin-bottom:1px;'></div>", unsafe_allow_html=True)
cols = st.columns(6)
for i, j in enumerate(s.js):
    with cols[i%6]:
        cl = "pista-activa" if j['p'] else "banquillo-espera"
        st.markdown(f"<div class='{cl}'>", unsafe_allow_html=True)
        cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0); mc, vc = divmod(int(cur), 60)
        tot = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0); mt, vt = divmod(int(tot), 60)
        st.markdown(f"<b style='font-size:0.75rem;'>{j['n']}</b>", 1)
        st.markdown(f"<b style='font-size:1.1rem;'>{mc:02d}:{vc:02d}</b>", 1)
        st.markdown(f"<span style='font-size:0.6rem;'>Σ{mt:02d}:{vt:02d} R:{j['r']}</span>", 1)
        if st.button("🔄", key=f"c_{i}", use_container_width=True):
            if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1; j["tt"] = 0.0
            elif j["p"]:
                if s.on and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                j["p"], j["i"] = False, None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# FOOTER AJUSTADO CON TARJETAS RIVAL
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 3, 2])
with f1:
    st.caption(f"Faltas LUD: {s.fl}")
    st.button("F+", key="flud", use_container_width=True, on_click=lambda: setattr(s, 'fl', s.fl+1))
    if st.button("TM LUD", use_container_width=True): stop_match(); s.tm, s.tm_i = True, time.time(); st.rerun()
with f2:
    t_lud, t_riv = st.columns(2)
    with t_lud: # Tarjetas LUD
        with st.popover(f"🟨 {s.al}", use_container_width=True):
            p_a = st.selectbox("Jugador", [j['n'] for j in s.js], key="alud")
            if st.button("A-LUD"): s.al+=1; s.eventos.append({'min':min_act,'info':f'🟨{p_a}'}); st.rerun()
        with st.popover(f"🟥 {s.rl}", use_container_width=True):
            p_r = st.selectbox("Jugador", [j['n'] for j in s.js], key="rlud")
            if st.button("R-LUD"): s.rl+=1; s.eventos.append({'min':min_act,'info':f'🟥{p_r}'}); st.rerun()
    with t_riv: # Tarjetas RIVAL
        with st.popover(f"🟨 {s.ar}", use_container_width=True):
            d_a = st.number_input("Dorsal", 1, 99, key="ariv")
            if st.button("A-RIVAL"): s.ar+=1; s.eventos.append({'min':min_act,'info':f'🟨#{d_a}'}); st.rerun()
        with st.popover(f"🟥 {s.rr}", use_container_width=True):
            d_r = st.number_input("Dorsal", 1, 99, key="rriv")
            if st.button("R-RIVAL"): s.rr+=1; s.eventos.append({'min':min_act,'info':f'🟥#{d_r}'}); st.rerun()
    st.columns(2)[0].button(f"🧤 {s.pm}", use_container_width=True, on_click=lambda: setattr(s, 'pm', s.pm+1))
    st.columns(2)[1].button(f"👟 {s.pp}", use_container_width=True, on_click=lambda: setattr(s, 'pp', s.pp+1))
with f3:
    st.caption(f"Faltas RIV: {s.fr}")
    st.button("F+", key="friv", use_container_width=True, on_click=lambda: setattr(s, 'fr', s.fr+1))
    if st.button("TM RIV", use_container_width=True): stop_match(); s.tm, s.tm_i = True, time.time(); st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
