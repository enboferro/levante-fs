import streamlit as st
import pandas as pd
import time
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LUD Match Control v34.0", layout="wide")

# --- CSS ULTRA-COMPACTO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; }
    .block-container { padding: 0.1rem 0.5rem !important; }
    
    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 2px; border-radius: 8px;
        color: white; height: 60px; margin-bottom: 5px;
    }
    .score-number { font-size: 2.2rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 2.8rem !important; font-weight: 700; text-align: center; line-height: 1; }
    
    .card { 
        border-radius: 6px; padding: 4px; text-align: center; border: 1px solid #333; margin-bottom: 4px; 
        height: 110px; display: flex; flex-direction: column; justify-content: center;
    }
    .player-name { font-size: 0.8rem !important; font-weight: 900 !important; color: #4B2E2A; text-transform: uppercase; margin-bottom: 2px; }
    .time-large { font-size: 1.6rem !important; font-weight: 900 !important; font-family: 'Roboto Mono'; line-height: 1; color: #cc0000; }
    .time-total { font-size: 0.65rem !important; font-weight: 700; opacity: 0.8; }

    .pista-portero { background-color: #008080 !important; color: white; }
    .pista-verde { background-color: #00FF41 !important; color: #000; }
    .pista-naranja { background-color: #FF5E00 !important; color: white; }
    .pista-roja { background-color: #FF0000 !important; color: white; animation: blinker 0.8s linear infinite; }
    .banquillo { background-color: #D1D1D1 !important; color: #4B2E2A !important; }
    @keyframes blinker { 50% { opacity: 0.4; } }

    .stButton > button { height: 26px !important; font-size: 0.75rem !important; padding: 0px !important; border-radius: 4px; }
    .btn-gol { background-color: #FFF !important; color: #000 !important; border: 1px solid #000 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'js' not in st.session_state:
    n = ["Serra", "Jose", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu", "Toro", "Silla", "Coque"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"g":0,"i":None,"p":False} for x in n],
        "eventos": [], "ml": 0, "mr": 0, "fl": 0, "fr": 0, 
        "ta": 0.0, "ic": None, "on": False, "rv": "RIVAL", "periodo": "1ª PARTE", "finalizado": False,
        "porteros": [n[0], n[1]],
        "historial_tiempos": [] # Para guardar datos de la 1ª parte
    })

s = st.session_state
st_autorefresh(1000, key="refresh_lud_v34")
ah = time.time()
tr_total = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr_total); mv, sv = divmod(int(rem), 60)
min_act = f"{s.periodo} {mv:02d}:{sv:02d}"

# --- LOGICA TIEMPOS ---
def toggle_timer():
    if s.finalizado: return
    now = time.time()
    if not s.on:
        if tr_total < 1200:
            s.ic, s.on = now, True
            for j in s.js: 
                if j["p"] and j["n"] not in s.porteros: j["i"] = now
    else:
        s.ta += now - s.ic; s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"] and j["n"] not in s.porteros:
                d = now - j["i"]; j["tot"] += d; j["tt"] += d; j["i"] = None

def terminar_periodo():
    if s.on: toggle_timer()
    if s.periodo == "1ª PARTE":
        # Guardamos snapshot de la 1ª parte
        s.historial_tiempos.append({
            "periodo": "1ª PARTE",
            "faltas_lud": s.fl, "faltas_riv": s.fr,
            "tiempos": [j['tot'] for j in s.js]
        })
        s.periodo = "2ª PARTE"
        s.ta = 0.0
        s.fl = 0; s.fr = 0 # Faltas se reinician en fútbol sala
        s.eventos.append({'Tiempo': 'FIN 1ªP', 'Evento': '🏁 Final Primera Parte'})
    else:
        s.finalizado = True
        s.eventos.append({'Tiempo': 'FIN PARTIDO', 'Evento': '🏁 Final del Partido'})
    st.rerun()

# --- UI TABS ---
t1, t2, t3, t4, t5, t6 = st.tabs(["🎮 PARTIDO", "⚠️ INCIDENCIAS", "📊 TOTALES", "📜 HISTORIAL", "📊 EXCEL", "⚙️ CONFIG"])

with t1:
    st.markdown(f"""
        <div class="scoreboard-container">
            <div style="text-align:center;"><div class="score-number">{s.ml}</div></div>
            <div class="stadium-clock">{mv:02d}:{sv:02d}</div>
            <div style="text-align:center;"><div class="score-number">{s.mr}</div></div>
        </div>
    """, unsafe_allow_html=True)

    c_top = st.columns([2, 1, 1, 1])
    if c_top[0].button("▶ START / PAUSE ⏸", use_container_width=True, type="primary"): toggle_timer(); st.rerun()
    
    with c_top[1]:
        d_gol_riv = st.number_input("Dorsal Rival", 1, 99, key="driv_gol", label_visibility="collapsed")
    if c_top[2].button(f"⚽ GOL {s.rv[:3]}", use_container_width=True): 
        s.mr+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL {s.rv} (#{d_gol_riv})'}); st.rerun()
    
    if c_top[3].button("🏁 PERIODO", use_container_width=True): terminar_periodo()

    jugadores_campo_pista = sum(1 for j in s.js if j['p'] and j['n'] not in s.porteros)
    cols = st.columns(3)
    for i, j in enumerate(s.js):
        with cols[i % 3]:
            es_p = j['n'] in s.porteros
            cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            tot = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            cl = "banquillo" if not j['p'] else ("pista-portero" if es_p else ("pista-verde" if cur < 240 else ("pista-naranja" if cur < 360 else "pista-roja")))
            
            st.markdown(f"""
                <div class='card {cl}'>
                    <div class='player-name'>{j['n']}</div>
                    <div class='time-large'>{int(cur//60):02d}:{int(cur%60):02d}</div>
                    <div class='time-total'>Σ {int(tot//60):02d}:{int(tot%60):02d} | ⚽ {j['g']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            puedo_entrar = es_p or jugadores_campo_pista < 4
            cb1, cb2 = st.columns([3, 1])
            if cb1.button("🔄", key=f"bt_{i}", use_container_width=True):
                if not j["p"]:
                    if puedo_entrar:
                        j["p"] = True
                        if not es_p: j["i"], j["r"], j["tt"] = (ah if s.on else None), j["r"]+1, 0.0
                else:
                    if not es_p and s.on and j["i"]: d_t = ah - j["i"]; j["tot"] += d_t; j["tt"] += d_t
                    j["p"], j["i"] = False, None
                st.rerun()
            if cb2.button("⚽", key=f"gol_{i}", use_container_width=True, help="Sumar gol"):
                j['g'] += 1; s.ml += 1
                s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL: {j["n"]}'})
                st.rerun()

with t2:
    st.subheader("⚠️ Incidencias")
    cl1, cl2 = st.columns(2)
    with cl1:
        st.markdown(f"### LUD (Faltas: {s.fl})")
        fl1, fl2 = st.columns(2)
        if fl1.button("FALTA +", key="flp"): s.fl += 1; s.eventos.append({'Tiempo':min_act,'Evento':'FALTA LUD'}); st.rerun()
        if fl2.button("FALTA -", key="flm"): s.fl = max(0, s.fl-1); st.rerun()
    with cl2:
        st.markdown(f"### {s.rv} (Faltas: {s.fr})")
        fr1, fr2 = st.columns(2)
        if fr1.button("FALTA + ", key="frp"): s.fr += 1; s.eventos.append({'Tiempo':min_act,'Evento':f'FALTA {s.rv}'}); st.rerun()
        if fr2.button("FALTA - ", key="frm"): s.fr = max(0, s.fr-1); st.rerun()

with t3:
    st.subheader("📊 Totales y Rendimiento")
    data_resumen = []
    for j in s.js:
        min_tot = int(j['tot'] // 60)
        seg_tot = int(j['tot'] % 60)
        data_resumen.append({
            "Jugador": j['n'],
            "Goles": j['g'],
            "Tiempo Total": f"{min_tot:02d}:{seg_tot:02d}",
            "Rotaciones": j['r']
        })
    st.table(pd.DataFrame(data_resumen))
    
    if s.historial_tiempos:
        st.markdown("### Resumen 1ª Parte")
        h1 = s.historial_tiempos[0]
        st.write(f"Faltas LUD: {h1['faltas_lud']} | Faltas {s.rv}: {h1['faltas_riv']}")

with t4:
    if s.eventos: st.table(pd.DataFrame(s.eventos[::-1]))
    else: st.info("Sin eventos")

with t5:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        pd.DataFrame(s.js).to_excel(writer, sheet_name='Jugadores', index=False)
        pd.DataFrame(s.eventos).to_excel(writer, sheet_name='Historial', index=False)
    st.download_button("📥 DESCARGAR INFORME EXCEL", buf.getvalue(), f"LUD_vs_{s.rv}.xlsx", use_container_width=True)

with t6:
    st.subheader("⚙️ Configuración Acta")
    new_names = []
    cols_cfg = st.columns(2)
    for i in range(14):
        with (cols_cfg[0] if i < 7 else cols_cfg[1]):
            n_val = st.text_input(f"Jugador {i+1}", value=s.js[i]['n'], key=f"cfg_{i}")
            new_names.append(n_val)
    if st.button("💾 ACTUALIZAR PLANTILLA"):
        s.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"g":0,"i":None,"p":False} for x in new_names]
        s.porteros = [new_names[0], new_names[1]]
        st.rerun()
    s.rv = st.text_input("Rival", s.rv).upper()
    if st.button("🗑️ RESET TOTAL"): st.session_state.clear(); st.rerun()
