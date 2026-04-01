import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="LUD FS", layout="wide")

# Estilos para números oscuros
st.markdown("<style>h1,h2,h3,p{color:black!important;}</style>",unsafe_allow_html=True)

if 'js' not in st.session_state:
    st.session_state.js = [{"id":i,"n":f"Jug {i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0} for i in range(14)]
if 'pt' not in st.session_state: st.session_state.pt = "T1"
if 'ml' not in st.session_state: st.session_state.ml = 0
if 'mr' not in st.session_state: st.session_state.mr = 0
if 'fl' not in st.session_state: st.session_state.fl = 0
if 'fr' not in st.session_state: st.session_state.fr = 0
if 'ac' not in st.session_state: st.session_state.ac = False

st.title("🐸 LUD FS - Control")

# Marcador y Faltas
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader(f"LUD: {st.session_state.ml}")
    if st.button("+GOL LUD"): st.session_state.ml+=1; st.rerun()
    st.write(f"Faltas: {st.session_state.fl}")
    if st.button("+FL"): st.session_state.fl+=1; st.rerun()
with c2:
    st.session_state.pt = st.radio("Parte:",["T1","T2"])
    if st.button("RESET"): st.session_state.clear(); st.rerun()
with c3:
    st.subheader(f"RIV: {st.session_state.mr}")
    if st.button("+GOL RIV"): st.session_state.mr+=1; st.rerun()
    st.write(f"Faltas: {st.session_state.fr}")
    if st.button("+FR"): st.session_state.fr+=1; st.rerun()

st.divider()

# Botón Play/Pausa
if not st.session_state.ac:
    if st.button("▶ INICIAR RELOJ"):
        st.session_state.ac = True
        now = time.time()
        for j in st.session_state.js:
            if j["p"]: j["ini"] = now
        st.rerun()
else:
    if st.button("⏸ PAUSAR RELOJ"):
        st.session_state.ac = False
        now = time.time()
        for j in st.session_state.js:
            if j["p"] and j["ini"]:
                if st.session_state.pt == "T1": j["t1"] += now - j["ini"]
                else: j["t2"] += now - j["ini"]
                j["ini"] = None
        st.rerun()

# Jugadores
for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        j = st.session_state.js[ji]
        with col:
            with st.container(border=True):
                j["n"] = st.text_input("Nombre:", j["n"], key=f"n{ji}")
                
                # Tiempo Vivo
                tt = j["t1"] if st.session_state.pt == "T1" else j["t2"]
                if st.session_state.ac and j["p"] and j["ini"]:
                    tt += time.time() - j["ini"]
                
                mm, ss = divmod(int(tt), 60)
                st.subheader(f"⏱ {mm:02d}:{ss:02d}")
                
                c_g, c_e = st.columns(2)
                if c_g.button(f"⚽ {j['g']}", key=f"g{ji}"):
                    j["g"]+=1; st.session_state.ml+=1; st.rerun()
                
                txt = "🔴 SALIR" if j["p"] else "🟢 ENTRAR"
                if c_e.button(txt, key=f"b{ji}"):
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

st.divider()
if st.button("💾 EXCEL"):
    df = pd.DataFrame([{"Nom": x["n"], "T1": round(x["t1"]/60,2), "T2": round(x["t2"]/60,2), "G": x["g"]} for x in st.session_state.js])
    st.download_button("Descargar", df.to_csv(index=False).encode('utf-8'), "partido.csv", "text/csv")
