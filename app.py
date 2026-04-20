import streamlit as st
import pandas as pd
import time
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LUD Control v37.3", layout="wide")

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
    })

s = st.session_state

# --- CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; }
    .block-container { padding: 0.1rem 0.5rem !important; }
    .scoreboard-container { background: #4B2E2A; padding: 5px; border-radius: 8px 8px 0 0; color: white; text-align: center; }
    .score-number { font-size: 2.5rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 3rem !important; font-weight: 700; line-height: 1; }
    .card { border-radius: 6px; padding: 4px; text-align: center; border: 1px solid #333; margin-bottom: 2px; height: 100px; display: flex; flex-direction: column; justify-content: center; }
    .player-name { font-size: 0.8rem !important; font-weight: 900 !important; text-transform: uppercase; margin-bottom: 1px; }
    .banquillo { background-color: #D1D1D1 !important; color: #000 !important; }
    .en-pista { color: #FFF !important; }
    .time-large { font-size: 1.9rem !important; font-weight: 900 !important; font-family: 'Roboto Mono'; line-height: 1; }
    .pista-portero { background-color: #008080 !important; }
    .pista-verde { background-color: #28a745 !important; }
    .pista-roja { background-color: #dc3545 !important; animation: blinker 0.8s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.7; } }
    .stButton > button { height: 28px !important; font-size: 0.7rem !important; border-radius: 3px; font-weight: bold !important; padding: 0px !important; }
    .porteria-section { background: #ffffff; padding: 8px; border-radius: 8px; border: 2px solid #4B2E2A; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(1000, key="refresh_v37_3")
ah = time.time()
tr_total = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr_total); mv, sv = divmod(int(rem), 60)
min_act = f"{s.periodo} {mv:02d}:{sv:02d}"

# --- LOGICA DE TIEMPOS ---
def toggle_timer():
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
                d = now - j["i"]
                j["tot"] += d
                j["tt"] += d
                j["i"] = None

def terminar_periodo():
    # 1. Parar crono y asegurar que se sumen los tiempos activos
    if s.on:
        toggle_timer()
    
    # 2. Resetear cronos de rotación actual (tarjetas) pero no el TOTAL (tot)
    for j in s.js:
        j["tt"] = 0.0
        j["i"] = None
        # Opcional: Si quieres que todos empiecen en el banquillo en el 2T, descomenta:
        # j["p"] = False 
    
    if s.periodo == "1ª PARTE":
        s.periodo = "2ª PARTE"
        s.ta = 0.0
        s.fl, s.fr = 0, 0
        s.eventos.append({'Minuto': 'FIN 1T', 'Evento': '🏁 FINAL 1ª PARTE', 'Cuarteto': '-'})
    else:
        s.finalizado = True
        s.eventos.append({'Minuto': 'FIN 2T', 'Evento': '🏁 FINAL PARTIDO', 'Cuarteto': '-'})
    st.rerun()

def get_cuarteto():
    pista = [j['n'] for j in s.js if j['p'] and j['n'] not in s.porteros]
    while len(pista) < 4: pista.append("-")
    return ", ".join(pista[:4])

# --- UI ---
tabs = st.tabs(["🎮 PARTIDO", "📊 TOTALES", "📜 HISTORIAL", "📥 EXPORTAR", "⚙️ CONFIG"])

with tabs[0]:
    st.markdown(f"""<div class="scoreboard-container"><div style="font-size:0.7rem;">{s.fecha} — {s.ciudad}</div><span class="score-number">{s.ml}</span><span class="stadium-clock">&nbsp;&nbsp;{mv:02d}:{sv:02d}&nbsp;&nbsp;</span><span class="score-number">{s.mr}</span></div>""", unsafe_allow_html=True)
    
    cf1, cf2, cf3, cf4, cf5, cf6 = st.columns([1,1,2,2,1,1])
    if cf1.button("➖", key="fl_m"): s.fl = max(0, s.fl-1); st.rerun()
    if cf2.button("➕", key="fl_p"): s.fl += 1; s.eventos.append({'Minuto': min_act, 'Evento': 'FALTA LUD', 'Cuarteto': None}); st.rerun()
    cf3.markdown(f"<div style='text-align:right; color:#FFCC00; font-weight:900;'>LUD: {s.fl}</div>", unsafe_allow_html=True)
    cf4.markdown(f"<div style='text-align:left; color:#FFCC00; font-weight:900;'>{s.rv[:5]}: {s.fr}</div>", unsafe_allow_html=True)
    if cf5.button("➕", key="fr_p"): s.fr += 1; s.eventos.append({'Minuto': min_act, 'Evento': f'FALTA {s.rv}', 'Cuarteto': None}); st.rerun()
    if cf6.button("➖", key="fr_m"): s.fr = max(0, s.fr-1); st.rerun()

    c_top = st.columns([2, 1, 1, 1])
    if c_top[0].button("▶ START / PAUSE ⏸", use_container_width=True, type="primary"): toggle_timer(); st.rerun()
    with c_top[1]: d_riv = st.number_input("Rival", 1, 99, key="dg", label_visibility="collapsed")
    if c_top[2].button(f"⚽ GOL {s.rv[:3]}", use_container_width=True):
        s.mr += 1; s.eventos.append({'Minuto': min_act, 'Evento': f'GOL {s.rv} (#{d_riv})', 'Cuarteto': get_cuarteto()}); st.rerun()
    if c_top[3].button("🏁 PERIODO", use_container_width=True): terminar_periodo()

    jugadores_activos = [j for j in s.js if j['n'].strip() != ""]
    cols = st.columns(3)
    p_count = sum(1 for j in jugadores_activos if j['p'] and j['n'] not in s.porteros)
    
    for idx, j in enumerate(jugadores_activos):
        with cols[idx % 3]:
            es_p = j['n'] in s.porteros
            cur_rot = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            tot_acum = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            
            cl = "banquillo" if not j['p'] else ("en-pista " + ("pista-portero" if es_p else ("pista-verde" if cur_rot < 240 else "pista-roja")))
            
            st.markdown(f"""
                <div class='card {cl}'>
                    <div class='player-name'>{j['n']}</div>
                    <div class='time-large'>{int(cur_rot//60):02d}:{int(cur_rot%60):02d}</div>
                    <div style='font-size:0.65rem;'>PARTE: {int(cur_rot//60):02d}:{int(cur_rot%60):02d} | ⚽ {j['g']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            b1, b2, b3, b4 = st.columns([1.5, 1, 0.8, 0.8])
            if b1.button("🔄", key=f"c_{idx}", use_container_width=True):
                if not j["p"]:
                    if es_p or p_count < 4:
                        j["p"] = True
                        if not es_p: j["i"], j["r"], j["tt"] = (ah if s.on else None), j["r"]+1, 0.0
                else:
                    if not es_p and s.on and j["i"]: d_t = ah - j["i"]; j["tot"] += d_t; j["tt"] += d_t
                    j["p"], j["i"] = False, None
                st.rerun()
            if b2.button("⚽", key=f"g_{idx}", use_container_width=True):
                j['g'] += 1; s.ml += 1; s.eventos.append({'Minuto': min_act, 'Evento': f'⚽ GOL: {j["n"]}', 'Cuarteto': get_cuarteto()}); st.rerun()
            if b3.button("🟨", key=f"ty_{idx}", use_container_width=True):
                s.eventos.append({'Minuto': min_act, 'Evento': f'🟨 Amarilla: {j["n"]}', 'Cuarteto': None})
            if b4.button("🟥", key=f"tr_{idx}", use_container_width=True):
                s.eventos.append({'Minuto': min_act, 'Evento': f'🟥 Roja: {j["n"]}', 'Cuarteto': None})

    st.markdown("<div class='porteria-section'>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    if p1.button("🧤 M ✅"): s.pm_ok += 1
    if p2.button("🧤 M ❌"): s.pm_err += 1
    if p3.button("👟 P ✅"): s.pp_ok += 1
    if p4.button("👟 P ❌"): s.pp_err += 1
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.subheader("📊 Totales Acumulados (Ambos Tiempos)")
    data_tiempos = []
    for j in jugadores_activos:
        # Sumamos el tiempo que lleva en pista si el crono está ON
        extra = (ah - j["i"] if s.on and j["p"] and j["i"] else 0)
        total_real = j["tot"] + extra
        m, s_val = divmod(int(total_real), 60)
        data_tiempos.append({
            "Jugador": j['n'],
            "Goles": j['g'],
            "Tiempo Total": f"{m:02d}:{s_val:02d}",
            "Rotaciones": j['r']
        })
    st.table(pd.DataFrame(data_tiempos))

with tabs[2]:
    if s.eventos:
        df_hist = pd.DataFrame(s.eventos[::-1]).fillna("-")
        st.table(df_hist)

with tabs[3]:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame([{"Rival": s.rv, "LUD": s.ml, "RIV": s.mr, "Faltas LUD": s.fl, "Faltas RIV": s.fr}]).to_excel(writer, sheet_name='Resumen', index=False)
        pd.DataFrame(s.eventos).to_excel(writer, sheet_name='Historial', index=False)
        pd.DataFrame([{"Jugador": j['n'], "Min": round(j['tot']/60, 2), "Goles": j['g']} for j in jugadores_activos]).to_excel(writer, sheet_name='Jugadores', index=False)
    st.download_button("📥 EXCEL", output.getvalue(), f"LUD_{s.rv}.xlsx", use_container_width=True)

with tabs[4]:
    c_config1, c_config2 = st.columns(2)
    with c_config1:
        s.rv = st.text_input("Rival", s.rv).upper()
        s.ciudad = st.text_input("Ciudad", s.ciudad).upper()
    with c_config2:
        s.fecha = st.text_input("Fecha", s.fecha)
    st.divider()
    new_names = []
    col_names1, col_names2 = st.columns(2)
    for i in range(14):
        with (col_names1 if i < 7 else col_names2):
            val_nombre = st.text_input(f"Jugador {i+1}", value=s.js[i]['n'] if i < len(s.js) else "", key=f"edit_n_{i}")
            new_names.append(val_nombre)
    if st.button("💾 GUARDAR CAMBIOS PLANTILLA"):
        s.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"g":0,"i":None,"p":False} for x in new_names]
        st.rerun()
    if st.button("🗑️ RESET TOTAL"): st.session_state.clear(); st.rerun()
