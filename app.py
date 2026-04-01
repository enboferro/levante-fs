import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Configuración de la página (Colores Levante UD)
st.set_page_config(page_title="Levante UD FS - Control", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 60px; font-size: 20px; font-weight: bold; }
    .pista { background-color: #28a745 !important; color: white !important; }
    .banquillo { background-color: #ff4d4d !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Inicializar estados si no existen
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = [
        {"id": i, "nombre": f"Jugador {i+1}", "total": 0.0, "inicio": None, "pista": False, "ent": 0}
        for i in range(14)
    ]
if 'activo' not in st.session_state:
    st.session_state.activo = False

# --- CABECERA ---
st.title("🐸 Levante UD FS - Control de Minutos")
col_info1, col_info2 = st.columns(2)
with col_info1:
    rival = st.text_input("Rival:", "Rival")
with col_info2:
    st.write(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y')}")

# --- BOTÓN DE PARTIDO ---
if not st.session_state.activo:
    if st.button("▶ INICIAR PARTIDO"):
        st.session_state.activo = True
        t = time.time()
        for j in st.session_state.jugadores:
            if j["pista"]: j["inicio"] = t
        st.rerun()
else:
    if st.button("⏸ PAUSAR PARTIDO"):
        st.session_state.activo = False
        t = time.time()
        for j in st.session_state.jugadores:
            if j["pista"] and j["inicio"]:
                j["total"] += t - j["inicio"]
                j["inicio"] = None
        st.rerun()

st.divider()

# --- LISTA DE JUGADORES ---
for i in range(0, 14, 2): # Filas de 2 jugadores para el iPad
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        j_idx = i + idx
        j = st.session_state.jugadores[j_idx]
        
        with col:
            with st.container(border=True):
                # Editar nombre
                j["nombre"] = st.text_input(f"Nombre {j_idx+1}", j["nombre"], key=f"name_{j_idx}")
                
                # Tiempo actual
                tt = j["total"]
                if st.session_state.activo and j["pista"] and j["inicio"]:
                    tt += time.time() - j["inicio"]
                mins, secs = divmod(int(tt), 60)
                
                st.subheader(f"⏱ {mins:02d}:{secs:02d}")
                st.write(f"Rotaciones: {j['ent']}")
                
                # Botón de cambio
                label = "EN PISTA" if j["pista"] else "BANQUILLO"
                if st.button(label, key=f"btn_{j_idx}"):
                    t = time.time()
                    if not j["pista"]:
                        j["pista"], j["ent"] = True, j["ent"] + 1
                        if st.session_state.activo: j["inicio"] = t
                    else:
                        if st.session_state.activo and j["inicio"]:
                            j["total"] += t - j["inicio"]
                        j["pista"], j["inicio"] = False, None
                    st.rerun()

# --- EXPORTAR ---
st.divider()
if st.button("💾 GENERAR RESUMEN EXCEL"):
    data = [{"Jugador": j["nombre"], "Minutos": round(j["total"]/60, 2), "Rot": j["ent"]} for j in st.session_state.jugadores]
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Archivo", csv, f"LUD_vs_{rival}.csv", "text/csv")
