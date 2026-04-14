import streamlit as st
import pandas as pd
import time
import io
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD Match Control v27.5", layout="wide")

# --- CSS MEJORADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; background-color: #f0f2f6; }
    .block-container { padding: 0.1rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #4B2E2A; color: white; border-radius: 10px 10px 0 0; padding: 10px 20px; }
    
    .scoreboard-container {
        display: flex; align-items: center; justify-content: space-around;
        background: #4B2E2A; padding: 5px; border-radius: 15px 15px 0 0;
        color: white; border-bottom: 2px solid rgba(255,255,255,0.1);
    }
    .fouls-bar {
        display: flex; justify-content: space-around; background: #000000; 
        color: #ffcc00; padding: 5px; border-radius: 0 0 15px 15px; 
        font-weight: 900; font-size: 1.2rem; margin-bottom: 10px;
        border-bottom: 4px solid #4B2E2A;
    }
    .score-number { font-size: 3.5rem !important; font-weight: 900; font-family: 'Roboto Mono'; line-height: 1; }
    .stadium-clock { font-family: 'Roboto Mono'; font-size: 4rem !important; font-weight: 700; text-align: center; line-height: 1; }
    
    .player-name { font-size: 1.15rem !important; font-weight: 900 !important; color: #4B2E2A !important; text-transform: uppercase; margin-bottom: 2px; }

    .pista-portero { background-color: #008080 !important; color: white; border-radius: 8px; padding: 10px 2px; text-align: center; font-weight: 900; border: 2px solid white; min-height: 115px; }
    .pista-verde { background-color: #00FF41 !important; color: #000; border-radius: 8px; padding: 5px 2px; text-align: center; font-weight: 900; min-height: 115px; }
    .pista-naranja { background-color: #FF5E00 !important; color: white !important; border-radius: 8px; padding: 5px 2px; text-align: center; font-weight: 900; border: 1px solid white; min-height: 115px; }
    .pista-roja { background-color: #FF0000 !important; color: white !important; border-radius: 8px; padding: 5px 2px; text-align: center; font-weight: 900; border: 2px solid #FFFF00; animation: blinker 0.8s linear infinite; min-height: 115px; }
    .banquillo { background-color: #D1D1D1 !important; color: #4B2E2A !important; border-radius: 8px; padding: 10px 2px; text-align: center; border: 1px solid #999; min-height: 115px; }

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
        "analisis_goles": [], "periodo": "1ª PARTE", "finalizado": False
    })

s = st.session_state
st_autorefresh(1000, key="f5_lud_v27_5")

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
            t_rot = j["tt"] + (ah - j["i"] if s.on and j["i"] else 0)
            mj, sj = divmod(int(t_rot), 60)
            cuarteto.append(f"{j['n']} ({mj:02d}:{sj:02d})")
    while len(cuarteto) < 4: cuarteto.append("-")
    s.analisis_goles.append({
        "Periodo": s.periodo, "Tiempo": f"{mv:02d}:{sv:02d}", "Tipo": tipo, "Detalle": detalle,
        "Marcador": f"{s.ml}-{s.mr}", "P1": cuarteto[0], "P2": cuarteto[1], "P3": cuarteto[2], "P4": cuarteto[3]
    })

# --- UI ---
t1, t2, t3, t4 = st.tabs(["🎮 PARTIDO", "📜 HISTORIAL", "⚽ GOLES", "📊 EXCEL"])

with t1:
    st.markdown(f'<div style="text-align:center; padding:5px;"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png" width="30"><span style="font-size:1.1rem; font-weight:900; color:#4B2E2A; margin-left:10px;">MATCH CONTROL BY KIKE - {s.periodo}</span></div>', unsafe_allow_html=True)
    
    timer_display = f"{max(0, 60 - int(ah - s.tm_i))}s" if s.tm else f"{mv:02d}:{sv:02d}"
    st.markdown(f"""
        <div class="scoreboard-container">
            <div style="text-align:center;"><div class="score-number">{s.ml}</div><div style="font-size:0.7rem; font-weight:900;">LUD</div></div>
            <div class="stadium-clock" style="color: {'#FF0000' if rem <= 0 else '#FFFFFF'};">{timer_display}</div>
            <div style="text-align:center;"><div class="score-number">{s.mr}</div><div style="font-size:0.7rem; font-weight:900;">{s.rv[:5]}</div></div>
        </div>
        <div class="fouls-bar">FALTAS: {s.fl} | RIVAL: {s.fr}</div>
    """, unsafe_allow_html=True)

    c_c = st.columns([2, 1])
    if c_c[0].button("▶ START / STOP ⏸", key="main_btn", use_container_width=True, disabled=s.finalizado): toggle_timer(); st.rerun()
    if c_c[1].button("🏁 FIN", key="end_btn", use_container_width=True, disabled=s.finalizado): finalizar_fase()

    c_g = st.columns(4)
    with c_g[0]:
        with st.popover("⚽ LUD", use_container_width=True):
            p = st.selectbox("Autor", [x['n'] for x in s.js], key="gl")
            if st.button("OK GOL"): s.ml+=1; capturar_tactico("GOL LUD", p); s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL LUD ({p})'}); st.rerun()
    with c_g[1]:
        with st.popover("⚽ RIV", use_container_width=True):
            d = st.number_input("Dorsal", 1, 99, key="gr")
            if st.button("OK RIV"): s.mr+=1; capturar_tactico("GOL RIV", f"#{d}"); s.eventos.append({'Tiempo':min_act,'Evento':f'⚽ GOL RIV (#{d})'}); st.rerun()
    with c_g[2]: s.rv = st.text_input("RIVAL", s.rv, label_visibility="collapsed").upper()
    with c_g[3]: 
        if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

    st.markdown("---")
    cols = st.columns(6)
    for i, j in enumerate(s.js):
        with cols[i%6]:
            es_portero = j['n'] in ["Serra", "Jose"]
            if not j['p']: cl = "banquillo"
            elif es_portero: cl = "pista-portero"
            else:
                cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
                cl = "pista-verde" if cur < 240 else ("pista-naranja" if cur < 360 else "pista-roja")
            
            st.markdown(f"<div class='{cl}'><span class='player-name'>{j['n']}</span>", unsafe_allow_html=True)
            if not es_portero:
                cur = j["tt"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
                tot = j["tot"] + (ah-j["i"] if s.on and j["p"] and j["i"] else 0)
                st.markdown(f"<div style='font-size:1.1rem; font-weight:900;'>{int(cur//60):02d}:{int(cur%60):02d}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:0.75rem; font-weight:700;'>Σ {int(tot//60):02d}:{int(tot%60):02d} | R:{j['r']}</div>", unsafe_allow_html=True)
            
            if st.button("🔄", key=f"bt_{i}", use_container_width=True, disabled=s.finalizado):
                if not j["p"]:
                    j["p"] = True
                    if not es_portero: j["i"], j["r"], j["tt"] = (ah if s.on else None), j["r"]+1, 0.0
                else:
                    if not es_portero and s.on and j["i"]: d_time = ah - j["i"]; j["tot"] += d_time; j["tt"] += d_time
                    j["p"], j["i"] = False, None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-control'>", unsafe_allow_html=True)
    f_l, f_m, f_r = st.columns([2, 4, 2])
    with f_l:
        if st.button("⏱️ TM LUD", key="tml", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); s.eventos.append({'Tiempo':min_act,'Evento':'⏱️ TM LUD'}); st.rerun()
        c_f = st.columns(2); c_f[0].button("F+", key="flp", on_click=lambda: setattr(s, 'fl', s.fl+1)); c_f[1].button("F-", key="flm", on_click=lambda: setattr(s, 'fl', max(0, s.fl-1)))
    with f_m:
        c_p = st.columns(4)
        with c_p[0]:
            with st.popover("LUD 🟨🟥"):
                py = st.selectbox("J", [x['n'] for x in s.js], key="sy")
                if st.button("AMARILLA", key="aly"): s.al+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟨 LUD ({py})'}); st.rerun()
                if st.button("ROJA", key="alr"): s.rl+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟥 LUD ({py})'}); st.rerun()
        with c_p[1]:
            with st.popover("RIV 🟨🟥"):
                dy = st.number_input("D", 1, 99, key="ny")
                if st.button("AMARILLA ", key="ary"): s.ar+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟨 RIV (#{dy})'}); st.rerun()
                if st.button("ROJA ", key="arr"): s.rr+=1; s.eventos.append({'Tiempo':min_act,'Evento':f'🟥 RIV (#{dy})'}); st.rerun()
        with c_p[2]:
            st.button(f"✅🧤({s.pm_ok})", key="mok", on_click=lambda: setattr(s, 'pm_ok', s.pm_ok+1)); st.button(f"❌🧤({s.pm_err})", key="mer", on_click=lambda: setattr(s, 'pm_err', s.pm_err+1))
        with c_p[3]:
            st.button(f"✅👟({s.pp_ok})", key="pok", on_click=lambda: setattr(s, 'pp_ok', s.pp_ok+1)); st.button(f"❌👟({s.pp_err})", key="per", on_click=lambda: setattr(s, 'pp_err', s.pp_err+1))
    with f_r:
        if st.button("⏱️ TM RIV", key="tmr", use_container_width=True): toggle_timer(); s.tm, s.tm_i = True, time.time(); s.eventos.append({'Tiempo':min_act,'Evento':'⏱️ TM RIVAL'}); st.rerun()
        c_f2 = st.columns(2); c_f2[0].button("F+ RIV", key="frp", on_click=lambda: setattr(s, 'fr', s.fr+1)); c_f2[1].button("F- RIV", key="frm", on_click=lambda: setattr(s, 'fr', max(0, s.fr-1)))
    st.markdown("</div>", unsafe_allow_html=True)

with t2: st.table(pd.DataFrame(s.eventos)) if s.eventos else st.info("Vacio")
with t3: st.table(pd.DataFrame(s.analisis_goles)) if s.analisis_goles else st.info("Vacio")
with t4:
    def p_calc(o, e): t=o+e; return f"{(o/t*100):.1f}%" if t>0 else "0.0%"
    st.subheader("Portería")
    st.write(f"🧤 Mano: {p_calc(s.pm_ok, s.pm_err)} | 👟 Pie: {p_calc(s.pp_ok, s.pp_err)}")
    st.markdown("---")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        pd.DataFrame({"Métrica": ["Goles LUD", "Goles RIV", "Faltas LUD", "Faltas RIV"], "Val": [s.ml, s.mr, s.fl, s.fr]}).to_excel(writer, sheet_name='Resumen', index=False)
        if s.eventos: pd.DataFrame(s.eventos).to_excel(writer, sheet_name='Historial', index=False)
        if s.analisis_goles: pd.DataFrame(s.analisis_goles).to_excel(writer, sheet_name='Goles', index=False)
        data_j = [{"Jugador": x["n"], "Total Min": f"{int((x['tot']+(ah-x['i'] if s.on and x['p'] and x['i'] else 0))//60):02d}:{int((x['tot']+(ah-x['i'] if s.on and x['p'] and x['i'] else 0))%60):02d}", "R": x["r"]} for x in s.js if x["n"] not in ["Serra", "Jose"]]
        pd.DataFrame(data_j).to_excel(writer, sheet_name='Jugadores', index=False)
    st.download_button(label="📥 DESCARGAR EXCEL", data=buf.getvalue(), file_name=f"LUD_{s.rv}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
