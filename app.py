import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="LUD ELITE", layout="wide")

# CONFIGURACIÓN: Autorefresh cada 1 segundo para el tiempo real
st_autorefresh(interval=1000, key="datarefresh")

ss = st.session_state

# 1. DATA (Inicialización)
if 'js' not in ss:
    ss.js = [{"id":i,"n":f"J{i+1}","t1":0.0,"t2":0.0,"ini":None,"p":False,"e":0,"g":0,"t":0,"per":0,"rec":0} for i in range(14)]
if 'rt1' not in ss: ss.rt1, ss.rt2, ss.pt = 0.0, 0.0, "T1"
if 'ml' not in ss: ss.ml, ss.mr, ss.fl, ss.fr = 0, 0, 0, 0
if 'ac' not in ss: ss.ac, ss.ig = False, None

# 2. MARCADOR
st.title("🐸 LUD FS - Panel de Élite")
c1, c2, c3 = st.columns(3)
with c1:
    st.header(f"LUD: {ss.ml}")
    if st.button("⚽ +GOL LUD"): ss.ml+=1; st.rerun()
    st.write(f"Faltas: {ss.fl}")
    if st.button("➕ FALTA LUD"): ss.fl+=1; st.rerun()
with c2:
    ss.pt = st.radio("Parte:",["T1","T2"], horizontal=True)
    if st.button("🔄 RESET"): ss.clear(); st.rerun()
with c3:
    st.header(f"RIV: {ss.mr}")
    if st.button("⚽ +GOL RIV"): ss.mr+=1; st.rerun()
    st.write(f"Faltas: {ss.fr}")
    if st.button("➕ FALTA RIV"): ss.fr+=1; st.rerun()

# 3. RELOJ DE JUEGO (TIEMPO REAL)
tg = ss.rt1 if ss.pt=="T1" else ss.rt2
if ss.ac and ss.ig: tg += time.time() - ss.ig
m, s = divmod(int(tg), 60)

cx, cy = st.columns(2)
with cx:
    if not ss.ac:
        if st.button("▶ START RELOJ", type="primary", use_container_width=True):
            ss.ac, now = True, time.time()
            ss.ig = now
            for j in ss.js:
                if j["p"]: j["ini"] = now
            st.rerun()
    else:
        if st.button("⏸ STOP RELOJ", type="secondary", use_container_width=True):
            ss.ac, now = False, time.time()
            if ss.pt=="T1": ss.rt1 += now - ss.ig
            else: ss.rt2 += now - ss.ig
            for j in ss.js:
                if j["p"] and j["ini"]:
                    if ss.pt=="T1": j["t1"] += now - j["ini"]
                    else: j["t2"] += now - j["ini"]
                    j["ini"] = None
            ss.ig = None; st.rerun()
with cy:
    st.markdown(f"<h1 style='text-align:center; color:red; font-size:60px;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)

# 4. PISTA Y SEMÁFORO
ep = sum(1 for j in ss.js if j["p"])
st.subheader(f"En Pista: {ep}/5")

for i in range(0, 14, 2):
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        ji = i + idx
        if ji >= 14: break
        j = ss.js[ji]
        with col:
            # Lógica de color de fatiga (Tiempo en el tramo actual)
            t_tramo = 0
            if j["p"] and j["ini"] and ss.ac:
                t_tramo = time.time() - j["ini"]
            
            # Definir color según fatiga (segundos)
            color_fatiga = "#000000" # Negro defecto
            if t_tramo > 360: color_fatiga = "#FF0000" # Rojo (+6 min)
            elif t_tramo > 240: color_fatiga = "#FF9900" # Naranja (+4 min)
            elif j["p"]: color_fatiga = "#28a745" # Verde (En pista fresco)

            with st.container(border=True):
                j["n"] = st.text_input("Nombre:", j["n"], key=f"n{ji}")
                
                # Tiempo total acumulado en vivo
                tj = j["t1"] if ss.pt=="T1" else j["t2"]
                if ss.ac and j["p"] and j["ini"]: tj += time.time() - j["ini"]
                mm, ss_j = divmod(int(tj), 60)
                
                # Visualización con Semáforo
                st.markdown(f"""
                <div style="padding:5px; border-radius:5px;">
                    <span style="font-size:20px; font-weight:bold;">⏱ {mm:02d}:{ss_j:02d}</span>
                    <span style="color:{color_fatiga}; font-size:24px; margin-left:20px;">●</span>
                    <span style="font-size:14px; color:gray; float:right;">Goles: {j['g']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Scouting
                ca, cb, cc = st.columns(3)
                if ca.button(f"🎯T:{j['t']}", key=f"t{ji}"): j["t"]+=1; st.rerun()
                if cb.button(f"⚠️P:{j['per']}", key=f"p{ji}"): j["per"]+=1; st.rerun()
                if cc.button(f"🛡️R:{j['rec']}", key=f"r{ji}"): j["rec"]+=1; st.rerun()
                
                # Cambio
                txt = "🔴 SALIR" if j["p"] else "🟢 ENTRAR"
                if st.button(txt, key=f"en{ji}", use_container_width=True):
                    now = time.time()
                    if not j["p"] and ep < 5:
                        j["p"], j["e"] = True, j["e"]+1
                        if ss.ac: j["ini"] = now
                        st.rerun()
                    elif j["p"]:
                        if ss.ac and j["ini"]:
                            if ss.pt=="T1": j["t1"] += now - j["ini"]
                            else: j["t2"] += now - j["ini"]
                        j["p"], j["ini"] = False, None; st.rerun()
                    else: st.toast("¡Ya hay 5!")

st.divider()
if st.button("💾 DESCARGAR EXCEL"):
    df = pd.DataFrame([{"J":x["n"],"Min":round((x["t1"]+x["t2"])/60,1),"G":x["g"],"T":x["t"],"P":x["per"],"R":x["rec"]} for x in ss.js])
    st.download_button("Bajar CSV", df.to_csv(index=False).encode('utf-8'), "stats.csv", "text/csv")
