import streamlit as st
import pandas as pd
import time
import io
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Master Compact", layout="wide", initial_sidebar_state="collapsed")

# --- CSS ULTRA COMPACTO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;900&display=swap');
    
    /* Eliminar márgenes de Streamlit */
    .block-container { padding: 0rem 0.5rem !important; max-width: 100% !important; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; overflow: hidden; }

    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { height: 35px; background-color: #4B2E2A; color: white; border-radius: 5px 5px 0 0; padding: 5px 10px; font-size: 0.8rem; }
    
    /* Marcador Compacto */
    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 2px; border-radius: 10px 10px 0 0;
        color: white; height: 60px;
    }
    .score-number { font-size: 2.5rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 3rem !important; font-weight: 700; text-align: center; line-height: 1; }
    
    .fouls-bar {
        display: flex; justify-content: space-around; background: #000000; 
        color: #ffcc00; padding: 2px; border-radius: 0 0 10px 10px; 
        font-weight: 900; font-size: 1rem; margin-bottom: 5px;
    }
    
    /* Fichas Jugadores Compactas */
    .player-name { font-size: 0.9rem !important; font-weight: 900 !important; color: #4B2E2A !important; text-transform: uppercase; margin-bottom: 0px; }
    
    .card { border-radius: 6px; padding: 4px 2px; text-align: center; border: 1px solid rgba(0,0,0,0.1); margin-bottom: 2px; }
    .pista-portero { background-color: #008080 !important; color: white; border: 2px solid white; height: 85px; }
    .pista-verde { background-color: #00FF41 !important; color: #000; height: 85px; }
    .pista-naranja { background-color: #FF5E00 !important; color: white; border: 1px solid white; height: 85px; }
    .pista-roja { background-color: #FF0000 !important; color: white; border: 2px solid #FFFF00; animation: blinker 0.8s linear infinite; height: 85px; }
    .banquillo { background-color: #D1D1D1 !important; color: #4B2E2A !important; border: 1px solid #999; height: 85px; }

    @keyframes blinker { 50% { opacity: 0.4; } }

    /* Footer Ajustado */
    .footer-control { background-color: #ffffff; padding: 4px; border-radius: 10px; border-top: 3px solid #4B2E2A; margin-top: 5px; }
    
    /* Botones más pequeños */
    .stButton > button { height: 28px !important; padding: 0px 5px !important; font-size: 0.7rem !important; }
    .main-btn-timer button { height: 45px !important; font-size: 1.2rem !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n],
        "eventos": [], "pm_ok": 0, "pm_err": 0, "pp_ok": 0, "pp_err": 0, 
        "al": 0, "rl": 0, "ar": 0, "rr": 0, "ml": 0, "mr": 0, "fl": 0, "fr": 0, 
        "ta": 0.0, "ic": None, "on": False, "rv": "RIVAL", "tm": False, "tm_i": None,
        "analisis_goles": [], "periodo": "1P", "finalizado": False
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v28")

ah = time.time()
tr_total = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr_total)
mv, sv = divmod(int(rem), 60)
min_act = f"{s.periodo} {mv:02d}:{sv:02d}"

# --- FUNCIONES ---
def toggle_timer():
    if s.finalizado: return
    now = time.time()
    if not s.on:
        if tr_total < 1200:
            s.ic, s.on = now, True
            for j in s.js: 
                if j["p"] and j["n"] not in ["Serra", "Jose"]: j["i"] = now
    else:
        s.ta += now - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"] and j["n"] not in ["Serra", "Jose"]:
                d = now - j["i"]; j["tot"] += d; j["tt"] += d; j["i"] = None

def finalizar_fase():
    if s.on: toggle_timer()
    s.eventos.append({'Tiempo': min_act, 'Evento': f'FIN {s.periodo}'})
    if s.periodo == "1P":
        s.periodo = "2P"; s.ta = 0.0; s.fl, s.fr = 0, 0
    else:
        s.finalizado = True; s.periodo = "FIN"
    st.rerun()

def capturar_tactico(tipo, detalle):
    cuarteto = []
    for j in s.js:
        if j['p'] and j['n'] not in ["Serra", "Jose"]:
            t_rot = j["tt"] + (ah - j["i"] if s.on and j["i"] else 0)
            mj, sj = divmod(int(t_rot), 60)
            cuarteto.append(f"{j['n']} ({mj:02d}:{sj:02d})")
    while len(cuarteto) < 4: cuarteto.append("-")
    s.analisis_goles.append({"P": s.periodo, "T": f"{mv:02d}:{sv:02d}", "Tipo": tipo, "Marcador": f"{s.ml}-{s.mr}", "P1": cuarteto[0], "P2": cuarteto[1], "P3": cuarteto[2], "P4": cuarteto[3]})

# --- UI ---
t1, t2, t3, t4 = st.tabs(["🎮 PARTIDO", "📜 LOG", "⚽ GOLES", "📊 EXCEL"])

with t1:
    timer_display = f"{max(0, 60 - int(ah - s.tm_i))}s" if s.tm else f"{mv:02d}:{sv:02d}"
    st.markdown(f"""
        <div class="scoreboard-container">
            <div style="text-align:center;"><div class="score-number">{s.ml}</div><div style="font-size:0.6rem; font-weight:900;">LUD</div></div>
            <div class="stadium-clock" style="color: {'#FF0000' if rem <= 0 else '#FFFFFF'};">{timer_display}</div>
            <div style="text-align:center;"><div class="score-number">{s.mr}</div><div style="font-size:0.6rem; font-weight:900;">{s.rv[:5]}</div></div>
        </div>
        <div class="fouls-bar">FALTAS: {s.fl} | RIVAL: {s.fr} | {s.periodo}</div>
    """, unsafe_allow_html=True)

    c_c = st.columns([2, 1, 1, 1, 1])
    with c_c[0]:
        st.markdown('<div class="main-btn-timer">', unsafe_allow_html=True)
        if st.button("▶ START / STOP ⏸", key="main_btn", use_container_width=True, disabled=s.finalizado): toggle_timer(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c_c[1]:
        if st.button("🏁 FIN", key="end_btn", use_container_width=True): finalizar_fase()
    with c_c[2]:
        with st.popover("⚽ LUD"):
            p = st.selectbox("Autor", [x['n'] for x in s.js], key="gl")
            if st.button("OK GOL LUD"): s.ml+=1; capturar_tactico("GOL LUD", p); s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL LUD ({p})'}); st.rerun()
    with c_c[3]:
        with st.popover("⚽ RIV"):
            d = st.number_input("Dorsal", 1, 99, key="gr")
            if st.button("OK GOL RIV"): s.mr+=1; capturar_tactico("GOL RIV", f"#{d}"); s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL RIV (#{d})'}); st.rerun()
    with c_c[4]: 
        if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

    cols = st.columns(5)
    for i, j in enumerate(s.js):
        with cols[i%5]:
            es_p = j['n'] in ["Serra", "Jose"]
            cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            tot = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            cl = "banquillo" if not j['p'] else ("pista-portero" if es_p else ("pista-verde" if cur < 240 else ("pista-naranja" if cur < 360 else "pista-roja")))
            
            st.markdown(f"<div class='card {cl}'><span class='player-name'>{j['n']}</span>", unsafe_allow_html=True)
            if not es_p:
                st.markdown(f"<div style='font-size:1rem; font-weight:900;'>{int(cur//60):02d}:{int(cur%60):02d}</div><div style='font-size:0.6rem;'>Σ {int(tot//60):02d}:{int(tot%60):02d} | R:{j['r']}</div>", unsafe_allow_html=True)
            if st.button("🔄", key=f"bt_{i}", use_container_width=True, disabled=s.finalizado):
                if not j["p"]:
                    j["p"] = True
                    if not es_p: j["i"], j["r"], j["tt"] = (ah if s.on else None), j["r"]+1, 0.0
                else:
                    if not es_p and s.on and j["i"]: d_t = ah - j["i"]; j["tot"] += d_t; j["tt"] += d_t
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
    f_l, f_m, f_r = st.columns([1, 2, 1])
    with f_l:
        st.button("⏱️ TM LUD", key="tml", on_click=lambda: (toggle_timer(), setattr(s, 'tm', True), setattr(s, 'tm_i', time.time())))
        st.button("F+ LUD", on_click=lambda: setattr(s, 'fl', s.fl+1))
    with f_m:
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            with st.popover("L🟨🟥"):
                py = st.selectbox("J", [x['n'] for x in s.js], key="sy")
                if st.button("AM LUD"): s.al+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟨 LUD ({py})'}); st.rerun()
                if st.button("ROJ LUD"): s.rl+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟥 LUD ({py})'}); st.rerun()
        with c2:
            with st.popover("R🟨🟥"):
                dy = st.number_input("D", 1, 99, key="ny")
                if st.button("AM RIV"): s.ar+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟨 RIV (#{dy})'}); st.rerun()
                if st.button("ROJ RIV"): s.rr+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟥 RIV (#{dy})'}); st.rerun()
        with c3: st.button(f"🧤 {s.pm_ok}|{s.pm_err}", on_click=lambda: setattr(s, 'pm_ok', s.pm_ok+1))
        with c4: st.button(f"👟 {s.pp_ok}|{s.pp_err}", on_click=lambda: setattr(s, 'pp_ok', s.pp_ok+1))
    with f_r:
        st.button("⏱️ TM RIV", key="tmr", on_click=lambda: (toggle_timer(), setattr(s, 'tm', True), setattr(s, 'tm_i', time.time())))
        st.button("F+ RIV", on_click=lambda: setattr(s, 'fr', s.fr+1))
    st.markdown("</div>", unsafe_allow_html=True)
