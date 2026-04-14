import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v25.0", layout="wide")

# --- CSS INTEGRAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #e0e0e0; overflow-x: hidden; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 12px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #4B2E2A; color: white; border-radius: 10px 10px 0 0; padding: 10px 20px; }

    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 5px; border-radius: 15px;
        color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border-bottom: 4px solid #000; margin-bottom: 5px;
    }
    .score-number { font-size: 3.5rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 4rem !important; font-weight: 700; text-align: center; line-height: 1; }

    .player-name {
        font-size: 1.1rem !important;
        font-weight: 900 !important;
        color: #4B2E2A !important;
        text-transform: uppercase;
        margin-bottom: 2px;
        line-height: 1;
    }

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
        "eventos": [], 
        "pm_ok": 0, "pm_err": 0, "pp_ok": 0, "pp_err": 0, 
        "al": 0, "rl": 0, "ar": 0, "rr": 0, 
        "ml": 0, "mr": 0, "fl": 0, "fr": 0, 
        "ta": 0.0, "ic": None, "on": False, 
        "pa": "1T", "rv": "RIVAL", "tm": False, "tm_i": None,
        "analisis_goles": [] # Filtrado solo a goles
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v25")

# --- LÓGICA DE TIEMPO ---
ah = time.time()
tr_total = s.ta + (ah - s.ic if s.on and s.ic else 0)
if tr_total >= 1200 and s.on:
    tr_total = 1200; s.ta = 1200; s.on, s.ic = False, None
    for j in s.js:
        if j["p"] and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d; j["i"]=None
    st.rerun()

