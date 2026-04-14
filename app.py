import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v23.3", layout="wide")

# --- CSS INTEGRAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #e0e0e0; overflow-x: hidden; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #4B2E2A; color: white; border-radius: 10px 10px 0 0; }

    .app-title-container { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 5px; }
    .app-title-text { font-size: 1.2rem; font-weight: 900; color: #4B2E2A; text-transform: uppercase; }

    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 5px; border-radius: 15px;
        color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border-bottom: 4px solid #000; margin-bottom: 5px;
    }
    .score-number { font-size: 3.5rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 4rem !important; font-weight: 700; text-align: center; line-height: 1; }

    .pista-portero { background-color: #008080 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 2px solid white; }
    .pista-verde { background-color: #00FF41 !important; color: #000; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; }
    .pista-naranja { background-color: #FF5E00 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 1px solid white; }
    .pista-roja { background-color: #FF0000 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; font-weight: 900; border: 2px solid #FFFF00; animation: blinker 0.8s linear infinite; }
    .banquillo { background-color: #444444 !important; color: white; border-radius: 8px; padding: 2px; text-align: center; opacity: 0.9; }
    @keyframes blinker { 50% { opacity: 0.4; } }

    .footer-control { background-color: #ffffff; padding: 8px; border-radius: 15px 15px 0 0; border-top: 5px solid #4B2E2A; margin-top: 10px; }
    
    div.stButton > button[key$="_ok"] { background-color: #d4edda !important; color: #155724 !important; border: 2px solid #155724 !important; font-size: 1.1rem !important; border-radius: 10px !important; }
    div.stButton > button[key$="_err"] { background-color: #f8d7da !important; color: #721c24 !important; border: 2px solid #721c24 !important; font-size: 1.1rem !important; border-radius: 10px !important; }
    .gk-block-title { font-size: 0.75rem; font-weight: bold; text-align: center; color: #4B2E2A; margin-bottom: 2px; text-transform: uppercase; }
    .gk-stat-total-v2 { font-size: 1rem; font-weight: bold; text-align: center; color: #4B2E2A; margin-top: 2px; }
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
        "ml": 0, "mr": 0, "fl": 0, "fr": 0, "ta": 0.0, "ic": None, "on": False, 
        "pa": "1T", "rv": "RIVAL", "tm": False, "tm_i": None,
        "analisis_tactico": []
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v23.3")

# --- LÓGICA ---
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

def capturar_cuarteto(evento_tipo, detalle):
    cuarteto = [j['n'] for j in s.js if j['p'] and j['n'] not in ["Serra", "Jose"]]
    while len(cuarteto) < 4: cuarteto.append("-")
    s.analisis_tactico.append({
        "Min": f"{mv:02d}:{sv:02d}", "Evento": evento_tipo, "Detalle": detalle,
        "Marcador": f"{s.ml}-{s.mr}", "P1": cuarteto[0], "P2": cuarteto[1], "P3": cuarteto[2], "P4": cuarteto[3]
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

# --- VISTA ---
tab1, tab2 = st.tabs(["🎮 PARTIDO", "📊 DATA TÁCTICA"])

with tab1:
    st.markdown(f'<div class="app-title-container"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="35"><div class="app-title-text">Match Control by Kike</div></div>', unsafe_allow_html=True)

    tm_sec = max(0, 60 - int(ah - s.tm_i)) if s.tm and s.tm_i else 0
    timer_display = f"{tm_sec}s" if s.tm else f"{mv:02d}:{sv:02d}"

    st.markdown(f"""
        <div class="scoreboard-container">
            <div style="text-align:center;"><div class="score-number">{s.ml}</div><div style="font-size:0.8rem; font-weight:900;">LEVANTE UD</div></div>
            <div class="stadium-clock" style="color: {'#FF0000' if rem <= 0 else '#FFFFFF'};">{timer_display}</div>
            <div style="text-align:center;"><div class="score-number">{s.mr}</div><div style="font-size:0.8rem; font-weight:900;">{s.rv[:8]}</div></div>
        </div>
        """, unsafe_allow_html=True)

    c_time = st.columns(3)
    for idx, col_key in enumerate(["tm_l", "tm_m", "tm_r"]):
        if c_time[idx].button("▶ START / STOP ⏸", key=col_key): toggle_timer(); st.rerun()

    c_goles = st.columns([1,1,1,1])
    with c_goles[0]:
        with st.popover("⚽ GOL LUD", use_container_width=True):
            p_gol = st.selectbox("Autor", [j['n'] for j in s.js], key="sb_gol_lud")
            if st.button("GOOOL!", key="btn_confirm_lud"): s.ml += 1; capturar_cuarteto("GOL LUD", p_gol); s.eventos.append({'min':min_act,'info':f'⚽{p_gol}'}); st.rerun()
    with c_goles[1]:
        with st.popover("⚽ GOL RIVAL", use_container_width=True):
            d_gol = st.number_input("Dorsal", 1, 99, key="ni_gol_riv")
            if st.button("GOL RIVAL", key="btn_confirm_riv"): s.mr += 1; capturar_cuarteto("GOL RIVAL", f"#{d_gol}"); s.eventos.append({'min':min_act,'info':f'⚽#{d_gol} RIV'}); st.rerun()
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
            st.markdown(f"<div style='font-size:0.8rem;'>{j['n']}</div><div style='font-size:1.1rem; font-weight:900;'>{mc:02d}:{vc:02d}</div><div style='font-size:0.6rem;'>Σ{mt:02d}:{vt:02d} | R:{j['r']}</div>", 1)
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
            if st.button("⏱️ TM LUD", key="bt_tml", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); capturar_cuarteto("TM LUD", "Iniciado"); st.rerun()
        with c_fl:
            st.button("F+", key="bt_flp", use_container_width=True, on_click=lambda: setattr(s, 'fl', s.fl+1))
            st.button("F-", key="bt_flm", use_container_width=True, on_click=lambda: setattr(s, 'fl', max(0, s.fl-1)))
            
    with f_m: 
        c_dis, c_gk = st.columns([1.1, 1])
        with c_dis: 
            st.markdown("<div style='text-align:center; font-size:0.75rem; font-weight:bold;'>TARJETAS</div>", unsafe_allow_html=True)
            col_d_l, col_d_r = st.columns(2)
            with col_d_l:
                with st.popover("L🟨", use_container_width=True):
                    p_y = st.selectbox("J", [j['n'] for j in s.js], key="sb_y_lud")
                    if st.button("OK 🟨", key="btn_ok_y_lud"): s.al+=1; capturar_cuarteto("🟨 LUD", p_y); s.eventos.append({'min':min_act,'info':f'🟨{p_y}'}); st.rerun()
                with st.popover("L🟥", use_container_width=True):
                    p_r = st.selectbox("J", [j['n'] for j in s.js], key="sb_r_lud")
                    if st.button("OK 🟥", key="btn_ok_r_lud"): s.rl+=1; capturar_cuarteto("🟥 LUD", p_r); s.eventos.append({'min':min_act,'info':f'🟥{p_r}'}); st.rerun()
            with col_d_r:
                with st.popover("R🟨", use_container_width=True):
                    d_y = st.number_input("D", 1, 99, key="ni_y_riv")
                    if st.button("OK 🟨", key="btn_ok_y_riv"): s.ar+=1; capturar_cuarteto("🟨 RIV", f"#{d_y}"); s.eventos.append({'min':min_act,'info':f'🟨#{d_y} RIV'}); st.rerun()
                with st.popover("R🟥", use_container_width=True):
                    d_r = st.number_input("D", 1, 99, key="ni_r_riv")
                    if st.button("OK 🟥", key="btn_ok_r_riv"): s.rr+=1; capturar_cuarteto("🟥 RIV", f"#{d_r}"); s.eventos.append({'min':min_act,'info':f'🟥#{d_r} RIV'}); st.rerun()

        with c_gk:
            st.markdown('<div class="gk-block-title">Saques</div>', unsafe_allow_html=True)
            st.markdown('<div class="gk-stat-total-v2">Mano 🧤</div>', unsafe_allow_html=True)
            c_m = st.columns(2)
            c_m[0].button(f"✅ ({s.pm_ok})", key="gk_m_ok", use_container_width=True, on_click=lambda: setattr(s, 'pm_ok', s.pm_ok+1))
            c_m[1].button(f"❌ ({s.pm_err})", key="gk_m_err", use_container_width=True, on_click=lambda: setattr(s, 'pm_err', s.pm_err+1))
            st.markdown('<div class="gk-stat-total-v2">Pie 👟</div>', unsafe_allow_html=True)
            c_p = st.columns(2)
            c_p[0].button(f"✅ ({s.pp_ok})", key="gk_p_ok", use_container_width=True, on_click=lambda: setattr(s, 'pp_ok', s.pp_ok+1))
            c_p[1].button(f"❌ ({s.pp_err})", key="gk_p_err", use_container_width=True, on_click=lambda: setattr(s, 'pp_err', s.pp_err+1))

    with f_r: 
        c_fr, c_tmr = st.columns([1, 1.5])
        with c_fr:
            st.button("F+", key="bt_frp", use_container_width=True, on_click=lambda: setattr(s, 'fr', s.fr+1))
            st.button("F-", key="bt_frm", use_container_width=True, on_click=lambda: setattr(s, 'fr', max(0, s.fr-1)))
        with c_tmr:
            if st.button("⏱️ TM RIVAL", key="bt_tmr", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); capturar_cuarteto("TM RIV", "Iniciado"); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("🧤 Análisis de Portería")
    def calc_perc(ok, err):
        total = ok + err
        return f"{(ok / total * 100):.1f}%" if total > 0 else "0.0%"
    col_stats_p1, col_stats_p2 = st.columns(2)
    with col_stats_p1: st.metric("🧤 Efectividad Saque MANO", calc_perc(s.pm_ok, s.pm_err), f"OK: {s.pm_ok} | X: {s.pm_err}")
    with col_stats_p2: st.metric("👟 Efectividad Saque PIE", calc_perc(s.pp_ok, s.pp_err), f"OK: {s.pp_ok} | X: {s.pp_err}")
    st.markdown("---")
    st.subheader("📋 Registro Táctico de Cuartetos")
    if s.analisis_tactico:
        df_tactica = pd.DataFrame(s.analisis_tactico)
        st.table(df_tactica)
        csv = df_tactica.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV Táctico", csv, "analisis_lud.csv", "text/csv")
