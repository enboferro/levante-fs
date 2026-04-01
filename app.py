import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Configuración de página
st.set_page_config(page_title="LUD FS - PRO Match Center", layout="wide", page_icon="🐸")

# Autorefresh cada 1 segundo para el cronómetro y posesión
st_autorefresh(interval=1000, key="futsalrefresh")

ss = st.session_state

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .reloj-box { background-color: #1E1E1E; border: 4px solid #7A0019; border-radius: 25px; padding: 15px; }
    .stButton>button { border-radius: 10px; font-weight: bold; transition: all 0.3s; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .bonus-alert { background-color: #FF0000 !important; animation: blink 1s infinite; }
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

# --- BARRA LATERAL: DATOS DEL PARTIDO ---
st.sidebar.header("📋 Datos del Encuentro")
nombre_rival = st.sidebar.text_input("Nombre del Rival", "RIVAL")
fecha_partido = st.sidebar.date_input("Fecha del Partido", datetime.now())
lugar_partido = st.sidebar.text_input("Pabellón", "Local/Visitante")

# 3. LÓGICA DE CÁLCULO DE POSESIÓN
now = time.time()
if ss.ac and ss.last_pos_check:
    diff = now - ss.last_pos_check
    if ss.pos_activa == "LUD": ss.t_pos_lud += diff
    elif ss.pos_activa == "RIVAL": ss.t_pos_riv += diff
    else: ss.t_pos_neu += diff
ss.last_pos_check = now

# 4. CABECERA DINÁMICA
col_esc, col_tit, col_res = st.columns([1, 4, 1])
with col_esc:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=80)
with col_tit:
    st.title(f"LEVANTE UD vs {nombre_rival.upper()}")
    st.caption(f"📅 {fecha_partido.strftime('%d/%m/%Y')} | 🏟️ {lugar_partido}")
with col_res:
    if st.button("🔄 RESET TOTAL"): 
        ss.clear()
        st.rerun()

# 5. MARCADOR Y RELOJ
m_col1, m_col2, m_col3 = st.columns([2, 2, 2])

with m_col1:
    bg_lud = "background:#FF0000;" if ss.fl >= 5 else "background:#003D7A;"
    st.markdown(f"<div style='text-align:center; {bg_lud} padding:15px; border-radius:15px; color:white;'> <h2 style='color:white !important; margin:0;'>LUD: {ss.ml}</h2><small>FALTAS: {ss.fl}</small></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("⚽ GOL LUD", key="g_l_main", use_container_width=True): ss.ml+=1; st.rerun()
    if c2.button("⚠️ FALTA L", key="f_l_main", use_container_width=True): ss.fl+=1; st.rerun()

with m_col2:
    tg = ss.rt1 if ss.pt=="T1" else ss.rt2
    if ss.ac and ss.ig: tg += now - ss.ig
    m, s = divmod(int(tg), 60)
    st.markdown(f"<div class='reloj-box'><h1 style='text-align:center; color:white; margin:0;'>{m:02d}:{s:02d}</h1></div>", unsafe_allow_html=True)
    
    if not ss.ac:
        if st.button("▶ EMPEZAR", type="primary", key="btn_start", use_container_width=True):
            ss.ac, ss.ig = True, now
            for j in ss.js:
                if j["p"]: j["ini"] = now
            st.rerun()
    else:
        if st.button("⏸ PARAR", type="secondary", key="btn_stop", use_container_width=True):
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
    bg_riv = "background:#FF0000;" if ss.fr >= 5 else "background:#7A0019;"
    st.markdown(f"<div style='text-align:center; {bg_riv} padding:15px; border-radius:15px; color:white;'><h2 style='color:white !important; margin:0;'>{nombre_rival.upper()}: {ss.mr}</h2><small>FALTAS: {ss.fr}</small></div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    if c3.button(f"⚽ GOL R", key="g_r_main", use_container_width=True): ss.mr+=1; st.rerun()
    if c4.button(f"⚠️ FALTA R", key="f_r_main", use_container_width=True): ss.fr+=1; st.rerun()

# 6. CONTROL DE POSESIÓN
st.divider()
st.subheader("🎮 Control de Posesión")
p1, p2, p3 = st.columns(3)
with p1:
    if st.button(f"🔵 LUD", key="pos_lud", use_container_width=True, type="primary" if ss.pos_activa=="LUD" else "secondary"):
        ss.pos_activa = "LUD"; st.rerun()
with p2:
    if st.button(f"⚪ NEUTRAL", key="pos_neu", use_container_width=True, type="primary" if ss.pos_activa=="NEUTRAL" else "secondary"):
        ss.pos_activa = "NEUTRAL"; st.rerun()
with p3:
    if st.button(f"🔴 {nombre_rival.upper()}", key="pos_riv", use_container_width=True, type="primary" if ss.pos_activa=="RIVAL" else "secondary"):
        ss.pos_activa = "RIVAL"; st.rerun()

total_p = ss.t_pos_lud + ss.t_pos_riv + 0.001
per_lud = (ss.t_pos_lud / total_p) * 100
st.progress(per_lud / 100, text=f"Posesión: LUD {int(per_lud)}% - {nombre_rival} {int(100-per_lud)}%")

# 7. PISTA Y JUGADORES
st.divider()
ep = sum(1 for j in ss.js if j["p"])
st.subheader(f"👥 En Pista: {ep}/5")

for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        if ji >= 14: break
        j = ss.js[ji]
        with col:
            with st.container():
                st.markdown(f"<div style='background:white; padding:10px; border-radius:10px; border-left: 5px solid {'#003D7A' if j['p'] else '#ccc'};'>", unsafe_allow_html=True)
                c_n, c_t = st.columns([2, 1])
                j["n"] = c_n.text_input(f"J{ji}", j["n"], key=f"n{ji}", label_visibility="collapsed")
                tj = j["t1"] + j["t2"]
                if ss.ac and j["p"] and j["ini"]: tj += now - j["ini"]
                mm, ss_j = divmod(int(tj), 60)
                c_t.write(f"⏱️ {mm:02d}:{ss_j:02d}")
                
                s1, s2, s3, s4, s5 = st.columns(5)
                if s1.button(f"🎯", key=f"t{ji}"): j["t"]+=1; st.rerun()
                if s2.button(f"⚠️", key=f"p{ji}"): j["per"]+=1; st.rerun()
                if s3.button(f"🛡️", key=f"r{ji}"): j["rec"]+=1; st.rerun()
                if s4.button(f"⚽", key=f"g{ji}"): j["g"]+=1; ss.ml+=1; st.rerun()
                txt = "🔴" if j["p"] else "🟢"
                if s5.button(txt, key=f"en{ji}"):
                    if not j["p"] and ep < 5:
                        j["p"], j["e"] = True, j["e"]+1
                        if ss.ac: j["ini"] = now
                    elif j["p"]:
                        if ss.ac and j["ini"]:
                            if ss.pt=="T1": j["t1"] += now - j["ini"]
                            else: j["t2"] += now - j["ini"]
                        j["p"], j["ini"] = False, None
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# 8. EXPORTACIÓN
st.divider()
df = pd.DataFrame([{"Jugador":x["n"],"Min":round((x["t1"]+x["t2"])/60,1),"Goles":x["g"],"Tiros":x["t"],"Pérdidas":x["per"],"Recup":x["rec"]} for x in ss.js])
df['Rival'] = nombre_rival
df['Fecha'] = fecha_partido

if st.button("💾 DESCARGAR DATOS PARTIDO", key="btn_download", use_container_width=True):
    nombre_archivo = f"Stats_{nombre_rival}_{fecha_partido.strftime('%Y%m%d')}.csv"
    st.download_button("Confirmar Descarga", df.to_csv(index=False).encode('utf-8'), nombre_archivo, "text/csv")
