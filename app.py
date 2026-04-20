import streamlit as st
import pandas as pd
import time
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LUD Match Control v36.4", layout="wide")

# --- INICIALIZACIÓN ---
if 'js' not in st.session_state:
    n_iniciales = ["Serra", "Jose", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu", "Toro", "Silla", "Coque"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"g":0,"i":None,"p":False} for x in n_iniciales],
        "eventos": [], "ml": 0, "mr": 0, "fl": 0, "fr": 0, 
        "pm_ok": 0, "pm_err": 0, "pp_ok": 0, "pp_err": 0,
        "ta": 0.0, "ic": None, "on": False, 
        "rv": "RIVAL", "ciudad": "VALENCIA", "fecha": datetime.now().strftime("%d/%m/%Y"),
        "periodo": "1ª PARTE", "finalizado": False,
        "porteros": [n_iniciales[0], n_iniciales[1]],
        "datos_1t": None 
    })

s = st.session_state

# --- CSS MEJORADO CON ICONOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; }
    .block-container { padding: 0.1rem 0.5rem !important; }
    .scoreboard-container { background: #4B2E2A; padding: 5px; border-radius: 8px 8px 0 0; color: white; text-align: center; }
    .match-info-sub { font-size: 0.9rem; opacity: 0.9; }
    .score-number { font-size: 2.5rem !important; font-weight: 900; font-family: 'Roboto Mono'; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 3rem !important; font-weight: 700; }
    .faltas-banner { background: #000; color: #FFCC00; padding: 3px; border-radius: 0 0 8px 8px; text-align: center; font-weight: 900; margin-bottom: 8px; }
    
    .card { border-radius: 6px; padding: 4px; text-align: center; border: 1px solid #333; margin-bottom: 4px; height: 112px; display: flex; flex-direction: column; justify-content: center; }
    .player-name { font-size: 0.85rem !important; font-weight: 900 !important; text-transform: uppercase; }
    
    .banquillo { background-color: #D1D1D1 !important; color: #000 !important; }
    .banquillo .time-large { color: #000 !important; }
    .en-pista { color: #FFF !important; }
    .en-pista .time-large { color: #FFF !important; text-shadow: 1px 1px 2px #000; }
    
    .time-large { font-size: 1.8rem !important; font-weight: 900 !important; font-family: 'Roboto Mono'; line-height: 1; }
    .time-total { font-size: 0.7rem !important; font-weight: 700; }
    
    .pista-portero { background-color: #008080 !important; }
    .pista-verde { background-color: #28a745 !important; }
    .pista-naranja { background-color: #fd7e14 !important; }
    .pista-roja { background-color: #dc3545 !important; animation: blinker 0.8s linear infinite; }
    
    @keyframes blinker { 50% { opacity: 0.7; } }
    
    /* Botones de Iconos */
    .stButton > button { height: 28px !important; font-size: 0.8rem !important; border-radius: 4px; padding: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(1000, key="refresh_v36_4")
ah = time.time()
tr_total = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr_total); mv, sv = divmod(int(rem), 60)
min_act = f"{s.periodo} {mv:02d}:{sv:02d}"

def get_cuarteto():
    pista = [j['n'] for j in s.js if j['p'] and j['n'] not in s.porteros]
    while len(pista) < 4: pista.append("-")
    return ", ".join(pista[:4])

def toggle_timer():
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

# --- UI TABS ---
tabs = st.tabs(["🎮 PARTIDO", "⚠️ INCIDENCIAS", "📊 TOTALES", "📜 HISTORIAL", "📥 EXPORTAR", "⚙️ CONFIG"])

with tabs[0]:
    st.markdown(f"""<div class="scoreboard-container"><div class="match-info-sub">{s.fecha} — {s.ciudad}</div><span class="score-number">{s.ml}</span><span class="stadium-clock">&nbsp;&nbsp;{mv:02d}:{sv:02d}&nbsp;&nbsp;</span><span class="score-number">{s.mr}</span></div><div class="faltas-banner">FALTAS: LUD {s.fl} — {s.rv} {s.fr}</div>""", unsafe_allow_html=True)

    c_top = st.columns([2, 1, 1, 1])
    if c_top[0].button("▶ START / PAUSE ⏸", use_container_width=True, type="primary"): toggle_timer(); st.rerun()
    with c_top[1]: d_riv = st.number_input("Dorsal Rival", 1, 99, key="dg", label_visibility="collapsed")
    if c_top[2].button(f"⚽ {s.rv[:3]}", use_container_width=True):
        s.mr += 1; s.eventos.append({'Tiempo': min_act, 'Evento': f'GOL {s.rv} (#{d_riv})', 'Cuarteto': get_cuarteto()}); st.rerun()
    
    if c_top[3].button("🏁 PERIODO" if s.periodo == "1ª PARTE" else "🏁 FINAL", use_container_width=True):
        if s.on: toggle_timer()
        if s.periodo == "1ª PARTE":
            s.datos_1t = {"faltas_lud": s.fl, "faltas_riv": s.fr, "goles_lud": s.ml, "goles_riv": s.mr}
            s.eventos.append({'Tiempo': min_act, 'Evento': '🏁 FIN 1ª PARTE', 'Cuarteto': '-'})
            s.periodo = "2ª PARTE"; s.ta = 0.0; s.fl, s.fr = 0, 0
        else:
            s.eventos.append({'Tiempo': min_act, 'Evento': '🏁 FIN PARTIDO', 'Cuarteto': '-'})
            s.finalizado = True
        st.rerun()

    jugadores_activos = [j for j in s.js if j['n'].strip() != ""]
    cols = st.columns(3)
    p_count = sum(1 for j in jugadores_activos if j['p'] and j['n'] not in s.porteros)
    
    for idx, j in enumerate(jugadores_activos):
        with cols[idx % 3]:
            es_p = j['n'] in s.porteros
            cur, tot = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0), j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            cl = "banquillo" if not j['p'] else ("en-pista " + ("pista-portero" if es_p else ("pista-verde" if cur < 240 else ("pista-naranja" if cur < 360 else "pista-roja"))))
            st.markdown(f"<div class='card {cl}'><div class='player-name'>{j['n']}</div><div class='time-large'>{int(cur//60):02d}:{int(cur%60):02d}</div><div class='time-total'>Σ {int(tot//60):02d}:{int(tot%60):02d} | ⚽ {j['g']}</div></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1])
            if c1.button("🔄 Cambio", key=f"c_{idx}", use_container_width=True):
                if not j["p"]:
                    if es_p or p_count < 4:
                        j["p"] = True
                        if not es_p: j["i"], j["r"], j["tt"] = (ah if s.on else None), j["r"]+1, 0.0
                else:
                    if not es_p and s.on and j["i"]: d_t = ah - j["i"]; j["tot"] += d_t; j["tt"] += d_t
                    j["p"], j["i"] = False, None
                st.rerun()
            
            with c2:
                if es_p:
                    # Iconos para Porteros
                    cm, cp = st.columns(2)
                    with cm:
                        if st.button("🧤✅", key=f"m_v_{idx}", help="Saque Mano OK"): s.pm_ok += 1
                        if st.button("🧤❌", key=f"m_x_{idx}", help="Saque Mano Error"): s.pm_err += 1
                    with cp:
                        if st.button("👟✅", key=f"p_v_{idx}", help="Saque Pie OK"): s.pp_ok += 1
                        if st.button("👟❌", key=f"p_x_{idx}", help="Saque Pie Error"): s.pp_err += 1
                else:
                    if st.button("⚽ GOL", key=f"g_{idx}", use_container_width=True):
                        j['g'] += 1; s.ml += 1; s.eventos.append({'Tiempo': min_act, 'Evento': f'⚽ GOL: {j["n"]}', 'Cuarteto': get_cuarteto()}); st.rerun()

with tabs[2]:
    st.subheader("📊 Totales")
    def p_calc(o, e): t=o+e; return f"{(o/t*100):.1f}%" if t>0 else "0.0%"
    st.write(f"🧤 **Mano:** {s.pm_ok} ✅ / {s.pm_err} ❌ ({p_calc(s.pm_ok, s.pm_err)}) | 👟 **Pie:** {s.pp_ok} ✅ / {s.pp_err} ❌ ({p_calc(s.pp_ok, s.pp_err)})")
    st.divider()
    st.table(pd.DataFrame([{"Jugador": j['n'], "Goles": j['g'], "Tiempo": f"{int(j['tot']//60):02d}:{int(j['tot']%60):02d}", "Rot": j['r']} for j in jugadores_activos]))

with tabs[4]:
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame([{"Rival": s.rv, "Goles LUD": s.ml, "Goles Rival": s.mr, "Mano OK": s.pm_ok, "Pie OK": s.pp_ok}]).to_excel(writer, sheet_name='Resumen', index=False)
            pd.DataFrame(s.eventos).to_excel(writer, sheet_name='Historial', index=False)
        st.download_button("📥 DESCARGAR EXCEL", output.getvalue(), f"LUD_{s.rv}.xlsx", use_container_width=True)
    except: st.error("Instala xlsxwriter")

with tabs[5]:
    st.subheader("⚙️ Configuración")
    s.rv = st.text_input("Rival", s.rv).upper()
    s.ciudad = st.text_input("Ciudad", s.ciudad).upper()
    s.fecha = st.text_input("Fecha", s.fecha)
    st.divider()
    new_names = []
    cols_cfg = st.columns(2)
    for i in range(14):
        with (cols_cfg[0] if i < 7 else cols_cfg[1]):
            new_names.append(st.text_input(f"Posición {i+1} {'(P)' if i<2 else ''}", value=s.js[i]['n'] if i < len(s.js) else "", key=f"cfg_{i}"))
    if st.button("💾 GUARDAR PLANTILLA"):
        s.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"g":0,"i":None,"p":False} for x in new_names]
        s.porteros = [new_names[0], new_names[1]]; st.rerun()
    if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()
