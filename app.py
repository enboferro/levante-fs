import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="LUD FS PRO", layout="wide")
st_autorefresh(interval=1000, key="futsal_refresh")

ss = st.session_state

# Estilos CSS básicos para evitar errores de renderizado
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .marcador-box { background: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .jugador-card { background: white; border-radius: 10px; padding: 10px; margin-bottom: 5px; border-left: 5px solid #ccc; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .pista-activa { border-left: 5px solid #003D7A !important; }
</style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE DATOS
if 'js' not in ss:
    nombres_fijos = [
        "Serra", "Julian", "Omar", "Tony", "Rochina",
        "Benages", "Pedrito", "Parre Jr", "Baeza", "Manu",
        "Pedro Toro", "Paco Silla", "Jose", "Coque", "Nacho Gomez"
    ]
    ss.js = []
    for i in range(15):
        ss.js.append({
            "n": nombres_fijos[i] if i < len(nombres_fijos) else f"J{i+1}",
            "t_total": 0.0, "ini": None, "p": False, "g": 0, "t": 0, "per": 0, "rec": 0
        })

if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'tiempo_acumulado' not in ss: ss.tiempo_acumulado = 0.0
if 'inicio_cronometro' not in ss: ss.inicio_cronometro = None
if 'corriendo' not in ss: ss.corriendo = False

# LÓGICA DEL TIEMPO
ahora = time.time()
tiempo_para_mostrar = ss.tiempo_acumulado
if ss.corriendo and ss.inicio_cronometro:
    tiempo_para_mostrar += ahora - ss.inicio_cronometro

# 3. CABECERA
col_esc, col_riv, col_reset = st.columns([1, 4, 1])
with col_esc:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=60)
with col_riv:
    rival_n = st.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()
with col_reset:
    if st.button("🔄 RESET"):
        for key in list(ss.keys()): del ss[key]
        st.rerun()

# 4. MARCADOR Y RELOJ
m1, m2, m3 = st.columns([2, 3, 2])

with m1:
    st.markdown(f"<div class='marcador-box'><h3>LUD</h3><h1 style='color:#003D7A;'>{ss.ml}</h1><p>Faltas: {ss.fl}</p></div>", unsafe_allow_html=True)
    if st.button("⚽ GOL LUD", use_container_width=True): 
        ss.ml += 1
        st.rerun()
    if st.button(f"⚠️ FALTA LUD (+1)", use_container_width=True):
        ss.fl += 1
        st.rerun()

with m2:
    mm, ss_val = divmod(int(tiempo_para_mostrar), 60)
    st.markdown(f"<div class='marcador-box'><h1 style='font-size:4rem;'>{mm:02d}:{ss_val:02d}</h1></div>", unsafe_allow_html=True)
    
    if not ss.corriendo:
        if st.button("▶ INICIAR TIEMPO", type="primary", use_container_width=True):
            ss.inicio_cronometro = ahora
            ss.corriendo = True
            for j in ss.js:
                if j["p"]: j["ini"] = ahora
            st.rerun()
    else:
        if st.button("⏸ PAUSAR TIEMPO", type="secondary", use_container_width=True):
            ss.tiempo_acumulado += ahora - ss.inicio_cronometro
            ss.corriendo = False
            for j in ss.js:
                if j["p"] and j["ini"]:
                    j["t_total"] += ahora - j["ini"]
                    j["ini"] = None
            ss.inicio_cronometro = None
            st.rerun()

with m3:
    st.markdown(f"<div class='marcador-box'><h3>{rival_n[:6]}</h3><h1 style='color:#7A0019;'>{ss.mr}</h1><p>Faltas: {ss.fr}</p></div>", unsafe_allow_html=True)
    if st.button(f"⚽ GOL {rival_n[:3]}", use_container_width=True): 
        ss.mr += 1
        st.rerun()
    if st.button(f"⚠️ FALTA {rival_n[:3]} (+1)", use_container_width=True):
        ss.fr += 1
        st.rerun()

# 5. LISTA DE JUGADORES (3 COLUMNAS)
st.divider()
en_pista = sum(1 for j in ss.js if j["p"])
st.markdown(f"<center><b>PISTA: {en_pista}/5</b></center>", unsafe_allow_html=True)

cols = st.columns(3)
for i, j in enumerate(ss.js):
    with cols[i % 3]:
        clase_pista = "pista-activa" if j["p"] else ""
        st.markdown(f"<div class='jugador-card {clase_pista}'>", unsafe_allow_html=True)
        
        c_nom, c_reloj = st.columns([2, 1])
        j["n"] = c_nom.text_input(f"n_{i}", j["n"], key=f"input_{i}", label_visibility="collapsed")
        
        # Tiempo individual
        t_jug = j["t_total"]
        if ss.corriendo and j["p"] and j["ini"]:
            t_jug += ahora - j["ini"]
        mj, sj = divmod(int(t_jug), 60)
        
        color_t = "#2b8a3e" if j["p"] else "#a61e4d"
        icono = "🟢" if j["p"] else "🔴"
        c_reloj.markdown(f"<span style='color:{color_t}; font-weight:bold;'>{icono} {mj:02d}:{sj:02d}</span>", unsafe_allow_html=True)
        
        # Acciones
        s1, s2, s3, s4 = st.columns(4)
        if s1.button("🎯", key=f"t_{i}"): j["t"] += 1
        if s2.button("🛡️", key=f"r_{i}"): j["rec"] += 1
        if s3.button("❌", key=f"p_{i}"): j["per"] += 1
        if s4.button("⚽", key=f"g_{i}"): 
            j["g"] += 1
            ss.ml += 1
            st.rerun()
        
        # Botón cambio
        label_btn = "BANCO" if j["p"] else "ENTRAR PISTA"
        if st.button(label_btn, key=f"ch_{i}", use_container_width=True):
            if not j["p"] and en_pista < 5:
                j["p"] = True
                if ss.corriendo: j["ini"] = ahora
            elif j["p"]:
                if ss.corriendo and j["ini"]:
                    j["t_total"] += ahora - j["ini"]
                j["p"], j["ini"] = False, None
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# 6. EXPORTAR
st.divider()
if st.button("💾 DESCARGAR INFORME"):
    df = pd.DataFrame([{"Jugador":x["n"],"Goles":x["g"],"Tiros":x["t"],"Robos":x["rec"],"Perdidas
