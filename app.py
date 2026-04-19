import streamlit as st
import pandas as pd
import time
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Configuración de página optimizada para iPad/Tablet
st.set_page_config(page_title="LUD Match Control v32.0", layout="wide")

# --- CSS INTEGRAL (DISEÑO ORIGINAL CON RELOJES GRANDES) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; }
    .block-container { padding: 0rem 0.5rem !important; }
    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 5px; border-radius: 10px 10px 0 0;
        color: white; height: 80px;
    }
    .score-number { font-size: 3.5rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 4rem !important; font-weight: 700; text-align: center; line-height: 1; }
    .fouls-bar {
        display: flex; justify-content: space-around; background: #000000; 
        color: #ffcc00; padding: 5px; border-radius: 0 0 10px 10px; 
        font-weight: 900; font-size: 1.2rem; margin-bottom: 8px;
    }
    .player-name { font-size: 1.1rem !important; font-weight: 900 !important; color: #4B2E2A !important; text-transform: uppercase; margin-bottom: 2px; }
    .card { 
        border-radius: 10px; padding: 8px; text-align: center; border: 2px solid #333; margin-bottom: 6px; 
        height: 145px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .pista-portero { background-color: #008080 !important; color: white; border: 2px solid white; }
    .pista-verde { background-color: #00FF41 !important; color: #000; }
    .pista-naranja { background-color: #FF5E00 !important; color: white; }
    .pista-roja { background-color: #FF0000 !important; color: white; border: 2px solid #FFFF00; animation: blinker 0.8s linear infinite; }
    .banquillo { background-color: #D1D1D1 !important; color: #4B2E2A !important; }
    @keyframes blinker { 50% { opacity: 0.4; } }
    .stButton > button { height: 45px !important; font-size: 1.2rem !important; font-weight: bold !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN (14 JUGADORES) ---
if 'js' not in st.session_state:
    n = ["Serra", "Jose", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu", "Toro", "Silla", "Coque"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n],
        "eventos": [], "pm_ok": 0, "pm_err": 0, "pp_ok": 0, "pp_err": 0, 
        "al": 0, "rl": 0, "ar": 0, "rr": 0, "ml": 0, "mr": 0, "fl": 0, "fr": 0, 
        "ta": 0.0, "ic": None, "on": False, "rv": "RIVAL", "lugar": "Pabellón", "fecha": datetime.now().date(),
        "tm": False, "tm_i": None, "analisis_goles": [], "periodo": "1ª PARTE", "finalizado": False,
        "porteros": [n[0], n[1]] 
    })

s = st.session_state
st_autorefresh(1000, key="refresh_lud_v32")

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
                if j["p"] and j["n"] not in s.porteros: j["i"] = now
    else:
        s.ta += now - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"] and j["n"] not in s.porteros:
                d = now - j["i"]; j["tot"] += d; j["tt"] += d; j["i"] = None

# --- UI TABS ---
t1, t2, t3, t4, t5 = st.tabs(["🎮 PARTIDO", "📜 HISTORIAL", "⚽ GOLES", "📊 EXCEL", "⚙️ CONFIG"])

with t1:
    # Cabecera Original Pro
    st.markdown(f"""
        <div class="scoreboard-container">
            <div style="text-align:center;"><div class="score-number">{s.ml}</div><div style="font-size:0.8rem; font-weight:900;">LUD</div></div>
            <div class="stadium-clock">{mv:02d}:{sv:02d}</div>
            <div style="text-align:center;"><div class="score-number">{s.mr}</div><div style="font-size:0.8rem; font-weight:900;">{s.rv[:8]}</div></div>
        </div>
        <div class="fouls-bar">FALTAS LUD: {s.fl} | {s.rv}: {s.fr} | {s.periodo}</div>
    """, unsafe_allow_html=True)

    c_top = st.columns([2, 1, 1, 1])
    if c_top[0].button("▶ START / PAUSE ⏸", key="main_btn", use_container_width=True, type="primary"): toggle_timer(); st.rerun()
    if c_top[1].button("⚽ GOL LUD", use_container_width=True): s.ml+=1; s.eventos.append({'Tiempo':min_act,'Evento':'⚽ GOL LUD'}); st.rerun()
    if c_top[2].button(f"⚽ {s.rv[:5]}", use_container_width=True): s.mr+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL {s.rv}'}); st.rerun()
    if c_top[3].button("🏁 FIN", use_container_width=True): 
        if s.on: toggle_timer()
        if s.periodo == "1ª PARTE": s.periodo = "2ª PARTE"; s.ta = 0.0; s.fl, s.fr = 0, 0
        else: s.finalizado = True
        st.rerun()

    st.markdown("---")
    
    # Cuadrícula de Jugadores (Ajustada para que los 14 quepan bien)
    jugadores_campo_pista = sum(1 for j in s.js if j['p'] and j['n'] not in s.porteros)
    
    cols = st.columns(3) # 3 columnas para iPad aprovecha mejor el ancho
    for i, j in enumerate(s.js):
        with cols[i % 3]:
            es_p = j['n'] in s.porteros
            cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            tot = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            
            cl = "banquillo" if not j['p'] else ("pista-portero" if es_p else ("pista-verde" if cur < 240 else ("pista-naranja" if cur < 360 else "pista-roja")))
            
            st.markdown(f"""
                <div class='card {cl}'>
                    <span class='player-name'>{j['n']}</span>
                    <div style='font-size:2.4rem; font-weight:900; line-height:1;'>{int(cur//60):02d}:{int(cur%60):02d}</div>
                    <div style='font-size:0.9rem; font-weight:700;'>TOTAL {int(tot//60):02d}:{int(tot%60):02d} | R:{j['r']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            puedo_entrar = es_p or jugadores_campo_pista < 4
            
            if st.button("CAMBIO 🔄", key=f"bt_{i}", use_container_width=True, disabled=s.finalizado):
                if not j["p"]:
                    if puedo_entrar:
                        j["p"] = True
                        if not es_p: j["i"], j["r"], j["tt"] = (ah if s.on else None), j["r"]+1, 0.0
                else:
                    if not es_p and s.on and j["i"]: d_t = ah - j["i"]; j["tot"] += d_t; j["tt"] += d_t
                    j["p"], j["i"] = False, None
                st.rerun()

with t5:
    st.subheader("⚙️ Configuración de Acta (14 Jugadores)")
    st.write("Complete los 14 nombres. **Los 2 primeros se tratarán como PORTEROS**.")
    
    new_names = []
    c_n1, c_n2 = st.columns(2)
    for i in range(14):
        with (c_n1 if i < 7 else c_n2):
            label = f"Posición {i+1} {'(PORTERO)' if i < 2 else ''}"
            val = st.text_input(label, value=s.js[i]['n'], key=f"cfg_n_{i}")
            new_names.append(val)
    
    if st.button("💾 ACTUALIZAR ACTA Y REINICIAR TIEMPOS"):
        s.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in new_names]
        s.porteros = [new_names[0], new_names[1]]
        st.success("Acta actualizada. Todos los cronómetros se han reseteado.")
        st.rerun()

    st.markdown("---")
    s.rv = st.text_input("Rival", s.rv).upper()
    s.lugar = st.text_input("Lugar", s.lugar)
    if st.button("🗑️ RESET TOTAL PARTIDO"):
        st.session_state.clear()
        st.rerun()
