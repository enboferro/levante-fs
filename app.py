import streamlit as st
import pandas as pd
import time, io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v20.1", layout="wide")

# --- CSS DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #e0e0e0; overflow-x: hidden; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }

    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 5px; border-radius: 0 0 15px 15px;
        color: #ffffff; box-shadow: 0 6px 15px rgba(0,0,0,0.4);
        border-bottom: 4px solid #000000;
    }
    .score-number { font-size: 4rem !important; font-weight: 900; line-height: 1; font-family: 'Roboto Mono', monospace; color: #ffffff; }
    .mini-stat { font-size: 0.85rem; color: #00f2ff; font-weight: 700; }

    .stadium-clock {
        font-family: 'Roboto Mono', monospace;
        font-size: 4.5rem !important;
        font-weight: 700; color: #ffffff;
        line-height: 0.8; text-align: center;
    }

    div.stButton > button[key^="tm_"] {
        width: 100% !important; height: 80px !important; 
        background-color: #ffffff !important;
        color: #4B2E2A !important;
        border: 5px solid #000000 !important;
        border-radius: 15px !important;
        font-size: 1.5rem !important; font-weight: 900 !important;
        box-shadow: 0 8px 0 #333333 !important;
        transition: all 0.05s ease-in-out !important;
    }
    div.stButton > button[key^="tm_"]:active { transform: translateY(4px) !important; box-shadow: 0 2px 0 #333333 !important; }

    .horizontal-timeline {
        display: flex; overflow-x: auto; background: #1a1a1a;
        padding: 5px; border-radius: 5px; margin: 4px 0;
        border: 2px solid #4B2E2A; gap: 6px; height: 40px; align-items: center;
    }
    .badge-lud { background: #4B2E2A; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 900; white-space: nowrap; border: 1px solid #fff; }
    .badge-riv { background: #000000; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 900; white-space: nowrap; border: 1px solid #fff; }

    .pista-portero { background-color: #008080 !important; color: white !important; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 2px solid white; }
    .pista-verde { background-color: #00FF41 !important; color: #000 !important; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; }
    .pista-naranja { background-color: #FF5E00 !important; color: white !important; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 1px solid white; }
    .pista-roja { background-color: #FF0000 !important; color: white !important; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 2px solid #FFFF00; animation: blinker 0.8s linear infinite; }
    .banquillo { background-color: #444444 !important; color: #ffffff !important; border-radius: 8px; padding: 2px; text-align: center; opacity: 0.9; }

    @keyframes blinker { 50% { opacity: 0.4; } }

    .footer-control {
        background-color: #ffffff; padding: 4px;
        border-radius: 15px 15px 0 0; border-top: 5px solid #4B2E2A;
        margin-top: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n],
        "eventos": [], "pm": 0, "pp": 0, "al": 0, "rl": 0, "ar": 0, "rr": 0, 
        "ml": 0, "mr": 0, "fl": 0, "fr": 0, "ta": 0.0, "ic": None, "on": False, 
        "pa": "1T", "rv": "RIVAL", "tm": False, "tm_i": None, "t1_abs": 0.0, "t2_abs": 0.0
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v20.1")

ah = time.time()
tr = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr)
min_act = int((tr if s.pa=="1T" else tr+1200) // 60)

def toggle_timer():
    if not s.on:
        s.ic, s.on, s.tm = time.time(), True, False
        for j in s.js: 
            if j["p"]: j["i"] = s.ic
    else:
        now = time.time()
        s.ta += now - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]:
                d = now - j["i"]; j["tot"] += d; j["tt"] += d; j["i"] = None

# --- UI SUPERIOR ---
mv, sv = divmod(int(rem), 60)
tm_sec = max(0, 60 - int(ah - s.tm_i)) if s.tm and s.tm_i else 0
timer_display = f"{tm_sec}s" if s.tm else f"{mv:02d}:{sv:02d}"

st.markdown(f"""
    <div class="scoreboard-container">
        <div style="text-align:center;">
            <div class="mini-stat">F: {s.fl} | 🟨: {s.al} | 🟥: {s.rl}</div>
            <div class="score-number">{s.ml}</div>
            <div style="font-size:0.9rem; font-weight:900;">LEVANTE UD</div>
        </div>
        <div class="stadium-clock">{timer_display}</div>
        <div style="text-align:center;">
            <div class="mini-stat">F: {s.fr} | 🟨: {s.ar} | 🟥: {s.rr}</div>
            <div class="score-number">{s.mr}</div>
            <div style="font-size:0.9rem; font-weight:900;">{s.rv[:8]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

c_bt = st.columns([1, 1, 1])
for i, col in enumerate(["tm_l", "tm_m", "tm_r"]):
    if c_bt[i].button("▶ START / STOP ⏸", key=col): toggle_timer(); st.rerun()

if s.eventos:
    tl_html = "".join([f"<span class='{'badge-riv' if ('#' in e['info'] or 'RIV' in e['info']) else 'badge-lud'}'>{e['min']}' {e['info']}</span>" for e in s.eventos])
    st.markdown(f"<div class='horizontal-timeline'>{tl_html}</div>", unsafe_allow_html=True)

# Goles y Config
c_act = st.columns([1, 1, 1, 1])
with c_act[0]:
    with st.popover("⚽ GOL LUD", use_container_width=True):
        p_gol = st.selectbox("Autor", [j['n'] for j in s.js], key="gl")
        if st.button("GOOOL LUD"): s.ml+=1; s.eventos.append({'min':min_act,'info':f'⚽{p_gol}'}); st.rerun()
with c_act[1]:
    with st.popover("⚽ GOL RIVAL", use_container_width=True):
        d_gol = st.number_input("Dorsal", 1, 99, key="gr")
        if st.button("GOL RIVAL"): s.mr+=1; s.eventos.append({'min':min_act,'info':f'⚽#{d_gol} RIV'}); st.rerun()
with c_act[2]: s.rv = st.text_input("Rival", s.rv, label_visibility="collapsed").upper()
with c_act[3]: 
    if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

# --- JUGADORES (Con contador de Rotaciones R) ---
cols = st.columns(6)
for i, j in enumerate(s.js):
    with cols[i%6]:
        cur_sec = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        tot_sec = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
        
        if not j['p']:
            cl = "banquillo"
        elif j['n'] in ["Serra", "Jose"]:
            cl = "pista-portero"
        else:
            if cur_sec < 240: cl = "pista-verde"
            elif cur_sec < 360: cl = "pista-naranja"
            else: cl = "pista-roja"
            
        st.markdown(f"<div class='{cl}'>", unsafe_allow_html=True)
        mc, vc = divmod(int(cur_sec), 60); mt, vt = divmod(int(tot_sec), 60)
        st.markdown(f"<div style='font-size:0.85rem; line-height:1;'>{j['n']}</div><div style='font-size:1.3rem; line-height:1;'>{mc:02d}:{vc:02d}</div><div style='font-size:0.7rem;'>Σ{mt:02d}:{vt:02d} | R:{j['r']}</div>", 1)
        if st.button("🔄", key=f"c_{i}", use_container_width=True):
            if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1; j["tt"] = 0.0
            elif j["p"]:
                if s.on and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                j["p"], j["i"] = False, None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([2.5, 3, 2.5])
with f1: 
    st.button("❌ F+", key="flp", use_container_width=True, on_click=lambda: setattr(s, 'fl', s.fl+1))
    st.button("F-", key="flm", use_container_width=True, on_click=lambda: setattr(s, 'fl', max(0, s.fl-1)))
    if st.button("⏱️ TM LUD"): toggle_timer(); s.tm, s.tm_i = True, time.time(); st.rerun()
with f2:
    c_t1, c_t2 = st.columns(2)
    with c_t1: # LUD
        with st.popover("🟨", use_container_width=True):
            p_a = st.selectbox("J", [j['n'] for j in s.js], key="alud")
            if st.button("OK LUD 🟨"): s.al+=1; s.eventos.append({'min':min_act,'info':f'🟨{p_a}'}); st.rerun()
        with st.popover("🟥", use_container_width=True):
            p_r = st.selectbox("J", [j['n'] for j in s.js], key="rlud")
            if st.button("OK LUD 🟥"): s.rl+=1; s.eventos.append({'min':min_act,'info':f'🟥{p_r}'}); st.rerun()
    with c_t2: # RIV
        with st.popover("🟨", use_container_width=True):
            d_a = st.number_input("D", 1, 99, key="ariv")
            if st.button("OK RIV 🟨"): s.ar+=1; s.eventos.append({'min':min_act,'info':f'🟨#{d_a} RIV'}); st.rerun()
        with st.popover("🟥", use_container_width=True):
            d_r = st.number_input("D", 1, 99, key="rriv")
            if st.button("OK RIV 🟥"): s.rr+=1; s.eventos.append({'min':min_act,'info':f'🟥#{d_r} RIV'}); st.rerun()
    c_p1, c_p2 = st.columns(2)
    c_p1.button(f"🧤 {s.pm}", use_container_width=True, on_click=lambda: setattr(s, 'pm', s.pm+1))
    c_p2.button(f"👟 {s.pp}", use_container_width=True, on_click=lambda: setattr(s, 'pp', s.pp+1))
with f3:
    st.button("❌ F+", key="frp", use_container_width=True, on_click=lambda: setattr(s, 'fr', s.fr+1))
    st.button("F-", key="frm", use_container_width=True, on_click=lambda: setattr(s, 'fr', max(0, s.fr-1)))
    if st.button("⏱️ TM RIV"): toggle_timer(); s.tm, s.tm_i = True, time.time(); st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
