import streamlit as st
import pandas as pd
import time
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Configuración de página
st.set_page_config(page_title="LUD Match Control v30.0", layout="wide")

# --- CSS RECUPERADO (Fichas Grandes y Legibles) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;900&display=swap');
    
    /* Evitar selección de texto y comportamientos extraños en iPad */
    * { -webkit-user-select: none; user-select: none; -webkit-tap-highlight-color: transparent; }
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; }
    .block-container { padding: 0.5rem !important; }
    
    /* Marcador Grande */
    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 10px; border-radius: 15px 15px 0 0;
        color: white; border-bottom: 2px solid rgba(255,255,255,0.1);
    }
    .score-number { font-size: 3.5rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 4rem !important; font-weight: 700; text-align: center; line-height: 1; }
    .fouls-bar {
        display: flex; justify-content: space-around; background: #000000; 
        color: #ffcc00; padding: 5px; border-radius: 0 0 15px 15px; 
        font-weight: 900; font-size: 1.2rem; margin-bottom: 15px;
    }

    /* ESTILO DE LOS BOTONES-NOMBRE (GRANDES Y MARRONES) */
    div.stButton > button[key^="name_btn_"] {
        height: 55px !important;
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        border-radius: 8px 8px 0 0 !important;
        margin-bottom: -5px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }

    /* Contenedor de la ficha para alinear tiempos */
    .stats-area {
        background-color: rgba(255,255,255,0.4);
        border-radius: 0 0 8px 8px;
        padding: 5px;
        border: 1px solid rgba(0,0,0,0.1);
        border-top: none;
        margin-bottom: 8px;
        text-align: center;
        min-height: 60px;
    }

    /* Footer */
    .footer-control { background-color: #ffffff; padding: 10px; border-radius: 15px; border-top: 5px solid #4B2E2A; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'js' not in st.session_state:
    n = ["Serra","Julian","Omar","Tony","Rochina","Benages","Pedrito","Parre Jr","Baeza","Manu","Pedro Toro","Paco Silla","Jose","Coque","Nacho Gomez"]
    st.session_state.update({
        "js": [{"n":x,"tt":0.0,"tot":0.0,"r":0,"i":None,"p":False} for x in n],
        "eventos": [], "pm_ok": 0, "pm_err": 0, "pp_ok": 0, "pp_err": 0, 
        "al": 0, "rl": 0, "ar": 0, "rr": 0, "ml": 0, "mr": 0, "fl": 0, "fr": 0, 
        "ta": 0.0, "ic": None, "on": False, "rv": "RIVAL", "lugar": "Pabellón", "fecha": datetime.now().date(),
        "tm": False, "tm_i": None, "analisis_goles": [], "periodo": "1ª PARTE", "finalizado": False
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v30")

ah = time.time()
tr_total = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr_total)
mv, sv = divmod(int(rem), 60)
min_act = f"{s.periodo} {mv:02d}:{sv:02d}"

# --- LÓGICA DE ROTACIÓN ---
def realizar_cambio(idx):
    j = s.js[idx]
    es_p = j['n'] in ["Serra", "Jose"]
    jugadores_campo_pista = sum(1 for x in s.js if x['p'] and x['n'] not in ["Serra", "Jose"])
    
    if not j["p"]:
        if es_p or jugadores_campo_pista < 4:
            j["p"] = True
            if not es_p:
                j["i"] = (time.time() if s.on else None)
                j["r"] += 1
                j["tt"] = 0.0
    else:
        if not es_p and s.on and j["i"]:
            d_t = time.time() - j["i"]
            j["tot"] += d_t
            j["tt"] += d_t
        j["p"], j["i"] = False, None

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

# --- UI ---
t1, t2, t3, t4, t5 = st.tabs(["🎮 PARTIDO", "📜 HISTORIAL", "⚽ GOLES", "📊 EXCEL", "⚙️ CONFIG"])

with t1:
    timer_display = f"{max(0, 60 - int(ah - s.tm_i))}s" if s.tm else f"{mv:02d}:{sv:02d}"
    st.markdown(f"""
        <div class="scoreboard-container">
            <div style="text-align:center;"><div class="score-number">{s.ml}</div><div style="font-size:0.8rem; font-weight:900;">LEVANTE UD</div></div>
            <div class="stadium-clock" style="color: {'#FF0000' if rem <= 0 else '#FFFFFF'};">{timer_display}</div>
            <div style="text-align:center;"><div class="score-number">{s.mr}</div><div style="font-size:0.8rem; font-weight:900;">{s.rv[:8]}</div></div>
        </div>
        <div class="fouls-bar">FALTAS LUD: {s.fl} | {s.rv}: {s.fr} | {s.periodo}</div>
    """, unsafe_allow_html=True)

    c_top = st.columns([2, 1, 1, 1, 1])
    if c_top[0].button("▶ START / STOP ⏸", key="main_btn", use_container_width=True, disabled=s.finalizado): toggle_timer(); st.rerun()
    if c_top[1].button("🏁 FIN PARTE", key="end_btn", use_container_width=True, disabled=s.finalizado): 
        if s.on: toggle_timer()
        s.eventos.append({'Tiempo': min_act, 'Evento': f'🏁 FIN {s.periodo}'})
        if s.periodo == "1ª PARTE": s.periodo = "2ª PARTE"; s.ta = 0.0; s.fl, s.fr = 0, 0
        else: s.finalizado = True; s.periodo = "FINAL"
        st.rerun()
    with c_top[2]:
        with st.popover("⚽ LUD", use_container_width=True):
            p_gol = st.selectbox("Autor", [x['n'] for x in s.js], key="gl")
            if st.button("OK GOL LUD"): s.ml+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL LUD ({p_gol})'}); st.rerun()
    with c_top[3]:
        with st.popover(f"⚽ {s.rv[:3]}", use_container_width=True):
            d_riv = st.number_input("Dorsal", 1, 99, key="sel_r")
            if st.button(f"OK GOL {s.rv[:3]}"): s.mr+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL {s.rv} (#{d_riv})'}); st.rerun()
    with c_top[4]: 
        if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

    st.markdown("---")
    
    cols = st.columns(5)
    for i, j in enumerate(s.js):
        with cols[i%5]:
            es_p = j['n'] in ["Serra", "Jose"]
            cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            tot = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            
            # Color del botón del nombre
            if not j['p']: b_col, t_col = "#D1D1D1", "#4B2E2A"
            elif es_p: b_col, t_col = "#008080", "#FFFFFF"
            else:
                if cur < 240: b_col, t_col = "#00FF41", "#000000"
                elif cur < 360: b_col, t_col = "#FF5E00", "#FFFFFF"
                else: b_col, t_col = "#FF0000", "#FFFFFF"

            # Inyectar CSS para el tamaño grande del botón de nombre
            st.markdown(f"""<style>div.stButton > button[key="name_btn_{i}"] {{ background-color: {b_col} !important; color: {t_col} !important; }}</style>""", unsafe_allow_html=True)
            
            # NOMBRE COMO BOTÓN PRINCIPAL
            if st.button(j['n'], key=f"name_btn_{i}", disabled=s.finalizado):
                realizar_cambio(i); st.rerun()
            
            # ÁREA DE ESTADÍSTICAS (ALINEADA)
            st.markdown('<div class="stats-area">', unsafe_allow_html=True)
            if not es_p:
                st.markdown(f"<div style='font-size:1.3rem; font-weight:900; color:#4B2E2A;'>{int(cur//60):02d}:{int(cur%60):02d}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:0.8rem; color:#4B2E2A;'>Σ {int(tot//60):02d}:{int(tot%60):02d} | R:{j['r']}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='padding-top:15px; font-weight:bold; color:#4B2E2A;'>PORTERO</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # BOTÓN DE CAMBIO AUXILIAR
            if st.button("🔄", key=f"bt_rot_{i}", use_container_width=True, disabled=s.finalizado):
                realizar_cambio(i); st.rerun()

    st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
    f_l, f_m, f_r = st.columns([2, 4, 2])
    with f_l:
        if st.button("⏱️ TM LUD", key="tml", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); st.rerun()
        c_f1 = st.columns(2)
        c_f1[0].button("F+ LUD", on_click=lambda: setattr(s, 'fl', s.fl+1))
        c_f1[1].button("F- LUD", on_click=lambda: setattr(s, 'fl', max(0, s.fl-1)))
    with f_m:
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            with st.popover("LUD 🟨🟥"):
                py = st.selectbox("Jugador", [x['n'] for x in s.js], key="sy_l")
                if st.button("🟨 LUD"): s.al+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟨 LUD ({py})'}); st.rerun()
                if st.button("🟥 LUD"): s.rl+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟥 LUD ({py})'}); st.rerun()
        with c2:
            with st.popover(f"{s.rv[:3]} 🟨🟥"):
                dy = st.number_input("Dorsal", 1, 99, key="sy_r")
                if st.button(f"🟨 {s.rv[:3]}"): s.ar+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟨 {s.rv} (#{dy})'}); st.rerun()
                if st.button(f"🟥 {s.rv[:3]}"): s.rr+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟥 {s.rv} (#{dy})'}); st.rerun()
        with c3:
            st.write("🧤 Mano")
            c_m = st.columns(2)
            c_m[0].button("✅", key="mok", on_click=lambda: setattr(s, 'pm_ok', s.pm_ok+1))
            c_m[1].button("❌", key="mer", on_click=lambda: setattr(s, 'pm_err', s.pm_err+1))
        with c4:
            st.write("👟 Pie")
            c_p = st.columns(2)
            c_p[0].button("✅ ", key="pok", on_click=lambda: setattr(s, 'pp_ok', s.pp_ok+1))
            c_p[1].button("❌ ", key="per", on_click=lambda: setattr(s, 'pp_err', s.pp_err+1))
    with f_r:
        if st.button(f"⏱️ TM {s.rv[:3]}", key="tmr", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); st.rerun()
        c_f2 = st.columns(2)
        c_f2[0].button(f"F+ RIV", on_click=lambda: setattr(s, 'fr', s.fr+1))
        c_f2[1].button(f"F- RIV", on_click=lambda: setattr(s, 'fr', max(0, s.fr-1)))
    st.markdown("</div>", unsafe_allow_html=True)

with t4:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        pd.DataFrame({"Métrica": ["Rival", "LUD", s.rv], "Valor": [s.rv, s.ml, s.mr]}).to_excel(writer, sheet_name='Resumen', index=False)
        pd.DataFrame(s.eventos).to_excel(writer, sheet_name='Historial', index=False)
    st.download_button(label="📥 EXCEL", data=buf.getvalue(), file_name=f"LUD_{s.rv}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

with t5:
    s.rv = st.text_input("Rival", s.rv).upper()
