import streamlit as st
import pandas as pd
import time
import io
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v27.0", layout="wide")

# --- CSS INTEGRAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #e0e0e0; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #4B2E2A; color: white; border-radius: 10px 10px 0 0; padding: 10px 20px; }
    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 5px; border-radius: 15px 15px 0 0;
        color: white; border-bottom: 2px solid rgba(255,255,255,0.1); margin-bottom: 0px;
    }
    .fouls-bar {
        display: flex; justify-content: space-around; background: #000000; 
        color: #ffcc00; padding: 5px; border-radius: 0 0 15px 15px; 
        font-weight: 900; font-size: 1.2rem; margin-bottom: 10px;
        border-bottom: 4px solid #4B2E2A;
    }
    .score-number { font-size: 3.5rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 4rem !important; font-weight: 700; text-align: center; line-height: 1; }
    .player-name { font-size: 1.1rem !important; font-weight: 900 !important; color: #4B2E2A !important; text-transform: uppercase; margin-bottom: 2px; }
    .pista-portero { background-color: #008080 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 2px solid white; }
    .pista-verde { background-color: #00FF41 !important; color: #000; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; }
    .pista-naranja { background-color: #FF5E00 !important; color: white !important; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 1px solid white; }
    .pista-roja { background-color: #FF0000 !important; color: white !important; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 2px solid #FFFF00; animation: blinker 0.8s linear infinite; }
    .banquillo { background-color: #444444 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; opacity: 0.9; }
    @keyframes blinker { 50% { opacity: 0.4; } }
    .footer-control { background-color: #ffffff; padding: 8px; border-radius: 15px 15px 0 0; border-top: 5px solid #4B2E2A; margin-top: 10px; }
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
        "analisis_goles": [],
        "periodo": "1ª PARTE" # <--- Control de periodo
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v27")

ah = time.time()
tr_total = s.ta + (ah - s.ic if s.on and s.ic else 0)
rem = max(0, 1200 - tr_total)
mv, sv = divmod(int(rem), 60)
min_act = f"{s.periodo} - {mv:02d}:{sv:02d}"

# --- FUNCIONES ---
def capturar_cuarteto_gol(tipo, detalle):
    cuarteto = [j for j in s.js if j['p'] and j['n'] not in ["Serra", "Jose"]]
    data_c = []
    for j in cuarteto:
        t_rot = j["tt"] + (ah - j["i"] if s.on and j["i"] else 0)
        mr, sr = divmod(int(t_rot), 60)
        data_c.append(f"{j['n']} ({mr:02d}:{sr:02d})")
    while len(data_c) < 4: data_c.append("-")
    s.analisis_goles.append({
        "Periodo": s.periodo, "Tiempo": f"{mv:02d}:{sv:02d}", "Tipo": tipo, "Detalle": detalle, 
        "Marcador": f"{s.ml}-{s.mr}", "P1": data_c[0], "P2": data_c[1], "P3": data_c[2], "P4": data_c[3]
    })

def toggle_timer():
    if not s.on:
        s.ic, s.on = time.time(), True
        for j in s.js: 
            if j["p"]: j["i"] = s.ic
    else:
        now = time.time(); s.ta += now - s.ic; s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]: d = now-j["i"]; j["tot"]+=d; j["tt"]+=d; j["i"]=None

def finalizar_parte():
    # Parar todo
    if s.on: toggle_timer()
    # Registrar evento de fin
    s.eventos.append({'Tiempo': 'FIN', 'Evento': f'🏁 FINALIZADA {s.periodo}'})
    # Cambiar a 2ª parte y resetear reloj
    if s.periodo == "1ª PARTE":
        s.periodo = "2ª PARTE"
        s.ta = 0.0
        # Opcional: Resetear faltas si quieres (Futsal las resetea)
        s.fl = 0
        s.fr = 0
    st.rerun()

# --- VISTA PRINCIPAL ---
tab1, tab2, tab3, tab4 = st.tabs(["🎮 PARTIDO", "📜 HISTORIAL", "⚽ GOLES", "📊 EXCEL TOTAL"])

with tab1:
    st.markdown(f'<div style="text-align:center; padding:5px;"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="35"><span style="font-size:1.2rem; font-weight:900; color:#4B2E2A; margin-left:10px;">MATCH CONTROL BY KIKE - {s.periodo}</span></div>', unsafe_allow_html=True)
    timer_display = f"{max(0, 60 - int(ah - s.tm_i))}s" if s.tm else f"{mv:02d}:{sv:02d}"
    
    st.markdown(f"""
        <div class="scoreboard-container">
            <div style="text-align:center;"><div class="score-number">{s.ml}</div><div style="font-size:0.8rem; font-weight:900;">LEVANTE UD</div></div>
            <div class="stadium-clock" style="color: {'#FF0000' if rem <= 0 else '#FFFFFF'};">{timer_display}</div>
            <div style="text-align:center;"><div class="score-number">{s.mr}</div><div style="font-size:0.8rem; font-weight:900;">{s.rv[:8]}</div></div>
        </div>
        <div class="fouls-bar">
            <span>FALTAS: {s.fl}</span>
            <span style="color:white; font-size:0.8rem; opacity:0.5;">VS</span>
            <span>FALTAS: {s.fr}</span>
        </div>
        """, unsafe_allow_html=True)

    c_time = st.columns([2, 1])
    if c_time[0].button("▶ START / STOP ⏸", key="main_timer_btn", use_container_width=True): toggle_timer(); st.rerun()
    if c_time[1].button(f"🏁 FIN {s.periodo}", key="fin_parte_btn", use_container_width=True): finalizar_parte()

    c_goles = st.columns([1,1,1,1])
    with c_goles[0]:
        with st.popover("⚽ GOL LUD", use_container_width=True):
            p_gol = st.selectbox("Autor", [j['n'] for j in s.js], key="sel_gol_lud")
            if st.button("GOOOL!", key="btn_gol_lud_ok"): s.ml += 1; capturar_cuarteto_gol("GOL LUD", p_gol); s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL LUD ({p_gol})'}); st.rerun()
    with c_goles[1]:
        with st.popover("⚽ GOL RIVAL", use_container_width=True):
            d_gol = st.number_input("Dorsal", 1, 99, key="num_gol_riv")
            if st.button("GOL RIVAL", key="btn_gol_riv_ok"): s.mr += 1; capturar_cuarteto_gol("GOL RIVAL", f"#{d_gol}"); s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL RIVAL (#{d_gol})'}); st.rerun()
    with c_goles[2]: s.rv = st.text_input("Rival", s.rv, label_visibility="collapsed", key="in_rival_name").upper()
    with c_goles[3]: 
        if st.button("🗑️ RESET TOTAL"): st.session_state.clear(); st.rerun()

    st.markdown("---")
    cols = st.columns(6)
    for i, j in enumerate(s.js):
        with cols[i%6]:
            cur_sec = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            tot_sec = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            cl = "banquillo" if not j['p'] else ("pista-portero" if j['n'] in ["Serra", "Jose"] else ("pista-verde" if cur_sec < 240 else ("pista-naranja" if cur_sec < 360 else "pista-roja")))
            st.markdown(f"<div class='{cl}'>", unsafe_allow_html=True)
            mc, vc = divmod(int(cur_sec), 60); mt, vt = divmod(int(tot_sec), 60)
            st.markdown(f"<div class='player-name'>{j['n']}</div><div style='font-size:1.2rem; font-weight:900;'>{mc:02d}:{vc:02d}</div><div style='font-size:0.65rem;'>Σ{mt:02d}:{vt:02d} | R:{j['r']}</div>", 1)
            if st.button("🔄", key=f"rot_btn_{i}", use_container_width=True):
                if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1; j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
    f_l, f_m, f_r = st.columns([2, 4, 2])
    with f_l:
        if st.button("⏱️ TM LUD", key="tm_lud_footer", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); s.eventos.append({'Tiempo':min_act,'Evento':'⏱️ TM LUD'}); st.rerun()
        c_f = st.columns(2); c_f[0].button("F+ LUD", key="flp", on_click=lambda: setattr(s, 'fl', s.fl+1)); c_f[1].button("F- LUD", key="flm", on_click=lambda: setattr(s, 'fl', max(0, s.fl-1)))
    with f_m:
        c_p = st.columns(4)
        with c_p[0]:
            with st.popover("LUD🟨🟥", use_container_width=True):
                p_y = st.selectbox("J", [x['n'] for x in s.js], key="sel_y_lud")
                if st.button("OK 🟨", key="btn_y_lud_ok"): s.al+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟨 LUD ({p_y})'}); st.rerun()
                if st.button("OK 🟥", key="btn_r_lud_ok"): s.rl+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟥 LUD ({p_y})'}); st.rerun()
        with c_p[1]:
            with st.popover("RIV🟨🟥", use_container_width=True):
                d_y = st.number_input("D", 1, 99, key="num_y_riv")
                if st.button("OK 🟨", key="btn_y_riv_ok"): s.ar+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟨 RIV (#{d_y})'}); st.rerun()
                if st.button("OK 🟥", key="btn_r_riv_ok"): s.rr+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟥 RIV (#{d_y})'}); st.rerun()
        with c_p[2]:
            st.button(f"✅🧤({s.pm_ok})", key="gk_m_ok", on_click=lambda: setattr(s, 'pm_ok', s.pm_ok+1), use_container_width=True)
            st.button(f"❌🧤({s.pm_err})", key="gk_m_err", on_click=lambda: setattr(s, 'pm_err', s.pm_err+1), use_container_width=True)
        with c_p[3]:
            st.button(f"✅👟({s.pp_ok})", key="gk_p_ok", on_click=lambda: setattr(s, 'pp_ok', s.pp_ok+1), use_container_width=True)
            st.button(f"❌👟({s.pp_err})", key="gk_p_err", on_click=lambda: setattr(s, 'pp_err', s.pp_err+1), use_container_width=True)
    with f_r:
        if st.button("⏱️ TM RIV", key="tm_riv_footer", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); s.eventos.append({'Tiempo':min_act,'Evento':'⏱️ TM RIVAL'}); st.rerun()
        c_f2 = st.columns(2); c_f2[0].button("F+ RIV", key="frp", on_click=lambda: setattr(s, 'fr', s.fr+1)); c_f2[1].button("F- RIV", key="frm", on_click=lambda: setattr(s, 'fr', max(0, s.fr-1)))
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    if s.eventos: st.table(pd.DataFrame(s.eventos))
    else: st.info("Sin eventos registrados")

with tab3:
    if s.analisis_goles: st.table(pd.DataFrame(s.analisis_goles))
    else: st.info("Sin goles registrados")

with tab4:
    def p_calc(o, e): t=o+e; return f"{(o/t*100):.1f}%" if t>0 else "0%"
    col1, col2 = st.columns(2)
    col1.metric("Saques Mano", p_calc(s.pm_ok, s.pm_err), f"OK: {s.pm_ok} | X: {s.pm_err}")
    col2.metric("Saques Pie", p_calc(s.pp_ok, s.pp_err), f"OK: {s.pp_ok} | X: {s.pp_err}")
    
    st.markdown("---")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        pd.DataFrame({"Dato": ["LUD", "RIV", "G.LUD", "G.RIV", "F.LUD", "F.RIV"], "Valor": [s.ml, s.mr, s.ml, s.mr, s.fl, s.fr]}).to_excel(writer, sheet_name='Resumen', index=False)
        if s.eventos: pd.DataFrame(s.eventos).to_excel(writer, sheet_name='Historial_Completo', index=False)
        if s.analisis_goles: pd.DataFrame(s.analisis_goles).to_excel(writer, sheet_name='Analisis_Goles', index=False)
        
        data_j = []
        for j in s.js:
            t_total_j = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            mj, sj = divmod(int(t_total_j), 60)
            data_j.append({"Jugador": j["n"], "Minutos": f"{mj:02d}:{sj:02d}", "Rot": j["r"]})
        pd.DataFrame(data_j).to_excel(writer, sheet_name='Estadisticas_Jugadores', index=False)
        
        data_p = [{"Tipo": "Mano", "OK": s.pm_ok, "X": s.pm_err, "%": p_calc(s.pm_ok, s.pm_err)},
                  {"Tipo": "Pie", "OK": s.pp_ok, "X": s.pp_err, "%": p_calc(s.pp_ok, s.pp_err)}]
        pd.DataFrame(data_p).to_excel(writer, sheet_name='Porteros', index=False)
    
    st.download_button(
        label="📥 DESCARGAR INFORME PARTIDO COMPLETO (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"LUD_Partido_Completo_vs_{s.rv}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="global_download_excel"
    )
