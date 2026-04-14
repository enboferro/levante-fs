import streamlit as st
import pandas as pd
import time
import io
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Configuración de página
st.set_page_config(page_title="LUD Match Control v29.0", layout="wide")

# --- CSS INTEGRAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; }
    .block-container { padding: 0rem 0.5rem !important; }
    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 2px; border-radius: 10px 10px 0 0;
        color: white; height: 55px;
    }
    .score-number { font-size: 2.2rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 2.8rem !important; font-weight: 700; text-align: center; line-height: 1; }
    .fouls-bar {
        display: flex; justify-content: space-around; background: #000000; 
        color: #ffcc00; padding: 2px; border-radius: 0 0 10px 10px; 
        font-weight: 900; font-size: 1rem; margin-bottom: 5px;
    }
    .player-name { font-size: 0.95rem !important; font-weight: 900 !important; color: #4B2E2A !important; text-transform: uppercase; margin-bottom: 0px; }
    .card { 
        border-radius: 8px; padding: 5px; text-align: center; border: 1px solid #999; margin-bottom: 4px; 
        height: 120px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .pista-portero { background-color: #008080 !important; color: white; border: 2px solid white; }
    .pista-verde { background-color: #00FF41 !important; color: #000; }
    .pista-naranja { background-color: #FF5E00 !important; color: white; }
    .pista-roja { background-color: #FF0000 !important; color: white; border: 2px solid #FFFF00; animation: blinker 0.8s linear infinite; }
    .banquillo { background-color: #D1D1D1 !important; color: #4B2E2A !important; }
    @keyframes blinker { 50% { opacity: 0.4; } }
    .footer-control { background-color: #ffffff; padding: 5px; border-radius: 10px; border-top: 4px solid #4B2E2A; margin-top: 5px; }
    .stButton > button { height: 30px !important; padding: 0px 5px !important; font-size: 0.75rem !important; }
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
st_autorefresh(1000, key="f5_lud_v29")

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
    s.eventos.append({'Tiempo': min_act, 'Evento': f'🏁 FIN {s.periodo}'})
    if s.periodo == "1ª PARTE":
        s.periodo = "2ª PARTE"; s.ta = 0.0; s.fl, s.fr = 0, 0
    else:
        s.finalizado = True; s.periodo = "FINAL"
    st.rerun()

def capturar_tactico(tipo, detalle):
    cuarteto = []
    for j in s.js:
        if j['p'] and j['n'] not in ["Serra", "Jose"]:
            t_r = j["tt"] + (ah - j["i"] if s.on and j["i"] else 0)
            mj, sj = divmod(int(t_r), 60)
            cuarteto.append(f"{j['n']} ({mj:02d}:{sj:02d})")
    while len(cuarteto) < 4: cuarteto.append("-")
    s.analisis_goles.append({"Periodo": s.periodo, "T": f"{mv:02d}:{sv:02d}", "Tipo": tipo, "Detalle": detalle, "Marcador": f"{s.ml}-{s.mr}", "P1": cuarteto[0], "P2": cuarteto[1], "P3": cuarteto[2], "P4": cuarteto[3]})

# --- UI TABS ---
t1, t2, t3, t4, t5 = st.tabs(["🎮 PARTIDO", "📜 HISTORIAL", "⚽ GOLES", "📊 EXCEL", "⚙️ CONFIG"])

with t1:
    timer_display = f"{max(0, 60 - int(ah - s.tm_i))}s" if s.tm else f"{mv:02d}:{sv:02d}"
    st.markdown(f"""
        <div class="scoreboard-container">
            <div style="text-align:center;"><div class="score-number">{s.ml}</div><div style="font-size:0.6rem; font-weight:900;">LUD</div></div>
            <div class="stadium-clock" style="color: {'#FF0000' if rem <= 0 else '#FFFFFF'};">{timer_display}</div>
            <div style="text-align:center;"><div class="score-number">{s.mr}</div><div style="font-size:0.6rem; font-weight:900;">{s.rv[:8]}</div></div>
        </div>
        <div class="fouls-bar">FALTAS LUD: {s.fl} | {s.rv}: {s.fr} | {s.periodo}</div>
    """, unsafe_allow_html=True)

    c_top = st.columns([2, 1, 1, 1, 1])
    if c_top[0].button("▶ START / STOP ⏸", key="main_btn", use_container_width=True, disabled=s.finalizado): toggle_timer(); st.rerun()
    if c_top[1].button("🏁 FIN", key="end_btn", use_container_width=True, disabled=s.finalizado): finalizar_fase()
    with c_top[2]:
        with st.popover("⚽ LUD", use_container_width=True):
            p = st.selectbox("Autor", [x['n'] for x in s.js], key="sel_l")
            if st.button("GOOOL LUD"): s.ml+=1; capturar_tactico("GOL LUD", p); s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL LUD ({p})'}); st.rerun()
    with c_top[3]:
        with st.popover(f"⚽ {s.rv[:5]}", use_container_width=True):
            d = st.number_input("Dorsal", 1, 99, key="sel_r")
            if st.button(f"GOL {s.rv[:5]}"): s.mr+=1; capturar_tactico(f"GOL {s.rv}", f"#{d}"); s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL {s.rv} (#{d})'}); st.rerun()
    with c_top[4]: 
        if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

    st.markdown("---")
    cols = st.columns(5)
    for i, j in enumerate(s.js):
        with cols[i%5]:
            es_p = j['n'] in ["Serra", "Jose"]
            cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            tot = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            cl = "banquillo" if not j['p'] else ("pista-portero" if es_p else ("pista-verde" if cur < 240 else ("pista-naranja" if cur < 360 else "pista-roja")))
            st.markdown(f"<div class='card {cl}'><span class='player-name'>{j['n']}</span>", unsafe_allow_html=True)
            if not es_p:
                st.markdown(f"<div><div style='font-size:0.9rem; font-weight:900;'>{int(cur//60):02d}:{int(cur%60):02d}</div><div style='font-size:0.6rem;'>Σ {int(tot//60):02d}:{int(tot%60):02d} | R:{j['r']}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
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
    f_l, f_m, f_r = st.columns([2, 4, 2])
    with f_l:
        st.button("⏱️ TM LUD", key="tml", on_click=lambda: (toggle_timer(), setattr(s, 'tm', True), setattr(s, 'tm_i', time.time())))
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
        st.button(f"⏱️ TM {s.rv[:3]}", key="tmr", on_click=lambda: (toggle_timer(), setattr(s, 'tm', True), setattr(s, 'tm_i', time.time())))
        c_f2 = st.columns(2)
        c_f2[0].button(f"F+ {s.rv[:3]}", on_click=lambda: setattr(s, 'fr', s.fr+1))
        c_f2[1].button(f"F- {s.rv[:3]}", on_click=lambda: setattr(s, 'fr', max(0, s.fr-1)))
    st.markdown("</div>", unsafe_allow_html=True)

with t2:
    if s.eventos: st.table(pd.DataFrame(s.eventos))
    else: st.info("Sin eventos")

with t3:
    if s.analisis_goles: st.table(pd.DataFrame(s.analisis_goles))
    else: st.info("Sin goles")

with t4:
    def p_calc(o, e): t=o+e; return f"{(o/t*100):.1f}%" if t>0 else "0.0%"
    st.subheader("Estadísticas Portería")
    st.write(f"🧤 Mano: {p_calc(s.pm_ok, s.pm_err)} (Total: {s.pm_ok+s.pm_err})")
    st.write(f"👟 Pie: {p_calc(s.pp_ok, s.pp_err)} (Total: {s.pp_ok+s.pp_err})")
    st.markdown("---")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        pd.DataFrame({"Métrica": ["Rival", "Fecha", "Lugar", "Goles LUD", f"Goles {s.rv}", "Faltas LUD", f"Faltas {s.rv}"], 
                      "Valor": [s.rv, s.fecha.strftime("%d/%m/%Y"), s.lugar, s.ml, s.mr, s.fl, s.fr]}).to_excel(writer, sheet_name='Resumen', index=False)
        if s.eventos: pd.DataFrame(s.eventos).to_excel(writer, sheet_name='Historial', index=False)
        if s.analisis_goles: pd.DataFrame(s.analisis_goles).to_excel(writer, sheet_name='Análisis Goles', index=False)
        data_j = [{"Jugador": x["n"], "Min Tot": f"{int(x['tot']//60):02d}:{int(x['tot']%60):02d}", "Rotaciones": x["r"]} for x in s.js if x["n"] not in ["Serra", "Jose"]]
        pd.DataFrame(data_j).to_excel(writer, sheet_name='Jugadores', index=False)
    
    file_name = f"LUD-vs-{s.rv.replace(' ', '_')}({s.fecha.strftime('%d-%m-%Y')}).xlsx"
    st.download_button(label=f"📥 DESCARGAR {file_name}", data=buf.getvalue(), file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

with t5:
    st.subheader("Configuración del Encuentro")
    s.rv = st.text_input("Nombre del Rival", s.rv).upper()
    s.lugar = st.text_input("Lugar del Partido", s.lugar)
    s.fecha = st.date_input("Fecha del Partido", s.fecha)
    st.info("Estos datos se utilizarán para el marcador y el informe final.")
