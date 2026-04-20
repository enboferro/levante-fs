import streamlit as st
import pandas as pd
import time
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Match Control Universal v38.6", layout="wide")

# --- INICIALIZACIÓN ---
if 'js' not in st.session_state:
    n_iniciales = ["Portero 1", "Portero 2", "Jugador 3", "Jugador 4", "Jugador 5", "Jugador 6", "Jugador 7", "Jugador 8", "Jugador 9", "Jugador 10", "Jugador 11", "Jugador 12", "Jugador 13", "Jugador 14"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"g":0,"i":None,"p":False} for x in n_iniciales],
        "eventos": [], "ml": 0, "mr": 0, "fl": 0, "fr": 0, 
        "pm_ok": 0, "pm_err": 0, "pp_ok": 0, "pp_err": 0,
        "ta": 0.0, "ic": None, "on": False, 
        "loc": "LOCAL", "rv": "RIVAL", "ciudad": "VALENCIA", "fecha": datetime.now().strftime("%d/%m/%Y"),
        "periodo": "1ª PARTE", "finalizado": False
    })

s = st.session_state

# --- FUNCIONES DE LÓGICA (DEFINIDAS ANTES DEL UI) ---
def fmt_time(seconds):
    m, sec = divmod(int(seconds), 60)
    return f"{m:02d}:{sec:02d}"

def p_calc(o, e):
    total = o + e
    return f"{(o / total * 100):.1f}%" if total > 0 else "0.0%"

def get_cuarteto():
    # Solo jugadores de campo (índices del 2 al final)
    pista = [j['n'] for i, j in enumerate(s.js) if j['p'] and i >= 2]
    while len(pista) < 4: pista.append("-")
    return ", ".join(pista[:4])

def toggle_timer():
    now = time.time()
    if not s.on:
        if tr_total < 1200: 
            s.ic, s.on = now, True
            for j in s.js: 
                if j["p"]: j["i"] = now
    else:
        s.ta += now - s.ic
        s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]:
                d = now - j["i"]; j["tot"] += d; j["tt"] += d; j["i"] = None

