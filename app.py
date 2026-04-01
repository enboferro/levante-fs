import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="LUD FS PRO", layout="wide")
st.markdown("<style>h1,h2,h3,p{color:black!important; font-weight:bold;}</style>",unsafe_allow_html=True)

# Inicializar datos (Minutos, Goles, Tiros, Pérdidas, Recuperaciones)
if 'js' not in st.session_state:
    st.session_state.js = [{"id":i,"n":f"Jug {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'pt' not in st.session_state: st.session_state.pt = "T1"
if 'ml' not in st.session_state: st.session_state.ml = 0
if 'mr' not in st.session_state: st.session_state.mr = 0
if 'fl' not in st.session_state: st.session_state.fl = 0
if 'fr' not in st.session_state: st.session_state.fr = 0
if 'ac' not in st.session_state: st.session_state.ac = False

# --- MARCADOR Y FALTAS ---
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader(f"LUD: {st.session_state.ml}")
    if st.button("+GOL LUD"): st.session_state.ml+=1; st.rerun()
    st.write(f"Faltas LUD: {st.session_state.fl}")
    if st.button("+FALTA LUD"): st.session_state.fl+=1; st.rerun()
with c2:
    st.session_state.pt = st.radio("Tiempo:",["T1","T2"])
    if st.button("RESET PARTIDO"): st.session_state.clear(); st.rerun()
with c3:
    st.subheader(f"RIV: {st.session_state.mr}")
    if st.button("+GOL RIV"): st.session_state.mr+=1; st.rerun()
    st.write(f"Faltas RIV: {st.session_state.fr}")
    if st.button("+FALTA RIV"): st.session_state.fr+=1; st.rerun()

# --- RELOJ ---
st.divider()
if not st.session_state.ac:
    if st.button("▶ INICIAR RELOJ", type="primary"):
        st.session_state.ac, now = True, time.time()
        for j in st.session_state.js:
            if j["p"]: j["ini"] = now
        st.rerun()
else:
    if st.button("⏸ PAUSAR RELOJ", type="secondary"):
        st.session_state.ac, now = False, time.time()
        for j in st.session_state.js:
            if j["p"] and j["ini"]:
                if st.session_state.pt == "T1": j["t1"] += now - j["ini"]
                else: j["t2"] += now - j["ini"]
                j["ini"] = None
        st.rerun()

# --- JUGADORES ---
for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        j = st.session_state.js[ji]
        with col:
            with st.container(border=True):
                j["n"] = st.text_input("Nombre:", j["n"], key=f"n{ji}")
                
                # Tiempo y Goles
                tt = (j["t1"] if st.session_state.pt == "T1" else j["t2"])
                if st.session_state.ac and j["p"] and j["ini"]: tt += time.time() - j["ini"]
                mm, ss = divmod(int(tt), 60)
                
                st.subheader(f"⏱ {mm:02d}:{ss:02d} | ⚽ {j['g']}")
                
                # Acciones rápidas (Tiros, Perdidas, Recup)
                ca, cb, cc = st.columns(3)
                if ca.button(f"🎯 {j['t']}", key=f"t{ji}"): j["t"]+=1; st.rerun()
                if cb.button(f"⚠️ {j['per']}", key=f"p{ji}"): j["per"]+=1; st.rerun()
                if cc.button(f"🛡️ {j['rec']}", key=f"r{ji}"): j["rec"]+=1; st.rerun()
                
                # Botones de juego
                c1, c2 = st.columns(2)
                if c1.button("⚽ GOL", key=f"go{ji}"):
                    j["g"]+=1; st.session_state.ml+=1; st.rerun()
                
                txt = "🔴 SALIR" if j["p"] else "🟢 ENTRAR"
                if c2.button(txt, key=f"en{ji}"):
                    now = time.time()
                    if not j["p"]:
                        j["p"], j["e"] = True, j["e"] + 1
                        if st.session_state.ac: j["ini"] = now
                    else:
                        if st.session_state.ac and j["ini"]:
                            if st.session_state.pt == "T1": j["t1"] += now - j["ini"]
                            else: j["t2"] += now - j["ini"]
                        j["p"], j["ini"] = False, None
                    st.rerun()

# --- EXPORTAR ---
st.divider()
if st.button("💾 DESCARGAR EXCEL"):
    df = pd.DataFrame([{"Jug":x["n"],"Min":round((x["t1"]+x["t2"])/60,1),"G":x["g"],"Tiros":x["t"],"Perd":x["per"],"Rec":x["rec"]} for x in st.session_state.js])
    st.download_button("Click aquí", df.to_csv(index=False).encode('utf-8'), "estadisticas.csv", "text/csv")
