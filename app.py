import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD FS PRO", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state

# --- CSS ULTRA COMPACTO ---
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    h1, h2, h3 {margin-bottom: 0rem; padding: 0px;}
    div[data-testid="stVerticalBlock"] > div {margin-bottom: -0.5rem;}
    .stButton>button {height: 2rem; font-size: 0.8rem !important; margin-bottom: 2px;}
    .jugador-box {
        background: white; 
        border: 1px solid #ddd; 
        border-radius: 5px; 
        padding: 5px; 
        margin-bottom: 2px;
    }
    input {height: 1.5rem !important;}
    </style>
    """, unsafe_allow_html=True)

# 1. INICIALIZACIÓN
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss:
    ss.rt1, ss.rt2, ss.pt, ss.ml, ss.mr, ss.fl, ss.fr = 0.0, 0.0, "T1", 0, 0, 0, 0
if 'ac' not in ss:
    ss.ac, ss.ig = False, None

now = time.time()

# 2. CABECERA COMPACTA
c_logo, c_rival, c_fecha, c_res = st.columns([0.5, 2, 1.5, 1])
c_logo.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=40)
riv = c_rival.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()
fec = c_fecha.date_input("FECHA", datetime.now(), label_visibility="collapsed")
if c_res.button("RESET TOTAL", use_container_width=True):
    ss.clear()
    st.rerun()

# 3. MARCADOR Y RELOJ EN UNA FILA
m1, m2, m3, m4, m5 = st.columns([1.5, 1, 2, 1, 1.5])
with m1:
    st.markdown(f"### 🐸 LUD: {ss.ml}")
    if st.button("⚽ GOL", key="gl_l"): ss.ml += 1; st.rerun()
    if st.button(f"⚠️ F: {ss.fl}", key="fl_l"): ss.fl += 1; st.rerun()

with m3:
    tv = ss.rt1 if ss.pt == "T1" else ss.rt2
    if ss.ac and ss.ig: tv += now - ss.ig
    m, s = divmod(int(tv), 60)
    st.markdown(f"<h1 style='text-align:center; margin:0;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
    if st.button("▶/⏸", use_container_width=True, type="primary"):
        if not ss.ac:
            ss.ac, ss.ig = True, now
            for j in ss.js:
                if j["p"]: j["ini"] = now
        else:
            ss.ac = False
            if ss.pt=="T1": ss.rt1 += now - ss.ig
            else: ss.rt2 += now - ss.ig
            for j in ss.js:
                if j["p"] and j["ini"]:
                    if ss.pt=="T1": j["t1"] += now - j["ini"]
                    else: j["t2"] += now - j["ini"]
                    j["ini"] = None
            ss.ig = None
        st.rerun()

with m5:
    st.markdown(f"### 🏟️ {riv[:5]}: {ss.mr}")
    if st.button(f"⚽ GOL ", key="gl_r"): ss.mr += 1; st.rerun()
    if st.button(f"⚠️ F: {ss.fr}", key="fl_r"): ss.fr += 1; st.rerun()

# 4. CONTADOR PISTA
ep = sum(1 for j in ss.js if j["p"])
st.markdown(f"<p style='text-align:center; background:#eee; margin:0;'><b>PISTA: {ep}/5</b></p>", unsafe_allow_html=True)

# 5. LISTA DE JUGADORES (3 COLUMNAS PARA AHORRAR ESPACIO VERTICAL)
st.write("")
cols_j = st.columns(3)
for i, j in enumerate(ss.js):
    with cols_j[i % 3]:
        st.markdown(f"<div class='jugador-box' style='border-left: 5px solid {'#003D7A' if j['p'] else '#ccc'};'>", unsafe_allow_html=True)
        
        # Fila 1: Nombre y Tiempo
        c_n, c_t = st.columns([2, 1])
        j["n"] = c_n.text_input(f"n{i}", j["n"], key=f"n{i}", label_visibility="collapsed")
        
        tj = j["t1"] + j["t2"]
        if ss.ac and j["p"] and j["ini"]: tj += now - j["ini"]
        mj, sj = divmod(int(tj), 60)
        c_t.write(f"⏱{mj:02d}:{sj:02d}")
        
        # Fila 2: Scouting y Cambio
        s1, s2, s3, s4, c_btn = st.columns([1,1,1,1,1.5])
        if s1.button(f"🎯{j['t']}", key=f"t{i}"): j["t"]+=1; st.rerun()
        if s2.button(f"🛡️{j['rec']}", key=f"r{i}"): j["rec"]+=1; st.rerun()
        if s3.button(f"❌{j['per']}", key=f"p{i}"): j["per"]+=1; st.rerun()
        if s4.button(f"⚽{j['g']}", key=f"g{i}"): j["g"]+=1; ss.ml+=1; st.rerun()
        
        txt = "🔴" if j["p"] else "🟢"
        if c_btn.button(txt, key=f"bt{i}", use_container_width=True):
            if not j["p"] and ep < 5:
                j["p"] = True
                if ss.ac: j["ini"] = now
            elif j["p"]:
                if ss.ac and j["ini"]:
                    if ss.pt=="T1": j["t1"] += now - j["ini"]
                    else: j["t2"] += now - j["ini"]
                j["p"], j["ini"] = False, None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# 6. EXPORTAR
if st.button("💾 DESCARGAR CSV", use_container_width=True):
    df = pd.DataFrame([{"Jugador":x["n"],"G":x["g"],"T":x["t"],"R":x["rec"],"P":x["per"]} for x in ss.js])
    st.download_button("CONFIRMAR", df.to_csv(index=False).encode('utf-8'), f"LUD_{riv}.csv", "text/csv")