# --- CSS (OPTIMIZADO LANDSCAPE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; }
    .block-container { padding: 0.1rem 0.5rem !important; }
    .scoreboard-container { background: #4B2E2A; padding: 4px; border-radius: 8px 8px 0 0; color: white; text-align: center; }
    .score-number { font-size: 2.2rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 2.8rem !important; font-weight: 700; line-height: 1; }
    
    /* Tarjetas alineadas 5 columnas */
    .card { border-radius: 6px; padding: 4px; text-align: center; border: 1px solid #333; margin-bottom: 2px; height: 95px; display: flex; flex-direction: column; justify-content: center; }
    .player-name { font-size: 0.75rem !important; font-weight: 900 !important; text-transform: uppercase; margin-bottom: 1px; }
    
    .banquillo { background-color: #D1D1D1 !important; color: #000 !important; }
    .en-pista { color: #FFF !important; }
    .time-large { font-size: 1.8rem !important; font-weight: 900 !important; font-family: 'Roboto Mono'; line-height: 0.9; }
    
    .pista-portero-navy { background-color: #000080 !important; border: 2px solid #FFF !important; } 
    .pista-verde { background-color: #28a745 !important; }
    .pista-roja { background-color: #dc3545 !important; animation: blinker 0.8s linear infinite; }
    
    @keyframes blinker { 50% { opacity: 0.7; } }
    .stButton > button { height: 28px !important; font-size: 0.7rem !important; border-radius: 4px; font-weight: bold !important; padding: 0px !important; }
    .porteria-section { background: #ffffff; padding: 5px; border-radius: 8px; border: 2px solid #000080; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

st_autorefresh(1000, key="refresh_v38_6")
ah = time.time()
tr_total = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr_total); mv, sv = divmod(int(rem), 60)
min_act = f"{s.periodo} {mv:02d}:{sv:02d}"

# --- UI TABS ---
tabs = st.tabs(["🎮 PARTIDO", "📊 TOTALES", "📜 HISTORIAL", "📥 EXCEL", "⚙️ CONFIG"])

with tabs[0]:
    # Marcador
    st.markdown(f"""<div class="scoreboard-container"><div style="font-size:0.6rem;">{s.fecha} — {s.ciudad}</div><span class="score-number">{s.ml}</span><span class="stadium-clock">&nbsp;&nbsp;{mv:02d}:{sv:02d}&nbsp;&nbsp;</span><span class="score-number">{s.mr}</span></div>""", unsafe_allow_html=True)
    
    # Faltas
    cf1, cf2, cf3, cf4, cf5, cf6 = st.columns([0.5, 0.5, 2, 2, 0.5, 0.5])
    if cf1.button("➖", key="fl_m"): s.fl = max(0, s.fl-1); st.rerun()
    if cf2.button("➕", key="fl_p"): s.fl += 1; s.eventos.append({'Minuto': min_act, 'Evento': f'FALTA {s.loc}', 'Cuarteto': '-'}); st.rerun()
    cf3.markdown(f"<div style='text-align:right; color:#FFCC00; font-weight:900;'>{s.loc}: {s.fl}</div>", unsafe_allow_html=True)
    cf4.markdown(f"<div style='text-align:left; color:#FFCC00; font-weight:900;'>{s.rv}: {s.fr}</div>", unsafe_allow_html=True)
    if cf5.button("➕", key="fr_p"): s.fr += 1; s.eventos.append({'Minuto': min_act, 'Evento': f'FALTA {s.rv}', 'Cuarteto': '-'}); st.rerun()
    if cf6.button("➖", key="fr_m"): s.fr = max(0, s.fr-1); st.rerun()

    # Controles Superiores (Goles y Tarjetas Rival)
    c_top = st.columns([2, 0.8, 1, 0.6, 0.6, 1])
    if c_top[0].button("▶ START / STOP", use_container_width=True, type="primary"): toggle_timer(); st.rerun()
    with c_top[1]: d_riv = st.number_input("Dor.", 1, 99, key="dg", label_visibility="collapsed")
    if c_top[2].button(f"⚽ GOL {s.rv[:3]}", use_container_width=True):
        s.mr += 1; s.eventos.append({'Minuto': min_act, 'Evento': f'⚽ GOL {s.rv} (#{d_riv})', 'Cuarteto': get_cuarteto()}); st.rerun()
    if c_top[3].button(f"🟨", use_container_width=True):
        s.eventos.append({'Minuto': min_act, 'Evento': f'🟨 Amarilla {s.rv} (#{d_riv})', 'Cuarteto': '-'})
    if c_top[4].button(f"🟥", use_container_width=True):
        s.eventos.append({'Minuto': min_act, 'Evento': f'🟥 Roja {s.rv} (#{d_riv})', 'Cuarteto': '-'})
    if c_top[5].button("🏁 PERIODO", use_container_width=True):
        if s.on: toggle_timer()
        for j in s.js: j["tt"] = 0.0; j["i"] = None
        if s.periodo == "1ª PARTE": s.periodo = "2ª PARTE"; s.ta = 0.0; s.fl, s.fr = 0, 0
        else: s.finalizado = True
        st.rerun()

    # CUADRÍCULA 5 COLUMNAS
    jugadores_activos = [j for j in s.js if j['n'].strip() != ""]
    cols = st.columns(5)
    p_campo_count = sum(1 for i, j in enumerate(jugadores_activos) if j['p'] and i >= 2)
    
    for idx, j in enumerate(jugadores_activos):
        with cols[idx % 5]:
            es_p_fijo = (idx < 2)
            cur_rot = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            cl = "banquillo" if not j['p'] else ("en-pista " + ("pista-portero-navy" if es_p_fijo else ("pista-verde" if cur_rot < 240 else "pista-roja")))
            
            st.markdown(f"<div class='card {cl}'><div class='player-name'>{j['n']}</div><div class='time-large'>{fmt_time(cur_rot)}</div><div style='font-size:0.6rem;'>⚽ {j['g']}</div></div>", unsafe_allow_html=True)
            
            # Botón de Cambio 50% ancho
            bt1, bt2 = st.columns([2, 2])
            with bt1:
                if st.button("🔄 Cambio", key=f"c_{idx}", use_container_width=True):
                    if not j["p"]:
                        if es_p_fijo or p_campo_count < 4:
                            j["p"] = True
                            j["i"], j["r"], j["tt"] = (ah if s.on else None), j["r"]+1, 0.0
                    else:
                        if s.on and j["i"]: d_t = ah - j["i"]; j["tot"] += d_t; j["tt"] += d_t
                        j["p"], j["i"] = False, None
                    st.rerun()
            with bt2:
                sc1, sc2, sc3 = st.columns([1, 1, 1])
                if sc1.button("⚽", key=f"g_{idx}"):
                    j['g'] += 1; s.ml += 1; s.eventos.append({'Minuto': min_act, 'Evento': f'⚽ GOL: {j["n"]}', 'Cuarteto': get_cuarteto()}); st.rerun()
                if sc2.button("🟨", key=f"ty_{idx}"): s.eventos.append({'Minuto': min_act, 'Evento': f'🟨 Amarilla: {j["n"]}', 'Cuarteto': '-'})
                if sc3.button("🟥", key=f"tr_{idx}"): s.eventos.append({'Minuto': min_act, 'Evento': f'🟥 Roja: {j["n"]}', 'Cuarteto': '-'})

    # Portería inferior
    st.markdown("<div class='porteria-section'>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    if p1.button("🧤 M ✅", use_container_width=True): s.pm_ok += 1
    if p2.button("🧤 M ❌", use_container_width=True): s.pm_err += 1
    if p3.button("👟 P ✅", use_container_width=True): s.pp_ok += 1
    if p4.button("👟 P ❌", use_container_width=True): s.pp_err += 1
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.subheader("📊 Totales")
    st.write(f"🧤 Mano: {p_calc(s.pm_ok, s.pm_err)} | 👟 Pie: {p_calc(s.pp_ok, s.pp_err)}")
    data_res = [{"Jugador": j['n'], "Goles": j['g'], "Tiempo Total": fmt_time(j['tot']), "Rot": j['r']} for j in jugadores_activos]
    st.table(pd.DataFrame(data_res))

with tabs[2]:
    if s.eventos: st.table(pd.DataFrame(s.eventos[::-1]).fillna("-"))

with tabs[3]:
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame([{"Local": s.loc, "Rival": s.rv, "Goles L": s.ml, "Goles R": s.mr}]).to_excel(writer, sheet_name='Resumen', index=False)
            pd.DataFrame(s.eventos).to_excel(writer, sheet_name='Historial', index=False)
            df_exc = pd.DataFrame([{"Jugador": j['n'], "Goles": j['g'], "Tiempo": fmt_time(j['tot'])} for j in jugadores_activos])
            df_exc.to_excel(writer, sheet_name='Jugadores', index=False)
        st.download_button("📥 DESCARGAR EXCEL", output.getvalue(), f"Match_{s.loc}_{s.rv}.xlsx", use_container_width=True)
    except: st.error("Asegúrate de que xlsxwriter esté en requirements.txt")

with tabs[4]:
    st.subheader("⚙️ Configuración")
    col1, col2, col3 = st.columns(3)
    s.loc = col1.text_input("Local", s.loc).upper()
    s.rv = col2.text_input("Rival", s.rv).upper()
    s.ciudad = col3.text_input("Ciudad", s.ciudad).upper()
    st.divider()
    new_names = []
    c1, c2 = st.columns(2)
    for i in range(14):
        with (c1 if i < 7 else c2):
            label = f"PORTERO {i+1}" if i < 2 else f"Jugador {i+1}"
            new_names.append(st.text_input(label, value=s.js[i]['n'] if i < len(s.js) else "", key=f"ed_n_{i}"))
    if st.button("💾 GUARDAR"):
        s.js = [{"n":x,"tt":0.0,"tot":0.0,"r":0,"g":0,"i":None,"p":False} for x in new_names]
        st.rerun()
    if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()
