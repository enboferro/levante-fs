import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Configuración de página
st.set_page_config(page_title="LUD FS - ANALYTICS PRO", layout="wide", page_icon="🐸")

# Autorefresh cada 1 segundo
st_autorefresh(interval=1000, key="futsalrefresh")

ss = st.session_state

# --- ESTILOS CSS PARA DISEÑO "GRANDE" ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    .header-box { background: linear-gradient(90deg, #003D7A, #7A0019); padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px; }
    .reloj-box { background-color: #1E1E1E; border: 5px solid #FFD700; border-radius: 30px; padding: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.4); }
    .reloj-text { color: white; font-size: 5rem !important; font-weight: bold; margin: 0; text-align: center; }
    .marcador-card { padding: 20px; border-radius: 20px; color: white; text-align: center; box-shadow: 0px 5px 15px rgba(0,0,0,0.2); }
    .stButton>button { height: 3.5rem; font-size: 1.2rem !important; border-radius: 12px; font-weight: bold; }
    h2 { font-size: 2.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"Jugador {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt = 0.0, 0.0, "T1"
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig = False, None
if 'pos_activa' not in ss: ss.pos_activa = "NEUTRAL"
if 't_pos_lud' not in ss: ss.t_pos_lud = 0.0
if 't_pos_riv' not in ss: ss.t_pos_riv = 0.0
if 't_pos_neu' not in ss: ss.t_pos_neu = 0.0
if 'last_pos_check' not in ss: ss.last_pos_check = None

# --- SECCIÓN SUPERIOR: DATOS INTEGRADOS ---
with st.container():
    c_logo, c_info, c_reset = st.columns([1, 4, 1])
    with c_logo:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=100)
    with c_info:
        col1, col2 = st.columns(2)
        rival = col1.text_input("NOMBRE DEL RIVAL", "RIVAL", label_visibility="collapsed").upper()
        fecha = col2.date_input("FECHA", datetime.now(), label_visibility="collapsed")
        st.markdown(f"<div class='header-box'><h1>LEVANTE UD vs {rival}</h1></div>", unsafe_allow_html=True)
    with c_reset:
        if st.button("⚠️ RESET TOTAL", use_container_width=True):
            ss.clear()
            st.rerun()

# 3. LÓGICA DE POSESIÓN
now = time.time()
if ss.ac and ss.last_pos_check:
    diff = now - ss.last_pos_check
    if ss.pos_activa == "LUD": ss.t_pos_lud += diff
    elif ss.pos_activa == "RIVAL": ss.t_pos_riv += diff
    else: ss.t_pos_neu += diff
ss.last_pos_check = now

# 4. MARCADOR PRINCIPAL (GIGANTE)
m_col1, m_col2, m_col3 = st.columns([2, 3, 2])

with m_col1:
    bg_lud = "background-color:#FF0000;" if ss.fl >= 5 else "background-color:#003D7A;"
    st.markdown(f"<div class='marcador-card' style='{bg_lud}'><h2>LUD</h2><h1 style='font-size:6rem; color:white;'>{ss.ml}</h1><p>FALTAS: {ss.fl}</p></div>", unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns(2)
    if c1.button("⚽ GOL", key="g_l", use_container_width=True): ss.ml+=1; st.rerun()
    if c2.button("⚠️ FALTA", key="f_l", use_container_width=True): ss.fl+=1; st.rerun()

with m_col2:
    tg = ss.rt1 if ss.pt=="T1" else ss.rt2
    if ss.ac and ss.ig: tg += now - ss.ig
    m, s = divmod(int(tg), 60)
    st.markdown(f"<div class='reloj-box'><p class='reloj-text'>{m:02d}:{s:02d}</p></div>", unsafe_allow_html=True)
    st.write("")
    if not ss.ac:
        if st.button("▶ INICIAR CRONÓMETRO", type="primary", use_container_width=True):
            ss.ac, ss.ig = True, now
            for j in ss.js:
                if j["p"]: j["ini"] = now
            st.rerun()
    else:
        if st.button("⏸ PARAR CRONÓMETRO", type="secondary", use_container_width=True):
            ss.ac = False
            if ss.pt=="T1": ss.rt1 += now - ss.ig
            else: ss.rt2 += now - ss.ig
            for j in ss.js:
                if j["p"] and j["ini"]:
                    if ss.pt=="T1": j["t1"] += now - j["ini"]
                    else: j["t2"] += now - j["ini"]
                    j["ini"] = None
            ss.ig = None; st.rerun()

with m_col3:
    bg_riv = "background-color:#FF0000;" if ss.fr >= 5 else "background-color:#7A0019;"
    st.markdown(f"<div class='marcador-card' style='{bg_riv}'><h2>{rival[:5]}</h2><h1 style='font-size:6rem; color:white;'>{ss.mr}</h1><p>FALTAS: {ss.fr}</p></div>", unsafe_allow_html=True)
    st.write("")
    c3, c4 = st.columns(2)
    if c3.button("⚽ GOL ", key="g_r", use_container_width=True): ss.mr+=1; st.rerun()
    if c4.button("⚠️ FALTA ", key="f_r", use_container_width=True): ss.fr+=1; st.rerun()

# 5. POSESIÓN (BOTONES GRANDES)
st.divider()
p1, p2, p3 = st.columns(3)
with p1:
    if st.button(f"🔵 POSESIÓN LUD", key="p_lud", use_container_width=True, type="primary" if ss.pos_activa=="LUD" else "secondary"):
        ss.pos_activa = "LUD"; st.rerun()
with p2:
    if st.button(f"⚪ NEUTRAL", key="p_neu", use_container_width=True, type="primary" if ss.pos_activa=="NEUTRAL" else "secondary"):
        ss.pos_activa = "NEUTRAL"; st.rerun()
with p3:
    if st.button(f"🔴 POSESIÓN {rival}", key="p_riv", use_container_width=True, type="primary" if ss.pos_activa=="RIVAL" else "secondary"):
        ss.pos_activa = "RIVAL"; st.rerun()

total_p = ss.t_pos_lud + ss.t_pos_riv + 0.001
per_lud = (ss.t_pos_lud / total_p) * 100
st.progress(per_lud / 100, text=f"POSESIÓN: LUD {int(per_lud)}% | {rival} {int(100-per_lud)}%")

# 6. JUGADORES (Tarjetas más limpias)
st.divider()
st.subheader(f"🏃 JUGADORES EN PISTA: {sum(1 for j in ss.js if j['p'])}/5")
for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        if ji >= 14: break
        j = ss.js[ji]
        with col:
            st.markdown(f"<div style='background:white; padding:15px; border-radius:15px; border-left: 10px solid {'#003D7A' if j['p'] else '#D3D3D3'}; box-shadow: 0px 2px 5px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
            c_n, c_t, c_btn = st.columns([2, 1, 1])
            j["n"] = c_n.text_input(f"Nombre J{ji}", j["n"], key=f"n{ji}", label_visibility="collapsed")
            tj = j["t1"] + j["t2"]
            if ss.ac and j["p"] and j["ini"]: tj += now - j["ini"]
            mm, ss_j = divmod(int(tj), 60)
            c_t.markdown(f"### {mm:02d}:{ss_j:02d}")
            if c_btn.button("🔴" if j["p"] else "🟢", key=f"en{ji}", use_container_width=True):
                if not j["p"] and sum(1 for x in ss.js if x["p"]) < 5:
                    j["p"], j["e"] = True, j["e"]+1
                    if ss.ac: j["ini"] = now
                elif j["p"]:
                    if ss.ac and j["ini"]:
                        if ss.pt=="T1": j["t1"] += now - j["ini"]
                        else: j["t2"] += now - j["ini"]
                    j["p"], j["ini"] = False, None
                st.rerun()
            
            s1, s2, s3, s4 = st.columns(4)
            if s1.button(f"🎯 {j['t']}", key=f"t{ji}", use_container_width=True): j["t"]+=1; st.rerun()
            if s2.button(f"⚠️ {j['per']}", key=f"p{ji}", use_container_width=True): j["per"]+=1; st.rerun()
            if s3.button(f"🛡️ {j['rec']}", key=f"r{ji}", use_container_width=True): j["rec"]+=1; st.rerun()
            if s4.button(f"⚽ {j['g']}", key=f"g{ji}", use_container_width=True): j["g"]+=1; ss.ml+=1; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# 7. EXPORTACIÓN
st.divider()
if st.button("💾 DESCARGAR INFORME DEL PARTIDO", use_container_width=True):
    df = pd.DataFrame([{"Jugador":x["n"],"Min":round((x["t1"]+x["t2"])/60,1),"Goles":x["g"],"Tiros":x["t"],"Pérdidas":x["per"],"Recup":x["rec"]} for x in ss.js])
    st.download_button("CONFIRMAR DESCARGA CSV", df.to_csv(index=False).encode('utf-8'), f"LUD_vs_{rival}_{fecha}.csv", "text/csv