rem = max(0, 1200 - tr_total)
mv, sv = divmod(int(rem), 60)
min_act = int(tr_total // 60)

def capturar_cuarteto_gol(tipo, detalle):
    cuarteto_data = []
    jugadores_en_pista = [j for j in s.js if j['p'] and j['n'] not in ["Serra", "Jose"]]
    for j in jugadores_en_pista:
        t_rot_sec = j["tt"] + (ah - j["i"] if s.on and j["i"] else 0)
        m_r, s_r = divmod(int(t_rot_sec), 60)
        cuarteto_data.append(f"{j['n']} ({m_r:02d}:{s_r:02d})")
    while len(cuarteto_data) < 4: cuarteto_data.append("-")
    s.analisis_goles.append({
        "Min": f"{mv:02d}:{sv:02d}", "Tipo": tipo, "Detalle": detalle,
        "Marcador": f"{s.ml}-{s.mr}", "P1": cuarteto_data[0], "P2": cuarteto_data[1], "P3": cuarteto_data[2], "P4": cuarteto_data[3]
    })

def toggle_timer():
    if tr_total >= 1200 and not s.on: return
    if not s.on:
        s.ic, s.on, s.tm = time.time(), True, False
        for j in s.js: 
            if j["p"]: j["i"] = s.ic
    else:
        now = time.time(); s.ta += now - s.ic; s.on, s.ic = False, None
        for j in s.js:
            if j["p"] and j["i"]: d = now-j["i"]; j["tot"]+=d; j["tt"]+=d; j["i"]=None

# --- PESTAÑAS ---
tab1, tab_hist, tab_tact, tab_stats = st.tabs(["🎮 PARTIDO", "📜 LINEA DE TIEMPO", "⚽ DATA GOLES", "🧤 PORTERÍA"])

with tab1:
    st.markdown(f'<div style="text-align:center; padding:5px;"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="35"><span style="font-size:1.2rem; font-weight:900; color:#4B2E2A; margin-left:10px;">MATCH CONTROL BY KIKE</span></div>', unsafe_allow_html=True)

    timer_display = f"{max(0, 60 - int(ah - s.tm_i))}s" if s.tm else f"{mv:02d}:{sv:02d}"
    st.markdown(f"""<div class="scoreboard-container"><div style="text-align:center;"><div class="score-number">{s.ml}</div><div style="font-size:0.8rem; font-weight:900;">LEVANTE UD</div></div><div class="stadium-clock" style="color: {'#FF0000' if rem <= 0 else '#FFFFFF'};">{timer_display}</div><div style="text-align:center;"><div class="score-number">{s.mr}</div><div style="font-size:0.8rem; font-weight:900;">{s.rv[:8]}</div></div></div>""", unsafe_allow_html=True)

    c_time = st.columns(3)
    for idx, ck in enumerate(["tm_l", "tm_m", "tm_r"]):
        if c_time[idx].button("▶ START / STOP ⏸", key=ck): toggle_timer(); st.rerun()

    c_goles = st.columns([1,1,1,1])
    with c_goles[0]:
        with st.popover("⚽ GOL LUD", use_container_width=True):
            p_gol = st.selectbox("Autor", [j['n'] for j in s.js], key="sb_gol_lud")
            if st.button("GOOOL!", key="confirm_lud"): s.ml += 1; capturar_cuarteto_gol("GOL LUD", p_gol); s.eventos.append({'min':min_act,'info':f'⚽ GOL LUD ({p_gol})'}); st.rerun()
    with c_goles[1]:
        with st.popover("⚽ GOL RIVAL", use_container_width=True):
            d_gol = st.number_input("Dorsal", 1, 99, key="ni_gol_riv")
            if st.button("GOL RIVAL", key="confirm_riv"): s.mr += 1; capturar_cuarteto_gol("GOL RIVAL", f"#{d_gol}"); s.eventos.append({'min':min_act,'info':f'⚽ GOL RIVAL (#{d_gol})'}); st.rerun()
    with c_goles[2]: s.rv = st.text_input("Rival", s.rv, label_visibility="collapsed").upper()
    with c_goles[3]: 
        if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

    st.markdown("---")
    cols = st.columns(6)
    for i, j in enumerate(s.js):
        with cols[i%6]:
            cur_sec = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            tot_sec = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
            cl = "banquillo" if not j['p'] else ("pista-portero" if j['n'] in ["Serra", "Jose"] else ("pista-verde" if cur_sec < 240 else ("pista-naranja" if cur_sec < 360 else "pista-roja")))
            st.markdown(f"<div class='{cl}'>", unsafe_allow_html=True)
            mc, vc = divmod(int(cur_sec), 60); mt, vt = divmod(int(tot_sec), 60)
            st.markdown(f"<div class='player-name'>{j['n']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:1.2rem; font-weight:900;'>{mc:02d}:{vc:02d}</div><div style='font-size:0.65rem;'>Σ{mt:02d}:{vt:02d} | R:{j['r']}</div>", 1)
            if st.button("🔄", key=f"btn_rot_{i}", use_container_width=True):
                if not j["p"] and sum(1 for x in s.js if x["p"]) < 5:
                    j["p"], j["i"], j["r"] = True, (ah if s.on else None), j["r"]+1; j["tt"] = 0.0
                elif j["p"]:
                    if s.on and j["i"]: d = ah-j["i"]; j["tot"]+=d; j["tt"]+=d
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
    f_l, f_m, f_r = st.columns([2.5, 3.5, 2.5])
    with f_l:
        c_tml, c_fl = st.columns([1.5, 1])
        with c_tml:
            if st.button("⏱️ TM LUD", key="bt_tml", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); s.eventos.append({'min':min_act,'info':f'⏱️ TM LUD'}); st.rerun()
        with c_fl:
            st.button("F+", key="bt_flp", use_container_width=True, on_click=lambda: setattr(s, 'fl', s.fl+1)); st.button("F-", key="bt_flm", use_container_width=True, on_click=lambda: setattr(s, 'fl', max(0, s.fl-1)))
    with f_m:
        c_dis, c_gk = st.columns([1.1, 1])
        with c_dis:
            col_d_l, col_d_r = st.columns(2)
            with col_d_l:
                with st.popover("L🟨", use_container_width=True):
                    p_y = st.selectbox("J", [j['n'] for j in s.js], key="sb_y_lud")
                    if st.button("OK 🟨", key="y_lud"): s.al+=1; s.eventos.append({'min':min_act,'info':f'🟨 Tarjeta LUD ({p_y})'}); st.rerun()
                with st.popover("L🟥", use_container_width=True):
                    p_r = st.selectbox("J", [j['n'] for j in s.js], key="sb_r_lud")
                    if st.button("OK 🟥", key="r_lud"): s.rl+=1; s.eventos.append({'min':min_act,'info':f'🟥 Tarjeta LUD ({p_r})'}); st.rerun()
            with col_d_r:
                with st.popover("R🟨", use_container_width=True):
                    d_y = st.number_input("D", 1, 99, key="ni_y_riv")
                    if st.button("OK 🟨", key="y_riv"): s.ar+=1; s.eventos.append({'min':min_act,'info':f'🟨 Tarjeta RIV (#{d_y})'}); st.rerun()
                with st.popover("R🟥", use_container_width=True):
                    d_r = st.number_input("D", 1, 99, key="ni_r_riv")
                    if st.button("OK 🟥", key="r_riv"): s.rr+=1; s.eventos.append({'min':min_act,'info':f'🟥 Tarjeta RIV (#{d_r})'}); st.rerun()
        with c_gk:
            c_m = st.columns(2); c_m[0].button(f"✅🧤({s.pm_ok})", key="gk_m_ok", on_click=lambda: setattr(s, 'pm_ok', s.pm_ok+1)); c_m[1].button(f"❌🧤({s.pm_err})", key="gk_m_err", on_click=lambda: setattr(s, 'pm_err', s.pm_err+1))
            c_p = st.columns(2); c_p[0].button(f"✅👟({s.pp_ok})", key="gk_p_ok", on_click=lambda: setattr(s, 'pp_ok', s.pp_ok+1)); c_p[1].button(f"❌👟({s.pp_err})", key="gk_p_err", on_click=lambda: setattr(s, 'pp_err', s.pp_err+1))
    with f_r:
        c_fr, c_tmr = st.columns([1, 1.5])
        with c_fr:
            st.button("F+", key="bt_frp", use_container_width=True, on_click=lambda: setattr(s, 'fr', s.fr+1)); st.button("F-", key="bt_frm", use_container_width=True, on_click=lambda: setattr(s, 'fr', max(0, s.fr-1)))
        with c_tmr:
            if st.button("⏱️ TM RIVAL", key="bt_tmr", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); s.eventos.append({'min':min_act,'info':f'⏱️ TM RIVAL'}); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with tab_hist:
    st.subheader("📜 Historial Completo del Partido")
    if s.eventos:
        df_hist = pd.DataFrame(s.eventos)
        st.table(df_hist)
    else:
        st.info("Aún no hay eventos registrados.")

with tab_tact:
    st.subheader("📋 Análisis Táctico: Cuartetos en Goles")
    if s.analisis_goles:
        st.table(pd.DataFrame(s.analisis_goles))
    else:
        st.info("Registra un gol para ver el análisis de fatiga del cuarteto.")

with tab_stats:
    st.subheader("🧤 Eficiencia Portería")
    def per(o, e): t=o+e; return f"{(o/t*100):.1f}%" if t>0 else "0%"
    c1, c2 = st.columns(2)
    c1.metric("Mano", per(s.pm_ok, s.pm_err), f"Total: {s.pm_ok+s.pm_err}")
    c2.metric("Pie", per(s.pp_ok, s.pp_err), f"Total: {s.pp_ok+s.pp_err}")
    st.markdown("---")
    if s.analisis_goles or s.eventos:
        st.download_button("📥 Descargar Datos Completos (CSV)", pd.DataFrame(s.eventos).to_csv(index=False).encode('utf-8'), "partido_lud.csv", "text/csv")
