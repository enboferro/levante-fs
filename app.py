import st as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN E INTERFAZ
st.set_page_config(page_title="LUD Match Center", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .marcador-container {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;
    }
    .jugador-card {
        background: white; border-radius: 10px; padding: 10px;
        margin-bottom: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE ESTADO
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"J{i+1}","t_total":0.0,"ini":None,"p":False,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'tiempo_acumulado' not in ss: ss.tiempo_acumulado = 0.0
if 'inicio_cronometro' not in ss: ss.inicio_cronometro = None
if 'corriendo' not in ss: ss.corriendo = False

# LÓGICA DEL RELOJ
tiempo_display = ss.tiempo_acumulado
if ss.corriendo and ss.inicio_cronometro:
    tiempo_display += time.time() - ss.inicio_cronometro

# 3. CABECERA
h1, h2, h3 = st.columns([1, 4, 1])
h1.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=60)
with h2:
    r_nom = st.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()
if h3.button("RESET TOTAL"):
    ss.clear()
    st.rerun()

# 4. MARCADOR Y CONTROL DE TIEMPO
m1, m2, m3 = st.columns([1, 1.5, 1])

with m1:
    st.markdown(f"<h2 style='text-align:center; color:#003D7A;'>LUD: {ss.ml}</h2>", unsafe_allow_html=True)
    if st.button("⚽ GOL LUD", key="btn_gol_l"): ss.ml += 1; st.rerun()
    if st.button(f"⚠️ FALTAS: {ss.fl}", key="btn_fal_l"): ss.fl += 1; st.rerun()

with m2:
    mm, ss_proc = divmod(int(tiempo_display), 60)
    st.markdown(f"<div class='marcador-container'><h1 style='font-size:4rem; margin:0;'>{mm:02d}:{ss_proc:02d}</h1></div>", unsafe_allow_html=True)
    
    col_play, col_pause = st.columns(2)
    if not ss.corriendo:
        if col_play.button("▶ INICIAR", type="primary", use_container_width=True):
            ss.inicio_cronometro = time.time()
            ss.corriendo = True
            for j in ss.js:
                if j["p"]: j["ini"] = time.time()
            st.rerun()
    else:
        if col_pause.button("⏸ PAUSAR", type="secondary", use_container_width=True):
            ss.tiempo_acumulado += time.time() - ss.inicio_cronometro
            ss.corriendo = False
            for j in ss.js:
                if j["p"] and j["ini"]:
                    j["t_total"] += time.time() - j["ini"]
                    j["ini"] = None
            st.rerun()

with m3:
    # LÍNEA CORREGIDA AQUÍ ABAJO (Línea 84 aprox.)
    st.markdown(f"<h2 style='text-align:center; color:#7A0019;'>{r_nom[:6]}: {ss.mr}</h2>", unsafe_allow_html=True)
    if st.button(f"⚽ GOL {r_nom[:3]}", key="btn_gol_r"): ss.mr += 1; st.rerun()
    if st.button(f"⚠️ FALTAS: {ss.fr}", key="btn_fal_r"): ss.fr += 1; st.rerun()

# 5. JUGADORES (Layout 3 columnas)
st.divider()
ep = sum(1 for j in ss.js if j["p"])
st.markdown(f"<div style='text-align:center;'><b>👥 EN PISTA: {ep}/5</b></div>", unsafe_allow_html=True)

cols = st.columns(3)
for i, j in enumerate(ss.js):
    with cols[i % 3]:
        color_borde = "#003D7A" if j["p"] else "#ccc"
        st.markdown(f"<div class='jugador-card' style='border-left: 5px solid {color_borde};'>", unsafe_allow_html=True)
        
        c_n, c_t = st.columns([2, 1])
        j["n"] = c_n.text_input(f"n{i}", j["n"], key=f"n{i}", label_visibility="collapsed")
        
        t_ind = j["t_total"]
        if ss.corriendo and j["p"] and j["ini"]:
            t_ind += time.time() - j["ini"]
        mj, sj = divmod(int(t_ind), 60)
        c_t.markdown(f"<div style='text-align:right;'>{mj:02d}:{sj:02d}</div>", unsafe_allow_html=True)
        
        # Scouting e Interruptor de Pista
        s1, s2, s3, s4, s5 = st.columns([1,1,1,1,1.5])
        if s1.button("🎯", key=f"tiro{i}"): j["t"]+=1
        if s2.button("🛡️", key=f"robo{i}"): j["rec"]+=1
        if s3.button("❌", key=f"perd{i}"): j["per"]+=1
        if s4.button("⚽", key=f"golj{i}"): j["g"]+=1; ss.ml+=1; st.rerun()
        
        btn_label = "BANCO" if j["p"] else "PISTA"
        if s5.button(btn_label, key=f"bt{i}"):
            if not j["p"] and ep < 5:
                j["p"] = True
                if ss.corriendo: j["ini"] = time.time()
            elif j["p"]:
                if ss.corriendo and j["ini"]:
                    j["t_total"] += time.time() - j["ini"]
                j["p"], j["ini"] = False, None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# 6. EXPORTAR
st.write("")
if st.button("💾 GENERAR INFORME CSV", use_container_width=True):
    df = pd.DataFrame([{"Jugador":x["n"],"Goles":x["g"],"Tiros":x["t"],"Robos":x["rec"],"Perdidas":x["per"],"Min":round(x["t_total"]/60,1)} for x in ss.js])
    st.download_button("Descargar Archivo", df.to_csv(index=False).encode('utf-8'), f"LUD_{r_nom}.csv", "text/csv")
