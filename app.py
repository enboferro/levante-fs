import streamlit as st
import pandas as pd
import time
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LUD Match Control v36.0", layout="wide")

# --- INICIALIZACIÓN ---
if 'js' not in st.session_state:
    n_iniciales = ["Serra", "Jose", "Julian", "Omar", "Tony", "Rochina", "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu", "Toro", "Silla", "Coque"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"g":0,"i":None,"p":False} for x in n_iniciales],
        "eventos": [], "ml": 0, "mr": 0, "fl": 0, "fr": 0, 
        "ta": 0.0, "ic": None, "on": False, 
        "rv": "RIVAL", "ciudad": "VALENCIA", "fecha": datetime.now().strftime("%d/%m/%Y"),
        "periodo": "1ª PARTE", "finalizado": False,
        "porteros": [n_iniciales[0], n_iniciales[1]]
    })

s = st.session_state

# --- CSS CONTRASTE DINÁMICO ---
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
    .card { border-radius: 6px; padding: 4px; text-align: center; border: 1px solid #333; margin-bottom: 4px; height: 105px; display: flex; flex-direction: column; justify-content: center; }
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
    .stButton > button { height: 26px !important; font-size: 0.75rem !important; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(1000, key="refresh_v36")
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

    c_top = st.columns([2, 1, 1, 1, 1])
    if c_top[0].button("▶ START / PAUSE ⏸", use_container_width=True, type="primary"): toggle_timer(); st.rerun()
    with c_top[1]: d_riv = st.number_input("Dorsal Rival", 1, 99, key="dg", label_visibility="collapsed")
    if c_top[2].button(f"⚽ {s.rv[:3]}", use_container_width=True):
        s.mr += 1; s.eventos.append({'Tiempo': min_act, 'Evento': f'GOL {s.rv} (#{d_riv})', 'Cuarteto': get_cuarteto()}); st.rerun()
    
    # BOTONES DE FIN DE TIEMPO
    if s.periodo == "1ª PARTE":
        if c_top[3].button("🏁 FIN 1T", use_container_width=True, help="Terminar Primera Parte"):
            if s.on: toggle_timer()
            s.eventos.append({'Tiempo': min_act, 'Evento': '🏁 FIN 1ª PARTE', 'Cuarteto': '-'})
            s.periodo = "2ª PARTE"; s.ta = 0.0; s.fl, s.fr = 0, 0; st.rerun()
    else:
        if c_top[3].button("🏁 FIN 2T", use_container_width=True, help="Terminar Partido"):
            if s.on: toggle_timer()
            s.eventos.append({'Tiempo': min_act, 'Evento': '🏁 FIN PARTIDO', 'Cuarteto': '-'})
            s.finalizado = True; st.rerun()

    cols = st.columns(3)
    p_count = sum(1 for j in s.js if j['p'] and j['n'] not in s.porteros)
    for i, j in enumerate(s.js):
        with cols[i % 3]:
            es_p = j['n'] in s.porteros
            cur, tot = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0), j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            cl = "banquillo" if not j['p'] else ("en-pista " + ("pista-portero" if es_p else ("pista-verde" if cur < 240 else ("pista-naranja" if cur < 360 else "pista-roja"))))
            st.markdown(f"<div class='card {cl}'><div class='player-name'>{j['n']}</div><div class='time-large'>{int(cur//60):02d}:{int(cur%60):02d}</div><div class='time-total'>Σ {int(tot//60):02d}:{int(tot%60):02d} | ⚽ {j['g']}</div></div>", unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            if c1.button("🔄", key=f"c_{i}", use_container_width=True):
                if not j["p"]:
                    if es_p or p_count < 4:
                        j["p"] = True
                        if not es_p: j["i"], j["r"], j["tt"] = (ah if s.on else None), j["r"]+1, 0.0
                else:
                    if not es_p and s.on and j["i"]: d_t = ah - j["i"]; j["tot"] += d_t; j["tt"] += d_t
                    j["p"], j["i"] = False, None
                st.rerun()
            if c2.button("⚽", key=f"g_{i}", use_container_width=True):
                j['g'] += 1; s.ml += 1; s.eventos.append({'Tiempo': min_act, 'Evento': f'⚽ GOL: {j["n"]}', 'Cuarteto': get_cuarteto()}); st.rerun()

with tabs[1]:
    st.subheader("⚠️ Incidencias")
    cl1, cl2 = st.columns(2)
    with cl1:
        st.markdown("### LUD")
        if st.button("FALTA + LUD"): s.fl += 1; s.eventos.append({'Tiempo': min_act, 'Evento': 'FALTA LUD', 'Cuarteto': get_cuarteto()}); st.rerun()
        p_sel = st.selectbox("Jugador LUD", [x['n'] for x in s.js], key="psel")
        if st.button("🟨 Amarilla LUD"): s.eventos.append({'Tiempo': min_act, 'Evento': f'🟨 Amarilla: {p_sel}', 'Cuarteto': get_cuarteto()})
        if st.button("🟥 Roja LUD"): s.eventos.append({'Tiempo': min_act, 'Evento': f'🟥 Roja: {p_sel}', 'Cuarteto': get_cuarteto()})
    with cl2:
        st.markdown(f"### {s.rv}")
        if st.button(f"FALTA + {s.rv}"): s.fr += 1; s.eventos.append({'Tiempo': min_act, 'Evento': f'FALTA {s.rv}', 'Cuarteto': get_cuarteto()}); st.rerun()
        d_tar = st.number_input("Dorsal Rival", 1, 99, key="dtar")
        if st.button(f"🟨 Amarilla {s.rv}"): s.eventos.append({'Tiempo': min_act, 'Evento': f'🟨 Amarilla {s.rv} (#{d_tar})', 'Cuarteto': get_cuarteto()})
        if st.button(f"🟥 Roja {s.rv}"): s.eventos.append({'Tiempo': min_act, 'Evento': f'🟥 Roja {s.rv} (#{d_tar})', 'Cuarteto': get_cuarteto()})

with tabs[2]:
    st.subheader("📊 Totales")
    res_df = pd.DataFrame([{"Jugador": j['n'], "Goles": j['g'], "Tiempo Total": f"{int(j['tot']//60):02d}:{int(j['tot']%60):02d}", "Rotaciones": j['r']} for j in s.js])
    st.table(res_df)

with tabs[3]:
    st.subheader("📜 Historial")
    if s.eventos: st.table(pd.DataFrame(s.eventos[::-1]))

with tabs[4]:
    st.subheader("📥 Exportar Datos Completos")
    if st.button("Generar Excel de Partido"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame([{"Rival": s.rv, "Ciudad": s.ciudad, "Fecha": s.fecha, "Goles LUD": s.ml, "Goles Rival": s.mr}]).to_excel(writer, sheet_name='Info_General', index=False)
            pd.DataFrame([{"Jugador": j['n'], "Goles": j['g'], "Segundos_Totales": j['tot'], "Rotaciones": j['r']} for j in s.js]).to_excel(writer, sheet_name='Jugadores', index=False)
            pd.DataFrame(s.eventos).to_excel(writer, sheet_name='Historial_Eventos', index=False)
        st.download_button(label="📥 Descargar Excel", data=output.getvalue(), file_name=f"LUD_Partido_{s.fecha}.xlsx", mime="application/vnd.ms-excel")

with tabs[5]:
    st.subheader("⚙️ Configuración")
    c1, c2, c3 = st.columns(3)
    s.rv, s.ciudad, s.fecha = c1.text_input("Rival", s.rv).upper(), c2.text_input("Ciudad", s.ciudad).upper(), c3.text_input("Fecha", s.fecha)
    st.divider()
    new_names = []
    cols_cfg = st.columns(2)
    for i in range(14):
        with (cols_cfg[0] if i < 7 else cols_cfg[1]):
            new_names.append(st.text_input(f"Jugador {i+1}", value=s.js[i]['n'], key=f"cfg_{i}"))
    if st.button("💾 GUARDAR PLANTILLA"):
        s.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"g":0,"i":None,"p":False} for x in new_names]
        s.porteros = [new_names[0], new_names[1]]; st.rerun()
    if st.button("🗑️ RESET TOTAL"): st.session_state.clear(); st.rerun()
