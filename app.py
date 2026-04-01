import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD FS - Match Center", layout="wide")
st_autorefresh(interval=1000, key="f5")
ss = st.session_state

# --- CSS PRO: LIMPIO Y MODERNO ---
st.markdown("""
    <style>
    /* Fondo y tipografía */
    .stApp { background-color: #f8f9fa; color: #1e1e1e; }
    
    /* Contenedor de Jugador */
    .jugador-card {
        background: white;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    /* Cabecera compacta */
    .block-container { padding-top: 1rem !important; }
    
    /* Estilo de los botones de estadísticas */
    .stButton>button {
        border: none;
        border-radius: 6px;
        background-color: #f1f3f5;
        color: #495057;
        font-size: 0.85rem !important;
        transition: background 0.2s;
        height: 2.2rem;
    }
    .stButton>button:hover { background-color: #e9ecef; border: none; }
    
    /* Botón de Entrada/Salida (Círculo) */
    .pista-btn-on { background-color: #2b8a3e !important; color: white !important; }
    .pista-btn-off { background-color: #adb5bd !important; color: white !important; }

    /* Marcador Central */
    .marcador-container {
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* Quitar espacios de Streamlit */
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
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

# 2. HEADER: DATOS PARTIDO
h1, h2, h3, h4 = st.columns([0.6, 2, 1.5, 1])
h1.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/1200px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png", width=50)
riv = h2.text_input("RIVAL", "RIVAL", label_visibility="collapsed").upper()
fec = h3.date_input("FECHA", datetime.now(), label_visibility="collapsed")
if h4.button("RESET TOTAL", use_container_width=True):
    ss.clear()
    st.rerun()

# 3. BLOQUE CENTRAL: MARCADOR Y RELOJ
m1, m2, m3 = st.columns([1, 1.2, 1])

with m1:
    st.markdown(f"<div style='text-align:center;'><b>🐸 LEVANTE UD</b><br><h1 style='color:#003D7A; margin:0;'>{ss.ml}</h1></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("⚽ GOL", key="gl_l"): ss.ml += 1; st.rerun()
    if c2.button(f"⚠️ F: {ss.fl}", key="fl_l"): ss.fl += 1; st.rerun()

with m2:
    tv = ss.rt1 if ss.pt == "T1" else ss.rt2
    if ss.ac and ss.ig: tv += now - ss.ig
    m, s = divmod(int(tv), 60)
    st.markdown(f"<div class='marcador-container'><h1 style='font-family:monospace; font-size:3.5rem; margin:0;'>{m:02d}:{s:02d}</h1></div>", unsafe_allow_html=True)
    if st.button("▶ / ⏸", use_container_width=True, type="primary"):
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

with m3:
    st.markdown(f"<div style='text-align:center;'><b>🏟️ {riv[:10]}</b><br><h1 style='color:#7A0019; margin:0;'>{ss.mr}</h1></div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    if c3.button("⚽ GOL", key="gl_r"): ss.mr += 1; st.rerun()
    if c4.button(f"⚠️ F: {ss.fr}", key="fl_r"): ss.fr += 1; st.rerun()

# 4. INDICADOR PISTA
ep = sum(1 for j in ss.js if j["p"])
st.markdown(f"<div style='text-align:center; font-size:0.8rem; color:#666;'>PISTA: <b>{ep}/5</b></div>", unsafe_allow_html=True)

# 5. GRID DE JUGADORES (3 COLUMNAS)
cols_j = st.columns(3)
for i, j in enumerate(ss.js):
    with cols_j[i % 3]:
        # Borde lateral cambia según si está en pista
        color_borde = "#003D7A" if j["p"] else "#f1f3f5"
        st.markdown(f"<div class='jugador-card' style='border-left: 6px solid {color_borde};'>", unsafe_allow_html=True)
        
        # Nombre y Tiempo
        c_n, c_t = st.columns([1.5, 1])
        j["n"] = c_n.text_input(f"n{i}", j["n"], key=f"n{i}", label_visibility="collapsed")
        
        tj = j["t1"] + j["t2"]
        if ss.ac and j["p"] and j["ini"]: tj += now - j["ini"]
        mj, sj = divmod(int(tj), 60)
        c_t.markdown(f"<div style='text-align:right; font-size:0.9rem;'>⏱ {mj:02d}:{sj:02d}</div>", unsafe_allow_html=True)
        
        # Scouting
        s1, s2, s3, s4, s5 = st.columns([1,1,1,1,1.2])
        if s1.button(f"🎯{j['t']}", key=f"t{i}"): j["t"]+=1; st.rerun()
        if s2.button(f"🛡️{j['rec']}", key=f"r{i}"): j["rec"]+=1; st.rerun()
        if s3.button(f"❌{j['per']}", key=f"p{i}"): j["per"]+=1; st.rerun()
        if s4.button(f"⚽{j['g']}", key=f"g{i}"): j["g"]+=1; ss.ml+=1; st.rerun()
        
        # Botón de Pista
        if s5.button("PISTA", key=f"bt{i}"):
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

# 6. FOOTER
st.markdown("---")
if st.button("💾 DESCARGAR INFORME CSV", use_container_width=True):
    df = pd.DataFrame([{"Jugador":x["n"],"G":x["g"],"T":x["t"],"R":x["rec"],"P":x["per"]} for x in ss.js])
    st.download_button("CONFIRMAR DESCARGA", df.to_csv(index=False).encode('utf-8'), f"LUD_{riv}.csv", "text/csv")
